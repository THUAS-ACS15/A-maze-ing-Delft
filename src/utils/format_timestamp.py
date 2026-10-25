from datetime import datetime


def format_timestamp(iso_str: str, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """
    Parses an ISO 8601 string (e.g., '2026-10-24T10:30:43.756Z')
    and returns a clean formatted date string.
    """
    if not iso_str:
        return ""

    # Replace 'Z' with +00:00 for Python 3.11+ datetime.fromisoformat compatibility
    clean_iso = iso_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(clean_iso)

    return dt.strftime(fmt)