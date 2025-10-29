"""Search Google in the default web browser."""

import webbrowser
from typing import Dict, Any


def search_google(query: str) -> Dict[str, Any]:
    """
    Search Google.

    Parameters
    ----------
    query:
        Search query

    Returns
    -------
    dict
        Status and message about the operation
    """
    try:
        if not query:
            return {"status": "error", "message": "Empty search query."}

        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return {"status": "success", "message": f"Searched Google for: '{query}'"}

    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
