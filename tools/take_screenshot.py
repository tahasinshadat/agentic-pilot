"""Capture a screenshot of the current screen."""

import asyncio
import base64
import io
from typing import Optional, Tuple
from PIL import ImageGrab, Image


async def take_screenshot() -> Optional[Tuple[Image.Image, dict]]:
    """
    Capture current screen and prepare for Gemini vision.

    Returns
    -------
    tuple
        Tuple of (PIL Image, Gemini-formatted data dict) or None if error
    """
    try:
        # Capture screenshot
        screenshot = await asyncio.to_thread(ImageGrab.grab)

        # Resize for API efficiency
        screenshot.thumbnail([1024, 1024])

        # Convert to bytes for Gemini
        image_io = io.BytesIO()
        screenshot.save(image_io, format="jpeg", quality=85)
        image_bytes = image_io.getvalue()

        # Format for Gemini
        gemini_data = {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(image_bytes).decode()
        }

        return screenshot, gemini_data

    except Exception as e:
        print(f"[Screenshot] Error: {e}")
        return None
