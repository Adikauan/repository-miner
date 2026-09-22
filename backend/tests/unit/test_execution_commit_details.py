from datetime import datetime, timezone
from uuid import uuid4

from repository_miner.executions.application.queries import execution_commit_details
from repository_miner.persistence.models import CommitVerification, ExecutionCommit, MiningExecution, MonitoringConfiguration, RepositoryExecution


def test_execution_commit_details_include_repository_and_verification_fields(db_session):
    configuration_id = str(uuid4())
    execution_id = str(uuid4())
    repository_execution_id = str(uuid4())
    commit_hash = "commit-synthetic"
    db_session.add(MonitoringConfiguration(id=configuration_id, name="Plan", gitlab_base_url="https://gitlab.example"))
    db_session.add(MiningExecution(id=execution_id, configuration_id=configuration_id, status="completed"))
    db_session.add(RepositoryExecution(id=repository_execution_id, execution_id=execution_id, repository_id="group/repository", branch="main"))
    db_session.add(ExecutionCommit(id=str(uuid4()), execution_id=execution_id, repository_execution_id=repository_execution_id, commit_hash=commit_hash, verification_source="new"))
    db_session.add(CommitVerification(
        id=str(uuid4()), configuration_id=configuration_id, repository_id="group/repository", branch="main",
        commit_hash=commit_hash, author_name="Synthetic Author", author_email="author@example.test",
        committed_at=datetime.now(timezone.utc), message="Synthetic commit", authorization_result="allowed",
        first_verified_execution_id=execution_id, verified_at=datetime.now(timezone.utc),
    ))
    db_session.commit()

    rows = execution_commit_details(db_session, execution_id)

    commit, repository, verification = rows[0]
    assert commit.commit_hash == commit_hash
    assert repository.repository_id == "group/repository"
    assert repository.branch == "main"
    assert verification.author_name == "Synthetic Author"
    assert verification.authorization_result == "allowed"
