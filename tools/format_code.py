"""Format code in current file (IDE-specific shortcut)."""

import asyncio
from typing import Any, Dict
import pyautogui


async def format_code() -> Dict[str, Any]:
    """
    Format code in current file (IDE-specific shortcut).

    Returns
    -------
    dict
        Status
    """
    try:
        # Common format shortcuts:
        # VS Code: Shift+Alt+F
        # PyCharm: Ctrl+Alt+L

        # Try VS Code first
        pyautogui.hotkey('shift', 'alt', 'f')

        await asyncio.sleep(0.3)

        return {"status": "success", "formatted": True}

    except Exception as e:
        return {"status": "error", "message": str(e)}
