"""
Play Music Tool
Intelligently plays music using Spotify if available, otherwise falls back to YouTube.
"""

import time
import pyautogui
import subprocess
import webbrowser
from typing import Dict, Any


def play_music(query: str) -> Dict[str, Any]:
    """
    Play music using the best available method.

    Priority:
    1. Try to open Spotify and search for the song
    2. If Spotify not found, open YouTube and play the song

    Args:
        query: The song/artist to play (e.g., "We Don't Talk Anymore by Charlie Puth")

    Returns:
        Dict with status and message
    """
    print(f"[PlayMusic] Attempting to play: {query}")

    # Try Spotify first
    spotify_result = _try_spotify(query)
    if spotify_result["success"]:
        return spotify_result

    # Fallback to YouTube
    print(f"[PlayMusic] Spotify failed ({spotify_result.get('error')}), using YouTube...")
    return _try_youtube(query)


def _try_spotify(query: str) -> Dict[str, Any]:
    """
    Try to play music in Spotify.

    Returns:
        Dict with success status and message/error
    """
    try:
        print("[PlayMusic] Launching Spotify...")

        # Try to launch Spotify
        process = subprocess.Popen(
            ["spotify"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait for Spotify to start (with timeout check)
        time.sleep(3)

        # Check if process is still running (Spotify found)
        if process.poll() is not None:
            # Process exited immediately - Spotify not found
            return {
                "success": False,
                "error": "Spotify executable not found"
            }

        # Focus the current window (Spotify should be foreground)
        pyautogui.click()
        time.sleep(0.3)

        # Use Ctrl+L to focus search bar in Spotify
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)

        # Type the search query
        pyautogui.write(query, interval=0.03)
        time.sleep(0.7)

        # Press Enter to search
        pyautogui.press('enter')
        time.sleep(1.5)

        # Press Enter again to play the first result
        pyautogui.press('enter')
        time.sleep(0.3)

        print(f"[PlayMusic] Playing '{query}' in Spotify")
        return {
            "success": True,
            "status": "success",
            "message": f"Playing '{query}' in Spotify",
            "method": "spotify"
        }

    except FileNotFoundError:
        # Spotify executable not found
        return {
            "success": False,
            "error": "Spotify not installed"
        }
    except PermissionError:
        # Can't execute Spotify
        return {
            "success": False,
            "error": "Permission denied to launch Spotify"
        }
    except Exception as e:
        # Other errors
        return {
            "success": False,
            "error": f"Spotify error: {str(e)}"
        }


def _try_youtube(query: str) -> Dict[str, Any]:
    """
    Play music on YouTube as fallback.

    Returns:
        Dict with success status and message
    """
    try:
        youtube_query = f"{query} official audio"
        youtube_url = f"https://www.youtube.com/results?search_query={youtube_query.replace(' ', '+')}"

        # Open YouTube search in browser
        print(f"[PlayMusic] Opening YouTube: {youtube_url}")
        webbrowser.open(youtube_url)
        time.sleep(2)

        # Get screen size to calculate click position dynamically
        screen_width, screen_height = pyautogui.size()

        # YouTube's first video is typically in the upper-left quadrant
        # Calculate position based on screen size (more reliable than hardcoded)
        click_x = int(screen_width * 0.25)  # 25% from left
        click_y = int(screen_height * 0.35)  # 35% from top

        print(f"[PlayMusic] Clicking first video at ({click_x}, {click_y})")
        pyautogui.click(click_x, click_y)
        time.sleep(0.5)

        return {
            "success": True,
            "status": "success",
            "message": f"Playing '{query}' on YouTube (Spotify not available)",
            "method": "youtube"
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": f"Failed to play music: {str(e)}",
            "error": str(e)
        }


# MCP integration
def get_tool_definition():
    """Return tool definition for MCP."""
    return {
        "name": "play_music",
        "description": "Play music or songs. Automatically uses Spotify if installed, otherwise uses YouTube. Use this tool for ANY music playback request (play song, play artist, play album, etc.). Examples: 'play We Don't Talk Anymore', 'play Charlie Puth', 'play rap music'.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "The song, artist, album, or playlist to play. Can include artist name for better results."
                }
            },
            "required": ["query"]
        }
    }
