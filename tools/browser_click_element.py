"""Click an element on the current browser page."""

from typing import Dict, Any


async def browser_click_element(browser_server, selector: str) -> Dict[str, Any]:
    """
    Click an element on the page.

    Parameters
    ----------
    browser_server:
        BrowserControlServer instance
    selector:
        CSS selector for the element to click

    Returns
    -------
    dict
        Status and clicked selector
    """
    try:
        if not browser_server.current_page:
            return {"status": "error", "message": "No active page"}

        await browser_server.current_page.click(selector)
        return {"status": "success", "clicked": selector}
    except Exception as e:
        return {"status": "error", "message": str(e)}
