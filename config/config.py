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
    WAKE_WORD = "sarah"  # Options: "jarvis", "sarah"
    ENERGY_THRESHOLD = 500  # Minimum audio energy for wake word detection

    # Audio settings
    SEND_SAMPLE_RATE = 16000  # Microphone input rate
    RECEIVE_SAMPLE_RATE = 24000  # TTS output rate (ChatTTS)
    CHUNK_SIZE = 1024

    # Gemini settings
    MODEL = "gemini-2.5-flash"  # Updated to 2.5 for better reasoning
    TOOL_RETRY_ATTEMPTS = 2  # Number of retries for failed tools (total attempts = 1 + retries)
    TOOL_RETRY_DELAY = 1.0  # Seconds to wait between retries

    MAX_CONVERSATION_TURNS = 20  # Maximum turns to keep in conversation history
    MAX_TOOL_ITERATIONS = 5  # Maximum tool execution iterations per interaction

    # Audio Recording Settings (moved from gemini.py)
    SILENCE_THRESHOLD = 300  # Audio energy threshold for silence detection
    SILENCE_DURATION = 3.5  # Seconds of silence to end recording
    MAX_RECORDING_DURATION = 15  # Maximum seconds for a single recording
    MIN_AUDIO_LENGTH = 0.5  # Minimum audio length in seconds
    MIN_TRANSCRIPTION_LENGTH = 3  # Minimum transcription text length

    # TTS Settings (moved from gemini.py)
    ELEVENLABS_VOICE_ID = "Z3R5wn05IrDiVCyEkUrK"  # Default voice ID (Jarvis)

    # Voice ID mapping for different assistants
    VOICE_IDS = {
        "jarvis": "UgBBYS2sOqTuMpoF3BR0",  # Jarvis voice
        "sarah": "Z3R5wn05IrDiVCyEkUrK"    # Sarah voice
    }
    # Serafina: 4tRn1lSkEn13EVTuqb0g

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


        # Validate numeric ranges
        if cls.TOOL_RETRY_ATTEMPTS < 0:
            raise ValueError(f"TOOL_RETRY_ATTEMPTS must be >= 0, got {cls.TOOL_RETRY_ATTEMPTS}")

        if cls.TOOL_RETRY_DELAY < 0:
            raise ValueError(f"TOOL_RETRY_DELAY must be >= 0, got {cls.TOOL_RETRY_DELAY}")

        if cls.MAX_CONVERSATION_TURNS < 1:
            raise ValueError(f"MAX_CONVERSATION_TURNS must be >= 1, got {cls.MAX_CONVERSATION_TURNS}")

        if cls.SILENCE_THRESHOLD < 0:
            raise ValueError(f"SILENCE_THRESHOLD must be >= 0, got {cls.SILENCE_THRESHOLD}")

        if cls.MAX_RECORDING_DURATION < cls.MIN_AUDIO_LENGTH:
            raise ValueError(f"MAX_RECORDING_DURATION must be >= MIN_AUDIO_LENGTH")


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

    @classmethod
    def get_voice_id(cls, assistant_name: str) -> str:
        """
        Get the ElevenLabs voice ID for the given assistant name.

        Args:
            assistant_name: Name of the assistant ("Jarvis" or "Sarah")

        Returns:
            Voice ID string for ElevenLabs
        """
        name_lower = assistant_name.lower()
        voice_id = cls.VOICE_IDS.get(name_lower, cls.ELEVENLABS_VOICE_ID)
        print(f"[Config] Using voice ID for {assistant_name}: {voice_id}")
        return voice_id
