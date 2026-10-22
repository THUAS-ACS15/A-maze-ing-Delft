from datetime import datetime, timedelta

def calculate_duration(start_time: str, end_time: str) -> timedelta:
    dt_start = datetime.fromisoformat(start_time)
    dt_end = datetime.fromisoformat(end_time)

    duration = dt_end - dt_start
    # Remove microseconds from the timedelta object
    return duration - timedelta(microseconds=duration.microseconds)