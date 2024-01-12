import pendulum
from datetime import datetime
import pytz


def print_tz(obj, tz=None):
    """
    # Example usage with a string timezone
    a = {
    "date_at": datetime(2024, 1, 12, 14, 7, 30, 21909, tzinfo=pytz.utc),
    "other_field": "value"
    }
    print_with_localtime(a, 'Asia/Seoul')

    # Example usage with a timezone instance
    b = {
    "date_at": datetime(2024, 1, 12, 14, 7, 30, 21909, tzinfo=pytz.utc),
    "other_field": "value"
    }
    seoul_tz = pendulum.timezone('Asia/Seoul')
    print_with_localtime(b, seoul_tz)

    """
    # Determine the appropriate timezone
    if isinstance(tz, str):
        local_tz = pendulum.timezone(tz)
    elif tz is None:
        local_tz = pendulum.local_timezone()
    else:
        local_tz = tz

    # Convert obj to dictionary if it's not already
    data = obj if isinstance(obj, dict) else obj.__dict__

    # Convert all datetime objects to local time
    for key, value in data.items():
        if isinstance(value, datetime) and value.tzinfo:
            # Convert aware datetime objects to local time
            data[key] = pendulum.instance(value).in_tz(local_tz)

    # Print the dictionary
    for key, value in data.items():
        print(f"{key}: {value}")
