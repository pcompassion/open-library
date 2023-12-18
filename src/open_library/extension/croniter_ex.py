#!/usr/bin/env python3
from croniter import croniter
from datetime import datetime, timedelta
from open_library.time.const import TimeUnit, TimeFrame


def estimate_interval(
    cron_expression,
    base_time=None,
    num_intervals=2,
    time_unit: TimeUnit = TimeUnit.SECOND,
):
    iter = croniter(cron_expression, base_time)
    times = [iter.get_next(datetime) for _ in range(num_intervals)]

    interval = (times[-1] - times[0]) / (num_intervals - 1)

    seconds = interval.total_seconds()
    match time_unit:
        case TimeUnit.SECOND:
            return seconds
        case TimeUnit.MINUTES:
            return seconds / 60
        case TimeUnit.HOURS:
            return seconds / 3600
        case _:
            raise ValueError("invalid TimeUnit")


def estimate_timeframe(
    cron_expression,
    base_time=None,
    num_intervals=2,
):
    seconds = estimate_interval(
        cron_expression, base_time, num_intervals, time_unit=TimeUnit.SECOND
    )

    # Find the closest TimeFrame
    for time_frame in TimeFrame:
        if time_frame.value and time_frame.value.total_seconds() == seconds:
            return time_frame

    return TimeFrame.UNDEFINED


if __name__ == "__main__":
    # Example usage
    cron_expression = "*/5 * * * *"  # Every 5 minutes
    base_time = datetime.now()

    intervals = estimate_interval(cron_expression, base_time)
    print(intervals)
