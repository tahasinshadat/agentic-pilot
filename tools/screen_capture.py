# Screen capture for vision capabilities.

import asyncio
import base64
import io
from typing import Optional, Tuple
from PIL import ImageGrab, Image


class ScreenCapture:
    # Handles screenshot capture for vision analysis.

    @staticmethod
    async def capture_screen(compress: bool = False) -> Optional[Tuple[Image.Image, dict]]:
        # Capture current screen and prepare for Gemini vision.
        #
        # Args:
        #     compress: If True, resize to 1024x1024 for API efficiency.
        #               If False (default), keep original size for accurate coordinates.
        #
        # Returns:
        #     Tuple of (PIL Image, Gemini-formatted data dict with dimensions)
        try:
            # Capture screenshot at full resolution
            screenshot = await asyncio.to_thread(ImageGrab.grab)

            # Store original dimensions before any compression
            original_width, original_height = screenshot.size

            # Optionally compress for API efficiency
            # For clicking operations, we should NOT compress to maintain coordinate accuracy
            if compress:
                screenshot.thumbnail([1024, 1024])

            # Convert to bytes for Gemini
            image_io = io.BytesIO()
            screenshot.save(image_io, format="jpeg", quality=95)  # Higher quality for better accuracy
            image_bytes = image_io.getvalue()

            # Format for Gemini with dimensions included
            gemini_data = {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode(),
                "width": original_width,
                "height": original_height
            }

            return screenshot, gemini_data

        except Exception as e:
            print(f"[ScreenCapture] Error: {e}")
            return None

    @staticmethod
    async def capture_region(x: int, y: int, width: int, height: int, compress: bool = False) -> Optional[Tuple[Image.Image, dict]]:
        # Capture specific screen region.
        #
        # Args:
        #     x, y: Top-left corner coordinates
        #     width, height: Region dimensions
        #     compress: If False (default), keep original size for accurate coordinates
        #
        # Returns:
        #     Tuple of (PIL Image, Gemini-formatted data dict with dimensions)
        try:
            bbox = (x, y, x + width, y + height)
            screenshot = await asyncio.to_thread(ImageGrab.grab, bbox=bbox)

            # Store original dimensions before any compression
            original_width, original_height = screenshot.size

            # Optionally compress
            if compress:
                screenshot.thumbnail([1024, 1024])

            # Convert to bytes
            image_io = io.BytesIO()
            screenshot.save(image_io, format="jpeg", quality=95)  # Higher quality for better accuracy
            image_bytes = image_io.getvalue()

            # Format for Gemini with dimensions included
            gemini_data = {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode(),
                "width": original_width,
                "height": original_height
            }

            return screenshot, gemini_data

        except Exception as e:
            print(f"[ScreenCapture] Error: {e}")
            return None
