from datetime import datetime

def current_datetime_utc() -> str:
    """Return the current date and time in UTC formatted as 'YYYY-MM-DD HH:MM:SS'"""
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

def get_app_version() -> str:
    """Get application version"""
    return "1.0.0"

def get_app_name() -> str:
    """Get application name"""
    return "MeterLabTools"