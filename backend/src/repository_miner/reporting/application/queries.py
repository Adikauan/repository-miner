from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from repository_miner.persistence.models import CommitVerification, ExecutionCommit, MiningExecution


def execution_report(session: Session, execution_id: str) -> dict[str, object]:
    execution = session.get(MiningExecution, execution_id)
    if execution is None:
        raise LookupError("execution not found")
    discovered = session.scalar(select(func.count(ExecutionCommit.id)).where(ExecutionCommit.execution_id == execution_id)) or 0
    verified = session.scalar(
        select(func.count(ExecutionCommit.id)).join(
            CommitVerification,
            (CommitVerification.commit_hash == ExecutionCommit.commit_hash)
            & (CommitVerification.first_verified_execution_id == execution_id),
        ).where(ExecutionCommit.execution_id == execution_id, ExecutionCommit.verification_source == "new")
    ) or 0
    if verified == 0 and execution.commits_verified:
        # Backward-compatible read for executions created before the durable
        # verification ledger was introduced.
        verified = execution.commits_verified
    allowed = session.scalar(
        select(func.count(ExecutionCommit.id)).join(
            CommitVerification,
            (CommitVerification.commit_hash == ExecutionCommit.commit_hash)
            & (CommitVerification.first_verified_execution_id == execution_id),
        ).where(ExecutionCommit.execution_id == execution_id, ExecutionCommit.verification_source == "new", CommitVerification.authorization_result == "allowed")
    ) or 0
    if allowed == 0 and execution.allowed_commits:
        allowed = execution.allowed_commits
    unauthorized = execution.unauthorized_commits if execution.unauthorized_commits and verified == execution.commits_verified else verified - allowed
    return {"execution_id": execution.id, "status": execution.status, "repositories_total": execution.repositories_total, "repositories_completed": execution.repositories_completed, "repositories_failed": execution.repositories_failed, "commits_discovered": discovered, "commits_verified": verified, "allowed_commits": allowed, "unauthorized_commits": unauthorized}
