"""Adjust screen brightness on Windows."""

from typing import Dict, Any


def adjust_brightness(change: int) -> Dict[str, Any]:
    """
    Adjust screen brightness by a percentage.

    Parameters
    ----------
    change : int
        Brightness change percentage (-100 to +100)
        Negative values decrease brightness, positive increase
        Scale is out of 100

    Returns
    -------
    dict
        Status and result with new brightness level

    Examples
    --------
    adjust_brightness(10)   # Increase brightness by 10%
    adjust_brightness(-20)  # Decrease brightness by 20%
    adjust_brightness(50)   # Increase brightness by 50%
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

        # Try using screen_brightness_control library
        try:
            import screen_brightness_control as sbc

            # Get current brightness
            current_brightness = sbc.get_brightness(display=0)
            if isinstance(current_brightness, list):
                current_brightness = current_brightness[0]
            current_brightness = int(current_brightness)

            # Calculate new brightness
            new_brightness = current_brightness + change
            new_brightness = max(0, min(100, new_brightness))  # Clamp to 0-100

            # Set new brightness
            sbc.set_brightness(new_brightness, display=0)

            # Determine direction
            if change > 0:
                direction = "increased"
            elif change < 0:
                direction = "decreased"
            else:
                direction = "unchanged"

            return {
                "status": "success",
                "message": f"Brightness {direction} from {current_brightness}% to {new_brightness}%",
                "previous_brightness": current_brightness,
                "new_brightness": new_brightness,
                "change": change
            }

        except ImportError:
            # Fallback: Try using WMI
            try:
                import wmi

                c = wmi.WMI(namespace='wmi')
                methods = c.WmiMonitorBrightnessMethods()[0]

                # Get current brightness
                current_brightness_query = c.WmiMonitorBrightness()[0]
                current_brightness = current_brightness_query.CurrentBrightness

                # Calculate new brightness
                new_brightness = current_brightness + change
                new_brightness = max(0, min(100, new_brightness))  # Clamp to 0-100

                # Set new brightness
                methods.WmiSetBrightness(new_brightness, 0)

                # Determine direction
                if change > 0:
                    direction = "increased"
                elif change < 0:
                    direction = "decreased"
                else:
                    direction = "unchanged"

                return {
                    "status": "success",
                    "message": f"Brightness {direction} from {current_brightness}% to {new_brightness}%",
                    "previous_brightness": current_brightness,
                    "new_brightness": new_brightness,
                    "change": change
                }

            except Exception as wmi_error:
                # Both methods failed
                return {
                    "status": "error",
                    "message": f"Failed to adjust brightness. Please install 'screen-brightness-control' package: pip install screen-brightness-control. Error: {str(wmi_error)}"
                }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Failed to adjust brightness: {str(e)}"
        }
