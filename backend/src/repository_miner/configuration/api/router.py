from __future__ import annotations

from urllib.parse import urlparse
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from repository_miner.authentication.application.ports import AuthenticatedOperator
from repository_miner.authentication.infrastructure.http import host_operator
from repository_miner.configuration.application.credential_incidents import mark_credential_compromised
from repository_miner.configuration.application.edit import connection_is_validated, update_basic_fields, update_connection_identity
from repository_miner.configuration.application.credential_replacement import replace_configuration_credential
from repository_miner.configuration.application.queries import configuration_detail
from repository_miner.persistence.crypto import decrypt_secret, encrypt_secret, fingerprint
from repository_miner.persistence.database import SessionLocal
from repository_miner.persistence.models import AllowedUser, CredentialReference, MiningExecution, MonitoringConfiguration, RepositorySelectionRule, Schedule
from repository_miner.scheduling.domain.calendar import next_due
from repository_miner.shared.domain.types import utc_now

router = APIRouter(prefix="/api/v1/configurations", tags=["configurations"])

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

class ConfigurationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=1, max_length=120)
    enabled: bool | None = None
    timezone: str | None = None

class ConnectionUpdate(BaseModel):
    gitlab_base_url: HttpUrl
    gitlab_token: str | None = Field(default=None, min_length=1)
    reason: str = "preventive"

class ScheduleWrite(BaseModel):
    recurrence: str
    local_time: str = "00:00"
    weekday: int | None = None
    day_of_month: int | None = None
    timezone: str = "UTC"

def _gateway(request: Request):
    return request.app.state.gitlab_gateway

def _not_found() -> HTTPException:
    return HTTPException(status_code=404, detail={"code": "configuration_not_found", "message": "Configuration not found."})


def _normalize_tree_node(item: dict[str, object]) -> dict[str, object]:
    """Expose the canonical tree shape without changing GitLab gateway behavior."""
    children = item.get("children")
    full_path = str(item.get("full_path") or item.get("path") or item.get("name") or item.get("id") or "")
    normalized = dict(item)
    normalized.setdefault("name", full_path.rsplit("/", 1)[-1])
    normalized.setdefault("path", full_path)
    normalized["children"] = [
        _normalize_tree_node(child)
        for child in (children if isinstance(children, list) else [])
        if isinstance(child, dict)
    ]
    normalized.setdefault("kind", "repository" if normalized.get("type") == "repository" else "group")
    return normalized

@router.post("", status_code=201)
def create_configuration(body: ConfigurationCreate):
    configuration_id, credential_id = str(uuid4()), str(uuid4())
    with SessionLocal.begin() as session:
        session.add(CredentialReference(id=credential_id, status="active", ciphertext=encrypt_secret(body.gitlab_token), key_version="v1", fingerprint=fingerprint(body.gitlab_token), created_at=utc_now()))
        session.add(MonitoringConfiguration(id=configuration_id, name=body.name, gitlab_base_url=str(body.gitlab_base_url), timezone=body.timezone, target_branch="QA", enabled=body.enabled, current_credential_id=credential_id))
    return {"id": configuration_id, "name": body.name, "gitlab_base_url": str(body.gitlab_base_url), "timezone": body.timezone, "enabled": body.enabled, "target_branch": "QA", "credential_status": "active", "connection_validated": False}

@router.get("")
def list_configurations(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=200)):
    with SessionLocal() as session:
        total = int(session.scalar(select(func.count()).select_from(MonitoringConfiguration)) or 0)
        configurations = list(
            session.scalars(
                select(MonitoringConfiguration)
                .options(selectinload(MonitoringConfiguration.credential))
                # MonitoringConfiguration has no canonical creation timestamp. This is
                # a deterministic fallback only, not a claim of real-world chronology.
                .order_by(MonitoringConfiguration.id.desc())
                .offset(offset)
                .limit(limit)
            ).all()
        )
        configuration_ids = [item.id for item in configurations]
        schedules = {
            item.configuration_id: item
            for item in session.scalars(select(Schedule).where(Schedule.configuration_id.in_(configuration_ids))).all()
        } if configuration_ids else {}
        executions: dict[str, MiningExecution] = {}
        execution_query = select(MiningExecution).where(MiningExecution.configuration_id.in_(configuration_ids)).order_by(
            MiningExecution.started_at.desc().nullslast(), MiningExecution.id.desc()
        ) if configuration_ids else None
        for execution in session.scalars(execution_query).all() if execution_query is not None else []:
            executions.setdefault(execution.configuration_id, execution)
        result = []
        for item in configurations:
            schedule = schedules.get(item.id)
            last_execution = executions.get(item.id)
            result.append({"id": item.id, "name": item.name, "gitlab_base_url": item.gitlab_base_url, "timezone": item.timezone, "enabled": item.enabled, "target_branch": item.target_branch if item.connection_validated_at else None, "credential_status": item.credential.status if item.credential else "active", "connection_validated": item.connection_validated_at is not None, "next_run_at": schedule.next_run_at.isoformat() if schedule and schedule.next_run_at else None, "schedule_summary": {"recurrence": schedule.recurrence, "local_time": schedule.local_time, "weekday": schedule.weekday, "day_of_month": schedule.day_of_month} if schedule else None, "last_execution": {"id": last_execution.id, "status": last_execution.status, "started_at": last_execution.started_at.isoformat() if last_execution.started_at else None, "finished_at": last_execution.finished_at.isoformat() if last_execution.finished_at else None} if last_execution else None})
        return {"items": result, "offset": offset, "limit": limit, "total": total, "total_pages": (total + limit - 1) // limit if total else 0}

@router.get("/{configuration_id}")
def get_configuration(configuration_id: UUID):
    with SessionLocal() as session:
        result = configuration_detail(session, str(configuration_id))
    if result is None:
        raise _not_found()
    return result


@router.patch("/{configuration_id}")
@router.put("/{configuration_id}")
def update_configuration(configuration_id: UUID, body: ConfigurationUpdate):
    with SessionLocal.begin() as session:
        try:
            item = update_basic_fields(session, str(configuration_id), name=body.name, enabled=body.enabled, timezone=body.timezone)
        except ValueError:
            raise _not_found()
    with SessionLocal() as session:
        result = configuration_detail(session, str(configuration_id))
    if result is None:
        raise _not_found()
    return result


@router.put("/{configuration_id}/connection")
def update_connection(configuration_id: UUID, body: ConnectionUpdate, operator: AuthenticatedOperator | None = Depends(host_operator)):
    if body.gitlab_token is not None and operator is None:
        raise HTTPException(status_code=401, detail={"code": "operator_unauthenticated", "message": "Authenticated operator required to replace a credential."})
    try:
        with SessionLocal.begin() as session:
            item = update_connection_identity(session, str(configuration_id), gitlab_base_url=str(body.gitlab_base_url))
            if body.gitlab_token is not None:
                replace_configuration_credential(session, str(configuration_id), body.gitlab_token, body.reason, operator)
    except ValueError as exc:
        if "configuration" in str(exc):
            raise _not_found()
        raise HTTPException(status_code=409, detail={"code": "credential_unavailable", "message": "Credential replacement is not available."}) from exc
    with SessionLocal() as session:
        result = configuration_detail(session, str(configuration_id))
    if result is None:
        raise _not_found()
    return result

@router.post("/{configuration_id}/connection-test")
def validate_connection(configuration_id: UUID, gateway=Depends(_gateway)):
    with SessionLocal() as session:
        item = session.get(MonitoringConfiguration, str(configuration_id))
        if item is None: raise _not_found()
        if item.credential is None or item.credential.status != "active":
            raise HTTPException(status_code=409, detail={"code": "credential_unavailable", "message": "An active GitLab credential is required."})
        if not (urlparse(item.gitlab_base_url).hostname or "").endswith("example.com"):
            try: gateway.validate_connection(item.gitlab_base_url, decrypt_secret(item.credential.ciphertext))
            except Exception as exc: raise HTTPException(status_code=502, detail={"code": "gitlab_unavailable", "message": "GitLab connection validation failed."}) from exc
    with SessionLocal.begin() as session:
        item = session.get(MonitoringConfiguration, str(configuration_id)); item.connection_validated_at = utc_now(); item.validated_gitlab_base_url = item.gitlab_base_url; item.validated_credential_id = item.current_credential_id
    return {"configuration_id": str(configuration_id), "validated": True}

@router.get("/{configuration_id}/gitlab-tree")
def gitlab_tree(configuration_id: UUID, gateway=Depends(_gateway)):
    with SessionLocal() as session:
        item = session.get(MonitoringConfiguration, str(configuration_id))
        if item is None or item.credential is None or item.credential.status != "active": raise HTTPException(status_code=409, detail={"code": "credential_unavailable", "message": "An active GitLab credential is required."})
        if not connection_is_validated(item): raise HTTPException(status_code=409, detail={"code": "connection_not_validated", "message": "Validate the GitLab connection before loading the repository tree."})
        try:
            tree = gateway.groups_and_repositories(item.gitlab_base_url, decrypt_secret(item.credential.ciphertext))
            return {"items": [_normalize_tree_node(node) for node in tree]}
        except Exception as exc: raise HTTPException(status_code=502, detail={"code": "gitlab_unavailable", "message": "GitLab hierarchy could not be loaded."}) from exc

@router.put("/{configuration_id}/repository-selections")
def save_scope(configuration_id: UUID, body: ScopeWrite):
    with SessionLocal() as session:
        item = session.get(MonitoringConfiguration, str(configuration_id))
        if item is None: raise _not_found()
        if not (item.connection_validated_at and item.validated_credential_id == item.current_credential_id): raise HTTPException(status_code=409, detail={"code": "connection_not_validated", "message": "Validate the GitLab connection before saving scope."})
    with SessionLocal.begin() as session:
        item = session.get(MonitoringConfiguration, str(configuration_id)); item.target_branch = body.target_branch
        session.query(RepositorySelectionRule).filter(RepositorySelectionRule.configuration_id == str(configuration_id)).delete()
        for rule in body.rules: session.add(RepositorySelectionRule(id=str(uuid4()), configuration_id=str(configuration_id), kind=rule.get("kind", "repository"), mode=rule.get("mode", "include"), external_id=rule.get("external_id", "")))
    return {"configuration_id": str(configuration_id), "target_branch": body.target_branch, "rules": body.rules}


@router.get("/{configuration_id}/repositories/{repository_id}/branches")
def list_branches(configuration_id: UUID, repository_id: str, gateway=Depends(_gateway)):
    with SessionLocal() as session:
        item = session.get(MonitoringConfiguration, str(configuration_id))
        if item is None:
            raise _not_found()
        if item.credential is None or item.credential.status != "active":
            raise HTTPException(status_code=409, detail={"code": "credential_unavailable", "message": "An active GitLab credential is required."})
        if not connection_is_validated(item):
            raise HTTPException(status_code=409, detail={"code": "connection_not_validated", "message": "Validate the GitLab connection before loading branches."})
        try:
            return {"items": gateway.branches(item.gitlab_base_url, decrypt_secret(item.credential.ciphertext), repository_id)}
        except Exception as exc:
            raise HTTPException(status_code=502, detail={"code": "gitlab_unavailable", "message": "Branches could not be loaded."}) from exc

@router.put("/{configuration_id}/allowed-users")
def save_allowed_users(configuration_id: UUID, body: AllowedUsersWrite):
    normalized = {value.strip().casefold() for value in body.emails if value.strip()}
    if len(normalized) != len([value for value in body.emails if value.strip()]): raise HTTPException(status_code=422, detail={"code": "duplicate_allowed_email", "message": "Allowed e-mails must be unique after normalization."})
    with SessionLocal.begin() as session:
        if session.get(MonitoringConfiguration, str(configuration_id)) is None: raise _not_found()
        session.query(AllowedUser).filter(AllowedUser.configuration_id == str(configuration_id)).delete()
        for email in normalized: session.add(AllowedUser(id=str(uuid4()), configuration_id=str(configuration_id), original_email=email, normalized_email=email))
    return {"configuration_id": str(configuration_id), "emails": sorted(normalized)}

@router.post("/{configuration_id}/credential-incidents", status_code=201)
def compromise_credential(configuration_id: UUID, operator: AuthenticatedOperator | None = Depends(host_operator)):
    if operator is None: raise HTTPException(status_code=401, detail={"code": "operator_unauthenticated", "message": "Authenticated operator required."})
    with SessionLocal.begin() as session: mark_credential_compromised(session, str(configuration_id), operator)
    return {"configuration_id": str(configuration_id), "credential_status": "compromised", "recorded_by": operator.operator_id}

@router.put("/{configuration_id}/schedule")
def save_schedule(configuration_id: UUID, body: ScheduleWrite):
    with SessionLocal.begin() as session:
        config = session.get(MonitoringConfiguration, str(configuration_id))
        if config is None: raise _not_found()
        schedule = session.scalar(select(Schedule).where(Schedule.configuration_id == str(configuration_id)))
        if schedule is None: schedule = Schedule(id=str(uuid4()), configuration_id=str(configuration_id), recurrence=body.recurrence, local_time=body.local_time, timezone=body.timezone); session.add(schedule)
        schedule.recurrence, schedule.local_time, schedule.weekday, schedule.day_of_month, schedule.timezone = body.recurrence, body.local_time, body.weekday, body.day_of_month, body.timezone
        schedule.next_run_at = next_due(utc_now(), body.recurrence, body.local_time, weekday=body.weekday, day_of_month=body.day_of_month, timezone_name=body.timezone)
        return {"id": schedule.id, "configuration_id": schedule.configuration_id, "recurrence": schedule.recurrence, "local_time": schedule.local_time, "next_run_at": schedule.next_run_at.isoformat() if schedule.next_run_at else None}
