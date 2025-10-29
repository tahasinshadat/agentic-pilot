"""Answer a question about what's visible on screen."""

import asyncio
from typing import Any, Dict
from .vision_helper import call_vision_api


async def answer_screen_question(gemini_client, screen_capture, question: str) -> Dict[str, Any]:
    """
    Answer a question about what's visible on screen.

    Parameters
    ----------
    gemini_client:
        Gemini API client instance
    screen_capture:
        ScreenCapture instance for taking screenshots
    question:
        The question to answer

    Returns
    -------
    dict
        Status, question, and answer
    """
    try:
        screenshot_tuple = await screen_capture.capture_screen()

        if not screenshot_tuple:
            return {"status": "error", "message": "Failed to capture screen"}

        screenshot_image, _ = screenshot_tuple

        prompt = f"Based on what you see on the screen, please answer this question:\n\n{question}"

        answer = await call_vision_api(gemini_client, screenshot_image, prompt)

        return {
            "status": "success",
            "question": question,
            "answer": answer
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
