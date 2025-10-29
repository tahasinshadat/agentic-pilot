"""Get current time and date information."""

from datetime import datetime
from typing import Dict, Any


def get_current_time() -> Dict[str, Any]:
    """
    Get current time and date information.

    Useful for calculating time delays for scheduled tasks.
    For example, if user says "open X at 9PM", you can:
    1. Call get_current_time() to get current time
    2. Calculate seconds until 9PM
    3. Call launch("X", calculated_seconds)

    Returns
    -------
    dict
        Current time information including:
        - current_time: Time in HH:MM:SS format
        - current_date: Date in YYYY-MM-DD format
        - current_datetime: Full datetime string
        - unix_timestamp: Unix timestamp (seconds since epoch)
        - hour: Current hour (0-23)
        - minute: Current minute (0-59)
        - second: Current second (0-59)

    Example
    -------
    >>> result = get_current_time()
    >>> print(result)
    {
        'status': 'success',
        'current_time': '14:30:45',
        'current_date': '2025-10-26',
        'current_datetime': '2025-10-26 14:30:45',
        'unix_timestamp': 1729954245,
        'hour': 14,
        'minute': 30,
        'second': 45
    }
    """
    try:
        now = datetime.now()

        return {
            "status": "success",
            "current_time": now.strftime("%H:%M:%S"),
            "current_date": now.strftime("%Y-%m-%d"),
            "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "unix_timestamp": int(now.timestamp()),
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second
        }

    except Exception as e:
        return {"status": "error", "message": f"Error getting time: {str(e)}"}
