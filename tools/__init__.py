"""Tools exposed to the agent and MCP."""

# Screen capture utility
from .screen_capture import ScreenCapture

# File operations
from .create_folder import create_folder
from .create_file import create_file
from .edit_file import edit_file
from .read_file import read_file
from .list_files import list_files

# Application control
from .launch import launch
from .smart_open import smart_open_simple as smart_open
from .play_music import play_music

# Time utilities
from .get_current_time import get_current_time

# Web tools
from .open_website import open_website
from .search_google import search_google

# Screen solver tools
from .analyze_screen import analyze_screen

# General UI interaction tools
from .click_on_screen import click_on_screen
from .type_text import type_text
from .fill_form_on_screen import fill_form_on_screen
from .move_mouse import move_mouse
from .move_text_cursor import move_text_cursor

# Code assistant tools
from .insert_code import insert_code
from .generate_code import generate_code
from .get_selected_code import get_selected_code
from .format_code import format_code
from .save_file import save_file
from .comment_code import comment_code

# Browser control tools (require browser_server instance)
from .browser_open_tab import browser_open_tab
from .browser_close_tab import browser_close_tab
from .browser_navigate import browser_navigate
from .browser_google_search import browser_google_search
from .browser_fill_form import browser_fill_form
from .browser_click_element import browser_click_element
from .browser_get_page_content import browser_get_page_content
from .browser_screenshot import browser_screenshot

# Accessibility tools
from .accessibility_shortcuts import accessibility_shortcuts
from .screen_color_filter import screen_color_filter


# System controls
from .adjust_volume import adjust_volume
from .adjust_brightness import adjust_brightness


# System controls
from .adjust_volume import adjust_volume
from .adjust_brightness import adjust_brightness

# Autopilot (PyAutoGUI-based computer control)
from .autopilot import execute_autopilot

__all__ = [
    # Utilities
    "ScreenCapture",
    # File operations
    "create_folder",
    "create_file",
    "edit_file",
    "read_file",
    "list_files",
    # Application control
    "launch",
    "smart_open",
    "play_music",
    # Time utilities
    "get_current_time",
    # Web tools
    "open_website",
    "search_google",
    # Screen solver
    "analyze_screen",
    # UI interaction
    "click_on_screen",
    "type_text",
    "fill_form_on_screen",
    "move_mouse",
    "move_text_cursor",
    # Code assistant
    "insert_code",
    "generate_code",
    "get_selected_code",
    "format_code",
    "save_file",
    "comment_code",
    # Accessibility Settings
    "screen_color_filter",
    "accessibility_shortcuts",
    # System controls
    "adjust_volume",
    "adjust_brightness",
    # System controls
    "adjust_volume",
    "adjust_brightness",
    # Browser control
    "browser_open_tab",
    "browser_close_tab",
    "browser_navigate",
    "browser_google_search",
    "browser_fill_form",
    "browser_click_element",
    "browser_get_page_content",
    "browser_screenshot",
    # Autopilot
    "execute_autopilot",
]
