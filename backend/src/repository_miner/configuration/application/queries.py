from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from repository_miner.persistence.models import AllowedUser, MonitoringConfiguration, RepositorySelectionRule, Schedule


def configuration_detail(session: Session, configuration_id: str) -> dict[str, object] | None:
    item = session.get(MonitoringConfiguration, configuration_id)
    if item is None:
        return None
    selections = session.scalars(select(RepositorySelectionRule).where(RepositorySelectionRule.configuration_id == configuration_id)).all()
    users = session.scalars(select(AllowedUser).where(AllowedUser.configuration_id == configuration_id).order_by(AllowedUser.normalized_email)).all()
    schedule = session.scalar(select(Schedule).where(Schedule.configuration_id == configuration_id))
    return {
        "id": item.id,
        "name": item.name,
        "gitlab_base_url": item.gitlab_base_url,
        "timezone": item.timezone,
        "enabled": item.enabled,
        "target_branch": item.target_branch if item.connection_validated_at else None,
        "credential_status": item.credential.status if item.credential else "compromised",
        "connection_validated": bool(item.connection_validated_at and item.validated_credential_id == item.current_credential_id),
        "allowed_emails": [user.original_email for user in users],
        "selections": [{"kind": rule.kind, "mode": rule.mode, "external_id": rule.external_id} for rule in selections],
        "schedule": ({
            "recurrence": schedule.recurrence,
            "local_time": schedule.local_time,
            "weekday": schedule.weekday,
            "day_of_month": schedule.day_of_month,
            "timezone": schedule.timezone,
            "next_run_at": schedule.next_run_at.isoformat() if schedule.next_run_at else None,
        } if schedule else None),
    }
