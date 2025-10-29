"""Navigate current browser tab to a URL."""

from typing import Dict, Any


async def browser_navigate(browser_server, url: str) -> Dict[str, Any]:
    """
    Navigate current tab to URL.

    Parameters
    ----------
    browser_server:
        BrowserControlServer instance
    url:
        URL to navigate to

    Returns
    -------
    dict
        Status, url, and title
    """
    try:
        if not browser_server.current_page:
            # Open new tab if no current page
            from tools.browser_open_tab import browser_open_tab
            return await browser_open_tab(browser_server, url)

        await browser_server.current_page.goto(url)
        return {
            "status": "success",
            "url": url,
            "title": await browser_server.current_page.title()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
