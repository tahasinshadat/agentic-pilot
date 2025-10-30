"""
Smart open with fallback - searches Windows first, then falls back to Chrome search.
Simplified version without OCR dependency.
"""

import time
import asyncio
import pyautogui
import subprocess
import webbrowser
from typing import Dict, Any


async def smart_open_simple(query: str, browser_server=None, gemini_client=None) -> Dict[str, Any]:
    """
    Smart open with heuristic-based app detection.

    Workflow:
    1. Check if it's a known quick-launch app → launch directly
    2. Use heuristics to determine if it looks like an app name
    3. If app-like → Try Windows Search and launch
    4. If web query → Open in Chrome and click first result

    Heuristics to determine if it's an app:
    - Single word queries
    - Known app names
    - No complex phrases like "how to", "tutorial", "documentation"

    Parameters
    ----------
    query : str
        What to open/search for
    browser_server : BrowserManager, optional
        Browser instance for clicking first result
    gemini_client : Client, optional
        Gemini client (unused currently)

    Returns
    -------
    dict
        Status and message about what happened

    Examples
    --------
    >>> smart_open_simple("calculator")  # Launches Calculator app
    >>> smart_open_simple("two sum leetcode")  # Searches in Chrome + clicks first result
    >>> smart_open_simple("python documentation")  # Searches in Chrome + clicks first result
    """
    try:
        if not query or not isinstance(query, str):
            return {"status": "error", "message": "Invalid query"}

        query = query.strip()
        query_lower = query.lower()

        # Try common apps directly first (fastest path)
        quick_apps = {
            "chrome": "chrome",
            "google": "chrome",
            "firefox": "firefox",
            "edge": "msedge",
            "notepad": "notepad",
            "calculator": "calc",
            "calc": "calc",
            "explorer": "explorer",
            "spotify": "spotify",
            "discord": "discord",
            "vscode": "code",
            "code": "code",
            "cmd": "cmd",
            "terminal": "wt",
            "powershell": "powershell"
        }

        if query_lower in quick_apps:
            subprocess.Popen([quick_apps[query_lower]])
            return {
                "status": "success",
                "message": f"Launched '{query}' directly",
                "action": "app"
            }

        # Heuristic: Determine if it looks like an app name
        non_app_keywords = [
            "how to", "tutorial", "documentation", "docs", "guide",
            "learn", "what is", "problem", "question", "solution",
            "leetcode", "github", "stackoverflow", "reddit"
        ]

        is_app_query = (
            len(query.split()) <= 2 and  # Short queries are usually apps
            not any(keyword in query_lower for keyword in non_app_keywords)
        )

        if is_app_query:
            # Try launching via Windows Search
            print(f"[SmartOpen] Attempting to launch '{query}' as application...")
            pyautogui.press('win')
            await asyncio.sleep(0.5)
            pyautogui.write(query, interval=0.05)
            await asyncio.sleep(0.8)
            pyautogui.press('enter')

            return {
                "status": "success",
                "message": f"Launched '{query}' from Windows Search",
                "action": "app"
            }
        else:
            # Web search: Open in Chrome and click first result
            print(f"[SmartOpen] Searching '{query}' in Chrome and clicking first result...")

            # Use Google search URL
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            await asyncio.sleep(2)  # Wait for browser to load

            # Click first result using dynamic screen position
            screen_width, screen_height = pyautogui.size()

            # Google's first result is typically in the center-left area
            # Calculate position based on screen size
            click_x = int(screen_width * 0.35)  # 35% from left
            click_y = int(screen_height * 0.40)  # 40% from top

            print(f"[SmartOpen] Clicking first result at ({click_x}, {click_y})")
            pyautogui.click(click_x, click_y)

            return {
                "status": "success",
                "message": f"Searched '{query}' in Chrome and opened first result",
                "action": "search"
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Error in smart_open: {str(e)}"
        }
