from datetime import datetime, timezone
from uuid import uuid4

import pytest

from repository_miner.executions.application.start_execution import start_persistent_execution
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.persistence.models import CredentialReference, MiningExecution, MonitoringConfiguration, RepositorySelectionRule


class EmptyGateway:
    def branch_head(self, *_args):
        return "head"

    def commits_after(self, *_args):
        return []

    def is_commit_reachable(self, *_args):
        return True


def configuration(session, *, enabled=True):
    cid, credential_id = str(uuid4()), str(uuid4())
    session.add(CredentialReference(id=credential_id, status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
    session.add(MonitoringConfiguration(id=cid, name="cfg", gitlab_base_url="https://gitlab.example.com", target_branch="QA", enabled=enabled, current_credential_id=credential_id))
    session.add(RepositorySelectionRule(id=str(uuid4()), configuration_id=cid, kind="repository", mode="include", external_id="repo"))
    session.commit()
    return cid


def test_manual_start_is_allowed_for_disabled_configuration(db_session):
    cid = configuration(db_session, enabled=False)
    execution = start_persistent_execution(db_session, EmptyGateway(), cid, operator_id="operator")
    assert execution.status == "completed"


def test_second_start_is_rejected_when_configuration_has_active_execution(db_session):
    cid = configuration(db_session)
    active = MiningExecution(id=str(uuid4()), configuration_id=cid, status="running")
    db_session.add(active)
    db_session.commit()
    with pytest.raises(RuntimeError, match="already active"):
        start_persistent_execution(db_session, EmptyGateway(), cid, operator_id="operator")
