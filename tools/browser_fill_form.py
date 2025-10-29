"""Fill form fields on the current browser page."""

from typing import Dict, Any


async def browser_fill_form(browser_server, fields: Dict[str, str]) -> Dict[str, Any]:
    """
    Fill form fields on current page.

    Parameters
    ----------
    browser_server:
        BrowserControlServer instance
    fields:
        Dictionary of {selector: value} pairs

    Returns
    -------
    dict
        Status, filled_fields list, and total_fields count
    """
    try:
        if not browser_server.current_page:
            return {"status": "error", "message": "No active page"}

        filled = []
        for selector, value in fields.items():
            try:
                # Try different selector strategies
                element = await browser_server.current_page.query_selector(selector)
                if not element:
                    # Try by name
                    element = await browser_server.current_page.query_selector(f'[name="{selector}"]')
                if not element:
                    # Try by id
                    element = await browser_server.current_page.query_selector(f'#{selector}')

                if element:
                    await element.fill(value)
                    filled.append(selector)
            except:
                pass

        return {
            "status": "success",
            "filled_fields": filled,
            "total_fields": len(fields)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
