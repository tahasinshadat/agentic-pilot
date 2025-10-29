"""Open a URL in the default web browser."""

import webbrowser
from typing import Dict, Any


def open_website(url: str) -> Dict[str, Any]:
    """
    Open a URL in default web browser.

    Parameters
    ----------
    url:
        URL to open

    Returns
    -------
    dict
        Status and message about the operation
    """
    try:
        if not url or not isinstance(url, str):
            return {"status": "error", "message": "Invalid URL."}

        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        webbrowser.open(url)
        return {"status": "success", "message": f"Opened: '{url}'"}

    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
