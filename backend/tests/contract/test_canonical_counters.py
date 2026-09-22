from datetime import datetime, timezone
from uuid import uuid4

from repository_miner.app import db_execution_view
from repository_miner.mining.application.persistent_runner import run_execution
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.persistence.models import (
    CredentialReference, MiningExecution, MonitoringConfiguration, RepositorySelectionRule,
)
from repository_miner.reporting.application.queries import execution_report


class EmptyGitLab:
    def branch_head(self, base_url, token, repository_id, branch):
        return "head"

    def commits_after(self, base_url, token, repository_id, branch, sha):
        return []


class RecordingPublisher:
    def __init__(self):
        self.events = []

    def publish(self, event_type, execution_id, configuration_id, payload, repository_id=None):
        self.events.append((event_type, payload))


def test_zero_commit_execution_exposes_canonical_counters_everywhere(db_session):
    configuration_id, credential_id = str(uuid4()), str(uuid4())
    db_session.add(CredentialReference(
        id=credential_id, status="active", ciphertext=encrypt_secret("token"), key_version="v1",
        fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc),
    ))
    db_session.add(MonitoringConfiguration(
        id=configuration_id, name="cfg", gitlab_base_url="https://gitlab.local",
        target_branch="QA", current_credential_id=credential_id,
    ))
    db_session.add(RepositorySelectionRule(
        id=str(uuid4()), configuration_id=configuration_id, kind="repository",
        mode="include", external_id="r1",
    ))
    execution = MiningExecution(id=str(uuid4()), configuration_id=configuration_id, status="pending")
    db_session.add(execution)
    db_session.commit()
    publisher = RecordingPublisher()

    result = run_execution(db_session, EmptyGitLab(), execution.id, publisher)
    view = db_execution_view(result)
    report = execution_report(db_session, execution.id)
    canonical = {"repositories_total", "repositories_completed", "repositories_failed", "commits_discovered", "commits_verified", "allowed_commits", "unauthorized_commits"}
    assert canonical.issubset(view)
    assert canonical.issubset(report)
    assert result.status == "completed"
    assert report["commits_discovered"] == report["commits_verified"] == 0
    for event_type, payload in publisher.events:
        if event_type in {"execution.started", "repository.completed", "execution.completed"}:
            counters = payload.get("counters") or payload.get("summary_counts") or payload
            assert canonical.issubset(counters)
