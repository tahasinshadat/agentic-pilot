"""Read and understand a form on the screen."""

import asyncio
from typing import Any, Dict
from .vision_helper import call_vision_api


async def read_form(gemini_client, screen_capture) -> Dict[str, Any]:
    """
    Read and understand a form on the screen.

    Parameters
    ----------
    gemini_client:
        Gemini API client instance
    screen_capture:
        ScreenCapture instance for taking screenshots

    Returns
    -------
    dict
        Status and form analysis
    """
    try:
        screenshot_tuple = await screen_capture.capture_screen()

        if not screenshot_tuple:
            return {"status": "error", "message": "Failed to capture screen"}

        screenshot_image, _ = screenshot_tuple

        prompt = """Analyze the form visible on the screen.

Please identify:
1. All form fields (name, email, address, etc.)
2. Field labels and their purposes
3. Required vs optional fields
4. Any validation requirements
5. Submit button location

Provide the information in a structured format."""

        form_analysis = await call_vision_api(gemini_client, screenshot_image, prompt)

        return {
            "status": "success",
            "form_analysis": form_analysis
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
