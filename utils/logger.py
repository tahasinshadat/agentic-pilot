"""
Simple logger for Jarvis.
"""

from datetime import datetime
from typing import Optional


class Logger:
    """Simple logging utility."""

    @staticmethod
    def log(category: str, message: str, level: str = "INFO"):
        """
        Log a message.

        Args:
            category: Log category (e.g., "WakeWord", "TTS", "Core")
            message: Log message
            level: Log level ("INFO", "ERROR", "DEBUG")
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] [{category}] {message}")

    @staticmethod
    def info(category: str, message: str):
        """Log info message."""
        Logger.log(category, message, "INFO")

    @staticmethod
    def error(category: str, message: str):
        """Log error message."""
        Logger.log(category, message, "ERROR")

    @staticmethod
    def debug(category: str, message: str):
        """Log debug message."""
        Logger.log(category, message, "DEBUG")
