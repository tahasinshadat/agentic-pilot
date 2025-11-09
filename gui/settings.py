"""
Settings Manager
Handles loading, saving, and managing user preferences for Jarvis.
"""

import json
import os
from typing import Dict, Any


class Settings:
    """Manages application settings."""

    DEFAULT_SETTINGS = {
        "assistant_name": "Jarvis",
        "glow_effect": "inward",  # "inward" or "outward"
        "voice_accent": "English",  # English, Australian, British, Indian, African
        "gui_color": "blue",  # blue, green, purple, red, cyan, yellow, orange, pink
        "animation_shape": "sphere",  # sphere, icosahedron
        "whisper_model": "base",  # tiny, base, small, medium, large (base recommended for accuracy/speed balance)
    }

    COLOR_MAP = {
        "blue": (0, 150, 255),
        "green": (50, 255, 100),
        "purple": (180, 100, 255),
        "red": (255, 80, 80),
        "cyan": (0, 255, 255),
        "yellow": (255, 220, 0),
        "orange": (255, 150, 0),
        "pink": (255, 100, 200),
    }

    # ElevenLabs voice IDs for different accents
    VOICE_MAP = {
        "English": "JBFqnCBsd6RMkjVDRZzb",  # George - American English
        "Australian": "yoZ06aMxZJJ28mfd3POQ",  # Sam - Australian
        "British": "Xb7hH8MSUJpSbSDYk0k2",  # Alice - British
        "Indian": "pFZP5JQG7iQjIQuC4Bku",  # Lily - Indian
        "African": "EXAVITQu4vr4xnSDxMaL",  # Bella - African
    }

    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize settings manager."""
        self.config_path = config_path
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                # Merge with defaults (in case new settings were added)
                settings = self.DEFAULT_SETTINGS.copy()
                settings.update(loaded)
                return settings
            except Exception as e:
                print(f"[Settings] Error loading settings: {e}")
                return self.DEFAULT_SETTINGS.copy()
        else:
            return self.DEFAULT_SETTINGS.copy()

    def save_settings(self):
        """Save current settings to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print(f"[Settings] Saved to {self.config_path}")
        except Exception as e:
            print(f"[Settings] Error saving settings: {e}")

    def get(self, key: str, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value and save."""
        self.settings[key] = value
        self.save_settings()

    def get_color_rgb(self) -> tuple:
        """Get RGB tuple for current GUI color."""
        color_name = self.get("gui_color", "blue")
        return self.COLOR_MAP.get(color_name, self.COLOR_MAP["blue"])

    def get_voice_id(self) -> str:
        """Get ElevenLabs voice ID for current accent."""
        accent = self.get("voice_accent", "English")
        return self.VOICE_MAP.get(accent, self.VOICE_MAP["English"])

    def get_assistant_name(self) -> str:
        """Get assistant name."""
        return self.get("assistant_name", "Jarvis")


# Global settings instance
_settings_instance = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
