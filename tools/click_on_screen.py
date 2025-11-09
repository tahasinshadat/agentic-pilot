"""Click on the screen using PyAutoGUI - simplified and reliable."""

from typing import Any, Dict, Optional
import pyautogui


async def click_on_screen(target: str = None, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
    """
    Click at a specific location on screen.

    Parameters
    ----------
    target: str, optional
        Description of what to click (informational only)
    x, y: int, optional
        Exact coordinates. If not provided, clicks at current mouse position.

    Returns
    -------
    dict
        Status and result
    """
    try:
        # Get screen size for validation
        screen_width, screen_height = pyautogui.size()

        # If exact coordinates provided, click there
        if x is not None and y is not None:
            # Clamp coordinates to screen bounds (safer than erroring)
            click_x = max(0, min(int(x), screen_width - 1))
            click_y = max(0, min(int(y), screen_height - 1))

            # Log if coordinates were clamped
            if click_x != x or click_y != y:
                print(f"[Click] Clamped coordinates from ({x}, {y}) to ({click_x}, {click_y})")

            pyautogui.click(click_x, click_y)
            message = f"Clicked at ({click_x}, {click_y})"
            if target:
                message += f" (target: {target})"

            return {
                "status": "success",
                "message": message,
                "x": click_x,
                "y": click_y
            }

        # Otherwise, click at current mouse position
        current_x, current_y = pyautogui.position()
        pyautogui.click()

        message = f"Clicked at current mouse position ({current_x}, {current_y})"
        if target:
            message += f" (target: {target})"

        return {
            "status": "success",
            "message": message,
            "x": current_x,
            "y": current_y
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

