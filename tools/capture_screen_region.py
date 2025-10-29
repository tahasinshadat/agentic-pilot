"""Capture a specific region of the screen."""

import asyncio
import base64
import io
from typing import Optional, Tuple
from PIL import ImageGrab, Image


async def capture_screen_region(x: int, y: int, width: int, height: int) -> Optional[Tuple[Image.Image, dict]]:
    """
    Capture specific screen region.

    Parameters
    ----------
    x, y:
        Top-left corner coordinates
    width, height:
        Region dimensions

    Returns
    -------
    tuple
        Tuple of (PIL Image, Gemini-formatted data dict) or None if error
    """
    try:
        bbox = (x, y, x + width, y + height)
        screenshot = await asyncio.to_thread(ImageGrab.grab, bbox=bbox)

        # Resize if needed
        screenshot.thumbnail([1024, 1024])

        # Convert to bytes
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
        print(f"[ScreenCapture] Error: {e}")
        return None
