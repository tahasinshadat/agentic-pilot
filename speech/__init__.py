"""
Speech components - wake word detection and TTS.
"""

from .wake_word import WakeWordDetector
from .tts import ElevenLabsTTS

__all__ = ['WakeWordDetector', 'ElevenLabsTTS']
