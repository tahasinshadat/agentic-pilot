"""
Smart open with fallback - searches Windows first, then falls back to Chrome search.
Follows the workflow: Windows Search Bar → App if found → Chrome search if not.
"""

import time
import pyautogui
import subprocess
import webbrowser
from typing import Dict, Any


def smart_open(query: str) -> Dict[str, Any]:
    """
    Smart open with automatic fallback.

    Workflow:
    1. Open Windows Search (Win key)
    2. Type the query
    3. Check if first result is an application (has "App" label)
    4. If yes → Launch it (press Enter)
    5. If no → Open Chrome and search for the query instead

    This ensures we only launch actual applications, and automatically
    search in Chrome for things like "two sum leetcode", "python docs", etc.

    Parameters
    ----------
    query : str
        What to open/search for

    Returns
    -------
    dict
        Status and message about what happened

    Examples
    --------
    >>> smart_open("calculator")  # Launches Calculator app
    >>> smart_open("two sum leetcode")  # Searches in Chrome
    >>> smart_open("python documentation")  # Searches in Chrome
    """
    try:
        if not query or not isinstance(query, str):
            return {"status": "error", "message": "Invalid query"}

        query = query.strip()

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

        query_lower = query.lower()
        if query_lower in quick_apps:
            # Launch directly
            subprocess.Popen(quick_apps[query_lower], shell=True)
            return {
                "status": "launched_app",
                "message": f"Launched '{query}' directly",
                "action": "app"
            }

        print(f"[SmartOpen] Searching for: '{query}'")

        # Open Windows Search
        pyautogui.press('win')
        time.sleep(0.6)

        # Type query
        pyautogui.write(query, interval=0.05)
        time.sleep(1.2)  # Wait for search results

        # Take a screenshot to check if it's an app
        # (We look for the "App" label that Windows adds to application results)
        try:
            import PIL.ImageGrab
            screenshot = PIL.ImageGrab.grab()

            # Convert to text using OCR-like detection (simple check)
            # Look for "App" text in top-left quadrant where search results appear
            import pytesseract
            from PIL import Image

            # Crop to search results area (top-left portion of screen)
            width, height = screenshot.size
            search_area = screenshot.crop((0, 0, width // 2, height // 2))

            # OCR to detect if "App" label is present
            text = pytesseract.image_to_string(search_area).lower()

            is_app = "app" in text or "application" in text

        except Exception:
            # If OCR fails, use heuristic: single words are more likely to be apps
            is_app = len(query.split()) <= 2 and query_lower in [
                "minecraft", "steam", "discord", "spotify", "vlc",
                "photoshop", "illustrator", "word", "excel", "powerpoint"
            ]

        if is_app:
            # It's an app - launch it
            print(f"[SmartOpen] Detected as application, launching...")
            pyautogui.press('enter')
            return {
                "status": "launched_app",
                "message": f"Launched application '{query}' from Windows Search",
                "action": "app"
            }
        else:
            # Not an app - close search and use Chrome instead
            print(f"[SmartOpen] Not an application, searching in Chrome...")
            pyautogui.press('esc')
            time.sleep(0.3)

            # Open Chrome and search
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)

            return {
                "status": "searched_in_browser",
                "message": f"Searched '{query}' in Chrome (not an application)",
                "action": "search"
            }

    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}


# Simplified version without OCR (more reliable)
async def smart_open_simple(query: str, browser_server=None, gemini_client=None) -> Dict[str, Any]:
    """
    Simplified smart open - uses heuristics instead of OCR.

    Heuristics to determine if it's an app:
    - Single word queries
    - Known app names
    - No complex phrases like "how to", "tutorial", "documentation"

    When searching, automatically clicks the first search result.
    """
    try:
        if not query or not isinstance(query, str):
            return {"status": "error", "message": "Invalid query"}

        query = query.strip()
        query_lower = query.lower()

        # Try common apps directly first
        quick_apps = {
            "chrome": "chrome", "google": "chrome", "firefox": "firefox",
            "edge": "msedge", "notepad": "notepad", "calculator": "calc",
            "calc": "calc", "explorer": "explorer", "spotify": "spotify",
            "discord": "discord", "vscode": "code", "code": "code"
        }

        if query_lower in quick_apps:
            subprocess.Popen(quick_apps[query_lower], shell=True)
            return {
                "status": "launched_app",
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
            time.sleep(0.5)
            pyautogui.write(query, interval=0.05)
            time.sleep(0.8)
            pyautogui.press('enter')

            return {
                "status": "launched_app",
                "message": f"Launched '{query}' via Windows Search",
                "action": "app"
            }
        else:
            # Search in Chrome and click first result using Vision
            print(f"[SmartOpen] Searching '{query}' in Chrome and opening first result...")

            # Open search in browser
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)

            # Wait for page to load
            import asyncio
            await asyncio.sleep(3.0)

            # Use vision to find and click the first actual search result
            try:
                if not gemini_client:
                    print("[SmartOpen] No Gemini client available, cannot use vision")
                    return {
                        "status": "searched_in_browser",
                        "message": f"Searched '{query}' in Chrome",
                        "action": "search"
                    }

                print(f"[SmartOpen] Using vision to find first search result...")

                from .vision_helper import call_vision_api
                from .screen_capture import ScreenCapture

                # Capture screen
                # CRITICAL: Do NOT compress screenshot - need accurate pixel coordinates for clicking
                screen_capture = ScreenCapture()
                screenshot_result = await screen_capture.capture_screen(compress=False)

                if not screenshot_result:
                    print("[SmartOpen] Failed to capture screen")
                    return {
                        "status": "searched_in_browser",
                        "message": f"Searched '{query}' in Chrome (could not capture screen)",
                        "action": "search"
                    }

                screenshot_image, _ = screenshot_result
                screen_width, screen_height = pyautogui.size()

                # Ask Gemini to find the first organic search result
                prompt = f"""You are looking at a Google search results page ({screen_width}x{screen_height} pixels).

Find the FIRST ORGANIC SEARCH RESULT. This is:
- The first blue clickable link/title of an actual website
- NOT an ad (skip ads)
- NOT "AI Overview" or "Gemini" sections
- NOT navigation buttons or filters
- Usually appears in the main content area, below any ads

Look for the first blue heading/title that is a real website result.

Return ONLY the center coordinates in format: "x:123, y:456"
Do not include any other text."""

                response = await call_vision_api(gemini_client, screenshot_image, prompt)

                # Parse coordinates
                import re
                match = re.search(r'x:\s*(\d+),\s*y:\s*(\d+)', response)

                if not match:
                    print(f"[SmartOpen] Could not parse coordinates from: {response}")
                    return {
                        "status": "searched_in_browser",
                        "message": f"Searched '{query}' but could not locate first result",
                        "action": "search"
                    }

                click_x = int(match.group(1))
                click_y = int(match.group(2))

                # Validate coordinates
                if click_x < 0 or click_x > screen_width or click_y < 0 or click_y > screen_height:
                    print(f"[SmartOpen] Invalid coordinates: ({click_x}, {click_y})")
                    return {
                        "status": "searched_in_browser",
                        "message": f"Searched '{query}' but got invalid coordinates",
                        "action": "search"
                    }

                print(f"[SmartOpen] Clicking first result at ({click_x}, {click_y})")
                pyautogui.click(click_x, click_y)
                time.sleep(0.5)

                return {
                    "status": "opened_first_result",
                    "message": f"Searched '{query}' and clicked first result at ({click_x}, {click_y})",
                    "action": "search"
                }

            except Exception as e:
                print(f"[SmartOpen] Could not click first result: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "status": "searched_in_browser",
                    "message": f"Searched '{query}' in Chrome (error clicking result: {str(e)})",
                    "action": "search"
                }

    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
