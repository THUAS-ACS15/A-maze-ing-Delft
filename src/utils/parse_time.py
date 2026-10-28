from datetime import timedelta


def parse_time_str(time_str: str) -> timedelta:
    """Convert ``H:MM:SS`` or ``D days, H:MM:SS`` into a timedelta."""
    time_str = time_str.strip()
    days = 0
    if " day" in time_str:
        day_part, time_str = time_str.split(", ", 1)
        days = int(day_part.split()[0])
    hours, minutes, seconds = map(int, time_str.split(":"))
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
