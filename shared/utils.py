# Utility Functions

from datetime import datetime


def current_datetime_utc():
    """Return the current date and time in UTC formatted as 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def your_function_name():
    """Your utility function description."""
    pass
