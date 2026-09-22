from datetime import datetime, timezone

from repository_miner.scheduling.domain.calendar import next_due


def test_daily_recurrence_rolls_to_next_day_after_configured_time():
    now = datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc)
    assert next_due(now, "daily", "09:00") == datetime(2026, 9, 21, 9, 0, tzinfo=timezone.utc)


def test_weekly_recurrence_respects_weekday_and_time():
    now = datetime(2026, 9, 20, 8, 0, tzinfo=timezone.utc)  # Sunday
    assert next_due(now, "weekly", "09:00", weekday=0) == datetime(2026, 9, 21, 9, 0, tzinfo=timezone.utc)


def test_monthly_recurrence_uses_last_calendar_day():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert next_due(now, "monthly", "09:00", day_of_month=31) == datetime(2026, 1, 31, 9, 0, tzinfo=timezone.utc)
    now = datetime(2026, 1, 31, 10, 0, tzinfo=timezone.utc)
    assert next_due(now, "monthly", "09:00", day_of_month=31) == datetime(2026, 2, 28, 9, 0, tzinfo=timezone.utc)


def test_recurrence_converts_local_time_to_utc():
    now = datetime(2026, 9, 20, 0, 0, tzinfo=timezone.utc)
    assert next_due(now, "daily", "09:00", timezone_name="America/Sao_Paulo") == datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)
