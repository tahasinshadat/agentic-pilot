"""Move text cursor (caret) in text editors using keyboard shortcuts."""

import asyncio
import pyautogui
from typing import Dict, Any, Literal


async def move_text_cursor(
    direction: Literal["up", "down", "left", "right", "line_start", "line_end", "file_start", "file_end"],
    count: int = 1
) -> Dict[str, Any]:
    """
    Move text cursor in a text editor using keyboard shortcuts.

    Parameters
    ----------
    direction : str
        Direction to move cursor:
        - "up": Move up N lines
        - "down": Move down N lines
        - "left": Move left N characters
        - "right": Move right N characters
        - "line_start": Move to start of line (Home)
        - "line_end": Move to end of line (End)
        - "file_start": Move to start of file (Ctrl+Home)
        - "file_end": Move to end of file (Ctrl+End)
    count : int
        Number of times to repeat the movement (for arrows)

    Returns
    -------
    dict
        Status and movement details

    Examples
    --------
    >>> await move_text_cursor("down", 5)  # Move down 5 lines
    >>> await move_text_cursor("line_end")  # Move to end of line
    >>> await move_text_cursor("file_start")  # Jump to top of file
    """
    try:
        if direction in ["up", "down", "left", "right"]:
            # Arrow key movement
            for _ in range(count):
                pyautogui.press(direction)
                await asyncio.sleep(0.05)

            return {
                "status": "success",
                "direction": direction,
                "count": count
            }

        elif direction == "line_start":
            pyautogui.press('home')
            return {
                "status": "success",
                "direction": "line_start"
            }

        elif direction == "line_end":
            pyautogui.press('end')
            return {
                "status": "success",
                "direction": "line_end"
            }

        elif direction == "file_start":
            pyautogui.hotkey('ctrl', 'home')
            return {
                "status": "success",
                "direction": "file_start"
            }

        elif direction == "file_end":
            pyautogui.hotkey('ctrl', 'end')
            return {
                "status": "success",
                "direction": "file_end"
            }

        else:
            return {
                "status": "error",
                "message": f"Invalid direction: {direction}"
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
