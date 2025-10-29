"""Perform a Google search in the browser."""

import asyncio
from typing import Dict, Any


async def browser_google_search(browser_server, query: str) -> Dict[str, Any]:
    """
    Perform a Google search in current or new tab.

    Parameters
    ----------
    browser_server:
        BrowserControlServer instance
    query:
        Search query

    Returns
    -------
    dict
        Status, query, url, and search results
    """
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

        if not browser_server.current_page:
            from tools.browser_open_tab import browser_open_tab
            return await browser_open_tab(browser_server, search_url, "search")

        await browser_server.current_page.goto(search_url)
        await asyncio.sleep(1)  # Wait for results

        # Extract search results
        results = []
        try:
            result_elements = await browser_server.current_page.query_selector_all('.g')
            for element in result_elements[:5]:  # Top 5 results
                title_elem = await element.query_selector('h3')
                link_elem = await element.query_selector('a')
                snippet_elem = await element.query_selector('.VwiC3b')

                if title_elem and link_elem:
                    title = await title_elem.inner_text()
                    link = await link_elem.get_attribute('href')
                    snippet = await snippet_elem.inner_text() if snippet_elem else ""

                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })
        except:
            pass

        return {
            "status": "success",
            "query": query,
            "url": search_url,
            "results": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
