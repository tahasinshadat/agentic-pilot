"""Type text at cursor or into a specific field."""

import asyncio
from typing import Any, Dict, Optional
import pyautogui
from .click_on_screen import click_on_screen


async def type_text(gemini_client, screen_capture, text: str, target_field: Optional[str] = None) -> Dict[str, Any]:
    """
    Type text at current cursor position or into a specified field.

    Parameters
    ----------
    gemini_client:
        Gemini API client instance
    screen_capture:
        ScreenCapture instance
    text: str
        Text to type
    target_field: str, optional
        Description of field to type into (will click it first)

    Returns
    -------
    dict
        Status and result
    """
    try:
        # If target field specified, click it first
        if target_field:
            click_result = await click_on_screen(gemini_client, screen_capture, target_field)
            if click_result.get("status") != "success":
                return {
                    "status": "error",
                    "message": f"Failed to click target field: {click_result.get('message')}"
                }
            # Small delay to ensure field is focused
            await asyncio.sleep(0.3)

        # Type the text
        pyautogui.write(text, interval=0.05)  # Small delay between keystrokes for reliability

        return {
            "status": "success",
            "message": f"Typed '{text}'" + (f" into {target_field}" if target_field else ""),
            "text": text,
            "target_field": target_field
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
