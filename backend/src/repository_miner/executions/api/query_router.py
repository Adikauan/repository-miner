from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from repository_miner.persistence.database import SessionLocal
from repository_miner.persistence.models import MiningExecution, ScheduleOccurrence
from repository_miner.executions.application.queries import execution_commit_details, execution_failures, execution_repositories

router = APIRouter(prefix="/api/v1/executions")


@router.get("")
def list_executions(configuration_id: str | None = None, status: str | None = None, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    with SessionLocal() as session:
        query = select(MiningExecution).order_by(MiningExecution.started_at.desc().nullslast(), MiningExecution.id.desc())
        if status:
            query = query.where(MiningExecution.status == status)
        if configuration_id:
            query = query.where(MiningExecution.configuration_id == configuration_id)
        rows = list(session.scalars(query.offset(offset).limit(limit)).all())
        scheduled_ids = set(session.scalars(select(ScheduleOccurrence.execution_id).where(ScheduleOccurrence.execution_id.in_([row.id for row in rows]))).all()) if rows else set()
        return {"items": [{"id": r.id, "configuration_id": r.configuration_id, "origin": "scheduled" if r.id in scheduled_ids else "manual", "status": r.status, "started_at": r.started_at.isoformat() if r.started_at else None, "finished_at": r.finished_at.isoformat() if r.finished_at else None, "repositories_total": r.repositories_total, "repositories_completed": r.repositories_completed, "repositories_failed": r.repositories_failed, "commits_discovered": r.commits_discovered, "commits_verified": r.commits_verified, "allowed_commits": r.allowed_commits, "unauthorized_commits": r.unauthorized_commits} for r in rows], "offset": offset, "limit": limit}


def _execution(execution_id: str):
    with SessionLocal() as session:
        item = session.get(MiningExecution, execution_id)
        if item is None:
            raise HTTPException(status_code=404, detail={"code": "execution_not_found", "message": "Execution not found."})
        return item


@router.get("/{execution_id}/repositories")
def repositories(execution_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    _execution(execution_id)
    with SessionLocal() as session:
        rows = execution_repositories(session, execution_id, offset, limit)
        return {"items": [{"id": r.id, "repository_id": r.repository_id, "branch": r.branch, "status": r.status, "observed_head": r.observed_head, "failure_reason": r.failure_reason} for r in rows], "offset": offset, "limit": limit}


@router.get("/{execution_id}/commits")
def commits(execution_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    _execution(execution_id)
    with SessionLocal() as session:
        rows = execution_commit_details(session, execution_id, offset, limit)
        return {"items": [{
            "commit_hash": commit.commit_hash,
            "repository": repository.repository_id,
            "branch": repository.branch,
            "author": verification.author_name if verification else None,
            "author_email": verification.author_email if verification else None,
            "committed_at": verification.committed_at.isoformat() if verification else None,
            "message": verification.message if verification else None,
            "authorization_result": verification.authorization_result if verification else None,
            "verification_source": commit.verification_source,
            "repository_execution_id": commit.repository_execution_id,
        } for commit, repository, verification in rows], "offset": offset, "limit": limit}


@router.get("/{execution_id}/failures")
def failures(execution_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    _execution(execution_id)
    with SessionLocal() as session:
        rows = execution_failures(session, execution_id, offset, limit)
        return {"items": [{"id": r.id, "repository_execution_id": r.repository_execution_id, "stage": r.stage, "code": r.code, "safe_reason": r.safe_reason, "occurred_at": r.occurred_at.isoformat()} for r in rows], "offset": offset, "limit": limit}
