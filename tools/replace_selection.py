"""Replace currently selected text with new code."""

import asyncio
from typing import Any, Dict
import pyautogui
import pyperclip


async def replace_selection(new_code: str) -> Dict[str, Any]:
    """
    Replace currently selected text with new code.

    Parameters
    ----------
    new_code:
        New code to replace selection with

    Returns
    -------
    dict
        Status and replacement details
    """
    try:
        # Save clipboard
        old_clipboard = pyperclip.paste()

        # Copy new code and verify it's set
        pyperclip.copy(new_code)

        # Wait and verify clipboard is set (with retries)
        max_retries = 5
        for i in range(max_retries):
            await asyncio.sleep(0.05)
            if pyperclip.paste() == new_code:
                break
            pyperclip.copy(new_code)

        # Paste (will replace selection)
        pyautogui.hotkey('ctrl', 'v')

        await asyncio.sleep(0.3)

        # Restore clipboard
        pyperclip.copy(old_clipboard)

        return {
            "status": "success",
            "replaced": True,
            "new_code_length": len(new_code)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
