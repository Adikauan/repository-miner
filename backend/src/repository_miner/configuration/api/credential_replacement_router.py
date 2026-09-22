from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from repository_miner.authentication.application.ports import AuthenticatedOperator
from repository_miner.authentication.infrastructure.http import host_operator
from repository_miner.configuration.application.credential_replacement import replace_configuration_credential
from repository_miner.persistence.database import SessionLocal


class CredentialReplacementBody(BaseModel):
    gitlab_token: str = Field(min_length=1)
    reason: str = "preventive"


router = APIRouter(prefix="/api/v1/configurations", tags=["credentials"])


@router.post("/{configuration_id}/credential-replacements", status_code=201)
def replace_credential_route(configuration_id: UUID, body: CredentialReplacementBody, operator: AuthenticatedOperator | None = Depends(host_operator)):
    if operator is None:
        raise HTTPException(status_code=401, detail={"code": "operator_unauthenticated", "message": "Authenticated operator required."})
    try:
        with SessionLocal.begin() as session:
            replacement = replace_configuration_credential(session, str(configuration_id), body.gitlab_token, body.reason, operator)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail={"code": "credential_replacement_rejected", "message": str(exc)}) from exc
    return {"configuration_id": str(configuration_id), "credential_status": replacement.status, "connection_validated": False, "reason": body.reason}
