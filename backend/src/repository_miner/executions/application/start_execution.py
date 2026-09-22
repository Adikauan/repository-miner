from __future__ import annotations

from uuid import uuid4
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from repository_miner.gitlab.application.ports import GitLabGateway
from repository_miner.mining.application.persistent_runner import run_execution
from repository_miner.persistence.models import AllowedUser, MiningExecution, MonitoringConfiguration, RepositorySelectionRule


def start_persistent_execution(session: Session, gateway: GitLabGateway, configuration_id: str, publisher=None, operator_id: str | None = None) -> MiningExecution:
    configuration = session.scalar(select(MonitoringConfiguration).where(MonitoringConfiguration.id == configuration_id).with_for_update())
    if configuration is None:
        raise ValueError("configuration not found")
    if configuration.credential is None or configuration.credential.status != "active":
        raise RuntimeError("GitLab credential is not active")
    active = session.scalar(select(MiningExecution).where(MiningExecution.configuration_id == configuration_id, MiningExecution.status.in_(["pending", "running"])).with_for_update())
    if active is not None:
        raise RuntimeError("execution already active")
    selections = session.scalars(select(RepositorySelectionRule).where(RepositorySelectionRule.configuration_id == configuration_id, RepositorySelectionRule.mode == "include")).all()
    allowed = session.scalars(select(AllowedUser.normalized_email).where(AllowedUser.configuration_id == configuration_id)).all()
    snapshot = {"configuration_id": configuration.id, "gitlab_base_url": configuration.gitlab_base_url, "target_branch": configuration.target_branch, "enabled": configuration.enabled, "repositories": [selection.external_id for selection in selections], "allowed_emails": sorted(allowed)}
    execution = MiningExecution(id=str(uuid4()), configuration_id=configuration_id, status="pending", created_by_operator_id=operator_id, snapshot_json=json.dumps(snapshot, sort_keys=True), snapshot_created_at=datetime.now(timezone.utc))
    session.add(execution)
    session.commit()
    return run_execution(session, gateway, execution.id, publisher)
