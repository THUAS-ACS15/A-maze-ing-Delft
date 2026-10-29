"""Human-readable formatting of ISO 8601 timestamps."""

from datetime import datetime


def format_timestamp(iso_str: str, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Format an ISO 8601 string (e.g. ``'2026-10-24T10:30:43.756Z'``) as a clean date string.

    Args:
        iso_str: ISO 8601 timestamp; a trailing ``Z`` is accepted.
        fmt: ``strftime`` format for the result.

    Returns:
        The formatted timestamp, or ``""`` if ``iso_str`` is empty.

    Raises:
        ValueError: If ``iso_str`` is not a valid ISO 8601 timestamp.
    """
    if not iso_str:
        return ""

    # Replace 'Z' with +00:00 for Python 3.11+ datetime.fromisoformat compatibility
    clean_iso = iso_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(clean_iso)

    return dt.strftime(fmt)