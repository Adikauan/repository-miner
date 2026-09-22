from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from repository_miner.persistence.models import CommitVerification, ExecutionCommit, MiningExecution, RepositoryExecution, RepositoryFailure


def page(query, offset: int = 0, limit: int = 50):
    return query.offset(max(0, offset)).limit(min(max(1, limit), 200))


def execution_repositories(session: Session, execution_id: str, offset: int = 0, limit: int = 50):
    return list(session.scalars(page(select(RepositoryExecution).where(RepositoryExecution.execution_id == execution_id).order_by(RepositoryExecution.repository_id), offset, limit)).all())


def execution_commits(session: Session, execution_id: str, offset: int = 0, limit: int = 50):
    return list(session.scalars(page(select(ExecutionCommit).where(ExecutionCommit.execution_id == execution_id).order_by(ExecutionCommit.commit_hash), offset, limit)).all())


def execution_commit_details(session: Session, execution_id: str, offset: int = 0, limit: int = 50):
    """Return execution commits enriched with their repository and verification metadata."""
    query = (
        select(ExecutionCommit, RepositoryExecution, CommitVerification)
        .join(RepositoryExecution, RepositoryExecution.id == ExecutionCommit.repository_execution_id)
        .join(MiningExecution, MiningExecution.id == ExecutionCommit.execution_id)
        .outerjoin(
            CommitVerification,
            and_(
                CommitVerification.configuration_id == MiningExecution.configuration_id,
                CommitVerification.repository_id == RepositoryExecution.repository_id,
                CommitVerification.branch == RepositoryExecution.branch,
                CommitVerification.commit_hash == ExecutionCommit.commit_hash,
            ),
        )
        .where(ExecutionCommit.execution_id == execution_id)
        .order_by(ExecutionCommit.commit_hash)
    )
    return list(session.execute(page(query, offset, limit)).all())


def execution_failures(session: Session, execution_id: str, offset: int = 0, limit: int = 50):
    return list(session.scalars(page(select(RepositoryFailure).where(RepositoryFailure.execution_id == execution_id).order_by(RepositoryFailure.occurred_at.desc(), RepositoryFailure.id.desc()), offset, limit)).all())
