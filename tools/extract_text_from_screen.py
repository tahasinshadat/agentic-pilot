"""Extract all text from the screen."""

import asyncio
from typing import Any, Dict
from .vision_helper import call_vision_api


async def extract_text_from_screen(gemini_client, screen_capture) -> Dict[str, Any]:
    """
    Extract all text from the screen.

    Parameters
    ----------
    gemini_client:
        Gemini API client instance
    screen_capture:
        ScreenCapture instance for taking screenshots

    Returns
    -------
    dict
        Status and extracted text
    """
    try:
        screenshot_tuple = await screen_capture.capture_screen()

        if not screenshot_tuple:
            return {"status": "error", "message": "Failed to capture screen"}

        screenshot_image, _ = screenshot_tuple

        prompt = "Extract all visible text from this screen. Organize it logically and preserve structure."

        extracted_text = await call_vision_api(gemini_client, screenshot_image, prompt)

        return {
            "status": "success",
            "text": extracted_text
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
