"""
ElevenLabs TTS Manager - Simple SDK Implementation
Copied EXACTLY from ada/Tutorials/6-textToSpeechwithGemini.py
"""

import asyncio
import os
from typing import Optional, Callable
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play


class ElevenLabsTTS:
    """
    ElevenLabs TTS using the simple SDK client.
    Exact implementation from ada tutorial - proven to work.
    """

    def __init__(self, api_key: str, voice_id: str = "UgBBYS2sOqTuMpoF3BR0"):
        """
        Initialize ElevenLabs TTS.

        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID to use (default: UgBBYS2sOqTuMpoF3BR0)
        """
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id

        print(f"[TTS] ElevenLabs SDK initialized with voice: {voice_id}")

    async def speak(
        self,
        text: str,
        on_start: Optional[Callable] = None,
        on_end: Optional[Callable] = None
    ):
        """
        Speak text using ElevenLabs SDK - EXACT tutorial implementation.

        Args:
            text: Text to speak
            on_start: Callback when speech starts
            on_end: Callback when speech ends
        """
        if not text or len(text.strip()) == 0:
            print("[TTS] No text to speak")
            return

        # CRITICAL: Use try-finally to GUARANTEE end callback fires
        try:
            # Trigger start callback
            if on_start:
                try:
                    if asyncio.iscoroutinefunction(on_start):
                        await on_start()
                    else:
                        on_start()
                except Exception as cb_error:
                    print(f"[TTS] Error in on_start callback: {cb_error}")

            print(f"[TTS] Generating speech: {text[:50]}...")

            # Generate speech using ElevenLabs - EXACT tutorial approach
            audio = await asyncio.to_thread(
                self.client.text_to_speech.convert,
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_flash_v2_5",
                output_format="mp3_44100_128"
            )

            print("[TTS] Playing audio...")

            # Play audio - EXACT tutorial approach
            await asyncio.to_thread(play, audio)

            print("[TTS] Playback complete")

        except Exception as e:
            print(f"[TTS] Error during speech: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # CRITICAL: Always trigger end callback, even on error
            if on_end:
                try:
                    if asyncio.iscoroutinefunction(on_end):
                        await on_end()
                    else:
                        on_end()
                except Exception as cb_error:
                    print(f"[TTS] Error in on_end callback: {cb_error}")

    def cleanup(self):
        """Clean up resources."""
        print("[TTS] Cleaned up")
