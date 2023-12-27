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
    SECOND_1 = timedelta(seconds=1)
    SECOND_5 = timedelta(seconds=5)
    SECOND_10 = timedelta(seconds=10)

    SECOND_30 = timedelta(seconds=30)

    MINUTE_1 = timedelta(minutes=1)
    MINUTE_3 = timedelta(minutes=3)
    MINUTE_5 = timedelta(minutes=5)
    MINUTE_10 = timedelta(minutes=10)
    HOUR_1 = timedelta(hours=1)
    DAY_1 = timedelta(days=1)
    WEEK_1 = timedelta(days=7)

    UNDEFINED = None
