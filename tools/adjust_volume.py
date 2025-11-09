"""Adjust system volume on Windows."""

from typing import Dict, Any
from pycaw.pycaw import AudioUtilities


def adjust_volume(change: int) -> Dict[str, Any]:
    """
    Adjust system volume by a percentage.

    Parameters
    ----------
    change : int
        Volume change percentage (-100 to +100)
        Negative values decrease volume, positive increase
        Scale is out of 100

    Returns
    -------
    dict
        Status and result with new volume level

    Examples
    --------
    adjust_volume(10)   # Increase volume by 10%
    adjust_volume(-20)  # Decrease volume by 20%
    adjust_volume(50)   # Increase volume by 50%
    """
    try:
        # Validate input
        if not isinstance(change, (int, float)):
            return {
                "status": "error",
                "message": f"Invalid change value: must be a number, got {type(change).__name__}"
            }

        change = int(change)
        if change < -100 or change > 100:
            return {
                "status": "error",
                "message": f"Change value must be between -100 and +100, got {change}"
            }

        # Get audio device endpoint volume
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume

        # Get current volume (0.0 to 1.0)
        current_volume = volume.GetMasterVolumeLevelScalar()
        current_percent = int(current_volume * 100)

        # Calculate new volume
        new_percent = current_percent + change
        new_percent = max(0, min(100, new_percent))  # Clamp to 0-100

        # Set new volume
        new_volume = new_percent / 100.0
        volume.SetMasterVolumeLevelScalar(new_volume, None)

        # Determine direction
        if change > 0:
            direction = "increased"
        elif change < 0:
            direction = "decreased"
        else:
            direction = "unchanged"

        return {
            "status": "success",
            "message": f"Volume {direction} from {current_percent}% to {new_percent}%",
            "previous_volume": current_percent,
            "new_volume": new_percent,
            "change": change
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Failed to adjust volume: {str(e)}"
        }
