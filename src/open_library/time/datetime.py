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


def intervals_overlap(interval1, interval2):
    start1, end1 = interval1
    start2, end2 = interval2

    # Overlap occurs if one interval starts before the other ends and ends after the other starts
    return max(start1, start2) < min(end1, end2)


def does_time_overlap_with_datetime_interval(time_interval, datetime_interval):
    start_time, end_time = time_interval  # time_interval like (18, 5)
    (
        datetime_start,
        datetime_end,
    ) = datetime_interval  # datetime_interval like (pendulum.datetime(2023, 12, 1, 19), pendulum.datetime(2023, 12, 2, 1))

    # Normalize the time interval for comparison
    # If end_time is less than start_time, it indicates wrapping to the next day

    start_time = start_time.hour + start_time.minute / 60
    end_time = end_time.hour + end_time.minute / 60
    if end_time < start_time:
        end_time += 24

    # Convert datetime interval to just time for comparison and handle day change
    datetime_start_time = datetime_start.hour + datetime_start.minute / 60
    datetime_end_time = datetime_end.hour + datetime_end.minute / 60

    # Adjust for day wrapping in datetime interval
    if start_time < end_time:
        end_time += 24

    if datetime_end_time < datetime_start_time:
        datetime_end_time += 24

    # Check for overlap
    latest_start = max(start_time, datetime_start_time)
    earliest_end = min(end_time, datetime_end_time)

    return latest_start < earliest_end


# # Example Usage:
# time_interval = (pendulum.time(18), pendulum.time(5))  # Represents 18:00 to 05:00
# datetime_interval1 = (
#     pendulum.datetime(2023, 12, 1, 19, 0),
#     pendulum.datetime(2023, 12, 2, 1, 0),
# )
# datetime_interval2 = (
#     pendulum.datetime(2023, 12, 1, 6, 0),
#     pendulum.datetime(2023, 12, 1, 15, 0),
# )

# print(
#     does_time_overlap_with_datetime_interval(time_interval, datetime_interval1)
# )  # Should print True
# print(
#     does_time_overlap_with_datetime_interval(time_interval, datetime_interval2)
# )  # Should print False
