from datetime import datetime, timezone
from uuid import uuid4

from repository_miner.gitlab.application.ports import CommitMetadata
from repository_miner.mining.application.persistent_runner import run_execution
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.persistence.models import AllowedUser, CredentialReference, MiningExecution, MonitoringConfiguration, RepositorySelectionRule
from repository_miner.reporting.application.queries import execution_report


class Gateway:
    def __init__(self, head, commits=None):
        self.head, self.commits = head, commits or []

    def branch_head(self, *_args): return self.head
    def is_commit_reachable(self, *_args): return True
    def commits_after(self, *_args): return list(self.commits)


def test_reused_verification_does_not_increase_later_report_counters(db_session):
    cid, cred = str(uuid4()), str(uuid4())
    db_session.add(CredentialReference(id=cred, status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
    db_session.add(MonitoringConfiguration(id=cid, name="report", gitlab_base_url="https://gitlab.example.com", target_branch="QA", current_credential_id=cred))
    db_session.add(RepositorySelectionRule(id=str(uuid4()), configuration_id=cid, kind="repository", mode="include", external_id="repo"))
    db_session.add(AllowedUser(id=str(uuid4()), configuration_id=cid, original_email="allowed@example.com", normalized_email="allowed@example.com"))
    db_session.commit()
    first = MiningExecution(id=str(uuid4()), configuration_id=cid, status="pending")
    db_session.add(first); db_session.commit()
    run_execution(db_session, Gateway("h1"), first.id)
    commit = CommitMetadata("h2", "Unknown", "unknown@example.com", datetime.now(timezone.utc), "msg")
    second = MiningExecution(id=str(uuid4()), configuration_id=cid, status="pending")
    db_session.add(second); db_session.commit()
    run_execution(db_session, Gateway("h2", [commit]), second.id)
    third = MiningExecution(id=str(uuid4()), configuration_id=cid, status="pending")
    db_session.add(third); db_session.commit()
    run_execution(db_session, Gateway("h2", [commit]), third.id)
    report = execution_report(db_session, third.id)
    assert report["commits_discovered"] == 1
    assert report["commits_verified"] == 0
    assert report["allowed_commits"] == 0
    assert report["unauthorized_commits"] == 0
