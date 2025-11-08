"""Fill form fields on the current browser page, with optional iframe targeting."""

from typing import Dict, Any, Optional


async def browser_fill_form(
    browser_server,
    fields: Dict[str, str],
    frame_url_contains: Optional[str] = None,
    frame_name: Optional[str] = None,
    frame_index: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Fill form fields on current page or within a specific iframe.

    Parameters
    ----------
    browser_server:
        BrowserControlServer instance
    fields:
        Dictionary of {selector: value} pairs. Keys may be CSS selectors or field names/ids.
    frame_url_contains:
        Optional substring to match target iframe URL
    frame_name:
        Optional exact iframe name
    frame_index:
        Optional index into page.frames() as a fallback

    Returns
    -------
    dict
        Status, filled_fields list, and total_fields count
    """
    try:
        page = browser_server.current_page
        if not page:
            return {"status": "error", "message": "No active page"}

        target = page
        if frame_url_contains or frame_name or frame_index is not None:
            frames = page.frames
            picked = None
            if frame_url_contains:
                for f in frames:
                    try:
                        if frame_url_contains in (getattr(f, "url", "") or ""):
                            picked = f
                            break
                    except Exception:
                        pass
            if not picked and frame_name:
                try:
                    picked = next((f for f in frames if (getattr(f, "name", "") or "") == frame_name), None)
                except Exception:
                    picked = None
            if not picked and frame_index is not None:
                try:
                    if 0 <= int(frame_index) < len(frames):
                        picked = frames[int(frame_index)]
                except Exception:
                    picked = None
            if picked:
                target = picked

        filled = []
        for selector, value in fields.items():
            try:
                # Try different selector strategies
                element = await target.query_selector(selector)
                if not element:
                    # Try by name
                    element = await target.query_selector(f'[name="{selector}"]')
                if not element:
                    # Try by id
                    element = await target.query_selector(f'#{selector}')

                if element:
                    await element.fill(value)
                    filled.append(selector)
            except Exception:
                # Skip individual field failures; continue others
                pass

        return {
            "status": "success",
            "filled_fields": filled,
            "total_fields": len(fields)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
