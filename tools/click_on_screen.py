"""Click on an element on the screen using AI vision to locate it."""

import asyncio
from typing import Any, Dict, Optional
import pyautogui
from .vision_helper import call_vision_api


async def click_on_screen(gemini_client, screen_capture, target: str, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
    """
    Click at a specific location or on a described element.

    Parameters
    ----------
    gemini_client:
        Gemini API client instance
    screen_capture:
        ScreenCapture instance
    target: str
        Description of what to click (e.g., "the submit button", "first text box")
    x, y: int, optional
        Exact coordinates if known

    Returns
    -------
    dict
        Status and result
    """
    try:
        # If exact coordinates provided, just click there
        if x is not None and y is not None:
            pyautogui.click(x, y)
            return {
                "status": "success",
                "message": f"Clicked at ({x}, {y})",
                "x": x,
                "y": y
            }

        # Otherwise, use AI vision to find the element
        # CRITICAL: Do NOT compress screenshot - we need 1:1 pixel coordinates for accurate clicking
        screenshot_tuple = await screen_capture.capture_screen(compress=False)
        if not screenshot_tuple:
            return {"status": "error", "message": "Failed to capture screen"}

        screenshot_image, _ = screenshot_tuple

        # Get screen size for accurate positioning
        screen_width, screen_height = pyautogui.size()

        prompt = f"""You are looking at a screenshot of a screen that is {screen_width}x{screen_height} pixels.

The user wants to click on: "{target}"

Please:
1. Identify the exact element matching "{target}" on the screen
2. Estimate the CENTER coordinates (x, y) of that element
3. Return ONLY the coordinates in this exact format: "x:123, y:456"

Be precise. The coordinates should be where the CENTER of the clickable element is located.
Do not include any other text, just the coordinates in the format above."""

        response = await call_vision_api(gemini_client, screenshot_image, prompt)

        # Parse coordinates from response
        import re
        match = re.search(r'x:\s*(\d+),\s*y:\s*(\d+)', response)

        if not match:
            return {
                "status": "error",
                "message": f"Could not parse coordinates from AI response: {response}"
            }

        click_x = int(match.group(1))
        click_y = int(match.group(2))

        # Clamp coordinates to screen bounds (safer than erroring)
        original_x, original_y = click_x, click_y
        click_x = max(0, min(click_x, screen_width - 1))
        click_y = max(0, min(click_y, screen_height - 1))

        # Log if coordinates were clamped
        if click_x != original_x or click_y != original_y:
            print(f"[Click] Clamped coordinates from ({original_x}, {original_y}) to ({click_x}, {click_y})")

        # Click!
        pyautogui.click(click_x, click_y)

        return {
            "status": "success",
            "message": f"Clicked on '{target}' at ({click_x}, {click_y})",
            "target": target,
            "x": click_x,
            "y": click_y
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
