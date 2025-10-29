"""Take a screenshot of the current browser page."""

import tempfile
from typing import Dict, Any


async def browser_screenshot(browser_server) -> Dict[str, Any]:
    """
    Take screenshot of current page.

    Parameters
    ----------
    browser_server:
        BrowserControlServer instance

    Returns
    -------
    dict
        Status and screenshot_path
    """
    try:
        if not browser_server.current_page:
            return {"status": "error", "message": "No active page"}

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        screenshot_path = temp_file.name
        temp_file.close()

        await browser_server.current_page.screenshot(path=screenshot_path)

        return {
            "status": "success",
            "screenshot_path": screenshot_path
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
