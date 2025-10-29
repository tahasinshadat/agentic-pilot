"""
Launch applications with scheduling support using Windows Search.
Works reliably by using Win+S search then launching the app.
"""

import time
import asyncio
import pyautogui
import subprocess
from typing import Dict, Any


def launch(app_name: str, delay_seconds: int = 0) -> Dict[str, Any]:
    """
    Launch an application by searching for it and optionally schedule it.

    Uses Windows Search (Win+S) to find and launch apps reliably.
    Can schedule launches in the future.

    Examples:
        launch("minecraft", 0)        # Launch immediately
        launch("chrome", 30)          # Launch in 30 seconds
        launch("spotify", 120)        # Launch in 2 minutes

    Parameters
    ----------
    app_name : str
        Name of the application to search for and launch
    delay_seconds : int
        Seconds to wait before launching (default: 0 for immediate)

    Returns
    -------
    dict
        Status and message about the operation
    """
    try:
        if not app_name or not isinstance(app_name, str):
            return {"status": "error", "message": "Invalid application name"}

        if not isinstance(delay_seconds, (int, float)) or delay_seconds < 0:
            return {"status": "error", "message": "Invalid delay"}

        # If delay, schedule it
        if delay_seconds > 0:
            # Run in background thread
            import threading
            def delayed_launch():
                time.sleep(delay_seconds)
                _launch_app_via_search(app_name)

            thread = threading.Thread(target=delayed_launch, daemon=True)
            thread.start()

            return {
                "status": "scheduled",
                "message": f"Scheduled '{app_name}' to launch in {delay_seconds} seconds"
            }
        else:
            # Launch immediately
            result = _launch_app_via_search(app_name)
            return result

    except Exception as e:
        return {"status": "error", "message": f"Error launching app: {str(e)}"}


def _launch_app_via_search(app_name: str) -> Dict[str, Any]:
    """
    Launch app using Windows Search.

    This is the most reliable method because it:
    1. Uses the same search users use manually
    2. Finds apps in Start Menu, installed programs, etc.
    3. Works with partial names
    """
    try:
        # First try direct command for common apps
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
            "code": "code"
        }

        app_lower = app_name.lower()
        if app_lower in quick_apps:
            subprocess.Popen(quick_apps[app_lower], shell=True)
            return {"status": "success", "message": f"Launched '{app_name}' directly"}

        # Use Windows Search for everything else
        print(f"[Launch] Searching for '{app_name}' using Windows Search...")

        # Open Windows Search
        pyautogui.press('win')
        time.sleep(0.5)

        # Type app name
        pyautogui.write(app_name, interval=0.05)
        time.sleep(0.8)

        # Press Enter to launch first result
        pyautogui.press('enter')

        return {
            "status": "success",
            "message": f"Launched '{app_name}' via Windows Search"
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to launch: {str(e)}"}
