"""
MCP Tool Execution
Executes tools from the tools directory.
"""

from typing import Any, Dict
import asyncio

# Import all tools
import tools


class BrowserManager:
    """Simple browser manager for browser tools."""

    def __init__(self):
        from playwright.async_api import async_playwright
        self.playwright = None
        self.browser = None
        self.pages = {}
        self.current_page = None

    async def initialize(self):
        """Initialize browser."""
        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()

            # Try to connect to existing Chrome first
            try:
                self.browser = await self.playwright.chromium.connect_over_cdp("http://localhost:9222")
                print("[Browser] Connected to existing Chrome")
            except Exception:
                # Launch new browser
                self.browser = await self.playwright.chromium.launch(headless=False)
                print("[Browser] Launched new browser")

            # Get default context
            contexts = self.browser.contexts
            if contexts:
                context = contexts[0]
                pages = context.pages
                if pages:
                    self.current_page = pages[0]
                    self.pages["main"] = self.current_page
        except Exception as e:
            print(f"[Browser] Init error: {e}")

    async def cleanup(self):
        """Cleanup browser."""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"[Browser] Cleanup error: {e}")


class ToolExecutor:
    """Execute tool calls from Gemini."""

    def __init__(self, gemini_client, screen_capture):
        """
        Initialize tool executor.

        Args:
            gemini_client: Gemini API client
            screen_capture: ScreenCapture instance
        """
        self.gemini_client = gemini_client
        self.screen_capture = screen_capture
        self.browser = BrowserManager()

    async def initialize(self):
        """Initialize executor (browser)."""
        print("[MCP] Initializing browser...")
        await self.browser.initialize()
        print("[MCP] Browser initialized!")

    async def execute(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool
            args: Tool arguments

        Returns:
            Tool result
        """
        try:
            print(f"[MCP] Executing tool: {tool_name}")

            # ==================== FILE OPERATIONS ====================
            if tool_name == "create_folder":
                return tools.create_folder(folder_path=args.get("folder_path"))

            elif tool_name == "create_file":
                return tools.create_file(
                    file_path=args.get("file_path"),
                    content=args.get("content")
                )

            elif tool_name == "edit_file":
                return tools.edit_file(
                    file_path=args.get("file_path"),
                    content=args.get("content")
                )

            elif tool_name == "read_file":
                return tools.read_file(file_path=args.get("file_path"))

            elif tool_name == "list_files":
                return tools.list_files(directory_path=args.get("directory_path"))

            # ==================== TIME UTILITIES ====================
            elif tool_name == "get_current_time":
                return tools.get_current_time()

            # ==================== APPLICATION CONTROL ====================
            elif tool_name == "play_music":
                return tools.play_music(query=args.get("query"))

            elif tool_name == "smart_open":
                return await tools.smart_open(
                    query=args.get("query"),
                    browser_server=self.browser,
                    gemini_client=self.gemini_client
                )

            elif tool_name == "launch":
                return tools.launch(
                    app_name=args.get("app_name"),
                    delay_seconds=args.get("delay_seconds", 0)
                )

            elif tool_name == "open_application":
                return tools.open_application(application_name=args.get("application_name"))

            # ==================== WEB TOOLS ====================
            elif tool_name == "open_website":
                return tools.open_website(url=args.get("url"))

            elif tool_name == "search_google":
                return tools.search_google(query=args.get("query"))

            # ==================== SCREENSHOT/VISION ====================
            elif tool_name == "take_screenshot":
                return await tools.take_screenshot(self.screen_capture)

            elif tool_name == "capture_screen_region":
                return await tools.capture_screen_region(
                    self.screen_capture,
                    x=args.get("x"),
                    y=args.get("y"),
                    width=args.get("width"),
                    height=args.get("height")
                )

            # ==================== SCREEN ANALYSIS ====================
            elif tool_name == "analyze_screen":
                return await tools.analyze_screen(
                    self.gemini_client,
                    self.screen_capture,
                    instruction=args.get("instruction")
                )

            elif tool_name == "solve_problem_on_screen":
                # Renamed from solve_leetcode - works for ANY problem
                return await tools.solve_problem_on_screen(
                    self.gemini_client,
                    self.screen_capture,
                    problem_type=args.get("problem_type")
                )

            elif tool_name == "solve_leetcode":
                # Legacy alias - redirect to new name
                return await tools.solve_problem_on_screen(
                    self.gemini_client,
                    self.screen_capture,
                    problem_type="coding"
                )

            elif tool_name == "read_form":
                return await tools.read_form(self.gemini_client, self.screen_capture)

            elif tool_name == "extract_text_from_screen":
                return await tools.extract_text_from_screen(self.gemini_client, self.screen_capture)

            elif tool_name == "answer_screen_question":
                return await tools.answer_screen_question(
                    self.gemini_client,
                    self.screen_capture,
                    question=args.get("question")
                )

            # ==================== GENERAL UI INTERACTION ====================
            elif tool_name == "click_on_screen":
                return await tools.click_on_screen(
                    self.gemini_client,
                    self.screen_capture,
                    target=args.get("target"),
                    x=args.get("x"),
                    y=args.get("y")
                )

            elif tool_name == "type_text":
                return await tools.type_text(
                    self.gemini_client,
                    self.screen_capture,
                    text=args.get("text"),
                    target_field=args.get("target_field")
                )

            elif tool_name == "fill_form_on_screen":
                return await tools.fill_form_on_screen(
                    self.gemini_client,
                    self.screen_capture,
                    field_values=args.get("field_values", {})
                )

            elif tool_name == "move_mouse":
                return tools.move_mouse(
                    x=args.get("x"),
                    y=args.get("y"),
                    relative=args.get("relative", False)
                )

            elif tool_name == "move_text_cursor":
                return await tools.move_text_cursor(
                    direction=args.get("direction"),
                    count=args.get("count", 1)
                )

            # ==================== CODE ASSISTANT ====================
            elif tool_name == "insert_code":
                return await tools.insert_code(
                    code=args.get("code"),
                    language=args.get("language", "python")
                )

            elif tool_name == "generate_code":
                return await tools.generate_code(
                    self.gemini_client,
                    prompt=args.get("prompt"),
                    language=args.get("language", "python")
                )

            elif tool_name == "replace_selection":
                return await tools.replace_selection(new_code=args.get("new_code"))

            elif tool_name == "get_selected_code":
                return await tools.get_selected_code()

            elif tool_name == "format_code":
                return await tools.format_code()

            elif tool_name == "save_file":
                return await tools.save_file()

            elif tool_name == "comment_code":
                return await tools.comment_code()

            # ==================== BROWSER CONTROL ====================
            elif tool_name == "browser_open_tab":
                # Default to about:blank if no URL provided - SMART INFERENCE
                url = args.get("url", "about:blank")
                return await tools.browser_open_tab(
                    self.browser,
                    url,
                    args.get("tab_name")
                )

            elif tool_name == "browser_close_tab":
                return await tools.browser_close_tab(self.browser, args.get("tab_id"))

            elif tool_name == "browser_navigate":
                return await tools.browser_navigate(self.browser, args.get("url"))

            elif tool_name == "browser_google_search":
                return await tools.browser_google_search(self.browser, args.get("query"))

            elif tool_name == "browser_fill_form":
                return await tools.browser_fill_form(self.browser, args.get("fields", {}))

            elif tool_name == "browser_click_element":
                return await tools.browser_click_element(self.browser, args.get("selector"))

            elif tool_name == "browser_get_page_content":
                return await tools.browser_get_page_content(self.browser)

            elif tool_name == "browser_screenshot":
                return await tools.browser_screenshot(self.browser)

            # ==================== UNKNOWN TOOL ====================
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "error_type": type(e).__name__
            }

    async def cleanup(self):
        """Cleanup resources."""
        await self.browser.cleanup()


# Global executor instance (will be initialized by agent)
_executor = None


def init_executor(gemini_client, screen_capture):
    """Initialize the global executor."""
    global _executor
    _executor = ToolExecutor(gemini_client, screen_capture)
    return _executor


async def initialize():
    """Initialize executor resources."""
    if _executor:
        await _executor.initialize()


async def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool using the global executor."""
    if not _executor:
        return {"success": False, "error": "Executor not initialized"}
    return await _executor.execute(tool_name, args)


async def cleanup():
    """Cleanup executor resources."""
    if _executor:
        await _executor.cleanup()
