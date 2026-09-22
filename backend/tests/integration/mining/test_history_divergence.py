from datetime import datetime, timezone
from uuid import uuid4

import pytest

from repository_miner.gitlab.application.ports import CommitMetadata
from repository_miner.mining.application.persistent_runner import run_execution
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.persistence.models import (
    CredentialReference, MiningExecution, MonitoringConfiguration,
    RepositoryCheckpoint, RepositoryFailure, RepositorySelectionRule,
)
from repository_miner.shared.api.errors import DomainError


class DivergingGitLab:
    def __init__(self, reachable: bool, branch_exists: bool = True):
        self.reachable = reachable
        self.branch_exists = branch_exists

    def branch_head(self, base_url, token, repository_id, branch):
        if not self.branch_exists:
            raise DomainError("gitlab_unexpected_response", "GitLab returned an unexpected response.")
        return "head-2"

    def is_commit_reachable(self, base_url, token, repository_id, branch, commit_hash):
        return self.reachable

    def commits_after(self, base_url, token, repository_id, branch, sha):
        raise AssertionError("divergent history must not list commits")


def seed(db_session):
    cid, cred = str(uuid4()), str(uuid4())
    db_session.add(CredentialReference(id=cred, status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
    db_session.add(MonitoringConfiguration(id=cid, name="cfg", gitlab_base_url="https://gitlab.local", target_branch="QA", current_credential_id=cred))
    db_session.add(RepositorySelectionRule(id=str(uuid4()), configuration_id=cid, kind="repository", mode="include", external_id="r1"))
    db_session.add(RepositoryCheckpoint(id=str(uuid4()), configuration_id=cid, repository_id="r1", branch="QA", baseline_hash="head-1", last_processed_hash="head-1", initialized_at=datetime.now(timezone.utc)))
    db_session.commit()
    return cid


@pytest.mark.parametrize("scenario", ["missing_checkpoint_commit", "rewritten_branch", "non_descendant_history"])
def test_divergent_history_preserves_checkpoint_and_blocks_listing(db_session, scenario):
    cid = seed(db_session)
    execution = MiningExecution(id=str(uuid4()), configuration_id=cid, status="pending")
    db_session.add(execution)
    db_session.commit()
    result = run_execution(db_session, DivergingGitLab(False), execution.id)
    assert result.status == "failed"
    checkpoint = db_session.query(RepositoryCheckpoint).one()
    assert checkpoint.last_processed_hash == "head-1"
    failure = db_session.query(RepositoryFailure).one()
    assert failure.code == "history_diverged"


def test_removed_branch_is_history_diverged_and_does_not_create_baseline(db_session):
    cid = seed(db_session)
    execution = MiningExecution(id=str(uuid4()), configuration_id=cid, status="pending")
    db_session.add(execution)
    db_session.commit()
    result = run_execution(db_session, DivergingGitLab(True, branch_exists=False), execution.id)
    assert result.status == "failed"
    assert db_session.query(RepositoryCheckpoint).one().last_processed_hash == "head-1"
    assert db_session.query(RepositoryFailure).one().code == "history_diverged"


def test_divergent_repository_remains_blocked_until_explicit_reset(db_session):
    cid = seed(db_session)
    for _ in range(2):
        execution = MiningExecution(id=str(uuid4()), configuration_id=cid, status="pending")
        db_session.add(execution)
        db_session.commit()
        result = run_execution(db_session, DivergingGitLab(False), execution.id)
        assert result.status == "failed"
    assert db_session.query(RepositoryCheckpoint).one().last_processed_hash == "head-1"
    assert db_session.query(RepositoryFailure).count() == 2
