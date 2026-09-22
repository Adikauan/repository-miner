from fastapi import APIRouter, HTTPException, Query
from repository_miner.persistence.database import SessionLocal
from repository_miner.reporting.application.queries import execution_report
from repository_miner.alerts.application.queries import alerts_for_execution, failures_for_execution

router = APIRouter(prefix="/api/v1/executions")


@router.get("/{execution_id}/report-v2")
def report(execution_id: str):
    with SessionLocal() as session:
        try:
            return execution_report(session, execution_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail={"code": "execution_not_found", "message": str(exc)})


@router.get("/{execution_id}/unauthorized-commits")
def unauthorized_commits(execution_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    with SessionLocal() as session:
        rows = alerts_for_execution(session, execution_id, offset, limit)
        return {"items": [{"id": r.id, "execution_id": r.execution_id, "configuration_id": r.configuration_id, "repository_id": r.repository_id, "branch": r.branch, "commit_hash": r.commit_hash, "author_name": r.author_name, "author_email": r.author_email, "committed_at": r.committed_at.isoformat()} for r in rows], "offset": offset, "limit": limit}


@router.get("/{execution_id}/failures-detail")
def failure_details(execution_id: str, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    with SessionLocal() as session:
        rows = failures_for_execution(session, execution_id, offset, limit)
        return {"items": [{"id": r.id, "repository_execution_id": r.repository_execution_id, "stage": r.stage, "code": r.code, "safe_reason": r.safe_reason, "occurred_at": r.occurred_at.isoformat()} for r in rows], "offset": offset, "limit": limit}
