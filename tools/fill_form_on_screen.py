"""Fill out multiple form fields on screen using AI vision."""

import asyncio
from typing import Any, Dict
from .click_on_screen import click_on_screen
from .type_text import type_text


async def fill_form_on_screen(gemini_client, screen_capture, field_values: Dict[str, str]) -> Dict[str, Any]:
    """
    Fill out multiple form fields visible on screen.

    Uses AI vision to identify fields and fills them with provided values.

    Parameters
    ----------
    gemini_client:
        Gemini API client instance
    screen_capture:
        ScreenCapture instance
    field_values: dict
        Dictionary mapping field descriptions to values
        Example: {"Step 1 answer": "51", "Step 2 first box": "544"}

    Returns
    -------
    dict
        Status and results for each field
    """
    try:
        results = {}
        failed_fields = []

        for field_desc, value in field_values.items():
            print(f"[FormFill] Filling '{field_desc}' with '{value}'")

            # Click the field
            click_result = await click_on_screen(gemini_client, screen_capture, field_desc)

            if click_result.get("status") != "success":
                failed_fields.append({
                    "field": field_desc,
                    "error": f"Could not click field: {click_result.get('message')}"
                })
                continue

            # Wait for field to focus
            await asyncio.sleep(0.2)

            # Clear any existing content (select all + delete)
            import pyautogui
            pyautogui.hotkey('ctrl', 'a')
            await asyncio.sleep(0.1)

            # Type the value
            pyautogui.write(str(value), interval=0.05)

            results[field_desc] = {
                "status": "success",
                "value": value
            }

            # Small delay before next field
            await asyncio.sleep(0.3)

        if failed_fields:
            return {
                "status": "partial_success",
                "message": f"Filled {len(results)} fields, {len(failed_fields)} failed",
                "filled": results,
                "failed": failed_fields
            }

        return {
            "status": "success",
            "message": f"Successfully filled {len(results)} form fields",
            "filled": results
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
