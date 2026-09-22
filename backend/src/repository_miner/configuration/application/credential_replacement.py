from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from repository_miner.authentication.application.ports import AuthenticatedOperator
from repository_miner.configuration.domain.credential_replacement import validate_replacement
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.persistence.models import CredentialIncident, CredentialReference, MonitoringConfiguration
from repository_miner.persistence.repositories import replace_credential
from repository_miner.shared.domain.types import utc_now


def replace_configuration_credential(session: Session, configuration_id: str, new_secret: str, reason: str, operator: AuthenticatedOperator) -> CredentialReference:
    configuration = session.get(MonitoringConfiguration, configuration_id)
    if configuration is None or configuration.credential is None:
        raise ValueError("credential unavailable")
    previous = configuration.credential
    validate_replacement(previous.status, reason)
    incident_id = None
    if previous.status == "compromised":
        incident = session.scalar(select(CredentialIncident).where(CredentialIncident.credential_id == previous.id).order_by(CredentialIncident.suspected_at.desc()))
        incident_id = incident.id if incident else None
    replacement = CredentialReference(id=str(uuid4()), status="active", ciphertext=encrypt_secret(new_secret), key_version="v1", fingerprint=fingerprint(new_secret), created_at=utc_now())
    replace_credential(session, configuration_id=configuration_id, previous=previous, replacement=replacement, operator_id=operator.operator_id, reason=reason, incident_id=incident_id)
    configuration.current_credential_id = replacement.id
    configuration.connection_validated_at = None
    configuration.validated_gitlab_base_url = None
    configuration.validated_credential_id = None
    return replacement
