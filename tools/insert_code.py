"""Insert code at the current cursor position in IDE."""

import asyncio
from typing import Any, Dict
import pyautogui
import pyperclip


async def insert_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Insert code at the current cursor position in IDE.

    Parameters
    ----------
    code:
        Code to insert
    language:
        Programming language (for context)

    Returns
    -------
    dict
        Status and insertion details
    """
    try:
        # Save current clipboard
        old_clipboard = pyperclip.paste()

        # Copy code to clipboard and verify it's set
        pyperclip.copy(code)

        # Wait and verify clipboard is set (with retries)
        max_retries = 5
        for i in range(max_retries):
            await asyncio.sleep(0.05)
            if pyperclip.paste() == code:
                break
            pyperclip.copy(code)  # Retry copy

        # Paste at cursor (Ctrl+V)
        pyautogui.hotkey('ctrl', 'v')

        # Wait for paste to complete
        await asyncio.sleep(0.3)

        # Restore clipboard
        pyperclip.copy(old_clipboard)

        return {
            "status": "success",
            "language": language,
            "lines_inserted": len(code.split('\n')),
            "characters": len(code)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
