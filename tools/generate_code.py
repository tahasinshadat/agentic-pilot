"""Generate code using Gemini and insert at cursor."""

import asyncio
from typing import Any, Dict
from tools.get_selected_code import get_selected_code
from tools.insert_code import insert_code
from config.config import Config


async def generate_code(
    gemini_client,
    prompt: str,
    language: str = "python"
) -> Dict[str, Any]:
    """
    Generate code using Gemini and insert at cursor.

    Parameters
    ----------
    gemini_client:
        Gemini client instance
    prompt:
        What code to generate
    language:
        Programming language

    Returns
    -------
    dict
        Status, generated code, and insertion result
    """
    try:
        # Get selected code for context (if any)
        selection_result = await get_selected_code()
        context = selection_result.get("selected_code", "")

        # Build prompt
        full_prompt = f"""Generate {language} code for the following request:

{prompt}

{f"Context (current selection):\n{context}" if context and len(context) > 5 else ""}

Requirements:
- Generate ONLY the code, no explanations
- Use proper indentation
- Follow {language} best practices
- Make it clean and efficient

Code:"""

        # Call Gemini
        def _call_gemini():
            response = gemini_client.models.generate_content(
                model=Config.MODEL,
                contents=full_prompt
            )
            return response.text

        generated_code = await asyncio.to_thread(_call_gemini)

        # Clean up code (remove markdown if present)
        import re
        code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', generated_code, re.DOTALL)
        if code_match:
            generated_code = code_match.group(1)

        generated_code = generated_code.strip()

        # Insert the code
        if context and len(context) > 5:
            # Replace selection
            insert_result = await replace_selection(generated_code)
        else:
            # Insert at cursor
            insert_result = await insert_code(generated_code, language)

        return {
            "status": "success",
            "prompt": prompt,
            "generated_code": generated_code,
            "inserted": insert_result.get("status") == "success"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
