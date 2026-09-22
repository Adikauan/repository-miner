from sqlalchemy import select
from repository_miner.persistence.models import UnauthorizedCommitAlert, RepositoryFailure


def alerts_for_execution(session, execution_id: str, offset: int = 0, limit: int = 50):
    return list(session.scalars(select(UnauthorizedCommitAlert).where(UnauthorizedCommitAlert.execution_id == execution_id).order_by(UnauthorizedCommitAlert.detected_at.desc(), UnauthorizedCommitAlert.id.desc()).offset(offset).limit(limit)).all())


def failures_for_execution(session, execution_id: str, offset: int = 0, limit: int = 50):
    return list(session.scalars(select(RepositoryFailure).where(RepositoryFailure.execution_id == execution_id).order_by(RepositoryFailure.occurred_at.desc(), RepositoryFailure.id.desc()).offset(offset).limit(limit)).all())
