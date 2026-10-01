"""Display helpers for englog."""


def format_duration(minutes: int) -> str:
    """Format minutes as '1h', '1h 5m' or '45m'."""
    hours, mins = divmod(max(0, minutes), 60)
    if hours == 0:
        return f"{mins}m"
    return f"{hours}h" if mins == 0 else f"{hours}h {mins}m"
