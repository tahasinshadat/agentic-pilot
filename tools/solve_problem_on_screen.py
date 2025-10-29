"""Solve ANY problem visible on screen (math, coding, homework, etc.)."""

import asyncio
from typing import Any, Dict, Optional
from .vision_helper import call_vision_api


async def solve_problem_on_screen(gemini_client, screen_capture, problem_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Solve ANY problem visible on screen using AI vision.

    Works for: math problems, coding challenges, homework questions, puzzles, etc.

    Parameters
    ----------
    gemini_client:
        Gemini API client instance
    screen_capture:
        ScreenCapture instance for taking screenshots
    problem_type: str, optional
        Hint about problem type (math, coding, etc.) - used to tailor the prompt

    Returns
    -------
    dict
        Status, solution, and answer(s)
    """
    try:
        screenshot_tuple = await screen_capture.capture_screen()

        if not screenshot_tuple:
            return {"status": "error", "message": "Failed to capture screen"}

        screenshot_image, _ = screenshot_tuple

        # Create smart prompt based on problem type hint
        if problem_type and "cod" in problem_type.lower():
            # Coding problem
            prompt = """You are looking at a coding problem on the screen.

Please:
1. Identify the problem and requirements
2. Provide the solution approach
3. Write clean, optimized code
4. Explain time and space complexity

Format your response clearly."""
        elif problem_type and "math" in problem_type.lower():
            # Math problem
            prompt = """You are looking at a math problem on the screen.

Please:
1. Identify what mathematical problem(s) are shown
2. Solve each problem step-by-step
3. Provide the final answer(s) clearly

For multiple-choice or fill-in-the-blank: provide ONLY the answer values.
Format: For each answer, clearly state what it is."""
        else:
            # Generic problem - be smart about it
            prompt = """Analyze what's on the screen and solve whatever problem(s) you see.

If it's a form with questions/problems:
1. Identify each question or problem
2. Solve or answer each one
3. Provide clear answers for each field

If it's a single problem:
1. Understand what's being asked
2. Solve it step-by-step
3. Give the final answer clearly

Be concise and accurate. If there are multiple answer fields, clearly specify which answer goes where."""

        solution = await call_vision_api(gemini_client, screenshot_image, prompt)

        return {
            "status": "success",
            "solution": solution,
            "type": problem_type or "general",
            "message": f"Problem solved. Solution: {solution[:200]}..." if len(solution) > 200 else f"Solution: {solution}"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


# Legacy alias for backwards compatibility
async def solve_leetcode(gemini_client, screen_capture) -> Dict[str, Any]:
    """Legacy alias - redirects to solve_problem_on_screen."""
    return await solve_problem_on_screen(gemini_client, screen_capture, problem_type="coding")
