from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from repository_miner.gitlab.application.ports import GitLabGateway
from repository_miner.persistence.crypto import decrypt_secret
from repository_miner.persistence.models import (
    BaselineResetAudit,
    CredentialReference,
    MonitoringConfiguration,
    RepositoryCheckpoint,
)


def reset_baseline(
    session: Session,
    gateway: GitLabGateway,
    *,
    configuration_id: str,
    repository_id: str,
    branch: str,
    operator_id: str,
    reason: str,
) -> BaselineResetAudit:
    if not operator_id or not operator_id.strip():
        raise PermissionError("authenticated operator required")
    configuration = session.get(MonitoringConfiguration, configuration_id)
    if configuration is None:
        raise ValueError("configuration not found")
    credential = session.get(CredentialReference, configuration.current_credential_id) if configuration.current_credential_id else None
    if credential is None or credential.status != "active":
        raise RuntimeError("GitLab credential is not active")
    # The external call is deliberately outside the transaction that mutates the
    # checkpoint and audit record.
    head = gateway.branch_head(configuration.gitlab_base_url, decrypt_secret(credential.ciphertext), repository_id, branch)
    checkpoint = session.scalar(select(RepositoryCheckpoint).where(
        RepositoryCheckpoint.configuration_id == configuration_id,
        RepositoryCheckpoint.repository_id == repository_id,
        RepositoryCheckpoint.branch == branch,
    ))
    previous = checkpoint.last_processed_hash if checkpoint is not None else None
    audit = BaselineResetAudit(
        id=str(uuid4()), configuration_id=configuration_id, repository_id=repository_id,
        branch=branch, previous_checkpoint_hash=previous, new_baseline_hash=head,
        operator_id=operator_id, reason=reason.strip() or "explicit baseline reset",
        created_at=datetime.now(timezone.utc),
    )
    session.add(audit)
    if checkpoint is None:
        checkpoint = RepositoryCheckpoint(
            id=str(uuid4()), configuration_id=configuration_id, repository_id=repository_id,
        branch=branch, baseline_hash=head, last_processed_hash=head,
            initialized_at=datetime.now(timezone.utc),
        )
        session.add(checkpoint)
    else:
        checkpoint.baseline_hash = head
        checkpoint.last_processed_hash = head
        checkpoint.advanced_at = datetime.now(timezone.utc)
    session.commit()
    return audit
