"""Worker scheduling utilities."""

from datetime import datetime, timedelta, timezone, time


def calculate_seconds_until_next_run(
    schedule_string: str,
    fallback_hour: int = 2,
    fallback_minute: int = 0,
) -> float:
    """Calculate seconds until next scheduled run based on cron-like schedule string.

    Args:
        schedule_string: Space-separated minute and hour (e.g., "0 2" for 2:00 AM).
        fallback_hour: Hour to use if schedule_string is invalid (default 2).
        fallback_minute: Minute to use if schedule_string is invalid (default 0).

    Returns:
        Seconds until next scheduled run (always non-negative).
    """
    schedule_parts = schedule_string.split()
    if len(schedule_parts) >= 2:
        minute = int(schedule_parts[0])
        hour = int(schedule_parts[1])
    else:
        minute, hour = fallback_minute, fallback_hour

    now = datetime.now(timezone.utc)
    target_time = time(hour, minute, 0, tzinfo=timezone.utc)

    if now.time() < target_time:
        next_run = datetime.combine(now.date(), target_time)
    else:
        next_run = datetime.combine(
            now.date() + timedelta(days=1), target_time
        )

    seconds_until = (next_run - now).total_seconds()
    return max(seconds_until, 0)
