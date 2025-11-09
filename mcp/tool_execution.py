"""
MCP Tool Execution
Executes tools from the tools directory.
"""

from typing import Any, Dict, Optional
import asyncio

# Import all tools
import tools

# Import new browser controller and interpreter
from mcp.browser_controller import BrowserController
from mcp.interpreter import CommandInterpreter


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
        self.browser = BrowserController()
        self.interpreter = CommandInterpreter()

    async def initialize(self):
        """Initialize executor (browser)."""
        print("[MCP] Initializing browser...")
        try:
            # Browser is lazy-loaded, so just mark as ready
            print("[MCP] Browser controller ready (will initialize on first use)")
        except Exception as e:
            print(f"[MCP] Browser initialization failed: {e}")
            print("[MCP] Some browser-based tools may not work. Continuing anyway...")

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
                    content=args.get("content"),
                    mode=args.get("mode", "replace"),
                    line_number=args.get("line_number")
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

            # ==================== WEB TOOLS ====================
            elif tool_name == "open_website":
                return tools.open_website(url=args.get("url"))

            elif tool_name == "search_google":
                return tools.search_google(query=args.get("query"))

            # ==================== SCREEN ANALYSIS ====================
            elif tool_name == "analyze_screen":
                return await tools.analyze_screen(
                    self.gemini_client,
                    self.screen_capture,
                    instruction=args.get("instruction")
                )

            # ==================== GENERAL UI INTERACTION ====================
            elif tool_name == "click_on_screen":
                return await tools.click_on_screen(
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

            elif tool_name == "get_selected_code":
                return await tools.get_selected_code()

            elif tool_name == "format_code":
                return await tools.format_code()

            elif tool_name == "save_file":
                return await tools.save_file()

            elif tool_name == "comment_code":
                return await tools.comment_code()

            # ==================== ACCESSIBILITY FEATURES ====================
            elif tool_name == "accessibility_shortcuts":
                return tools.accessibility_shortcuts(
                    narrator=args.get("narrator"),
                    live_captions=args.get("live_captions"),
                    onscreen_keyboard=args.get("onscreen_keyboard"),
                    magnifier=args.get("magnifier")
                )

            elif tool_name == "screen_color_filter":
                return tools.screen_color_filter(filter_code=args.get("filter_code"))

            # ==================== SYSTEM CONTROLS ====================
            elif tool_name == "adjust_volume":
                return tools.adjust_volume(change=args.get("change"))

            elif tool_name == "adjust_brightness":
                return tools.adjust_brightness(change=args.get("change"))

            # ==================== BROWSER CONTROL (Selenium) ====================
            elif tool_name == "browser_navigate":
                return self.browser.navigate(url=args.get("url"))

            elif tool_name == "browser_click_element":
                return self.browser.click_element(
                    selector=args.get("selector"),
                    selector_type=args.get("selector_type", "css")
                )

            elif tool_name == "browser_fill_form":
                return self.browser.fill_form(field_values=args.get("fields", {}))
                return await tools.browser_fill_form(
                    self.browser,
                    args.get("fields", {}),
                    args.get("frame_url_contains"),
                    args.get("frame_name"),
                    args.get("frame_index"),
                )

            elif tool_name == "browser_click_element":
                return await tools.browser_click_element(
                    self.browser,
                    args.get("selector"),
                    args.get("frame_url_contains"),
                    args.get("frame_name"),
                    args.get("frame_index"),
                )
            
            # ==================== APPOINTMENTS ====================
            elif tool_name == "make_appointment":
                return await tools.make_appointment(
                    self.browser,
                    booking_url=args.get("booking_url"),
                    date_text=args.get("date_text"),
                    time_text=args.get("time_text"),
                    patient=args.get("patient", {}),
                )

            elif tool_name == "browser_get_page_content":
                return self.browser.get_page_content()

            elif tool_name == "browser_screenshot":
                return self.browser.screenshot(filepath=args.get("filepath"))

            elif tool_name == "browser_execute_script":
                return self.browser.execute_script(script=args.get("script"))

            # ==================== AUTOPILOT ====================
            elif tool_name == "execute_autopilot":
                return await tools.execute_autopilot(
                    self.gemini_client,
                    self.screen_capture,
                    objective=args.get("objective"),
                    max_iterations=args.get("max_iterations", 10),
                    tool_executor=self  # Pass ToolExecutor so autopilot can call other tools
                )

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
        if self.browser:
            self.browser.close()


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
