from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from repository_miner.persistence.models import (
    CommitVerification,
    CredentialReference,
    MiningExecution,
    RepositoryCheckpoint,
    UnauthorizedCommitAlert,
)


def now() -> datetime:
    return datetime.now(timezone.utc)


def get_verification(session: Session, configuration_id: str, repository_id: str, branch: str, commit_hash: str) -> CommitVerification | None:
    return session.scalar(select(CommitVerification).where(
        CommitVerification.configuration_id == configuration_id,
        CommitVerification.repository_id == repository_id,
        CommitVerification.branch == branch,
        CommitVerification.commit_hash == commit_hash,
    ))


def persist_verification_and_alert(session: Session, *, configuration_id: str, execution_id: str, repository_id: str, branch: str, commit_hash: str, author_name: str, author_email: str | None, committed_at: datetime, message: str, allowed: bool) -> tuple[CommitVerification, UnauthorizedCommitAlert | None, bool]:
    existing = get_verification(session, configuration_id, repository_id, branch, commit_hash)
    if existing is not None:
        return existing, None, False
    verification = CommitVerification(
        id=str(uuid4()), configuration_id=configuration_id, repository_id=repository_id,
        branch=branch, commit_hash=commit_hash, author_name=author_name,
        author_email=author_email, committed_at=committed_at, message=message,
        authorization_result="allowed" if allowed else "unauthorized",
        first_verified_execution_id=execution_id, verified_at=now(),
    )
    session.add(verification)
    alert = None
    if not allowed:
        alert = UnauthorizedCommitAlert(
            id=str(uuid4()), configuration_id=configuration_id, execution_id=execution_id,
            commit_verification_id=verification.id, repository_id=repository_id,
            branch=branch, commit_hash=commit_hash, author_name=author_name,
            author_email=author_email, committed_at=committed_at, detected_at=now(),
        )
        session.add(alert)
    session.flush()
    return verification, alert, True


def create_baseline(session: Session, *, configuration_id: str, repository_id: str, branch: str, head_sha: str) -> RepositoryCheckpoint:
    checkpoint = RepositoryCheckpoint(
        id=str(uuid4()), configuration_id=configuration_id, repository_id=repository_id,
        branch=branch, baseline_hash=head_sha, last_processed_hash=head_sha,
        initialized_at=now(), advanced_at=None,
    )
    session.add(checkpoint)
    session.flush()
    return checkpoint


def advance_checkpoint(session: Session, *, configuration_id: str, repository_id: str, branch: str, head_sha: str) -> RepositoryCheckpoint:
    checkpoint = session.scalar(select(RepositoryCheckpoint).where(
        RepositoryCheckpoint.configuration_id == configuration_id,
        RepositoryCheckpoint.repository_id == repository_id,
        RepositoryCheckpoint.branch == branch,
    ))
    if checkpoint is None:
        return create_baseline(session, configuration_id=configuration_id, repository_id=repository_id, branch=branch, head_sha=head_sha)
    checkpoint.last_processed_hash = head_sha
    checkpoint.advanced_at = now()
    session.flush()
    return checkpoint


def replace_credential(session: Session, *, configuration_id: str, previous: CredentialReference, replacement: CredentialReference, operator_id: str, reason: str, incident_id: str | None = None) -> None:
    previous.status = "replaced"
    previous.replaced_by_id = replacement.id
    session.add(replacement)
    from repository_miner.persistence.models import CredentialReplacement
    session.add(CredentialReplacement(
        id=str(uuid4()), configuration_id=configuration_id,
        previous_credential_id=previous.id, replacement_credential_id=replacement.id,
        reason=reason, replaced_by=operator_id, replaced_at=now(), incident_id=incident_id,
    ))
