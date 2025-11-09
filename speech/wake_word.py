"""
Wake word detection using faster-whisper.
Detects 'Hey Jarvis' or 'Hey Sarah'.
"""

import asyncio
import os
import struct
import tempfile
import wave
from typing import Callable, Optional
import pyaudio
from faster_whisper import WhisperModel
from gui.settings import get_settings


class WakeWordDetector:
    """
    Detects wake words using transcription-based approach.
    Supports: 'Hey Jarvis', 'Jarvis', 'Hey Sarah', 'Sarah'
    """

    def __init__(self, wake_word: str = "jarvis", energy_threshold: int = 300):
        """
        Initialize wake word detector.

        Args:
            wake_word: 'jarvis' or 'sarah'
            energy_threshold: Minimum audio energy to trigger transcription (lowered for better sensitivity)
        """
        self.wake_word = wake_word.lower()
        self.energy_threshold = energy_threshold
        self.is_running = False
        self.continuous_mode = False
        self.audio_stream = None

        # Load Whisper model from settings
        settings = get_settings()
        model_name = settings.get("whisper_model", "base")
        print(f"[WakeWord] Loading Whisper model: {model_name}...")
        self.model = WhisperModel(model_name, device="cpu", compute_type="int8")
        print(f"[WakeWord] Model '{model_name}' loaded!")

        # Audio settings
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.record_seconds = 3  # Longer window for better detection (increased from 2)

    async def start_detection(self, callback: Callable):
        """
        Start wake word detection loop.

        Args:
            callback: Async function to call when wake word detected
                     Should accept optional 'command_text' parameter
        """
        self.is_running = True

        pya = pyaudio.PyAudio()
        self.audio_stream = pya.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        print(f"[WakeWord] Listening for '{self.wake_word}'...")

        try:
            while self.is_running:
                # Record audio chunk (shorter for better responsiveness)
                frames = []
                has_speech = False

                for _ in range(0, int(self.rate / self.chunk * self.record_seconds)):
                    data = await asyncio.to_thread(
                        self.audio_stream.read,
                        self.chunk,
                        exception_on_overflow=False
                    )
                    frames.append(data)

                    # Check energy level
                    pcm = struct.unpack_from("h" * self.chunk, data)
                    energy = sum(abs(x) for x in pcm) / self.chunk
                    if energy > self.energy_threshold:
                        has_speech = True

                # Process if speech detected
                if has_speech:
                    # In continuous mode, trigger immediately
                    if self.continuous_mode:
                        await callback()
                        await asyncio.sleep(1)  # Prevent immediate re-trigger
                        continue

                    # Otherwise check for wake word
                    text = await self._transcribe_audio(frames, pya)
                    text_lower = text.lower().strip()

                    # Check for wake words
                    wake_words = [
                        self.wake_word,
                        f"hey {self.wake_word}",
                        f"ok {self.wake_word}",
                    ]

                    # Find which wake word was detected
                    detected_wake_word = None
                    for ww in wake_words:
                        if ww in text_lower:
                            detected_wake_word = ww
                            break

                    if detected_wake_word:
                        print(f"[WakeWord] Detected wake word in: '{text}'")

                        # Extract command text after wake word (if any)
                        # Use regex to find wake word with optional punctuation
                        import re

                        # Create pattern that matches wake word with optional punctuation/spaces
                        # For "hey jarvis" -> matches "hey jarvis", "Hey, Jarvis.", "hey jarvis,", etc.
                        wake_pattern = detected_wake_word.replace(' ', r'[\s,\.]*')
                        match = re.search(wake_pattern, text_lower, re.IGNORECASE)

                        command_text = ""
                        if match:
                            # Get position after the matched wake word
                            wake_end = match.end()
                            command_text = text[wake_end:].strip()

                            # Remove leading punctuation
                            command_text = command_text.lstrip('.,!?:; ')

                        # Pass command text to callback if it exists
                        if command_text and len(command_text) > 3:
                            print(f"[WakeWord] Captured command with wake word: '{command_text}'")
                            await callback(command_text=command_text)
                        else:
                            await callback()

                        # Longer cooldown to avoid re-detecting during command recording
                        await asyncio.sleep(5)

        except Exception as e:
            print(f"[WakeWord] Error: {e}")
        finally:
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            pya.terminate()

    async def _transcribe_audio(self, frames, pya) -> str:
        """Transcribe audio frames using Whisper."""
        try:
            # Save to temp WAV file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            temp_file.close()

            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(pya.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))

            # Transcribe
            segments, _ = await asyncio.to_thread(
                self.model.transcribe,
                temp_path,
                language="en",
                beam_size=1
            )
            text = " ".join([segment.text for segment in segments])

            # Clean up
            os.unlink(temp_path)

            return text

        except Exception as e:
            print(f"[WakeWord] Transcription error: {e}")
            return ""

    def stop_detection(self):
        """Stop wake word detection."""
        self.is_running = False

    def set_continuous_mode(self, enabled: bool):
        """
        Enable/disable continuous listening mode.

        Args:
            enabled: If True, trigger on any speech (no wake word needed)
        """
        self.continuous_mode = enabled
        print(f"[WakeWord] Continuous mode: {enabled}")

    def set_wake_word(self, wake_word: str):
        """
        Change wake word.

        Args:
            wake_word: 'jarvis' or 'sarah'
        """
        self.wake_word = wake_word.lower()
        print(f"[WakeWord] Wake word changed to: {wake_word}")
