"""
Play Music Tool
Intelligently plays music using Spotify if available, otherwise falls back to YouTube.
"""

import time
import pyautogui
import subprocess
import webbrowser


def play_music(query: str) -> str:
    """
    Play music using the best available method.

    Priority:
    1. Try to open Spotify and search for the song
    2. If Spotify not found, open YouTube and play the song

    Args:
        query: The song/artist to play (e.g., "We Don't Talk Anymore by Charlie Puth")

    Returns:
        Success message describing what was done
    """
    print(f"[PlayMusic] Attempting to play: {query}")

    try:
        # Try to launch Spotify
        print("[PlayMusic] Launching Spotify...")
        subprocess.Popen("spotify", shell=True)
        time.sleep(3)  # Wait for Spotify to open

        # Click in the center to focus Spotify window
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
        return f"Playing '{query}' in Spotify"

    except Exception as e:
        # Spotify not available, use YouTube
        print(f"[PlayMusic] Spotify failed ({e}), using YouTube...")
        youtube_query = f"{query} official audio"
        youtube_url = f"https://www.youtube.com/results?search_query={youtube_query.replace(' ', '+')}"

        # Open YouTube search in browser
        webbrowser.open(youtube_url)
        time.sleep(2)

        # Click first video
        # YouTube first video is typically at around (300, 350) on a standard screen
        pyautogui.click(400, 350)

        return f"Playing '{query}' on YouTube (Spotify not available)"


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
