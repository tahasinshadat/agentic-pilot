"""Close a browser tab."""

from typing import Dict, Any


async def browser_close_tab(browser_server, tab_id: str = None) -> Dict[str, Any]:
    """
    Close a specific tab or the current tab.

    Parameters
    ----------
    browser_server:
        BrowserControlServer instance
    tab_id:
        ID of tab to close (optional, closes current if not specified)

    Returns
    -------
    dict
        Status and message
    """
    try:
        if tab_id and tab_id in browser_server.pages:
            page = browser_server.pages[tab_id]
            await page.close()
            del browser_server.pages[tab_id]
            if browser_server.current_page == page and browser_server.pages:
                browser_server.current_page = list(browser_server.pages.values())[0]
        elif browser_server.current_page:
            await browser_server.current_page.close()
            # Remove from pages dict
            for tid, p in list(browser_server.pages.items()):
                if p == browser_server.current_page:
                    del browser_server.pages[tid]
                    break
            if browser_server.pages:
                browser_server.current_page = list(browser_server.pages.values())[0]

        return {"status": "success", "message": "Tab closed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
