from __future__ import annotations

import calendar
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def next_due(now: datetime, recurrence: str, local_time: str, *, weekday: int | None = None, day_of_month: int | None = None, timezone_name: str = "UTC") -> datetime:
    zone = ZoneInfo(timezone_name)
    local = now.astimezone(zone).replace(second=0, microsecond=0)
    hour, minute = (int(part) for part in local_time.split(":", 1))
    candidate = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if recurrence == "daily":
        if candidate <= local:
            candidate += timedelta(days=1)
    elif recurrence == "weekly":
        target = 0 if weekday is None else int(weekday)
        delta = (target - candidate.weekday()) % 7
        candidate += timedelta(days=delta)
        if candidate <= local:
            candidate += timedelta(days=7)
    elif recurrence == "monthly":
        target = max(1, int(day_of_month or 1))
        candidate = candidate.replace(day=min(target, calendar.monthrange(candidate.year, candidate.month)[1]))
        if candidate <= local:
            year, month = candidate.year + (1 if candidate.month == 12 else 0), 1 if candidate.month == 12 else candidate.month + 1
            candidate = candidate.replace(year=year, month=month, day=min(target, calendar.monthrange(year, month)[1]))
    else:
        raise ValueError("unsupported recurrence")
    return candidate.astimezone(ZoneInfo("UTC"))
