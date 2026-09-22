from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from repository_miner.gitlab.application.ports import GitLabGateway
from repository_miner.gitlab.application.hierarchy import resolve_selection
from repository_miner.persistence.crypto import decrypt_secret
from repository_miner.persistence.models import (
    AllowedUser,
    CommitVerification,
    ExecutionCommit,
    CredentialReference,
    MiningExecution,
    MonitoringConfiguration,
    RepositoryCheckpoint,
    RepositoryExecution,
    RepositoryFailure,
    RepositorySelectionRule,
    UnauthorizedCommitAlert,
)
from repository_miner.persistence.repositories import persist_verification_and_alert


class HistoryDivergedError(RuntimeError):
    code = "history_diverged"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _email(value: str | None) -> str | None:
    return value.strip().casefold() if value and value.strip() else None


def _active_token(session: Session, configuration: MonitoringConfiguration) -> str:
    credential = session.get(CredentialReference, configuration.current_credential_id) if configuration.current_credential_id else None
    if credential is None or credential.status != "active":
        raise RuntimeError("GitLab credential is not active")
    return decrypt_secret(credential.ciphertext)


def _selected_repositories(session: Session, configuration_id: str) -> list[str]:
    rows = session.scalars(select(RepositorySelectionRule).where(
        RepositorySelectionRule.configuration_id == configuration_id,
        RepositorySelectionRule.mode == "include",
    )).all()
    return list(dict.fromkeys(row.external_id for row in rows))


def _effective_repositories(session: Session, configuration: MonitoringConfiguration, gateway: GitLabGateway) -> list[str]:
    """Expand group/subgroup rules only when the configured scope needs it."""
    rows = session.scalars(select(RepositorySelectionRule).where(
        RepositorySelectionRule.configuration_id == configuration.id,
        RepositorySelectionRule.mode == "include",
    )).all()
    if not rows:
        return []
    if not any(row.kind in {"group", "subgroup"} for row in rows):
        return list(dict.fromkeys(row.external_id for row in rows))
    tree = gateway.groups_and_repositories(configuration.gitlab_base_url, _active_token(session, configuration))
    return resolve_selection(tree, [{"kind": row.kind, "external_id": row.external_id} for row in rows])


def run_execution(session: Session, gateway: GitLabGateway, execution_id: str, publisher=None) -> MiningExecution:
    execution = session.get(MiningExecution, execution_id)
    if execution is None:
        raise ValueError("execution not found")
    configuration = session.get(MonitoringConfiguration, execution.configuration_id)
    if configuration is None:
        raise ValueError("configuration not found")
    execution.status = "running"
    execution.started_at = execution.started_at or _now()
    session.commit()
    allowed = set(session.scalars(select(AllowedUser.normalized_email).where(AllowedUser.configuration_id == configuration.id)).all())
    # Scope expansion is an external read and therefore happens before any
    # repository transaction. Repository-only selections remain compatible with
    # lightweight GitLab fakes that do not implement hierarchy discovery.
    try:
        repositories = _effective_repositories(session, configuration, gateway)
    except Exception as exc:
        execution.status = "failed"
        execution.finished_at = _now()
        execution.terminal_reason = "scope_resolution_failed"
        session.commit()
        if publisher:
            publisher.publish("execution.failed", execution.id, configuration.id, {"status": "failed", "finished_at": execution.finished_at.isoformat(), "reason": "scope_resolution_failed"})
        return execution
    execution.repositories_total = len(repositories)
    session.commit()
    if publisher:
        publisher.publish("execution.started", execution.id, configuration.id, {"status": "running", "started_at": execution.started_at.isoformat(), "repositories_total": execution.repositories_total, "repositories_completed": execution.repositories_completed, "repositories_failed": execution.repositories_failed, "commits_discovered": execution.commits_discovered, "commits_verified": execution.commits_verified, "allowed_commits": execution.allowed_commits, "unauthorized_commits": execution.unauthorized_commits})
    successes = 0
    failures = 0

    for repository_id in repositories:
        repository_execution = RepositoryExecution(
            id=str(uuid4()), execution_id=execution.id, repository_id=repository_id,
            branch=configuration.target_branch, status="running",
        )
        session.add(repository_execution)
        session.commit()
        if publisher:
            publisher.publish("repository.started", execution.id, configuration.id, {"repository_execution_id": repository_execution.id, "status": "running", "started_at": _now().isoformat()}, repository_id=repository_id)
        try:
            # Every external call is preceded by an active-credential check and is made
            # outside an open database transaction.
            token = _active_token(session, configuration)
            session.commit()
            checkpoint = session.scalar(select(RepositoryCheckpoint).where(
                RepositoryCheckpoint.configuration_id == configuration.id,
                RepositoryCheckpoint.repository_id == repository_id,
                RepositoryCheckpoint.branch == configuration.target_branch,
            ))
            try:
                head = gateway.branch_head(configuration.gitlab_base_url, token, repository_id, configuration.target_branch)
            except Exception as exc:
                if checkpoint is not None and getattr(exc, "code", None) in {"gitlab_unexpected_response", "gitlab_malformed_payload"}:
                    raise HistoryDivergedError("history_diverged") from exc
                raise
            if checkpoint is None:
                checkpoint = RepositoryCheckpoint(
                    id=str(uuid4()), configuration_id=configuration.id, repository_id=repository_id,
                    branch=configuration.target_branch, baseline_hash=head, last_processed_hash=head,
                    initialized_at=_now(),
                )
                repository_execution.observed_head = head
                repository_execution.status = "completed"
                execution.repositories_completed += 1
                session.add(checkpoint)
                session.commit()
                successes += 1
                if publisher:
                    publisher.publish("repository.completed", execution.id, configuration.id, {"repository_execution_id": repository_execution.id, "status": "completed", "finished_at": _now().isoformat(), "counters": {"repositories_total": execution.repositories_total, "repositories_completed": execution.repositories_completed, "repositories_failed": execution.repositories_failed, "commits_discovered": 0, "commits_verified": 0, "allowed_commits": 0, "unauthorized_commits": 0}}, repository_id=repository_id)
                continue

            token = _active_token(session, configuration)
            session.commit()
            reachability = getattr(gateway, "is_commit_reachable", None)
            if reachability is not None:
                try:
                    reachable = reachability(
                        configuration.gitlab_base_url, token, repository_id,
                        configuration.target_branch, checkpoint.last_processed_hash,
                    )
                except Exception as exc:
                    # A missing branch/checkpoint and an invalid ancestry comparison
                    # are operational history divergence, not a new baseline.
                    if getattr(exc, "code", None) in {"gitlab_unexpected_response", "gitlab_malformed_payload"}:
                        raise HistoryDivergedError("history_diverged") from exc
                    raise
                if not reachable:
                    raise HistoryDivergedError("history_diverged")
            commits = gateway.commits_after(configuration.gitlab_base_url, token, repository_id, configuration.target_branch, checkpoint.last_processed_hash)
            for commit in commits:
                execution.commits_discovered += 1
                session.commit()
                existing = session.scalar(select(CommitVerification).where(
                    CommitVerification.configuration_id == configuration.id,
                    CommitVerification.repository_id == repository_id,
                    CommitVerification.branch == configuration.target_branch,
                    CommitVerification.commit_hash == commit.sha,
                ))
                if existing is not None:
                    session.add(ExecutionCommit(id=str(uuid4()), execution_id=execution.id, repository_execution_id=repository_execution.id, commit_hash=commit.sha, verification_source="reused"))
                    session.commit()
                    continue
                normalized = _email(commit.author_email)
                is_allowed = normalized is not None and normalized in allowed
                session.commit()
                with session.begin():
                    _, alert, created = persist_verification_and_alert(
                        session, configuration_id=configuration.id, execution_id=execution.id,
                        repository_id=repository_id, branch=configuration.target_branch,
                        commit_hash=commit.sha, author_name=commit.author_name,
                        author_email=normalized, committed_at=commit.committed_at,
                        message=commit.message, allowed=is_allowed,
                    )
                    session.add(ExecutionCommit(id=str(uuid4()), execution_id=execution.id, repository_execution_id=repository_execution.id, commit_hash=commit.sha, verification_source="new"))
                if created:
                    execution.commits_verified += 1
                    if alert is None:
                        execution.allowed_commits += 1
                    else:
                        execution.unauthorized_commits += 1
                    if publisher and alert is not None:
                        publisher.publish("unauthorized_commit.detected", execution.id, configuration.id, {"alert_id": alert.id, "repository_execution_id": repository_execution.id, "commit_hash": commit.sha}, repository_id=repository_id)
                session.commit()
                if publisher:
                    publisher.publish("repository.progress", execution.id, configuration.id, {"repository_execution_id": repository_execution.id, "repositories_total": execution.repositories_total, "repositories_completed": execution.repositories_completed, "repositories_failed": execution.repositories_failed, "commits_discovered": execution.commits_discovered, "commits_verified": execution.commits_verified, "allowed_commits": execution.allowed_commits, "unauthorized_commits": execution.unauthorized_commits}, repository_id=repository_id)

            # Only a fully processed repository advances its checkpoint.
            checkpoint.last_processed_hash = head
            checkpoint.advanced_at = _now()
            repository_execution.observed_head = head
            repository_execution.status = "completed"
            execution.repositories_completed += 1
            session.commit()
            successes += 1
            if publisher:
                publisher.publish("repository.completed", execution.id, configuration.id, {"repository_execution_id": repository_execution.id, "status": "completed", "finished_at": _now().isoformat(), "counters": {"repositories_total": execution.repositories_total, "repositories_completed": execution.repositories_completed, "repositories_failed": execution.repositories_failed, "commits_discovered": execution.commits_discovered, "commits_verified": execution.commits_verified, "allowed_commits": execution.allowed_commits, "unauthorized_commits": execution.unauthorized_commits}}, repository_id=repository_id)
        except Exception as exc:
            session.rollback()
            failures += 1
            repository_execution = session.get(RepositoryExecution, repository_execution.id)
            if repository_execution:
                repository_execution.status = "failed"
                repository_execution.failure_reason = str(exc)[:512]
            execution.repositories_failed += 1
            failure_code = getattr(exc, "code", "repository_processing_failed")
            failure_reason = "history_diverged" if failure_code == "history_diverged" else str(exc)[:512]
            failure = RepositoryFailure(
                id=str(uuid4()), execution_id=execution.id, repository_execution_id=repository_execution.id,
                stage="mining", code=failure_code, safe_reason=failure_reason,
                occurred_at=_now(), continued=True, correlation_id=str(uuid4()),
            )
            session.add(failure)
            session.commit()
            if publisher:
                publisher.publish("repository.failed", execution.id, configuration.id, {"repository_execution_id": repository_execution.id, "status": "failed", "finished_at": _now().isoformat(), "failure_id": failure.id}, repository_id=repository_id)

    execution.finished_at = _now()
    if not repositories or failures == 0:
        execution.status = "completed"
    elif successes > 0:
        execution.status = "partially_completed"
    else:
        execution.status = "failed"
    session.commit()
    if publisher:
        publisher.publish(f"execution.{execution.status}", execution.id, configuration.id, {"status": execution.status, "finished_at": execution.finished_at.isoformat(), "summary_counts": {"repositories_total": execution.repositories_total, "repositories_completed": execution.repositories_completed, "repositories_failed": execution.repositories_failed, "commits_discovered": execution.commits_discovered, "commits_verified": execution.commits_verified, "allowed_commits": execution.allowed_commits, "unauthorized_commits": execution.unauthorized_commits}})
    return execution
