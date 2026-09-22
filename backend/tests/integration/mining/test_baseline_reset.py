from datetime import datetime, timezone
from uuid import uuid4

import pytest

from repository_miner.mining.application.baseline_reset import reset_baseline
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.persistence.models import (
    BaselineResetAudit, CredentialReference, MiningExecution, MonitoringConfiguration,
    RepositoryCheckpoint, RepositorySelectionRule, CommitVerification, UnauthorizedCommitAlert,
)


class ResetGitLab:
    def branch_head(self, base_url, token, repository_id, branch):
        return "new-head"


def test_reset_requires_operator_and_preserves_checkpoint_history(db_session):
    cid, cred = str(uuid4()), str(uuid4())
    db_session.add(CredentialReference(id=cred, status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
    db_session.add(MonitoringConfiguration(id=cid, name="cfg", gitlab_base_url="https://gitlab.local", current_credential_id=cred))
    db_session.add(RepositoryCheckpoint(id=str(uuid4()), configuration_id=cid, repository_id="r1", branch="QA", baseline_hash="old", last_processed_hash="old", initialized_at=datetime.now(timezone.utc)))
    execution = MiningExecution(id=str(uuid4()), configuration_id=cid, status="completed")
    db_session.add(execution)
    verification = CommitVerification(
        id=str(uuid4()), configuration_id=cid, repository_id="r1", branch="QA", commit_hash="old-commit",
        author_name="Alice", author_email="alice@example.com", committed_at=datetime.now(timezone.utc),
        message="old", authorization_result="unauthorized", first_verified_execution_id=execution.id,
        verified_at=datetime.now(timezone.utc),
    )
    db_session.add(verification)
    db_session.add(UnauthorizedCommitAlert(
        id=str(uuid4()), configuration_id=cid, execution_id=execution.id, commit_verification_id=verification.id,
        repository_id="r1", branch="QA", commit_hash="old-commit", author_name="Alice",
        author_email="alice@example.com", committed_at=verification.committed_at, detected_at=datetime.now(timezone.utc),
    ))
    db_session.commit()
    with pytest.raises(PermissionError):
        reset_baseline(db_session, ResetGitLab(), configuration_id=cid, repository_id="r1", branch="QA", operator_id="", reason="recovery")
    audit = reset_baseline(db_session, ResetGitLab(), configuration_id=cid, repository_id="r1", branch="QA", operator_id="operator-1", reason="history recovery")
    assert audit.previous_checkpoint_hash == "old"
    assert audit.new_baseline_hash == "new-head"
    assert audit.operator_id == "operator-1"
    checkpoint = db_session.query(RepositoryCheckpoint).one()
    assert checkpoint.last_processed_hash == "new-head"
    assert db_session.query(MiningExecution).count() == 1
    assert db_session.query(CommitVerification).count() == 1
    assert db_session.query(UnauthorizedCommitAlert).count() == 1
