"""Click an element on the current browser page, with optional iframe targeting."""

from typing import Dict, Any, Optional


async def browser_click_element(
    browser_server,
    selector: str,
    frame_url_contains: Optional[str] = None,
    frame_name: Optional[str] = None,
    frame_index: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Click an element on the page or within a specific iframe.

    Parameters
    ----------
    browser_server:
        BrowserControlServer instance
    selector:
        CSS selector for the element to click
    frame_url_contains:
        Optional substring to match target iframe URL
    frame_name:
        Optional exact iframe name
    frame_index:
        Optional index into page.frames() as a fallback

    Returns
    -------
    dict
        Status, clicked selector, and frame url (if targeted)
    """
    try:
        page = browser_server.current_page
        if not page:
            return {"status": "error", "message": "No active page"}

        target = page
        picked_url = None

        if frame_url_contains or frame_name or frame_index is not None:
            # Resolve a target frame by URL substring, name, or index
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
                try:
                    picked_url = getattr(picked, "url", None)
                except Exception:
                    picked_url = None

        await target.click(selector)
        res: Dict[str, Any] = {"status": "success", "clicked": selector}
        if picked_url:
            res["frame_url"] = picked_url
        return res
    except Exception as e:
        return {"status": "error", "message": str(e)}
