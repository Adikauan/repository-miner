from datetime import datetime, timezone
from uuid import uuid4

from repository_miner.gitlab.application.ports import CommitMetadata
from repository_miner.mining.application.persistent_runner import run_execution
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.persistence.models import (
    AllowedUser, CredentialReference, MiningExecution, MonitoringConfiguration,
    RepositoryCheckpoint, RepositorySelectionRule, CommitVerification, UnauthorizedCommitAlert,
)


class FakeGitLab:
    def __init__(self, heads, commits=None, failures=None, compromise=None):
        self.heads = heads
        self.commits = commits or {}
        self.failures = failures or set()
        self.compromise = compromise
        self.calls = []

    def branch_head(self, base_url, token, repository_id, branch):
        self.calls.append(("head", repository_id))
        if repository_id in self.failures:
            raise RuntimeError("gitlab unavailable")
        if self.compromise == ("head", repository_id):
            self.compromise = None
        return self.heads[repository_id]

    def commits_after(self, base_url, token, repository_id, branch, sha):
        self.calls.append(("commits", repository_id, sha))
        return list(self.commits.get(repository_id, []))


def seed(session, repos=("r1",), allowed=("dev@example.com",)):
    cid, cred = str(uuid4()), str(uuid4())
    session.add(CredentialReference(id=cred, status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
    session.add(MonitoringConfiguration(id=cid, name="cfg", gitlab_base_url="https://gitlab.local", target_branch="QA", current_credential_id=cred))
    for repo in repos:
        session.add(RepositorySelectionRule(id=str(uuid4()), configuration_id=cid, kind="repository", mode="include", external_id=repo))
    for email in allowed:
        session.add(AllowedUser(id=str(uuid4()), configuration_id=cid, original_email=email, normalized_email=email))
    session.commit()
    return cid, cred


def execute(session, gateway, cid):
    execution = MiningExecution(id=str(uuid4()), configuration_id=cid, status="pending")
    session.add(execution)
    session.commit()
    return run_execution(session, gateway, execution.id)


def test_baseline_then_incremental_and_idempotent(db_session):
    cid, _ = seed(db_session)
    first = execute(db_session, FakeGitLab({"r1": "h1"}), cid)
    assert first.status == "completed"
    assert db_session.scalar(__import__('sqlalchemy').select(RepositoryCheckpoint).where(RepositoryCheckpoint.configuration_id == cid)).last_processed_hash == "h1"
    commit = CommitMetadata("h2", "Unknown", "UNKNOWN@EXAMPLE.COM", datetime.now(timezone.utc), "msg")
    second = execute(db_session, FakeGitLab({"r1": "h2"}, {"r1": [commit]}), cid)
    assert second.commits_verified == 1 and second.unauthorized_commits == 1
    assert db_session.query(CommitVerification).count() == 1
    assert db_session.query(UnauthorizedCommitAlert).count() == 1
    third = execute(db_session, FakeGitLab({"r1": "h2"}, {"r1": [commit]}), cid)
    assert third.commits_verified == 0 and third.unauthorized_commits == 0


def test_one_repository_failure_does_not_stop_other_and_checkpoint_not_advanced(db_session):
    cid, _ = seed(db_session, repos=("bad", "good"))
    execution = execute(db_session, FakeGitLab({"bad": "b1", "good": "g1"}, failures={"bad"}), cid)
    assert execution.status == "partially_completed"
    assert execution.repositories_completed == 1 and execution.repositories_failed == 1
    assert db_session.query(RepositoryCheckpoint).filter_by(repository_id="bad").count() == 0


def test_all_repositories_failed_sets_failed(db_session):
    cid, _ = seed(db_session, repos=("bad",))
    execution = execute(db_session, FakeGitLab({"bad": "b1"}, failures={"bad"}), cid)
    assert execution.status == "failed"


def test_compromised_credential_stops_future_repository_calls(db_session):
    cid, credential_id = seed(db_session, repos=("r1", "r2"))

    class CompromisingGateway(FakeGitLab):
        def branch_head(self, base_url, token, repository_id, branch):
            result = super().branch_head(base_url, token, repository_id, branch)
            if repository_id == "r1":
                credential = db_session.get(CredentialReference, credential_id)
                credential.status = "compromised"
                db_session.commit()
            return result

    execution = execute(db_session, CompromisingGateway({"r1": "h1", "r2": "h2"}), cid)
    assert execution.status == "partially_completed"
    assert execution.repositories_completed == 1 and execution.repositories_failed == 1
    assert db_session.query(RepositoryCheckpoint).filter_by(repository_id="r1").count() == 1
    assert db_session.query(RepositoryCheckpoint).filter_by(repository_id="r2").count() == 0
