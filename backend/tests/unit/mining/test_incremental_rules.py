from datetime import datetime, timezone
from uuid import uuid4

from repository_miner.gitlab.application.ports import CommitMetadata
from repository_miner.mining.application.persistent_runner import run_execution
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.persistence.models import CredentialReference, MiningExecution, MonitoringConfiguration, RepositoryCheckpoint, RepositorySelectionRule


class Gateway:
    def __init__(self, head: str, commits: list[CommitMetadata] | None = None):
        self.head = head
        self.commits = commits or []

    def branch_head(self, *_args):
        return self.head

    def is_commit_reachable(self, *_args):
        return True

    def commits_after(self, *_args):
        return list(self.commits)


def seed(session):
    configuration_id, credential_id = str(uuid4()), str(uuid4())
    session.add(CredentialReference(id=credential_id, status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
    session.add(MonitoringConfiguration(id=configuration_id, name="cfg", gitlab_base_url="https://gitlab.example.com", target_branch="QA", current_credential_id=credential_id))
    session.add(RepositorySelectionRule(id=str(uuid4()), configuration_id=configuration_id, kind="repository", mode="include", external_id="repo"))
    session.commit()
    return configuration_id


def execute(session, configuration_id, gateway):
    execution = MiningExecution(id=str(uuid4()), configuration_id=configuration_id, status="pending")
    session.add(execution)
    session.commit()
    return run_execution(session, gateway, execution.id)


def test_first_execution_creates_baseline_without_historical_verification(db_session):
    configuration_id = seed(db_session)
    execution = execute(db_session, configuration_id, Gateway("h1", [CommitMetadata("old", "A", "a@example.com", datetime.now(timezone.utc), "old")]))
    checkpoint = db_session.query(RepositoryCheckpoint).one()
    assert execution.status == "completed"
    assert execution.commits_discovered == 0
    assert checkpoint.baseline_hash == "h1"


def test_existing_checkpoint_processes_only_new_commits(db_session):
    configuration_id = seed(db_session)
    execute(db_session, configuration_id, Gateway("h1"))
    commit = CommitMetadata("h2", "A", "a@example.com", datetime.now(timezone.utc), "new")
    execution = execute(db_session, configuration_id, Gateway("h2", [commit]))
    assert execution.commits_discovered == 1
    assert execution.commits_verified == 1
