from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from repository_miner.authentication.application.ports import AuthenticatedOperator
from repository_miner.persistence.models import CredentialIncident, MonitoringConfiguration
from repository_miner.shared.domain.types import utc_now


def mark_credential_compromised(session: Session, configuration_id: str, operator: AuthenticatedOperator) -> CredentialIncident:
    configuration = session.get(MonitoringConfiguration, configuration_id)
    if configuration is None or configuration.credential is None:
        raise ValueError("configuration credential not found")
    credential = configuration.credential
    credential.status = "compromised"
    credential.compromised_at = utc_now()
    incident = session.scalar(select(CredentialIncident).where(CredentialIncident.credential_id == credential.id, CredentialIncident.status == "open"))
    if incident is None:
        incident = CredentialIncident(id=str(uuid4()), credential_id=credential.id, status="open", suspected_by=operator.operator_id, safe_reason="suspected credential exposure", suspected_at=utc_now())
        session.add(incident)
    return incident
