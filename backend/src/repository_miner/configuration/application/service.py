from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.persistence.models import CredentialReference, MonitoringConfiguration
from repository_miner.shared.domain.types import utc_now


def create_configuration(session: Session, *, name: str, gitlab_base_url: str, gitlab_token: str, timezone: str = "UTC", enabled: bool = True) -> MonitoringConfiguration:
    credential_id = str(uuid4())
    configuration = MonitoringConfiguration(id=str(uuid4()), name=name, gitlab_base_url=gitlab_base_url, timezone=timezone, target_branch="QA", enabled=enabled, current_credential_id=credential_id)
    session.add(CredentialReference(id=credential_id, status="active", ciphertext=encrypt_secret(gitlab_token), key_version="v1", fingerprint=fingerprint(gitlab_token), created_at=utc_now()))
    session.add(configuration)
    return configuration


def get_configuration(session: Session, configuration_id: str) -> MonitoringConfiguration | None:
    return session.get(MonitoringConfiguration, configuration_id)


def update_configuration(session: Session, configuration_id: str, *, name: str | None = None, enabled: bool | None = None, timezone: str | None = None) -> MonitoringConfiguration:
    configuration = session.get(MonitoringConfiguration, configuration_id)
    if configuration is None:
        raise ValueError("configuration not found")
    if name is not None:
        configuration.name = name
    if enabled is not None:
        configuration.enabled = enabled
    if timezone is not None:
        configuration.timezone = timezone
    return configuration


def invalidate_connection(session: Session, configuration: MonitoringConfiguration) -> None:
    configuration.connection_validated_at = None
    configuration.validated_gitlab_base_url = None
    configuration.validated_credential_id = None
