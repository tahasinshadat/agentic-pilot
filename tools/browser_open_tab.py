"""Open a new browser tab with the specified URL."""

from typing import Dict, Any


async def browser_open_tab(browser_server, url: str, tab_name: str = None) -> Dict[str, Any]:
    """
    Open a new tab with the given URL.

    Parameters
    ----------
    browser_server:
        BrowserControlServer instance
    url:
        URL to open
    tab_name:
        Optional name for the tab

    Returns
    -------
    dict
        Status, tab_id, url, and title
    """
    try:
        context = browser_server.browser.contexts[0]
        page = await context.new_page()
        await page.goto(url)

        tab_id = tab_name or f"tab_{len(browser_server.pages)}"
        browser_server.pages[tab_id] = page
        browser_server.current_page = page

        return {
            "status": "success",
            "tab_id": tab_id,
            "url": url,
            "title": await page.title()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
