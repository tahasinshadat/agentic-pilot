"""Toggle comment on selected lines."""

import asyncio
from typing import Any, Dict
import pyautogui


async def comment_code() -> Dict[str, Any]:
    """
    Toggle comment on selected lines.

    Returns
    -------
    dict
        Status
    """
    try:
        # Ctrl+/ is common across most IDEs
        pyautogui.hotkey('ctrl', '/')
        await asyncio.sleep(0.2)
        return {"status": "success", "toggled": True}

    except Exception as e:
        return {"status": "error", "message": str(e)}
