"""Save current file."""

import asyncio
from typing import Any, Dict
import pyautogui


async def save_file() -> Dict[str, Any]:
    """
    Save current file.

    Returns
    -------
    dict
        Status
    """
    try:
        pyautogui.hotkey('ctrl', 's')
        await asyncio.sleep(0.2)
        return {"status": "success", "saved": True}

    except Exception as e:
        return {"status": "error", "message": str(e)}
