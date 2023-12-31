#!/usr/bin/env python3

import pendulum
import calendar
from pendulum import Date


def find_nth_weekday_of_month(
    year: int, month: int, weekday: int, n: int
) -> Date | None:
    """
    Find the nth occurrence of a weekday in a specific month and year.

    :param year: The year as an integer (e.g., 2024).
    :param month: The month as an integer (1-12).
    :param weekday: The day of the week using calendar module constants (e.g., calendar.MONDAY).
    :param n: The nth occurrence of the weekday to find.
    :return: A datetime.date object representing the nth weekday of the given month and year, or None if it does not exist.

    # Example usage: Find the 2nd Tuesday (calendar.TUESDAY) of January 2024
    print(find_nth_weekday_of_month(2024, 1, calendar.TUESDAY, 2))

    """
    # Create a calendar month matrix
    month_calendar = calendar.monthcalendar(year, month)

    # Count the number of occurrences of the weekday
    weekday_count = 0
    for week in month_calendar:
        if week[weekday] != 0:
            weekday_count += 1
            if weekday_count == n:  # Found the nth weekday
                return pendulum.date(year, month, week[weekday])

    # If the nth weekday does not exist (e.g., asking for the 5th Monday in a month that only has 4)
    return None
