from datetime import datetime, timezone
from uuid import uuid4

from repository_miner.persistence.models import ExecutionCommit, MiningExecution
from repository_miner.reporting.application.queries import execution_report


def test_report_uses_execution_counters_and_discovered_observations(db_session):
    execution_id = str(uuid4())
    db_session.add(MiningExecution(id=execution_id, configuration_id=str(uuid4()), status="completed", commits_verified=2, allowed_commits=1, unauthorized_commits=1, repositories_completed=1))
    db_session.add(ExecutionCommit(id=str(uuid4()), execution_id=execution_id, repository_execution_id=str(uuid4()), commit_hash="a", verification_source="new"))
    db_session.add(ExecutionCommit(id=str(uuid4()), execution_id=execution_id, repository_execution_id=str(uuid4()), commit_hash="b", verification_source="reused"))
    db_session.commit()
    result = execution_report(db_session, execution_id)
    assert result["commits_discovered"] == 2
    assert result["commits_verified"] == 2
    assert result["allowed_commits"] + result["unauthorized_commits"] == result["commits_verified"]
