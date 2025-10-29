"""Get text content of the current browser page."""

from typing import Dict, Any


async def browser_get_page_content(browser_server) -> Dict[str, Any]:
    """
    Get text content of current page.

    Parameters
    ----------
    browser_server:
        BrowserControlServer instance

    Returns
    -------
    dict
        Status, url, title, and content
    """
    try:
        if not browser_server.current_page:
            return {"status": "error", "message": "No active page"}

        content = await browser_server.current_page.inner_text('body')
        title = await browser_server.current_page.title()
        url = browser_server.current_page.url

        return {
            "status": "success",
            "url": url,
            "title": title,
            "content": content[:5000]  # Limit to 5000 chars
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
