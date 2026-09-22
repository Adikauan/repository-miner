from __future__ import annotations

from repository_miner.scheduling.domain.calendar import next_due
from repository_miner.shared.domain.types import utc_now
from repository_miner.persistence.models import Schedule
from sqlalchemy.orm import Session

from repository_miner.persistence.models import MonitoringConfiguration


def update_basic_fields(session: Session, configuration_id: str, *, name: str | None = None, timezone: str | None = None, enabled: bool | None = None) -> MonitoringConfiguration:
    item = session.get(MonitoringConfiguration, configuration_id)
    if item is None:
        raise ValueError("configuration not found")
    if name is not None:
        item.name = name
    if timezone is not None:
        item.timezone = timezone
    if enabled is not None:
        item.enabled = enabled
        schedule = session.query(Schedule).filter(Schedule.configuration_id == configuration_id).one_or_none()
        if schedule is not None:
            schedule.next_run_at = (
                next_due(utc_now(), schedule.recurrence, schedule.local_time, weekday=schedule.weekday, day_of_month=schedule.day_of_month, timezone_name=schedule.timezone)
                if enabled else None
            )
    return item


def update_connection_identity(session: Session, configuration_id: str, *, gitlab_base_url: str) -> MonitoringConfiguration:
    item = session.get(MonitoringConfiguration, configuration_id)
    if item is None:
        raise ValueError("configuration not found")
    if item.gitlab_base_url != gitlab_base_url:
        item.gitlab_base_url = gitlab_base_url
        item.connection_validated_at = None
        item.validated_gitlab_base_url = None
        item.validated_credential_id = None
    return item


def connection_is_validated(item: MonitoringConfiguration) -> bool:
    return bool(item.connection_validated_at and item.validated_credential_id == item.current_credential_id)
