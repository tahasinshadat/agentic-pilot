import asyncio
from typing import Dict


EMBED_URL = (
    "https://secure.daylight-health.com/appointments/embed_appt"
    "?dietitian_id=2241617&appt_type_ids=%5B406437%5D"
)
FRAME_HINT = "secure.daylight-health.com/appointments"


async def main():
    # Lazy import to use repo types
    from mcp.tool_execution import BrowserManager
    from tools.browser_open_tab import browser_open_tab
    from tools.browser_click_element import browser_click_element
    from tools.browser_fill_form import browser_fill_form
    from tools.browser_get_page_content import browser_get_page_content

    bm = BrowserManager()
    await bm.initialize()
    try:
        open_res = await browser_open_tab(bm, EMBED_URL)
        if open_res.get("status") != "success":
            print("OPEN_ERROR:", open_res)
            return

        page = bm.current_page
        # Small wait for frames to load
        await page.wait_for_timeout(1000)

        # Dump frames to verify
        print("Frames loaded:")
        for f in page.frames:
            print(" -", getattr(f, "name", None), getattr(f, "url", None))

        # Click date (11/17). Try several selector variants inside the iframe.
        date_text = "17"  # day button often shows day-of-month
        date_selectors = [
            f'button:has-text("{date_text}")',
            f'[role="button"]:has-text("{date_text}")',
            f'[aria-label*="Nov 17"]',
        ]
        for sel in date_selectors:
            res = await browser_click_element(
                bm,
                sel,
                frame_url_contains=FRAME_HINT,
            )
            print("DATE_CLICK", sel, res)
            if res.get("status") == "success":
                break

        # Click time
        time_text = "12:00 PM"
        time_selectors = [
            f'button:has-text("{time_text}")',
            f'[role="button"]:has-text("{time_text}")',
            f'[data-testid*="time"]:has-text("{time_text}")',
        ]
        for sel in time_selectors:
            res = await browser_click_element(
                bm,
                sel,
                frame_url_contains=FRAME_HINT,
            )
            print("TIME_CLICK", sel, res)
            if res.get("status") == "success":
                break

        # Fill only name fields (no submit)
        patient = {"first_name": "John", "last_name": "Smith"}
        field_map = {
            'input[name="first_name"]': patient["first_name"],
            'input[name="last_name"]': patient["last_name"],
        }
        fill_res = await browser_fill_form(
            bm,
            field_map,
            frame_url_contains=FRAME_HINT,
        )
        print("FILL", fill_res)

        # Grab a short content snippet for verification
        content_res = await browser_get_page_content(bm)
        print("CONTENT_TITLE:", content_res.get("title"))
        print("CONTENT_URL:", content_res.get("url"))
        snippet = (content_res.get("content") or "")[:400]
        print("CONTENT_SNIPPET:\n", snippet)

    finally:
        await bm.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

