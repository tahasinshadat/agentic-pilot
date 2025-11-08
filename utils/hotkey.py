"""
Global hotkey handler for JARVIS.
Supports Win+J to trigger listening without wake word.
"""

import asyncio
import keyboard
from utils.logger import Logger


class HotkeyHandler:
    """
    Manages global hotkeys for JARVIS.
    """

    def __init__(self, jarvis_core, event_loop):
        """
        Initialize hotkey handler.

        Args:
            jarvis_core: GeminiCore instance
            event_loop: Async event loop for the core
        """
        self.jarvis = jarvis_core
        self.loop = event_loop
        self.registered = False

    def register_hotkeys(self):
        """
        Register all global hotkeys.
        """
        try:
            # Register Win+J hotkey
            keyboard.add_hotkey('windows+j', self._on_hotkey_pressed, suppress=True)
            self.registered = True
            Logger.info("Hotkey", "Win+J hotkey registered - Press to activate listening")

        except Exception as e:
            Logger.error("Hotkey", f"Failed to register hotkeys: {e}")

    def _on_hotkey_pressed(self):
        """
        Handle hotkey press (called from keyboard library thread).
        """
        Logger.info("Hotkey", "Win+J pressed - Triggering listening")

        # Schedule the async trigger in the event loop
        asyncio.run_coroutine_threadsafe(
            self.jarvis.trigger_listening(),
            self.loop
        )

    def unregister_hotkeys(self):
        """
        Unregister all hotkeys.
        """
        if self.registered:
            try:
                keyboard.remove_hotkey('windows+j')
                self.registered = False
                Logger.info("Hotkey", "Hotkeys unregistered")
            except Exception as e:
                Logger.error("Hotkey", f"Error unregistering hotkeys: {e}")
