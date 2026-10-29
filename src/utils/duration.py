"""Elapsed-time calculation between ISO timestamps."""

from datetime import datetime, timedelta

def calculate_duration(start_time: str, end_time: str) -> timedelta:
    """Return the time between two ISO 8601 timestamps, truncated to whole seconds.

    Args:
        start_time: Start timestamp (``datetime.fromisoformat`` format).
        end_time: End timestamp in the same format; both must be naive or both timezone-aware.

    Returns:
        ``end_time - start_time`` without microseconds.

    Raises:
        ValueError: If either timestamp is not valid ISO 8601.
        TypeError: If one timestamp is timezone-aware and the other is not.
    """
    dt_start = datetime.fromisoformat(start_time)
    dt_end = datetime.fromisoformat(end_time)

    duration = dt_end - dt_start
    # Remove microseconds from the timedelta object
    return duration - timedelta(microseconds=duration.microseconds)