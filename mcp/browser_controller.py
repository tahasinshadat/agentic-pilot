"""
Selenium-based browser controller for reliable web interaction.

Uses Selenium WebDriver with automatic driver management for browser automation.
"""

from typing import Dict, Any, Optional, List
import time


class BrowserController:
    """
    Controls browser using Selenium WebDriver.

    Provides reliable clicking, form filling, and navigation.
    """

    def __init__(self):
        """Initialize browser controller (lazy loading)."""
        self.driver = None
        self._initialized = False

    def _ensure_driver(self):
        """Ensure Selenium driver is initialized."""
        if self._initialized and self.driver:
            # Verify driver is still alive
            try:
                self.driver.current_url
                return
            except:
                print("[BrowserController] Driver session lost, reinitializing...")
                self._initialized = False
                self.driver = None

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager

            # Try to connect to existing Chrome first (on port 9222)
            try:
                print("[BrowserController] Attempting to connect to Chrome on port 9222...")
                options = Options()
                options.add_experimental_option("debuggerAddress", "localhost:9222")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                print("[BrowserController] Successfully connected to existing Chrome")
                self._initialized = True
                return
            except Exception as e:
                print(f"[BrowserController] Could not connect to existing Chrome: {e}")

            # Launch new Chrome instance with minimal options
            print("[BrowserController] Launching new Chrome instance...")
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--start-maximized')
            # Keep browser open even if script crashes
            options.add_experimental_option("detach", True)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("[BrowserController] Launched new Chrome instance")

            self._initialized = True

        except Exception as e:
            print(f"[BrowserController] Failed to initialize: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Browser initialization failed: {e}")

    def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.

        Parameters
        ----------
        url : str
            URL to navigate to

        Returns
        -------
        dict
            Status and result
        """
        try:
            self._ensure_driver()

            # Add https:// if no protocol specified
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            self.driver.get(url)
            time.sleep(1)  # Wait for page to start loading

            return {
                "status": "success",
                "message": f"Navigated to {url}",
                "url": self.driver.current_url
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to navigate: {str(e)}"
            }

    def click_element(self, selector: str, selector_type: str = "css") -> Dict[str, Any]:
        """
        Click an element by selector.

        Parameters
        ----------
        selector : str
            Element selector (CSS, XPath, ID, etc.)
        selector_type : str
            Type of selector: 'css', 'xpath', 'id', 'name', 'class', 'tag'

        Returns
        -------
        dict
            Status and result
        """
        try:
            # Validate inputs
            if not selector:
                return {
                    "status": "error",
                    "message": "No selector provided. Please provide a CSS selector, XPath, or element ID.",
                    "help": "Example: browser_click_element(selector='#submit-button') or browser_click_element(selector='//button[@type=\"submit\"]', selector_type='xpath')"
                }

            self._ensure_driver()

            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException

            # Map selector type to By constant
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
                "link_text": By.LINK_TEXT,
                "partial_link_text": By.PARTIAL_LINK_TEXT
            }

            by = by_map.get(selector_type.lower(), By.CSS_SELECTOR)

            print(f"[BrowserController] Looking for element: {selector} (type: {selector_type})")
            print(f"[BrowserController] Current URL: {self.driver.current_url}")

            # Wait for element to be present first
            wait = WebDriverWait(self.driver, 10)

            try:
                element = wait.until(EC.presence_of_element_located((by, selector)))
                print(f"[BrowserController] Element found, waiting for it to be clickable...")
            except TimeoutException:
                return {
                    "status": "error",
                    "message": f"Element not found: {selector}",
                    "selector": selector,
                    "selector_type": selector_type,
                    "url": self.driver.current_url,
                    "help": "The element was not found on the page. Check the selector and ensure the page has loaded."
                }

            # Wait for element to be clickable
            try:
                element = wait.until(EC.element_to_be_clickable((by, selector)))
            except TimeoutException:
                return {
                    "status": "error",
                    "message": f"Element found but not clickable: {selector}",
                    "selector": selector,
                    "help": "The element exists but is not clickable (might be hidden or disabled)"
                }

            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)

            # Click the element
            element.click()
            print(f"[BrowserController] Successfully clicked element")

            return {
                "status": "success",
                "message": f"Clicked element: {selector}",
                "selector": selector,
                "selector_type": selector_type
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"[BrowserController] Error clicking element: {error_details}")

            return {
                "status": "error",
                "message": f"Failed to click element: {str(e) or 'Unknown error'}",
                "selector": selector,
                "error_type": type(e).__name__,
                "help": "Try using analyze_screen and click_on_screen with coordinates instead."
            }

    def fill_form(self, field_values: Dict[str, str]) -> Dict[str, Any]:
        """
        Fill form fields with values.

        Parameters
        ----------
        field_values : dict
            Map of selector to value
            Format: {"#email": "test@example.com", "#password": "pass123"}

        Returns
        -------
        dict
            Status and results
        """
        try:
            self._ensure_driver()

            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            filled_fields = []

            for selector, value in field_values.items():
                try:
                    # Wait for field to be present
                    wait = WebDriverWait(self.driver, 10)
                    element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )

                    # Clear and fill the field
                    element.clear()
                    element.send_keys(value)
                    filled_fields.append(selector)

                except Exception as e:
                    print(f"[BrowserController] Failed to fill {selector}: {e}")

            if len(filled_fields) == len(field_values):
                return {
                    "status": "success",
                    "message": f"Filled {len(filled_fields)} fields",
                    "filled_fields": filled_fields
                }
            else:
                return {
                    "status": "partial",
                    "message": f"Filled {len(filled_fields)}/{len(field_values)} fields",
                    "filled_fields": filled_fields,
                    "total_requested": len(field_values)
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to fill form: {str(e)}"
            }

    def get_page_content(self) -> Dict[str, Any]:
        """
        Get current page content.

        Returns
        -------
        dict
            Status and page info
        """
        try:
            self._ensure_driver()

            return {
                "status": "success",
                "url": self.driver.current_url,
                "title": self.driver.title,
                "html": self.driver.page_source[:5000]  # First 5000 chars
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get page content: {str(e)}"
            }

    def screenshot(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """
        Take a screenshot of the current page.

        Parameters
        ----------
        filepath : str, optional
            Path to save screenshot. If None, returns base64 data.

        Returns
        -------
        dict
            Status and screenshot info
        """
        try:
            self._ensure_driver()

            if filepath:
                self.driver.save_screenshot(filepath)
                return {
                    "status": "success",
                    "message": f"Screenshot saved to {filepath}",
                    "filepath": filepath
                }
            else:
                screenshot_b64 = self.driver.get_screenshot_as_base64()
                return {
                    "status": "success",
                    "message": "Screenshot captured",
                    "data": screenshot_b64
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to take screenshot: {str(e)}"
            }

    def execute_script(self, script: str) -> Dict[str, Any]:
        """
        Execute JavaScript on the page.

        Parameters
        ----------
        script : str
            JavaScript code to execute

        Returns
        -------
        dict
            Status and result
        """
        try:
            self._ensure_driver()

            result = self.driver.execute_script(script)

            return {
                "status": "success",
                "message": "Script executed",
                "result": result
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Script execution failed: {str(e)}"
            }

    def close(self):
        """Close the browser."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None
                self._initialized = False

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
