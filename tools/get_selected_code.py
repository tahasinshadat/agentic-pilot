"""Get currently selected code/text."""

import asyncio
from typing import Any, Dict
import pyautogui
import pyperclip


async def get_selected_code() -> Dict[str, Any]:
    """
    Get currently selected code/text.

    Returns
    -------
    dict
        Status and selected code
    """
    try:
        # Save clipboard
        old_clipboard = pyperclip.paste()

        # Copy selection
        pyautogui.hotkey('ctrl', 'c')

        # Wait for clipboard to update (with retries)
        selected_text = old_clipboard
        max_retries = 10
        for i in range(max_retries):
            await asyncio.sleep(0.05)
            current_clipboard = pyperclip.paste()
            if current_clipboard != old_clipboard:
                selected_text = current_clipboard
                break

        # Restore clipboard
        pyperclip.copy(old_clipboard)

        return {
            "status": "success",
            "selected_code": selected_text,
            "length": len(selected_text)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
