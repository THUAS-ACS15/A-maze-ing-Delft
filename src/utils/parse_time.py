"""Parsing of ``str(timedelta)`` style duration strings."""

from datetime import timedelta


def parse_time_str(time_str: str) -> timedelta:
    """Convert ``H:MM:SS`` or ``D days, H:MM:SS`` into a timedelta.

    Args:
        time_str: Duration text as produced by ``str(timedelta)``. Fractional seconds are not supported.

    Returns:
        The equivalent timedelta.

    Raises:
        ValueError: If the text does not match the expected format.
    """
    time_str = time_str.strip()
    days = 0
    if " day" in time_str:
        # str(timedelta) renders spans over a day as "2 days, 3:04:05" (or "1 day, ...").
        day_part, time_str = time_str.split(", ", 1)
        days = int(day_part.split()[0])
    hours, minutes, seconds = map(int, time_str.split(":"))
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
