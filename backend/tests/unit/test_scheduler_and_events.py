from datetime import datetime, time, timezone

from repository_miner.executions.application.event_publisher import ExecutionEventPublisher
from repository_miner.scheduling.domain.calendar import next_due


def test_daily_and_weekly_occurrences_are_clock_controlled():
    now = datetime(2026, 9, 19, 10, 0, tzinfo=timezone.utc)
    assert next_due(now, "daily", "09:00") == datetime(2026, 9, 20, 9, 0, tzinfo=timezone.utc)
    assert next_due(now, "weekly", "11:00", weekday=0) == datetime(2026, 9, 21, 11, 0, tzinfo=timezone.utc)


def test_monthly_falls_back_to_last_day_including_leap_year():
    now = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert next_due(now, "monthly", "12:00", day_of_month=31) == datetime(2024, 1, 31, 12, 0, tzinfo=timezone.utc)
    feb = datetime(2024, 2, 1, 0, 0, tzinfo=timezone.utc)
    assert next_due(feb, "monthly", "12:00", day_of_month=31) == datetime(2024, 2, 29, 12, 0, tzinfo=timezone.utc)


def test_event_publisher_envelope_and_monotonic_revision():
    hub = ExecutionEventPublisher()
    first = hub.publish("execution.started", "e1", "c1", {"status": "running"})
    second = hub.publish("repository.progress", "e1", "c1", {"commits_verified": 1}, repository_id="r1")
    assert first["revision"] == 1 and second["revision"] == 2
    assert [e["type"] for e in hub.since("e1", 1)] == ["repository.progress"]
