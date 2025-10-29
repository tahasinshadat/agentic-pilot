"""Move mouse cursor to a specific position or relative to current position."""

import pyautogui
from typing import Dict, Any, Optional


def move_mouse(x: Optional[int] = None, y: Optional[int] = None, relative: bool = False) -> Dict[str, Any]:
    """
    Move mouse cursor to a position.

    Parameters
    ----------
    x : int, optional
        X coordinate (absolute or relative)
    y : int, optional
        Y coordinate (absolute or relative)
    relative : bool
        If True, move relative to current position. If False, move to absolute position.

    Returns
    -------
    dict
        Status and new mouse position

    Examples
    --------
    >>> move_mouse(500, 300)  # Move to (500, 300)
    >>> move_mouse(100, 0, relative=True)  # Move 100 pixels right
    >>> move_mouse(0, -50, relative=True)  # Move 50 pixels up
    """
    try:
        if x is None and y is None:
            return {"status": "error", "message": "At least one coordinate (x or y) must be provided"}

        current_x, current_y = pyautogui.position()

        if relative:
            # Move relative to current position
            new_x = current_x + (x if x is not None else 0)
            new_y = current_y + (y if y is not None else 0)
        else:
            # Move to absolute position
            new_x = x if x is not None else current_x
            new_y = y if y is not None else current_y

        # Get screen size for validation
        screen_width, screen_height = pyautogui.size()

        # Clamp to screen bounds
        new_x = max(0, min(new_x, screen_width - 1))
        new_y = max(0, min(new_y, screen_height - 1))

        # Move mouse
        pyautogui.moveTo(new_x, new_y, duration=0.2)  # Smooth movement

        return {
            "status": "success",
            "from": {"x": current_x, "y": current_y},
            "to": {"x": new_x, "y": new_y},
            "relative": relative
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
