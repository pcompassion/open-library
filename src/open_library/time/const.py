#!/usr/bin/env python3
from enum import Enum, auto
from datetime import timedelta


class TimeUnit(str, Enum):
    MINUTE = "minute"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    SECOND = "second"
    HOUR = "hour"


class TimeFrame(Enum):
    MINUTE_1 = timedelta(minutes=1)
    MINUTE_3 = timedelta(minutes=3)
    MINUTE_5 = timedelta(minutes=5)
    HOUR_1 = timedelta(hours=1)
    DAY_1 = timedelta(days=1)

    UNDEFINED = None
