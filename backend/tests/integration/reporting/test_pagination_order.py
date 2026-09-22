from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from repository_miner.app import app
from repository_miner.persistence.database import SessionLocal
from repository_miner.persistence.models import MiningExecution, RepositoryFailure, UnauthorizedCommitAlert


def test_report_pages_are_stable_without_duplicates_or_omissions():
    execution_id = str(uuid4())
    configuration_id = str(uuid4())
    with SessionLocal.begin() as session:
        session.add(MiningExecution(id=execution_id, configuration_id=configuration_id, status="completed"))
        for index in range(5):
            timestamp = datetime(2026, 1, index + 1, tzinfo=UTC)
            session.add(UnauthorizedCommitAlert(id=f"alert-{execution_id[:8]}-{index}", configuration_id=configuration_id, execution_id=execution_id, commit_verification_id=f"verification-{execution_id[:8]}-{index}", repository_id="repo", branch="main", commit_hash=f"hash-{index}", author_name="Synthetic", author_email=None, committed_at=timestamp, detected_at=timestamp))
            session.add(RepositoryFailure(id=f"failure-{execution_id[:8]}-{index}", execution_id=execution_id, repository_execution_id=f"repository-execution-{execution_id[:8]}-{index}", stage="clone", code=f"failure-{index}", safe_reason="synthetic", occurred_at=timestamp, continued=True, correlation_id=f"correlation-{index}"))
    with TestClient(app) as client:
        alert_pages = [client.get(f"/api/v1/executions/{execution_id}/unauthorized-commits?offset={offset}&limit=2").json()["items"] for offset in (0, 2, 4)]
        failure_pages = [client.get(f"/api/v1/executions/{execution_id}/failures?offset={offset}&limit=2").json()["items"] for offset in (0, 2, 4)]
    alert_ids = [item["id"] for page in alert_pages for item in page]
    failure_ids = [item["id"] for page in failure_pages for item in page]
    assert alert_ids == [f"alert-{execution_id[:8]}-{index}" for index in range(4, -1, -1)]
    assert failure_ids == [f"failure-{execution_id[:8]}-{index}" for index in range(4, -1, -1)]
    assert len(alert_ids) == len(set(alert_ids)) == 5
    assert len(failure_ids) == len(set(failure_ids)) == 5
