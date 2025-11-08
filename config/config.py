"""
Configuration for Jarvis assistant.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for Jarvis."""

    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

    # Wake word settings
    WAKE_WORD = "jarvis"  # Options: "jarvis", "sarah"
    ENERGY_THRESHOLD = 500  # Minimum audio energy for wake word detection

    # Audio settings
    SEND_SAMPLE_RATE = 16000  # Microphone input rate
    RECEIVE_SAMPLE_RATE = 24000  # TTS output rate (ChatTTS)
    CHUNK_SIZE = 1024

    # Gemini settings
    MODEL = "gemini-2.5-flash"  # Updated to 2.5 for better reasoning
    TOOL_RETRY_ATTEMPTS = 2  # Number of retries for failed tools (total attempts = 1 + retries)
    TOOL_RETRY_DELAY = 1.0  # Seconds to wait between retries

    # ChatTTS settings
    TTS_COMPILE = False  # Set to True for faster inference (requires compatible GPU)

    # Video settings
    VIDEO_MODE = "none"  # Options: "camera", "screen", "none"

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        if not cls.ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")

        print("[Config] Configuration validated successfully")

    @classmethod
    def get_wake_word(cls) -> str:
        """Get configured wake word."""
        return cls.WAKE_WORD

    @classmethod
    def set_wake_word(cls, wake_word: str):
        """Set wake word."""
        if wake_word.lower() in ["jarvis", "sarah"]:
            cls.WAKE_WORD = wake_word.lower()
            print(f"[Config] Wake word set to: {wake_word}")
        else:
            print(f"[Config] Invalid wake word: {wake_word}")
