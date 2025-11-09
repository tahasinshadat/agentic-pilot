"""
Command Interpreter for PyAutoGUI commands.

Processes JSON commands and executes corresponding PyAutoGUI function calls.
Based on Open-Interface architecture for reliable computer control.
"""

import json
import time
from typing import Any, Dict, List
import pyautogui


class CommandInterpreter:
    """
    Interprets and executes PyAutoGUI commands from JSON format.

    Supported commands:
    - All pyautogui functions (click, write, press, hotkey, moveTo, etc.)
    - sleep: Wait for specified seconds
    """

    def __init__(self):
        """Initialize the interpreter."""
        # Configure pyautogui for safety
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.1  # Small pause between actions

    def process_commands(self, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a list of commands sequentially.

        Parameters
        ----------
        commands : list of dict
            List of command objects with format:
            {
                "function": "click",
                "parameters": {"x": 500, "y": 300},
                "justification": "Click the submit button"
            }

        Returns
        -------
        dict
            Success status and results
        """
        results = []

        for i, command in enumerate(commands):
            try:
                result = self.process_command(command)
                results.append({
                    "step": i + 1,
                    "command": command.get("function"),
                    "success": True,
                    "justification": command.get("justification", "")
                })
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed at step {i + 1}: {str(e)}",
                    "failed_command": command,
                    "error_type": type(e).__name__,
                    "completed_steps": i
                }

        return {
            "status": "success",
            "message": f"Executed {len(results)} commands successfully",
            "results": results
        }

    def process_command(self, command: Dict[str, Any]) -> None:
        """
        Process a single command.

        Parameters
        ----------
        command : dict
            Command object with function, parameters, and optional justification

        Raises
        ------
        Exception
            If command execution fails
        """
        function_name = command.get("function")
        parameters = command.get("parameters", {})
        justification = command.get("justification", "")

        if not function_name:
            raise ValueError("Command must have a 'function' field")

        print(f"[Interpreter] Executing: {function_name} - {justification}")

        # Execute the command
        self.execute_function(function_name, parameters)

    def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> None:
        """
        Execute a PyAutoGUI or sleep function.

        Parameters
        ----------
        function_name : str
            Name of the function to execute
        parameters : dict
            Parameters to pass to the function

        Raises
        ------
        ValueError
            If function is not supported
        """
        # Handle sleep separately
        if function_name == "sleep":
            secs = parameters.get("secs") or parameters.get("seconds", 0)
            if secs > 0:
                time.sleep(secs)
            return

        # Check if it's a pyautogui function
        if not hasattr(pyautogui, function_name):
            raise ValueError(f"Unknown function: {function_name}")

        function_to_call = getattr(pyautogui, function_name)

        # Special handling for specific functions
        if function_name == "write":
            # Handle both 'string' and 'text' parameter names
            text = parameters.get("string") or parameters.get("text", "")
            interval = parameters.get("interval", 0.05)
            function_to_call(text, interval=interval)

        elif function_name == "press":
            # Handle both 'keys'/'key' and single/multiple presses
            keys = parameters.get("keys") or parameters.get("key")
            if not keys:
                raise ValueError("press() requires 'key' or 'keys' parameter")

            presses = parameters.get("presses", 1)
            interval = parameters.get("interval", 0.1)
            function_to_call(keys, presses=presses, interval=interval)

        elif function_name == "hotkey":
            # hotkey expects multiple key arguments, not a dict
            # Parameters could be: {"key1": "ctrl", "key2": "c"}
            # or: {"keys": ["ctrl", "c"]}
            if "keys" in parameters:
                keys = parameters["keys"]
                function_to_call(*keys)
            else:
                # Extract all key values in order
                keys = [v for k, v in sorted(parameters.items())]
                function_to_call(*keys)

        elif function_name == "click":
            # Click can have x, y, button, clicks parameters
            function_to_call(**parameters)

        elif function_name == "moveTo":
            # Move mouse to position
            function_to_call(**parameters)

        elif function_name == "dragTo":
            # Drag to position
            function_to_call(**parameters)

        elif function_name == "scroll":
            # Scroll up or down
            function_to_call(**parameters)

        else:
            # For all other functions, pass parameters as-is
            function_to_call(**parameters)


def parse_commands_from_json(json_str: str) -> List[Dict[str, Any]]:
    """
    Parse commands from JSON string.

    Expects format:
    {
        "steps": [
            {"function": "...", "parameters": {...}, "justification": "..."},
            ...
        ]
    }

    Or just a list:
    [
        {"function": "...", "parameters": {...}, "justification": "..."},
        ...
    ]

    Parameters
    ----------
    json_str : str
        JSON string containing commands

    Returns
    -------
    list of dict
        List of command objects
    """
    try:
        data = json.loads(json_str)

        # Handle both formats
        if isinstance(data, dict) and "steps" in data:
            return data["steps"]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("Invalid command format: expected list or dict with 'steps' key")

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")
