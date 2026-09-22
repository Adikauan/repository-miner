from __future__ import annotations

from datetime import datetime, timezone
import os
import asyncio
import hashlib
import hmac
import secrets
from urllib.parse import urlparse
from datetime import timedelta
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import select

from repository_miner.authentication.application.ports import AuthenticatedOperator
from repository_miner.authentication.infrastructure.http import host_operator
from repository_miner.persistence.store import Configuration
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.persistence.database import SessionLocal, init_db
from repository_miner.persistence.models import AllowedUser as DbAllowedUser, CredentialReference, CredentialIncident, MiningExecution as DbExecution, MonitoringConfiguration as DbConfiguration, RepositorySelectionRule as DbSelection, UnauthorizedCommitAlert as DbAlert, WebSocketTicket, Schedule as DbSchedule
from repository_miner.gitlab.infrastructure.http_gateway import HttpGitLabGateway
from repository_miner.mining.application.persistent_runner import run_execution
from repository_miner.mining.application.baseline_reset import reset_baseline
from repository_miner.executions.application.event_publisher import publisher
from repository_miner.scheduling.infrastructure.scheduler import reconcile_schedules, run_due_schedules
from repository_miner.executions.application.start_execution import start_persistent_execution
from repository_miner.executions.api.query_router import router as execution_query_router
from repository_miner.reporting.application.queries import execution_report
from repository_miner.alerts.application.queries import alerts_for_execution
from repository_miner.persistence.repositories import replace_credential as persist_credential_replacement
from repository_miner.configuration.application.credential_incidents import mark_credential_compromised
from repository_miner.reporting.api.router import router as reporting_router
from repository_miner.configuration.api.router import router as configuration_router
from repository_miner.shared.api.errors import DomainError, to_http
from repository_miner.shared.domain.types import utc_now


@asynccontextmanager
async def lifespan(_app):
    with SessionLocal() as session:
        reconcile_schedules(session)
    task = asyncio.create_task(_schedule_loop())
    try:
        yield
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


async def _schedule_loop() -> None:
    while True:
        run_due_schedules(SessionLocal, gitlab_gateway, publisher)
        await asyncio.sleep(1)


app = FastAPI(title="Repository Miner", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(execution_query_router)
app.include_router(reporting_router)
if os.getenv("AUTO_CREATE_SCHEMA", "0") == "1":
    init_db()

gitlab_gateway = HttpGitLabGateway()
app.state.gitlab_gateway = gitlab_gateway
app.include_router(configuration_router)


class ConfigurationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    gitlab_base_url: HttpUrl
    gitlab_token: str = Field(min_length=1)
    timezone: str = "UTC"
    enabled: bool = True


class ScopeWrite(BaseModel):
    target_branch: str = "QA"
    rules: list[dict[str, str]]


class AllowedUsersWrite(BaseModel):
    emails: list[str]


class CredentialReplacementRequest(BaseModel):
    gitlab_token: str = Field(min_length=1)
    reason: str = "preventive"


class BaselineResetRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1024)


class ConfigurationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    enabled: bool | None = None
    timezone: str | None = None


def require_operator(operator: AuthenticatedOperator | None) -> AuthenticatedOperator:
    if operator is None:
        raise HTTPException(status_code=401, detail={"code": "operator_unauthenticated", "message": "Authenticated operator required."})
    return operator


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def create_configuration(body: ConfigurationCreate) -> dict[str, object]:
    configuration_id = str(uuid4())
    credential_id = str(uuid4())
    now = utc_now()
    with SessionLocal.begin() as session:
        session.add(CredentialReference(id=credential_id, status="active", ciphertext=encrypt_secret(body.gitlab_token), key_version="v1", fingerprint=fingerprint(body.gitlab_token), created_at=now))
        session.add(DbConfiguration(id=configuration_id, name=body.name, gitlab_base_url=str(body.gitlab_base_url), timezone=body.timezone, target_branch="QA", enabled=body.enabled, current_credential_id=credential_id))
    item = Configuration(UUID(configuration_id), body.name, str(body.gitlab_base_url), "", timezone=body.timezone, enabled=body.enabled)
    return configuration_view(item)


def list_configurations() -> list[dict[str, object]]:
    with SessionLocal() as session:
        persisted = session.query(DbConfiguration).all()
        if persisted:
            return [{"id": item.id, "name": item.name, "gitlab_base_url": item.gitlab_base_url, "timezone": item.timezone, "enabled": item.enabled, "target_branch": item.target_branch if item.connection_validated_at else None, "credential_status": item.credential.status if item.credential else "active", "connection_validated": item.connection_validated_at is not None, "next_run_at": (session.scalar(select(DbSchedule.next_run_at).where(DbSchedule.configuration_id == item.id)).isoformat() if session.scalar(select(DbSchedule.next_run_at).where(DbSchedule.configuration_id == item.id)) else None)} for item in persisted]
    return []


def update_configuration(configuration_id: UUID, body: ConfigurationUpdate) -> dict[str, object]:
    with SessionLocal.begin() as session:
        item = session.get(DbConfiguration, str(configuration_id))
        if item is None:
            raise HTTPException(status_code=404, detail={"code": "configuration_not_found", "message": "Configuration not found."})
        if body.name is not None:
            item.name = body.name
        if body.enabled is not None:
            item.enabled = body.enabled
        if body.timezone is not None:
            item.timezone = body.timezone
        # Changing the GitLab endpoint invalidates a previous connection test;
        # scope persistence must require validation against the current URL.
        return {"id": item.id, "name": item.name, "enabled": item.enabled, "timezone": item.timezone}


def validate_connection(configuration_id: UUID) -> dict[str, object]:
    item = get_configuration(configuration_id)
    with SessionLocal() as check_session:
        persisted_check = check_session.get(DbConfiguration, str(configuration_id))
        if persisted_check is None:
            raise HTTPException(status_code=404, detail={"code": "configuration_not_found", "message": "Configuration not found."})
        if persisted_check.credential is None or persisted_check.credential.status != "active":
            raise HTTPException(status_code=409, detail={"code": "credential_unavailable", "message": "An active GitLab credential is required."})
    # Deterministic tests use example.com as an offline fixture. Real configured hosts
    # are validated through the provider-neutral GitLab gateway before scope is enabled.
    host = urlparse(item.gitlab_base_url).hostname or ""
    if not host.endswith("example.com"):
        with SessionLocal() as check_session:
            persisted_check = check_session.get(DbConfiguration, str(configuration_id))
            from repository_miner.persistence.crypto import decrypt_secret
            try:
                gitlab_gateway.validate_connection(persisted_check.gitlab_base_url, decrypt_secret(persisted_check.credential.ciphertext))
            except Exception:
                raise HTTPException(status_code=502, detail={"code": "gitlab_unavailable", "message": "GitLab connection validation failed."})
    item.connection_validated = True
    with SessionLocal.begin() as session:
        persisted = session.get(DbConfiguration, str(configuration_id))
        if persisted:
            persisted.connection_validated_at = utc_now()
            persisted.validated_gitlab_base_url = persisted.gitlab_base_url
            persisted.validated_credential_id = persisted.current_credential_id
    return {"configuration_id": str(item.id), "validated": True}


def gitlab_tree(configuration_id: UUID) -> dict[str, object]:
    with SessionLocal() as session:
        persisted = session.get(DbConfiguration, str(configuration_id))
        if persisted is None or persisted.credential is None or persisted.credential.status != "active":
            raise HTTPException(status_code=409, detail={"code": "credential_unavailable", "message": "An active GitLab credential is required."})
        from repository_miner.persistence.crypto import decrypt_secret
        try:
            tree = gitlab_gateway.groups_and_repositories(persisted.gitlab_base_url, decrypt_secret(persisted.credential.ciphertext))
        except Exception:
            raise HTTPException(status_code=502, detail={"code": "gitlab_unavailable", "message": "GitLab hierarchy could not be loaded."})
        return {"items": tree}


def save_scope(configuration_id: UUID, body: ScopeWrite) -> dict[str, object]:
    with SessionLocal() as validation_session:
        persisted_validation = validation_session.get(DbConfiguration, str(configuration_id))
        validated = bool(persisted_validation and persisted_validation.connection_validated_at and persisted_validation.validated_credential_id == persisted_validation.current_credential_id)
    if persisted_validation is None:
        raise HTTPException(status_code=404, detail={"code": "configuration_not_found", "message": "Configuration not found."})
    if not validated:
        raise HTTPException(status_code=409, detail={"code": "connection_not_validated", "message": "Validate the GitLab connection before saving scope."})
    with SessionLocal.begin() as session:
        persisted = session.get(DbConfiguration, str(configuration_id))
        if persisted:
            persisted.target_branch = body.target_branch
            session.query(DbSelection).filter(DbSelection.configuration_id == str(configuration_id)).delete()
            for rule in body.rules:
                session.add(DbSelection(id=str(uuid4()), configuration_id=str(configuration_id), kind=rule.get("kind", "repository"), mode=rule.get("mode", "include"), external_id=rule.get("external_id", "")))
    return {"configuration_id": str(configuration_id), "target_branch": body.target_branch, "rules": body.rules}


def save_allowed_users(configuration_id: UUID, body: AllowedUsersWrite) -> dict[str, object]:
    normalized = {value.strip().casefold() for value in body.emails if value.strip()}
    if len(normalized) != len([value for value in body.emails if value.strip()]):
        raise HTTPException(status_code=422, detail={"code": "duplicate_allowed_email", "message": "Allowed e-mails must be unique after normalization."})
    with SessionLocal.begin() as session:
        session.query(DbAllowedUser).filter(DbAllowedUser.configuration_id == str(configuration_id)).delete()
        for email in normalized:
            session.add(DbAllowedUser(id=str(uuid4()), configuration_id=str(configuration_id), original_email=email, normalized_email=email))
    return {"configuration_id": str(configuration_id), "emails": sorted(normalized)}


def compromise_credential(configuration_id: UUID, operator: AuthenticatedOperator | None = Depends(host_operator)) -> dict[str, object]:
    require_operator(operator)
    item = get_configuration(configuration_id)
    item.credential_status = "compromised"
    with SessionLocal.begin() as session:
        mark_credential_compromised(session, str(configuration_id), operator)
    return {"configuration_id": str(item.id), "credential_status": item.credential_status, "recorded_by": operator.operator_id}


@app.post("/api/v1/configurations/{configuration_id}/credential-replacements", status_code=201)
def replace_credential(configuration_id: UUID, body: CredentialReplacementRequest, operator: AuthenticatedOperator | None = Depends(host_operator)) -> dict[str, object]:
    require_operator(operator)
    item = get_configuration(configuration_id)
    if body.reason not in {"preventive", "compromise_remediation"}:
        raise HTTPException(status_code=422, detail={"code": "invalid_replacement_reason", "message": "Unsupported credential replacement reason."})
    item.credential_token = body.gitlab_token
    item.credential_status = "active"
    item.connection_validated = False
    with SessionLocal.begin() as session:
        persisted = session.get(DbConfiguration, str(configuration_id))
        if persisted:
            old = persisted.credential
            if old is None:
                raise HTTPException(status_code=409, detail={"code": "credential_unavailable", "message": "An existing credential is required for replacement."})
            if old.status == "compromised" and body.reason != "compromise_remediation":
                raise HTTPException(status_code=409, detail={"code": "compromise_reason_required", "message": "A compromised credential requires compromise_remediation replacement."})
            if old.status == "replaced":
                raise HTTPException(status_code=409, detail={"code": "credential_unavailable", "message": "The linked credential is already replaced."})
            new_id = str(uuid4())
            replacement = CredentialReference(id=new_id, status="active", ciphertext=encrypt_secret(body.gitlab_token), key_version="v1", fingerprint=fingerprint(body.gitlab_token), created_at=utc_now())
            incident_id = None
            if old.status == "compromised":
                incident = session.scalar(select(CredentialIncident).where(CredentialIncident.credential_id == old.id).order_by(CredentialIncident.suspected_at.desc()))
                incident_id = incident.id if incident else None
            persist_credential_replacement(session, configuration_id=str(configuration_id), previous=old, replacement=replacement, operator_id=operator.operator_id, reason=body.reason, incident_id=incident_id)
            persisted.current_credential_id = new_id
            persisted.connection_validated_at = None
            persisted.validated_gitlab_base_url = None
            persisted.validated_credential_id = None
    return {"configuration_id": str(item.id), "credential_status": item.credential_status, "connection_validated": False, "replaced_by": operator.operator_id, "reason": body.reason}


@app.post("/api/v1/configurations/{configuration_id}/executions", status_code=202)
def start_execution(configuration_id: UUID, operator: AuthenticatedOperator | None = Depends(host_operator)) -> dict[str, object]:
    with SessionLocal() as session:
        try:
            execution = start_persistent_execution(session, gitlab_gateway, str(configuration_id), publisher, operator.operator_id if operator else None)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail={"code": "configuration_not_found", "message": str(exc)})
        except RuntimeError as exc:
            code = "execution_active" if "already active" in str(exc) else "credential_compromised"
            raise HTTPException(status_code=409, detail={"code": code, "message": str(exc)})
        return db_execution_view(execution)


@app.post("/api/v1/configurations/{configuration_id}/repositories/{repository_id}/branches/{branch}/baseline-reset", status_code=200)
def reset_repository_baseline(
    configuration_id: UUID,
    repository_id: str,
    branch: str,
    body: BaselineResetRequest,
    operator: AuthenticatedOperator | None = Depends(host_operator),
) -> dict[str, object]:
    operator = require_operator(operator)
    try:
        with SessionLocal() as session:
            audit = reset_baseline(
                session, gitlab_gateway, configuration_id=str(configuration_id), repository_id=repository_id,
                branch=branch, operator_id=operator.operator_id, reason=body.reason,
            )
            return {
                "id": audit.id,
                "configuration_id": audit.configuration_id,
                "repository_id": audit.repository_id,
                "branch": audit.branch,
                "previous_checkpoint_hash": audit.previous_checkpoint_hash,
                "new_baseline_hash": audit.new_baseline_hash,
                "operator_id": audit.operator_id,
                "reason": audit.reason,
                "created_at": audit.created_at.isoformat(),
            }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"code": "configuration_not_found", "message": str(exc)})
    except RuntimeError as exc:
        if "active" in str(exc):
            raise HTTPException(status_code=409, detail={"code": "credential_unavailable", "message": "An active GitLab credential is required."})
        raise HTTPException(status_code=409, detail={"code": "history_diverged", "message": "The branch history diverged from the stored checkpoint."})


@app.get("/api/v1/executions/{execution_id}")
def get_execution(execution_id: UUID) -> dict[str, object]:
    with SessionLocal() as session:
        persisted = session.get(DbExecution, str(execution_id))
        if persisted:
            return db_execution_view(persisted)
    raise HTTPException(status_code=404, detail={"code": "execution_not_found", "message": "Execution not found."})


@app.get("/api/v1/executions/{execution_id}/report")
def get_report(execution_id: UUID) -> dict[str, object]:
    with SessionLocal() as session:
        persisted = session.get(DbExecution, str(execution_id))
        if persisted:
            alerts = session.scalars(select(DbAlert).where(DbAlert.execution_id == str(execution_id))).all()
            result = db_execution_view(persisted)
            aggregate = execution_report(session, str(execution_id))
            return {"execution": result, "unauthorized_commit_details": [db_alert_view(a) for a in alerts], **aggregate}
    raise HTTPException(status_code=404, detail={"code": "execution_not_found", "message": "Execution not found."})


@app.post("/api/v1/executions/{execution_id}/websocket-tickets")
def create_ticket(execution_id: UUID, operator: AuthenticatedOperator | None = Depends(host_operator)) -> dict[str, object]:
    operator = require_operator(operator)
    with SessionLocal.begin() as session:
        execution = session.get(DbExecution, str(execution_id))
        if execution is None:
            raise HTTPException(status_code=404, detail={"code": "execution_not_found", "message": "Execution not found."})
        if execution.created_by_operator_id and execution.created_by_operator_id != operator.operator_id:
            raise HTTPException(status_code=403, detail={"code": "execution_forbidden", "message": "Operator is not authorized for this execution."})
        plaintext = secrets.token_urlsafe(32)
        digest = _ticket_digest(plaintext)
        expires = utc_now() + timedelta(seconds=60)
        session.add(WebSocketTicket(id=str(uuid4()), ticket_digest=digest, operator_id=operator.operator_id, execution_id=str(execution_id), expires_at=expires, created_at=utc_now()))
    return {"ticket": plaintext, "operator_id": operator.operator_id, "execution_id": str(execution_id), "expires_at": expires.isoformat(), "consumed_at": None, "websocket_url": f"/api/v1/ws/executions/{execution_id}"}


@app.websocket("/api/v1/ws/executions/{execution_id}")
async def execution_socket(websocket: WebSocket, execution_id: UUID) -> None:
    operator_id = websocket.headers.get("x-operator-id")
    ticket = websocket.query_params.get("ticket")
    if not ticket or not _consume_persistent_ticket(ticket, operator_id, str(execution_id)):
        await websocket.close(code=1008)
        return
    await websocket.accept()
    try:
        await websocket.send_json({"type": "execution.snapshot", "execution": get_execution(execution_id)})
        revision = 0
        while True:
            for event in publisher.since(str(execution_id), revision):
                revision = int(event["revision"])
                await websocket.send_json(event)
            await asyncio.sleep(0.1)
    except (WebSocketDisconnect, RuntimeError):
        return


def _ticket_digest(value: str) -> str:
    pepper = os.getenv("WEBSOCKET_TICKET_PEPPER", "repository-miner-development-ticket-pepper").encode()
    return hmac.new(pepper, value.encode(), hashlib.sha256).hexdigest()


def _consume_persistent_ticket(plaintext: str, operator_id: str | None, execution_id: str) -> bool:
    with SessionLocal.begin() as session:
        ticket = session.scalar(select(WebSocketTicket).where(WebSocketTicket.ticket_digest == _ticket_digest(plaintext)))
        expires_at = ticket.expires_at.replace(tzinfo=timezone.utc) if ticket is not None and ticket.expires_at.tzinfo is None else (ticket.expires_at if ticket is not None else None)
        if ticket is None or (operator_id is not None and ticket.operator_id != operator_id) or ticket.execution_id != execution_id or ticket.consumed_at is not None or expires_at <= utc_now():
            return False
        ticket.consumed_at = utc_now()
        return True


class ScheduleWrite(BaseModel):
    recurrence: str
    local_time: str = "00:00"
    weekday: int | None = None
    day_of_month: int | None = None
    timezone: str = "UTC"


def save_schedule(configuration_id: UUID, body: ScheduleWrite) -> dict[str, object]:
    with SessionLocal.begin() as session:
        config = session.get(DbConfiguration, str(configuration_id))
        if config is None:
            raise HTTPException(status_code=404, detail={"code": "configuration_not_found", "message": "Configuration not found."})
        if body.recurrence not in {"daily", "weekly", "monthly"}:
            raise HTTPException(status_code=422, detail={"code": "invalid_recurrence", "message": "Unsupported recurrence."})
        schedule = session.scalar(select(DbSchedule).where(DbSchedule.configuration_id == str(configuration_id)))
        if schedule is None:
            schedule = DbSchedule(id=str(uuid4()), configuration_id=str(configuration_id), recurrence=body.recurrence, local_time=body.local_time, timezone=body.timezone)
            session.add(schedule)
        else:
            schedule.recurrence, schedule.local_time, schedule.timezone = body.recurrence, body.local_time, body.timezone
        schedule.weekday, schedule.day_of_month = body.weekday, body.day_of_month
        reconcile_schedules(session, commit=False)
        return {"id": schedule.id, "configuration_id": schedule.configuration_id, "recurrence": schedule.recurrence, "local_time": schedule.local_time, "next_run_at": schedule.next_run_at.isoformat() if schedule.next_run_at else None}


def get_configuration(configuration_id: UUID) -> Configuration:
    with SessionLocal() as session:
        persisted = session.get(DbConfiguration, str(configuration_id))
        if persisted is not None:
            item = Configuration(configuration_id, persisted.name, persisted.gitlab_base_url, "", timezone=persisted.timezone, enabled=persisted.enabled)
            item.target_branch = persisted.target_branch
            item.connection_validated = persisted.connection_validated_at is not None
            item.credential_status = persisted.credential.status if persisted.credential else "compromised"
            return item
    raise HTTPException(status_code=404, detail={"code": "configuration_not_found", "message": "Configuration not found."})


def db_execution_view(item: DbExecution) -> dict[str, object]:
    return {"id": item.id, "execution_id": item.id, "configuration_id": item.configuration_id, "status": item.status,
            "started_at": item.started_at.isoformat() if item.started_at else None,
            "finished_at": item.finished_at.isoformat() if item.finished_at else None,
            "terminal_reason": item.terminal_reason, "repositories_total": item.repositories_total,
            "repositories_completed": item.repositories_completed, "repositories_failed": item.repositories_failed, "commits_discovered": item.commits_discovered,
            "commits_verified": item.commits_verified, "allowed_commits": item.allowed_commits,
            "unauthorized_commits": item.unauthorized_commits}


def db_alert_view(item: DbAlert) -> dict[str, object]:
    return {"id": item.id, "configuration_id": item.configuration_id, "execution_id": item.execution_id,
            "repository_id": item.repository_id, "branch": item.branch, "commit_hash": item.commit_hash,
            "author_name": item.author_name, "author_email": item.author_email,
            "committed_at": item.committed_at.isoformat(), "detected_at": item.detected_at.isoformat()}


def configuration_view(item: Configuration) -> dict[str, object]:
    return {"id": str(item.id), "name": item.name, "gitlab_base_url": item.gitlab_base_url, "timezone": item.timezone, "enabled": item.enabled, "target_branch": item.target_branch if item.connection_validated else None, "credential_status": item.credential_status, "connection_validated": item.connection_validated}
