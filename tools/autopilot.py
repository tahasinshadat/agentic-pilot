"""
Autopilot - PyAutoGUI-based Computer Control
Inspired by Open-Interface, adapted for JARVIS.

This module provides recursive autopilot capabilities for complex UI automation.
"""

import asyncio
import json
from time import sleep
from typing import Any, Dict, List, Optional
import pyautogui
from config.config import Config


class AutopilotInterpreter:
    """
    Interprets and executes PyAutoGUI commands from JSON.
    Similar to Open-Interface's Interpreter but async-compatible.
    """

    def __init__(self):
        """Initialize the autopilot interpreter."""
        # Disable PyAutoGUI fail-safe (cursor in corner) for better control
        pyautogui.FAILSAFE = False

    def execute_command(self, command: Dict[str, Any]) -> bool:
        """
        Execute a single PyAutoGUI command.

        Args:
            command: Dict with 'function', 'parameters', and optional 'human_readable_justification'

        Returns:
            True if successful, False otherwise
        """
        try:
            function_name = command.get('function')
            parameters = command.get('parameters', {})
            justification = command.get('human_readable_justification', '')

            if justification:
                print(f"[Autopilot] {justification}")

            # Execute the function
            self._execute_function(function_name, parameters)
            return True

        except Exception as e:
            print(f"[Autopilot] Error executing command: {e}")
            print(f"[Autopilot] Command was: {json.dumps(command, indent=2)}")
            return False

    def execute_commands(self, commands: List[Dict[str, Any]]) -> bool:
        """
        Execute a list of PyAutoGUI commands in sequence.

        Args:
            commands: List of command dicts

        Returns:
            True if all successful, False if any failed
        """
        for command in commands:
            success = self.execute_command(command)
            if not success:
                return False
        return True

    def _execute_function(self, function_name: str, parameters: Dict[str, Any]) -> None:
        """
        Execute a PyAutoGUI function or sleep command.

        Args:
            function_name: Name of the function to execute
            parameters: Parameters for the function
        """
        # Handle sleep separately
        if function_name == "sleep":
            secs = parameters.get("secs", parameters.get("seconds", 0))
            sleep(secs)
            return

        # Check if it's a valid pyautogui function
        if not hasattr(pyautogui, function_name):
            raise ValueError(f"Unknown function: {function_name}")

        function_to_call = getattr(pyautogui, function_name)

        # Special handling for specific functions
        if function_name == 'write':
            # 'write' function - handle both 'string' and 'text' parameter names
            text_to_write = parameters.get('string') or parameters.get('text')
            interval = parameters.get('interval', 0.05)
            function_to_call(text_to_write, interval=interval)

        elif function_name == 'press':
            # 'press' function - handle both 'keys' and 'key' parameter names
            keys_to_press = parameters.get('keys') or parameters.get('key')
            presses = parameters.get('presses', 1)
            interval = parameters.get('interval', 0.1)
            function_to_call(keys_to_press, presses=presses, interval=interval)

        elif function_name == 'hotkey':
            # 'hotkey' function - expects multiple key arguments
            keys = list(parameters.values())
            function_to_call(*keys)

        elif function_name == 'click':
            # 'click' function - handle clicks with coordinates
            x = parameters.get('x')
            y = parameters.get('y')
            clicks = parameters.get('clicks', 1)
            interval = parameters.get('interval', 0.0)
            button = parameters.get('button', 'left')

            if x is not None and y is not None:
                function_to_call(x, y, clicks=clicks, interval=interval, button=button)
            else:
                function_to_call(clicks=clicks, interval=interval, button=button)

        elif function_name == 'moveTo':
            # 'moveTo' function - move mouse to coordinates
            x = parameters.get('x')
            y = parameters.get('y')
            duration = parameters.get('duration', 0)
            function_to_call(x, y, duration=duration)

        elif function_name == 'doubleClick':
            # 'doubleClick' function - double click at coordinates
            x = parameters.get('x')
            y = parameters.get('y')
            interval = parameters.get('interval', 0.0)
            button = parameters.get('button', 'left')
            if x is not None and y is not None:
                function_to_call(x, y, interval=interval, button=button)
            else:
                function_to_call(interval=interval, button=button)

        elif function_name == 'rightClick':
            # 'rightClick' function - right click at coordinates
            x = parameters.get('x')
            y = parameters.get('y')
            if x is not None and y is not None:
                function_to_call(x, y)
            else:
                function_to_call()

        elif function_name == 'dragTo':
            # 'dragTo' function - drag to coordinates
            x = parameters.get('x')
            y = parameters.get('y')
            duration = parameters.get('duration', 0)
            button = parameters.get('button', 'left')
            function_to_call(x, y, duration=duration, button=button)

        elif function_name in ['keyDown', 'keyUp']:
            # 'keyDown' and 'keyUp' functions - hold/release key
            key = parameters.get('key') or parameters.get('keys')
            function_to_call(key)

        else:
            # For other functions, pass parameters as-is
            function_to_call(**parameters)


async def execute_autopilot(
    gemini_client,
    screen_capture,
    objective: str,
    max_iterations: int = 10,
    tool_executor=None
) -> Dict[str, Any]:
    """
    Execute autopilot mode for complex UI automation tasks.
    Uses recursive execution with screenshot feedback, similar to Open-Interface.

    Args:
        gemini_client: Gemini API client for vision and decision-making
        screen_capture: ScreenCapture instance for screenshots
        objective: The user's objective to accomplish
        max_iterations: Maximum number of iterations to prevent infinite loops

    Returns:
        Dict with status and result
    """
    try:
        interpreter = AutopilotInterpreter()

        # Load autopilot-specific context with available tools
        from mcp.tool_schemas import get_tool_schemas
        available_tools = get_tool_schemas()
        # Exclude execute_autopilot to prevent recursion
        available_tools = [t for t in available_tools if t['name'] != 'execute_autopilot']

        autopilot_context = _get_autopilot_context(available_tools)

        for step_num in range(max_iterations):
            print(f"[Autopilot] Step {step_num + 1}/{max_iterations}")

            # Capture current screen state
            screenshot_result = await screen_capture.capture_screen()
            if not screenshot_result:
                return {
                    "status": "error",
                    "message": "Failed to capture screenshot"
                }

            screenshot_image, gemini_data = screenshot_result

            # Get screen dimensions
            screen_width = gemini_data.get("width", screenshot_image.width)
            screen_height = gemini_data.get("height", screenshot_image.height)

            # Convert screenshot to bytes for Gemini
            import io
            import base64
            image_io = io.BytesIO()
            screenshot_image.save(image_io, format="JPEG", quality=95)
            image_bytes = image_io.getvalue()

            # Build request for Gemini
            from google.genai import types

            user_message = f"""Objective: {objective}
Step Number: {step_num}
Screen Dimensions: {screen_width}x{screen_height} pixels

{autopilot_context}

Analyze the current screen state and provide the next steps to accomplish the objective.
Return your response in the exact JSON format specified in the context.

IMPORTANT: The screen is {screen_width} pixels wide and {screen_height} pixels tall. Use these dimensions when calculating click coordinates."""

            user_parts = [
                types.Part(text=user_message),
                types.Part(
                    inline_data=types.Blob(
                        mime_type="image/jpeg",
                        data=base64.b64encode(image_bytes).decode('utf-8')
                    )
                )
            ]

            contents = [types.Content(role="user", parts=user_parts)]

            # Get instructions from Gemini
            def _call():
                return gemini_client.models.generate_content(
                    model=Config.MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT"],
                        temperature=0.7
                    )
                )

            response = await asyncio.to_thread(_call)
            response_text = getattr(response, "text", "") or ""

            # Parse JSON response
            try:
                # Extract JSON from response (remove markdown code blocks if present)
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group()

                instructions = json.loads(response_text)
            except json.JSONDecodeError:
                # Retry with explicit JSON request
                print("[Autopilot] Malformed JSON, retrying...")
                continue

            # Check if task is complete
            if instructions.get('done'):
                print(f"[Autopilot] Task complete: {instructions['done']}")
                return {
                    "status": "success",
                    "message": instructions['done'],
                    "steps_taken": step_num + 1
                }

            # Execute steps (can be PyAutoGUI commands or tool calls)
            steps = instructions.get('steps', [])
            if not steps:
                print("[Autopilot] No steps provided, continuing...")
                continue

            print(f"[Autopilot] Executing {len(steps)} steps...")

            # Execute each step (PyAutoGUI or tool call)
            for step in steps:
                try:
                    # Check if this is a tool call (has 'tool' field) or PyAutoGUI command (has 'function' field)
                    if 'tool' in step:
                        # Tool call - execute via ToolExecutor
                        tool_name = step['tool']

                        # Prevent recursive autopilot calls
                        if tool_name == 'execute_autopilot':
                            print("[Autopilot] Skipping recursive autopilot call")
                            continue

                        if not tool_executor:
                            print(f"[Autopilot] Cannot call tool '{tool_name}' - no ToolExecutor provided")
                            continue

                        justification = step.get('human_readable_justification', '')
                        if justification:
                            print(f"[Autopilot] Tool: {justification}")

                        # Execute the tool
                        result = await tool_executor.execute(tool_name, step.get('parameters', {}))
                        print(f"[Autopilot] Tool '{tool_name}' result: {result.get('status', 'unknown')}")

                    elif 'function' in step:
                        # PyAutoGUI command - execute via interpreter
                        success = interpreter.execute_command(step)
                        if not success:
                            print(f"[Autopilot] Warning: Command failed: {step.get('function')}")
                    else:
                        print(f"[Autopilot] Invalid step format: {step}")

                except Exception as e:
                    print(f"[Autopilot] Error executing step: {e}")
                    # Continue with next step instead of failing completely
                    continue

            # Small delay before next iteration
            await asyncio.sleep(0.5)

        # Max iterations reached
        return {
            "status": "partial",
            "message": f"Autopilot reached maximum iterations ({max_iterations}). Task may be incomplete.",
            "steps_taken": max_iterations
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Autopilot error: {str(e)}"
        }


def _get_autopilot_context(available_tools: list) -> str:
    """
    Get the autopilot-specific context for Gemini.
    Comprehensive PyAutoGUI documentation with keyboard-first approach + available tools.
    """
    # Build tools list for context
    tools_list = "\n".join([
        f"- {tool['name']}: {tool['description'][:150]}..."
        for tool in available_tools[:15]  # Limit to top 15 to save tokens
    ])

    return f"""
You are controlling a computer through PyAutoGUI commands AND JARVIS tools. Return valid JSON responses.

JSON Format:
{{
    "steps": [
        {{
            "function": "...",  // For PyAutoGUI commands
            "parameters": {{"key": "value"}},
            "human_readable_justification": "..."
        }},
        {{
            "tool": "...",  // For JARVIS tools
            "parameters": {{"key": "value"}},
            "human_readable_justification": "..."
        }}
    ],
    "done": null or "completion message"
}}

==================== AVAILABLE JARVIS TOOLS ====================

You can call these tools in your steps using "tool" field instead of "function":

{tools_list}

CRITICAL: Use tools FIRST before PyAutoGUI when possible!
- To open websites: use "open_website" tool, NOT PyAutoGUI
- To search Google: use "search_google" tool, NOT PyAutoGUI
- To launch apps: use "launch" or "smart_open" tools
- To create/edit files: use file operation tools

Example using tools:
{{
    "steps": [
        {{
            "tool": "open_website",
            "parameters": {{"url": "https://nytimes.com/games/wordle"}},
            "human_readable_justification": "Opening Wordle website"
        }},
        {{
            "function": "sleep",
            "parameters": {{"secs": 3}},
            "human_readable_justification": "Waiting for page to load"
        }}
    ],
    "done": null
}}

==================== AVAILABLE FUNCTIONS ====================

1. sleep(secs=X) - Wait for X seconds (for apps/pages to load)
2. pyautogui.write(string="text", interval=0.05) - Type text at current cursor position
3. pyautogui.press(keys="key_name", presses=1, interval=0.1) - Press a key one or more times
4. pyautogui.hotkey('key1', 'key2', ...) - Press key combination (e.g., Ctrl+C)
5. pyautogui.keyDown('key') - Hold down a key
6. pyautogui.keyUp('key') - Release a key
7. pyautogui.click(x=X, y=Y, clicks=1, button='left') - Click at coordinates (button: 'left', 'right', 'middle')
8. pyautogui.doubleClick(x=X, y=Y) - Double click at coordinates
9. pyautogui.rightClick(x=X, y=Y) - Right click at coordinates
10. pyautogui.moveTo(x=X, y=Y, duration=0) - Move mouse to coordinates
11. pyautogui.scroll(clicks=X) - Scroll up (positive) or down (negative)
12. pyautogui.dragTo(x=X, y=Y, duration=0) - Drag mouse to coordinates

==================== KEYBOARD-FIRST APPROACH ====================

CRITICAL: ALWAYS prefer keyboard shortcuts over mouse clicks for better accuracy!

Common Windows Shortcuts:
- Ctrl+A: Select all
- Ctrl+C: Copy
- Ctrl+V: Paste
- Ctrl+X: Cut
- Ctrl+Z: Undo
- Ctrl+Y: Redo
- Ctrl+F: Find
- Ctrl+S: Save
- Ctrl+N: New window
- Ctrl+T: New tab
- Ctrl+W: Close tab
- Ctrl+Shift+T: Reopen closed tab
- Alt+Tab: Switch windows
- Alt+F4: Close window
- Win+D: Show desktop
- Win+E: Open File Explorer
- Win+S: Open Windows Search
- Win+L: Lock computer
- Win+Arrow keys: Snap windows

Browser Shortcuts (Chrome, Edge, Firefox):
- Ctrl+L: Focus address bar
- Ctrl+Enter: Add .com to URL and go
- Ctrl+Tab: Next tab
- Ctrl+Shift+Tab: Previous tab
- Ctrl+1 through Ctrl+8: Switch to specific tab
- Ctrl+9: Switch to last tab
- F5 or Ctrl+R: Refresh page
- Ctrl+Shift+Delete: Clear browsing data
- Ctrl+H: History
- Ctrl+J: Downloads
- Ctrl+Shift+N: New incognito window

Text Editing Shortcuts:
- Home: Go to start of line
- End: Go to end of line
- Ctrl+Home: Go to start of document
- Ctrl+End: Go to end of document
- Ctrl+Left/Right: Move by word
- Shift+Arrow keys: Select text
- Ctrl+Shift+Left/Right: Select word
- Ctrl+Backspace: Delete word before cursor
- Ctrl+Delete: Delete word after cursor

==================== COMPLETE KEY NAMES ====================

Letters: 'a'-'z' (lowercase)
Numbers: '0'-'9'
Function Keys: 'f1' through 'f24'

Special Keys:
'enter', 'return' (same as enter)
'tab'
'space'
'backspace'
'delete', 'del' (same)
'esc', 'escape' (same)
'up', 'down', 'left', 'right' (arrow keys)
'home', 'end'
'pageup', 'pagedown'
'insert'

Modifier Keys:
'shift', 'shiftleft', 'shiftright'
'ctrl', 'ctrlleft', 'ctrlright', 'control' (same as ctrl)
'alt', 'altleft', 'altright', 'option' (Mac equivalent)
'win', 'winleft', 'winright', 'command' (Mac equivalent)

Punctuation and Symbols:
'!', '@', '#', '$', '%', '^', '&', '*', '(', ')'
'-', '_', '=', '+', '[', ']', '{', '}', '\\', '|'
';', ':', "'", '"', ',', '<', '.', '>', '/', '?'
'`', '~'

Numpad Keys:
'num0' through 'num9'
'numlock', 'divide', 'multiply', 'subtract', 'add', 'decimal', 'enter'

Other:
'printscreen', 'prtsc', 'prtscr' (all same)
'scrolllock'
'pause'
'capslock'
'apps', 'menu' (context menu key)

==================== CRITICAL GUIDELINES ====================

1. KEYBOARD FIRST: Always try keyboard shortcuts before clicking
   - To open app: Win+S, type name, press Enter (don't click search icon!)
   - To navigate UI: Use Tab, Shift+Tab, Arrow keys, Enter
   - To select options: Space bar (checkboxes), Enter (buttons)
   - To fill forms: Tab between fields, type directly (no clicking!)

2. MOUSE ONLY WHEN NECESSARY:
   - Use mouse ONLY when keyboard shortcuts don't work
   - When clicking, calculate coordinates based on screen dimensions
   - Look carefully at screenshot to identify correct elements
   - For dynamic UIs, add sleep() before clicking

3. TASK COMPLETION:
   - Set "done" to completion message ONLY when task is truly finished
   - Don't add more steps when done is set
   - Return done=null if you need another screenshot to continue

4. ITERATION CONTROL:
   - Send 3-5 steps at a time, then request new screenshot (done=null)
   - This allows you to verify results before continuing
   - Don't try to complete entire task in one iteration

5. TIMING AND RELIABILITY:
   - Add sleep(1-3) after opening apps/webpages
   - Add sleep(0.5) after major actions before verification
   - For typing, use interval=0.05 for natural speed

6. ERROR PREVENTION:
   - Never overwrite user data - create new files/tabs
   - If task becomes unclear, stop with explanation
   - Verify screen state before proceeding with sensitive actions

==================== POPUP & LOGIN HANDLING ====================

CRITICAL: Handle popups and login screens properly!

POPUP DETECTION & HANDLING:
When you see popups, modals, or overlay dialogs, ALWAYS handle them FIRST:

Common popup types to look for:
- Cookie consent banners ("Accept Cookies", "Accept All", "I Agree")
- Newsletter signups ("Subscribe", "No Thanks", "Close", "X")
- Age verification ("I'm 18+", "Enter", "Continue")
- Terms of service ("Accept", "I Agree", "Continue")
- Welcome messages ("Get Started", "Continue", "Skip", "X")
- Location permission requests ("Allow", "Block", "Not Now")
- Notification requests ("Allow", "Block", "Later")
- App install prompts ("Install", "No Thanks", "Continue in Browser")

How to handle popups:
1. IDENTIFY: Look at the screenshot - is there a popup/modal?
2. LOCATE DISMISS BUTTON: Find "Accept", "Continue", "X", "Close", "No Thanks", etc.
3. CLICK IT: Use click() or press Enter/Esc to dismiss
4. WAIT: Add sleep(1) after dismissing to let page settle
5. VERIFY: Request new screenshot to confirm popup is gone

Example popup handling:
{{{{
    "steps": [
        {{{{"function": "click", "parameters": {{{{"x": 960, "y": 400}}}}, "human_readable_justification": "Clicking 'Accept Cookies' button"}}}},
        {{{{"function": "sleep", "parameters": {{{{"secs": 1}}}}, "human_readable_justification": "Waiting for popup to close"}}}}
    ],
    "done": null
}}}}

Keyboard shortcuts to dismiss popups:
- Esc key: Closes most modals/dialogs
- Enter key: Clicks default "OK" or "Continue" button
- Tab + Enter: Navigate to button then click it

LOGIN FORM DETECTION:
If you see a login/authentication form (username/password fields), STOP IMMEDIATELY:

How to identify login forms:
- Input fields labeled "Username", "Email", "Password"
- "Sign In", "Log In", "Login" buttons
- "Forgot Password?" links
- OAuth buttons ("Sign in with Google/Facebook/Apple")

When login detected, return this EXACT response:
{{{{
    "steps": [],
    "done": "LOGIN_REQUIRED: I detected a login form. Please log in to your account, then ask me to continue the task."
}}}}

DO NOT attempt to:
- Fill in login credentials (security risk)
- Click "Sign In" or "Log In" buttons
- Continue with the task

After user logs in, they will ask you to continue. Start by requesting a new screenshot.

==================== WINDOWS-SPECIFIC TIPS ====================

Opening Applications:
1. hotkey('win', 's') - Open Windows Search
2. sleep(1) - Wait for search to appear
3. write('app_name', interval=0.05) - Type app name
4. sleep(0.5) - Wait for search results
5. press('enter') - Launch first result

File Operations:
- Ctrl+N: New file/window
- Ctrl+O: Open file
- Ctrl+S: Save file
- Ctrl+Shift+S: Save As
- F2: Rename selected file
- Delete: Move to Recycle Bin

Window Management:
- Win+Left: Snap left
- Win+Right: Snap right
- Win+Up: Maximize
- Win+Down: Minimize/Restore
- Alt+Tab: Switch windows
- Alt+F4: Close window

==================== EXAMPLE RESPONSES ====================

Example 1: Opening Chrome and navigating to website
{{
    "steps": [
        {{"function": "hotkey", "parameters": {{"key1": "win", "key2": "s"}}, "human_readable_justification": "Opening Windows Search"}},
        {{"function": "sleep", "parameters": {{"secs": 1}}, "human_readable_justification": "Waiting for search"}},
        {{"function": "write", "parameters": {{"string": "chrome", "interval": 0.05}}, "human_readable_justification": "Typing Chrome"}},
        {{"function": "press", "parameters": {{"keys": "enter"}}, "human_readable_justification": "Launching Chrome"}}
    ],
    "done": null
}}

Example 2: Filling form with keyboard
{{
    "steps": [
        {{"function": "press", "parameters": {{"keys": "tab"}}, "human_readable_justification": "Moving to first field"}},
        {{"function": "write", "parameters": {{"string": "John Doe", "interval": 0.05}}, "human_readable_justification": "Entering name"}},
        {{"function": "press", "parameters": {{"keys": "tab"}}, "human_readable_justification": "Moving to email field"}},
        {{"function": "write", "parameters": {{"string": "john@example.com", "interval": 0.05}}, "human_readable_justification": "Entering email"}}
    ],
    "done": null
}}

Example 3: Task complete
{{
    "steps": [],
    "done": "Successfully completed the Wordle puzzle in 4 attempts"
}}

==================== REMEMBER ====================

- KEYBOARD FIRST, mouse last!
- Always analyze the screenshot carefully
- Include screen dimensions in coordinate calculations
- Request new screenshot frequently (done=null)
- Set done ONLY when task is truly complete
- Reply with VALID JSON only
"""


# Export the main function
__all__ = ['execute_autopilot']
