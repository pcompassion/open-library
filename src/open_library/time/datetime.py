#!/usr/bin/env python3
import pendulum


def now_local():
    return pendulum.now(tz=pendulum.local_timezone())


# Function to determine the date based on the time and base_date
def determine_datetime(time_str, base_datetime, time_format):
    hour = int(time_str[:2])
    if hour > 23:
        hour = hour - 24
        time_str = f"{hour:02d}{time_str[2:]}"

    time = pendulum.from_format(time_str, time_format).time()
    date = None
    base_date = base_datetime.date()
    base_time = base_datetime.time()

    if time < base_time:
        date = base_date
    else:
        date = base_date.subtract(days=1)
    datetime = pendulum.DateTime.combine(date, time).in_tz(base_datetime.tzinfo)
    datetime_str = datetime.to_iso8601_string()
    native_datetime = datetime.fromisoformat(datetime_str)
    return native_datetime


def combine(date, time):
    datetime = pendulum.DateTime.combine(date, time)
    return datetime
