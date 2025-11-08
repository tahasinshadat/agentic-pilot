"""
MCP Tool Schemas - ALL tools for Gemini API
Centralized tool definitions in proper Gemini format (OBJECT, STRING, etc.)
"""

from typing import List, Dict, Any


TOOL_SCHEMAS: List[Dict[str, Any]] = [
    # ==================== FILE OPERATIONS ====================
    {
        "name": "create_folder",
        "description": "Creates a new folder at the specified path. Use when user wants to make a new directory.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "folder_path": {
                    "type": "STRING",
                    "description": "The path for the new folder (e.g., 'projects/new_folder')"
                }
            },
            "required": ["folder_path"]
        }
    },
    {
        "name": "create_file",
        "description": "Creates a new file with specified content. Use when user wants to create a document.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "file_path": {"type": "STRING", "description": "File path (e.g., 'notes.txt')"},
                "content": {"type": "STRING", "description": "File content"}
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "edit_file",
        "description": "Edits an existing file with new content. Supports three modes: 'replace' (default, overwrites entire file), 'append' (adds content to end), 'insert' (inserts at specific line). Use when user wants to modify a file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "file_path": {"type": "STRING", "description": "Path to file to edit"},
                "content": {"type": "STRING", "description": "Content to write/append/insert"},
                "mode": {"type": "STRING", "description": "Edit mode: 'replace' (default), 'append', or 'insert'"},
                "line_number": {"type": "INTEGER", "description": "Line number for insert mode (required when mode='insert')"}
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "read_file",
        "description": "Reads content from a file. Use when user wants to know what's in a file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "file_path": {"type": "STRING", "description": "Path to file to read"}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "list_files",
        "description": "Lists all files in a directory. Use when user wants to see what files are in a folder.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "directory_path": {"type": "STRING", "description": "Directory to list files from"}
            },
            "required": ["directory_path"]
        }
    },

    # ==================== TIME UTILITIES ====================
    {
        "name": "get_current_time",
        "description": "Get current time and date. REQUIRED for scheduling tasks - use this to calculate delays. For 'open X at 9PM', call this first, calculate seconds until 9PM, then use launch() with that delay.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    # ==================== APPOINTMENTS ====================
    {
        "name": "make_appointment",
        "description": "Book an appointment using an embedded Daylight/Stripe scheduler on a booking page.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "booking_url": {"type": "STRING", "description": "URL of the booking page that contains the embedded scheduler"},
                "date_text": {"type": "STRING", "description": "Visible date label to click, e.g., 'Wed, Nov 12' or '12'"},
                "time_text": {"type": "STRING", "description": "Visible time label to click, e.g., '2:30 PM'"},
                "patient": {"type": "OBJECT", "description": "Patient fields (first_name, last_name, email, phone, dob)"}
            },
            "required": ["booking_url", "date_text", "time_text", "patient"]
        }
    },

    # ==================== APPLICATION CONTROL ====================
    {
        "name": "play_music",
        "description": "**USE THIS FOR ALL MUSIC PLAYBACK** - Play music, songs, artists, albums, or playlists. Automatically uses Spotify if installed (preferred), otherwise falls back to YouTube. This is the ONLY tool for playing music. Examples: 'play We Don't Talk Anymore', 'play Charlie Puth', 'play rap music', 'play Imagine Dragons album'.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "The song, artist, album, or playlist to play. Include artist name for better results (e.g., 'We Don't Talk Anymore by Charlie Puth')."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "smart_open",
        "description": "Opens applications or web content. For applications (Chrome, Calculator, Spotify), it launches them. For web searches or specific pages ('two sum leetcode', 'python documentation'), it searches in Chrome and clicks the first result. Use this when the user says 'open X'. For 'search X' without wanting to open a link, use browser_google_search instead.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "What to open - can be app name or web search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "launch",
        "description": "Launch applications immediately or schedule them for later using Windows Search. Use for time-scheduled launches like 'open X at 9PM'. For immediate opens, prefer smart_open. Examples: launch('minecraft', 0) for immediate, launch('chrome', 30) for 30 seconds later.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {
                    "type": "STRING",
                    "description": "Name of the application to search for and launch (e.g., 'minecraft', 'chrome', 'spotify')"
                },
                "delay_seconds": {
                    "type": "INTEGER",
                    "description": "Seconds to wait before launching. 0 for immediate (default). For scheduled launches like 'at 9PM', calculate the time difference and pass it here."
                }
            },
            "required": ["app_name"]
        }
    },

    # ==================== WEB TOOLS ====================
    {
        "name": "open_website",
        "description": "Opens a website in the default browser. Use when user wants to visit a URL.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "url": {"type": "STRING", "description": "URL to open (e.g., 'youtube.com', 'https://google.com')"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "search_google",
        "description": "Opens Google search results page in default browser. Shows results WITHOUT clicking anything. Use when user says 'search X' and wants to browse results themselves.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search query"}
            },
            "required": ["query"]
        }
    },

    # ==================== AUTOPILOT (PRIMARY ACTION TOOL) ====================
    {
        "name": "execute_autopilot",
        "description": "PRIMARY ACTION TOOL - USE THIS WHEN USER WANTS YOU TO DO ANYTHING. Autopilot takes control of the screen to complete multi-step tasks by analyzing screenshots in a loop and executing PyAutoGUI commands. Use for: solving problems, filling forms, playing games, navigating UIs, opening apps AND doing something with them. When user says DO/SOLVE/COMPLETE/FILL/PLAY/OPEN AND DO X, use this tool. Examples: 'solve today's wordle' -> autopilot opens Wordle and solves it; 'fill out this form' -> autopilot fills form step by step; 'send an email' -> autopilot opens email, composes, sends.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "objective": {
                    "type": "STRING",
                    "description": "Clear description of what task to complete (e.g., 'Open NY Times Wordle and solve today's puzzle', 'Fill out the visible form with user information')"
                },
                "max_iterations": {
                    "type": "INTEGER",
                    "description": "Maximum number of screenshot-analyze-execute cycles (default: 10)"
                }
            },
            "required": ["objective"]
        }
    },

    # ==================== SCREEN ANALYSIS ====================
    {
        "name": "analyze_screen",
        "description": "INFORMATION TOOL - Use when user wants to READ/UNDERSTAND what's on screen. Analyzes and describes screen content but does NOT take any action. Returns text description only. Use when user says: 'what do you see', 'read this', 'what's on my screen'. For DOING things (clicking, typing, solving), use execute_autopilot instead.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "instruction": {"type": "STRING", "description": "Optional specific instruction for analysis"}
            }
        }
    },

    # ==================== GENERAL UI INTERACTION ====================
    {
        "name": "click_on_screen",
        "description": "Clicks at a specific location on screen OR clicks on an element you can see. Use when user wants to click something. You can describe what to click (e.g., 'the submit button', 'the text box with 51 in it') and the tool will find and click it using AI vision.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "target": {"type": "STRING", "description": "Description of what to click (e.g., 'the submit button', 'first text box', 'the answer field')"},
                "x": {"type": "INTEGER", "description": "Optional X coordinate if you know exact position"},
                "y": {"type": "INTEGER", "description": "Optional Y coordinate if you know exact position"}
            },
            "required": ["target"]
        }
    },
    {
        "name": "type_text",
        "description": "Types text at the current cursor position OR into a specific field on screen. Use when user wants to type/input text anywhere (forms, text editors, search boxes, etc.). Works by simulating keyboard typing.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "text": {"type": "STRING", "description": "Text to type"},
                "target_field": {"type": "STRING", "description": "Optional description of which field to type into (e.g., 'the answer box', 'first input field'). If provided, will click the field first."}
            },
            "required": ["text"]
        }
    },
    {
        "name": "fill_form_on_screen",
        "description": "Fills out multiple form fields visible on screen. Intelligently identifies form fields using AI vision and fills them with provided values. Use when user wants to fill out a form with multiple fields.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "field_values": {
                    "type": "OBJECT",
                    "description": "Dictionary mapping field descriptions to values. E.g., {'Step 1 answer': '51', 'Step 2 first box': '544', 'Step 2 second box': '11'}"
                }
            },
            "required": ["field_values"]
        }
    },
    {
        "name": "move_mouse",
        "description": "Moves the mouse cursor to a specific position or relative to current position. Use when user wants to move the mouse without clicking.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "x": {"type": "INTEGER", "description": "X coordinate (absolute or relative)"},
                "y": {"type": "INTEGER", "description": "Y coordinate (absolute or relative)"},
                "relative": {"type": "BOOLEAN", "description": "If true, move relative to current position. If false (default), move to absolute position"}
            }
        }
    },
    {
        "name": "move_text_cursor",
        "description": "Moves the text cursor (caret) in a text editor using keyboard shortcuts. Use when user wants to move cursor in code/text without typing.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "direction": {
                    "type": "STRING",
                    "description": "Direction to move: 'up', 'down', 'left', 'right', 'line_start', 'line_end', 'file_start', 'file_end'"
                },
                "count": {"type": "INTEGER", "description": "Number of times to repeat movement (for arrow keys, default: 1)"}
            },
            "required": ["direction"]
        }
    },

    # ==================== CODE ASSISTANT ====================
    {
        "name": "insert_code",
        "description": "Inserts code at cursor position in an IDE. Use when user wants to insert specific code.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "code": {"type": "STRING", "description": "Code to insert"},
                "language": {"type": "STRING", "description": "Programming language (default: python)"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "generate_code",
        "description": "Generates code using AI and inserts at cursor. Use when user wants AI to write code for them.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "prompt": {"type": "STRING", "description": "Description of what code to generate"},
                "language": {"type": "STRING", "description": "Programming language (default: python)"}
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "get_selected_code",
        "description": "Gets the currently selected code from IDE. Use when you need to see what code is selected.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "format_code",
        "description": "Formats the current file in IDE. Use when user wants to clean up code formatting.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "save_file",
        "description": "Saves the current file in IDE. Use when user wants to save their work.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "comment_code",
        "description": "Toggles comments on selected lines in IDE. Use when user wants to comment/uncomment code.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    # ==================== ACCESSIBILITY FEATURES ====================
    {
        "name": "accessibility_shortcuts.py",
        "description": "Toggles Windows accessibility features like Narrator, Magnifier, On-Screen Keyboard, and Live Captions based on user preferences. Use when user wants to enable/disable accessibility tools.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "narrator": {"type": "BOOLEAN", "description": "Toggle Narrator (True to toggle, False/None to leave as-is)"},
                "live_captions": {"type": "BOOLEAN", "description": "Toggle Live Captions (True to toggle, False/None to leave as-is)"},
                "onscreen_keyboard": {"type": "BOOLEAN", "description": "Toggle On-Screen Keyboard (True to toggle, False/None to leave as-is)"},
                "magnifier": {"type": "BOOLEAN", "description": "Toggle Magnifier (True to toggle, False/None to leave as-is)"}
            }
        }
    },
    {
        "name": "screen_color_filter.py",
        "description": "Enables or disables Windows color filters (grayscale, inverted, etc.) based on user preference. Use when user wants to change screen color settings for accessibility.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filter_code": {
                    "type": "INTEGER",
                    "description": "Color filter code: -1 to disable (the default screen, no filter), 0 for grayscale (for those experiencing visual overstimulation for ADHD), 1 for inverted (for those with low vision), 2 for grayscale inverted (solves no condition, just for fun), 3 for deuteranopia, 4 for protanopia, 5 for tritanopia, 6 for warm (for those who want blue light reduction for better sleep AKA night light), 7 for dim (for those with epilepsy or eye strain), 8 for low contrast (for those with dyslexia where visual stress makes it difficult to read), 9 for high contrast (primary solution for those with low vision), 10 for warm dim (combined blue light reduction and dimming), 11 for warm low contrast (combined blue light reduction and low contrast)."
                }
            },
            "required": ["filter_code"]
        }
    },
    # ==================== BROWSER CONTROL ====================
    {
        "name": "browser_open_tab",
        "description": "Opens a new browser tab. If no URL is provided, opens an empty tab (about:blank). Use when user wants to open a new tab.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "url": {"type": "STRING", "description": "URL to open. Optional - if not provided, opens empty tab."},
                "tab_name": {"type": "STRING", "description": "Optional tab identifier"}
            },
            "required": []
        }
    },
    {
        "name": "browser_close_tab",
        "description": "Closes a browser tab. Use when user wants to close a tab.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "tab_id": {"type": "STRING", "description": "Tab ID to close (optional, closes current if not specified)"}
            }
        }
    },
    {
        "name": "browser_navigate",
        "description": "Navigates to URL in current browser tab. Use when user wants to go to a different page.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "url": {"type": "STRING", "description": "URL to navigate to"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "browser_google_search",
        "description": "Performs a Google search and shows results WITHOUT clicking anything. Use when user says 'search X' or 'look up X' and wants to browse results themselves. For 'open X', use smart_open instead (which clicks first result).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "browser_fill_form",
        "description": "Fills out form fields in browser. Use when user wants to auto-fill a form. Supports targeting an iframe.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "fields": {"type": "OBJECT", "description": "Dictionary of field selectors (or names/ids) to values"},
                "frame_url_contains": {"type": "STRING", "description": "Substring to match target iframe URL (optional)"},
                "frame_name": {"type": "STRING", "description": "Exact iframe name (optional)"},
                "frame_index": {"type": "INTEGER", "description": "Index in page.frames() (optional)"}
            },
            "required": ["fields"]
        }
    },
    {
        "name": "browser_click_element",
        "description": "Clicks an element in browser by selector. Supports targeting an iframe.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "selector": {"type": "STRING", "description": "CSS selector for element to click"},
                "frame_url_contains": {"type": "STRING", "description": "Substring to match target iframe URL (optional)"},
                "frame_name": {"type": "STRING", "description": "Exact iframe name (optional)"},
                "frame_index": {"type": "INTEGER", "description": "Index in page.frames() (optional)"}
            },
            "required": ["selector"]
        }
    },
    {
        "name": "browser_get_page_content",
        "description": "Extracts text content from current browser page. Use when user wants to read page content.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "browser_screenshot",
        "description": "Takes screenshot of current browser page. Use when user wants to capture browser content.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    }
]


def get_tool_schemas() -> List[Dict[str, Any]]:
    """Get all tool schemas."""
    return TOOL_SCHEMAS.copy()


def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """Get schema for a specific tool by name."""
    for schema in TOOL_SCHEMAS:
        if schema["name"] == tool_name:
            return schema
    return None


def format_tools_for_gemini() -> List[Dict[str, Any]]:
    """
    Format tool schemas for Gemini function calling API.
    Returns the schemas as-is since they're already in Gemini format.
    """
    return get_tool_schemas()
