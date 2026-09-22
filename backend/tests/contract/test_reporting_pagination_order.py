from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from repository_miner.app import app
from repository_miner.persistence.database import SessionLocal
from repository_miner.persistence.models import MiningExecution, RepositoryFailure, UnauthorizedCommitAlert


def _seed_report_rows() -> str:
    execution_id = str(uuid4())
    configuration_id = str(uuid4())
    with SessionLocal.begin() as session:
        session.add(MiningExecution(id=execution_id, configuration_id=configuration_id, status="completed"))
        for suffix, detected_at in (("old", datetime(2026, 1, 1, tzinfo=UTC)), ("new", datetime(2026, 1, 3, tzinfo=UTC))):
            session.add(UnauthorizedCommitAlert(id=f"alert-{suffix}-{execution_id[:8]}", configuration_id=configuration_id, execution_id=execution_id, commit_verification_id=f"verification-{suffix}-{execution_id[:8]}", repository_id="repo", branch="main", commit_hash=f"hash-{suffix}", author_name="Synthetic", author_email=None, committed_at=detected_at, detected_at=detected_at))
            session.add(RepositoryFailure(id=f"failure-{suffix}-{execution_id[:8]}", execution_id=execution_id, repository_execution_id=f"repository-execution-{suffix}-{execution_id[:8]}", stage="clone", code=f"failure-{suffix}", safe_reason="synthetic", occurred_at=detected_at, continued=True, correlation_id=f"correlation-{suffix}"))
    return execution_id


def test_reporting_lists_return_newest_alerts_and_failures_first():
    execution_id = _seed_report_rows()
    with TestClient(app) as client:
        alerts = client.get(f"/api/v1/executions/{execution_id}/unauthorized-commits?offset=0&limit=1").json()
        failures = client.get(f"/api/v1/executions/{execution_id}/failures?offset=0&limit=1").json()
    assert alerts["items"][0]["commit_hash"] == "hash-new"
    assert failures["items"][0]["code"] == "failure-new"
