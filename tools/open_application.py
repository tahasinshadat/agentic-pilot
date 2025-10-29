"""Open or launch a desktop application."""

import sys
import subprocess
from typing import Dict, Any


def open_application(application_name: str) -> Dict[str, Any]:
    """
    Open/launch a desktop application.

    Parameters
    ----------
    application_name:
        Name of the application to open (e.g., 'chrome', 'notepad', 'calculator')

    Returns
    -------
    dict
        Status and message about the operation
    """
    try:
        if not application_name or not isinstance(application_name, str):
            return {"status": "error", "message": "Invalid application name."}

        command = []
        shell_mode = False

        # Windows
        if sys.platform == "win32":
            app_map = {
                "calculator": "calc",
                "calc": "calc",
                "notepad": "notepad",
                "chrome": "chrome",
                "google chrome": "chrome",
                "firefox": "firefox",
                "edge": "msedge",
                "explorer": "explorer",
                "file explorer": "explorer",
                "vscode": "code",
                "vs code": "code",
                "spotify": "spotify",
                "discord": "discord"
            }
            app_command = app_map.get(application_name.lower(), application_name)
            command = f"start {app_command}"
            shell_mode = True

        # macOS
        elif sys.platform == "darwin":
            app_map = {
                "calculator": "Calculator",
                "chrome": "Google Chrome",
                "google chrome": "Google Chrome",
                "firefox": "Firefox",
                "finder": "Finder",
                "textedit": "TextEdit",
                "spotify": "Spotify"
            }
            app_name = app_map.get(application_name.lower(), application_name)
            command = ["open", "-a", app_name]

        # Linux
        else:
            command = [application_name.lower()]

        subprocess.Popen(command, shell=shell_mode)
        return {"status": "success", "message": f"Launched '{application_name}'"}

    except FileNotFoundError:
        return {"status": "error", "message": f"Application '{application_name}' not found."}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
