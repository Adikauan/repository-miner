from datetime import datetime, timezone
from uuid import uuid4

from repository_miner.persistence.models import CommitVerification, MiningExecution, UnauthorizedCommitAlert
from repository_miner.reporting.application.queries import execution_report


def test_alert_remains_owned_by_original_detection_execution(db_session):
    configuration_id = str(uuid4())
    original_id, later_id = str(uuid4()), str(uuid4())
    db_session.add_all([
        MiningExecution(id=original_id, configuration_id=configuration_id, status="completed", unauthorized_commits=1),
        MiningExecution(id=later_id, configuration_id=configuration_id, status="completed"),
    ])
    verification = CommitVerification(
        id=str(uuid4()), configuration_id=configuration_id, repository_id="r1", branch="QA",
        commit_hash="abc", author_name="Unknown", author_email=None,
        committed_at=datetime.now(timezone.utc), message="change", authorization_result="unauthorized",
        first_verified_execution_id=original_id, verified_at=datetime.now(timezone.utc),
    )
    db_session.add(verification)
    db_session.add(UnauthorizedCommitAlert(
        id=str(uuid4()), configuration_id=configuration_id, execution_id=original_id,
        commit_verification_id=verification.id, repository_id="r1", branch="QA", commit_hash="abc",
        author_name="Unknown", author_email=None, committed_at=verification.committed_at,
        detected_at=datetime.now(timezone.utc),
    ))
    db_session.commit()
    assert db_session.query(UnauthorizedCommitAlert).filter_by(execution_id=later_id).count() == 0
    assert execution_report(db_session, later_id)["unauthorized_commits"] == 0
