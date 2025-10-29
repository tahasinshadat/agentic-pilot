"""Analyze what's on the screen and provide insights."""

import asyncio
from typing import Any, Dict
from .vision_helper import call_vision_api


async def analyze_screen(gemini_client, screen_capture, instruction: str = None) -> Dict[str, Any]:
    """
    Analyze what's on the screen and provide insights.

    Parameters
    ----------
    gemini_client:
        Gemini API client instance
    screen_capture:
        ScreenCapture instance for taking screenshots
    instruction:
        Optional specific instruction (e.g., "solve this leetcode problem")

    Returns
    -------
    dict
        Status and analysis result
    """
    try:
        # Capture screenshot - returns (Image, dict) tuple or None
        screenshot_tuple = await screen_capture.capture_screen()

        if not screenshot_tuple:
            return {"status": "error", "message": "Failed to capture screen"}

        # Extract the PIL image
        screenshot_image, _ = screenshot_tuple

        # Prepare prompt
        if instruction:
            prompt = f"{instruction}\n\nAnalyze the screen and provide a detailed response."
        else:
            prompt = "Describe what you see on the screen in detail."

        # Call vision API with proper format
        analysis = await call_vision_api(gemini_client, screenshot_image, prompt)

        return {
            "status": "success",
            "analysis": analysis,
            "instruction": instruction
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
