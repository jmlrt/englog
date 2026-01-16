"""Timestamp and formatting helpers for englog."""

import re
from datetime import datetime


def get_current_time() -> str:
    """Get current time in HH:MM format (24-hour, local timezone)."""
    return datetime.now().strftime("%H:%M")


def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


def format_duration(minutes: int) -> str:
    """Format duration in minutes as 'Xh Ym' or 'Xm' format."""
    if minutes < 0:
        minutes = 0
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins}m" if hours > 0 else f"{mins}m"


def parse_duration(duration_str: str) -> int:
    """Parse duration string like '1h 23m' or '45m' into minutes."""
    hour_match = re.search(r"(\d+)h", duration_str)
    min_match = re.search(r"(\d+)m", duration_str)
    hours = int(hour_match.group(1)) if hour_match else 0
    minutes = int(min_match.group(1)) if min_match else 0
    return hours * 60 + minutes


def calculate_duration_minutes(start_time: str, end_time: str) -> int:
    """Calculate duration in minutes between two HH:MM times."""
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    return max(0, int((end - start).total_seconds() // 60))


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """Return singular or plural form based on count."""
    if plural is None:
        plural = singular + "s"
    return singular if count == 1 else plural
