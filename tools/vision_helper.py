"""Helper for vision API calls using proper Gemini format."""

import asyncio
import io
from typing import Tuple
from PIL import Image


async def call_vision_api(gemini_client, screenshot_image: Image.Image, prompt: str) -> str:
    """
    Call Gemini vision API with proper format using types.Part.from_bytes().

    Parameters
    ----------
    gemini_client:
        Gemini API client instance
    screenshot_image:
        PIL Image object
    prompt:
        Text prompt for the vision model

    Returns
    -------
    str
        Response text from Gemini
    """
    from google.genai import types
    from config import Config

    # Convert PIL Image to bytes (proper Gemini format)
    image_io = io.BytesIO()
    screenshot_image.save(image_io, format="JPEG", quality=85)
    image_bytes = image_io.getvalue()

    # Call Gemini with proper API format
    def _call():
        response = gemini_client.models.generate_content(
            model=Config.MODEL,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                prompt
            ]
        )
        return response.text

    return await asyncio.to_thread(_call)
