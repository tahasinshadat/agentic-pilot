from typing import Dict, Any

DAYLIGHT_BOOKING_HINT = "secure.daylight-health.com/appointments"


async def make_appointment(
    browser_server,
    booking_url: str,
    date_text: str,
    time_text: str,
    patient: Dict[str, str],
) -> Dict[str, Any]:
    """
    Navigate to Daylight booking URL and schedule an appointment via the embedded Stripe scheduler.

    Parameters
    ----------
    browser_server: BrowserControlServer instance
    booking_url: URL to the page containing the embedded Daylight/Stripe scheduler
    date_text: Visible date label to click (e.g., "Wed, Nov 12" or just a day number like "12")
    time_text: Visible time label to click (e.g., "2:30 PM")
    patient: Dict with keys like first_name, last_name, email, phone, dob (MM/DD/YYYY)
    """
    try:
        from .browser_navigate import browser_navigate
        from .browser_open_tab import browser_open_tab
        from .browser_click_element import browser_click_element
        from .browser_fill_form import browser_fill_form
        from .browser_get_page_content import browser_get_page_content
        from .browser_screenshot import browser_screenshot

        # 1) Ensure page is open at booking URL
        if not browser_server.current_page:
            open_res = await browser_open_tab(browser_server, booking_url)
            if open_res.get("status") != "success":
                return {"status": "error", "message": f"Failed to open booking page: {open_res.get('message')}"}
        else:
            nav_res = await browser_navigate(browser_server, booking_url)
            if nav_res.get("status") != "success":
                return {"status": "error", "message": f"Failed to navigate to booking page: {nav_res.get('message')}"}

        page = browser_server.current_page

        # 2) Wait briefly for embedded scheduler to load
        try:
            await page.wait_for_timeout(1000)
        except Exception:
            pass

        # 3) Click date inside the Daylight/Stripe iframe
        date_selectors = [
            f'button:has-text("{date_text}")',
            f'[role="button"]:has-text("{date_text}")',
            f'[aria-label*="{date_text}"]',
        ]
        clicked_date = False
        for sel in date_selectors:
            res = await browser_click_element(
                browser_server,
                sel,
                frame_url_contains=DAYLIGHT_BOOKING_HINT,
            )
            if res.get("status") == "success":
                clicked_date = True
                break

        if not clicked_date:
            await browser_screenshot(browser_server)
            return {"status": "error", "message": f"Could not click date: {date_text}"}

        # 4) Click time slot inside the same iframe
        time_selectors = [
            f'button:has-text("{time_text}")',
            f'[role="button"]:has-text("{time_text}")',
            f'[data-testid*="time"]:has-text("{time_text}")',
        ]
        clicked_time = False
        for sel in time_selectors:
            res = await browser_click_element(
                browser_server,
                sel,
                frame_url_contains=DAYLIGHT_BOOKING_HINT,
            )
            if res.get("status") == "success":
                clicked_time = True
                break

        if not clicked_time:
            await browser_screenshot(browser_server)
            return {"status": "error", "message": f"Could not click time: {time_text}"}

        # 5) Fill patient form fields
        field_map = {
            'input[name="first_name"]': patient.get("first_name", ""),
            'input[name="last_name"]': patient.get("last_name", ""),
            'input[name="email"]': patient.get("email", ""),
            'input[name="phone"]': patient.get("phone", ""),
            'input[name*="dob"]': patient.get("dob", ""),
        }

        await browser_fill_form(
            browser_server,
            field_map,
            frame_url_contains=DAYLIGHT_BOOKING_HINT,
        )

        # 6) Optional: accept terms/consent if present
        await browser_click_element(
            browser_server,
            'input[type="checkbox"]',
            frame_url_contains=DAYLIGHT_BOOKING_HINT,
        )

        # 7) Submit/confirm
        submit_candidates = [
            'button:has-text("Confirm")',
            'button:has-text("Book")',
            '[role="button"]:has-text("Confirm")',
        ]
        submitted = False
        for sel in submit_candidates:
            res = await browser_click_element(
                browser_server,
                sel,
                frame_url_contains=DAYLIGHT_BOOKING_HINT,
            )
            if res.get("status") == "success":
                submitted = True
                break

        if not submitted:
            await browser_screenshot(browser_server)
            return {"status": "error", "message": "Could not find/press confirmation button"}

        # 8) Read success page content (top-level; frame content would need a dedicated getter)
        content_res = await browser_get_page_content(browser_server)
        snippet = (content_res.get("content") or "")[:1000]

        return {
            "status": "success",
            "details": {
                "url": page.url,
                "confirmation_snippet": snippet,
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

