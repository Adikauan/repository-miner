from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from repository_miner.persistence.models import CredentialReference, MiningExecution, MonitoringConfiguration, Schedule, ScheduleOccurrence
from repository_miner.scheduling.domain.calendar import next_due


def reconcile_schedules(session: Session, now: datetime | None = None, *, commit: bool = True) -> None:
    now = now or datetime.now(timezone.utc)
    for schedule in session.scalars(select(Schedule)).all():
        config = session.get(MonitoringConfiguration, schedule.configuration_id)
        if config is None or not config.enabled:
            continue
        # Keep an overdue due_at intact so startup reconciliation can collapse
        # downtime into one latest occurrence. Only uninitialized schedules get a
        # first due time here.
        if schedule.next_run_at is None:
            schedule.next_run_at = next_due(now, schedule.recurrence, schedule.local_time, weekday=schedule.weekday, day_of_month=schedule.day_of_month, timezone_name=schedule.timezone)
    if commit:
        session.commit()


def claim_due_occurrences(session: Session, now: datetime | None = None) -> list[ScheduleOccurrence]:
    now = now or datetime.now(timezone.utc)
    claimed: list[ScheduleOccurrence] = []
    for schedule in session.scalars(select(Schedule).where(Schedule.next_run_at <= now)).all():
        config = session.get(MonitoringConfiguration, schedule.configuration_id)
        if config is None:
            continue
        # Collapse all missed occurrences to the most recent due time and advance
        # the persisted schedule beyond now. This is idempotent across restarts.
        latest_due = schedule.next_run_at
        while True:
            candidate = next_due(latest_due, schedule.recurrence, schedule.local_time, weekday=schedule.weekday, day_of_month=schedule.day_of_month, timezone_name=schedule.timezone)
            if candidate > now:
                break
            latest_due = candidate
        next_future = next_due(latest_due, schedule.recurrence, schedule.local_time, weekday=schedule.weekday, day_of_month=schedule.day_of_month, timezone_name=schedule.timezone)
        schedule.next_run_at = next_future
        existing = session.scalar(select(ScheduleOccurrence).where(
            ScheduleOccurrence.configuration_id == config.id, ScheduleOccurrence.due_at == latest_due,
        ))
        if existing is not None:
            continue
        if not config.enabled:
            session.add(ScheduleOccurrence(id=str(uuid4()), configuration_id=config.id, due_at=latest_due, status="skipped_disabled", safe_reason="configuration disabled"))
            continue
        credential = session.get(CredentialReference, config.current_credential_id) if config.current_credential_id else None
        if credential is None or credential.status != "active":
            session.add(ScheduleOccurrence(id=str(uuid4()), configuration_id=config.id, due_at=latest_due, status="skipped_compromised", safe_reason="credential unavailable"))
            continue
        active = session.scalar(select(MiningExecution).where(MiningExecution.configuration_id == config.id, MiningExecution.status.in_(["pending", "running"])))
        if active is not None:
            session.add(ScheduleOccurrence(id=str(uuid4()), configuration_id=config.id, due_at=latest_due, status="skipped_active", safe_reason="execution already active"))
            continue
        occurrence = ScheduleOccurrence(id=str(uuid4()), configuration_id=config.id, due_at=latest_due, status="started")
        try:
            session.add(occurrence)
            session.flush()
        except Exception:
            session.rollback()
            continue
        claimed.append(occurrence)
    session.commit()
    return claimed


def run_due_schedules(session_factory, gateway, publisher=None, now: datetime | None = None) -> int:
    from repository_miner.executions.application.start_execution import start_persistent_execution
    with session_factory() as session:
        occurrences = claim_due_occurrences(session, now)
        count = 0
        for occurrence in occurrences:
            try:
                execution = start_persistent_execution(session, gateway, occurrence.configuration_id, publisher)
                # The occurrence remains `started` with its execution reference;
                # the execution itself is the durable completion record.
                occurrence.status = "started"
                occurrence.execution_id = execution.id
                count += 1
            except RuntimeError as exc:
                occurrence.status = "skipped" if "active" in str(exc) or "credential" in str(exc) else "failed"
                occurrence.safe_reason = str(exc)[:512]
        session.commit()
        return count
