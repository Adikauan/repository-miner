from __future__ import annotations

import calendar
from datetime import date, datetime, time


def monthly_due(year: int, month: int, day: int, local_time: time) -> datetime:
    last_day = calendar.monthrange(year, month)[1]
    return datetime.combine(date(year, month, min(day, last_day)), local_time)

