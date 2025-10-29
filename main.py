"""
Jarvis - Advanced AI Assistant
Main entry point with floating GUI.
"""

import sys
import asyncio
import threading
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot

from config import Config
from agent.gemini import GeminiCore
from gui.floating_window import FloatingAssistantWindow
from utils.logger import Logger


class JarvisApp(QObject):
    """
    Main Jarvis application.
    Coordinates GUI and AI core.
    """

    # Signals for thread-safe GUI updates
    show_listening = Signal()
    show_thinking = Signal()
    show_speaking = Signal()
    show_idle = Signal()

    def __init__(self):
        super().__init__()

        # Validate configuration
        Config.validate()

        # Initialize Gemini core
        self.jarvis = GeminiCore(
            gemini_api_key=Config.GEMINI_API_KEY,
            wake_word=Config.WAKE_WORD
        )

        # Set up callbacks
        self.jarvis.on_listening = self._on_listening
        self.jarvis.on_thinking = self._on_thinking
        self.jarvis.on_speaking_start = self._on_speaking_start
        self.jarvis.on_speaking_end = self._on_speaking_end
        self.jarvis.on_idle = self._on_idle

        # GUI window (will be created in Qt thread)
        self.gui = None

        # Event loop for async core
        self.loop = asyncio.new_event_loop()
        self.core_thread = None

    def setup_gui(self):
        """Setup floating GUI window."""
        self.gui = FloatingAssistantWindow()

        # Connect signals to GUI
        self.show_listening.connect(self.gui.set_listening)
        self.show_thinking.connect(self.gui.set_thinking)
        self.show_speaking.connect(self.gui.set_speaking)
        self.show_idle.connect(self.gui.set_idle)

        # Set wake word in GUI
        self.gui.name_label.setText(Config.WAKE_WORD.upper())

        Logger.info("App", "GUI initialized")

    def start(self):
        """Start Jarvis core in background thread."""
        self.core_thread = threading.Thread(target=self._run_async_core, daemon=True)
        self.core_thread.start()

        Logger.info("App", f"Jarvis started! Say 'Hey {Config.WAKE_WORD.capitalize()}'")

    def _run_async_core(self):
        """Run async core in separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.jarvis.start())

    # Async callbacks from Jarvis core
    async def _on_listening(self):
        """Called when Jarvis starts listening."""
        Logger.info("App", "Listening...")
        self.show_listening.emit()

    async def _on_thinking(self):
        """Called when Jarvis is thinking."""
        Logger.info("App", "Thinking...")
        self.show_thinking.emit()

    async def _on_speaking_start(self):
        """Called when Jarvis starts speaking."""
        Logger.info("App", "Speaking...")
        self.show_speaking.emit()

    async def _on_speaking_end(self):
        """Called when Jarvis finishes speaking."""
        Logger.info("App", "Speech finished")

    async def _on_idle(self):
        """Called when Jarvis goes idle."""
        Logger.info("App", "Idle")
        self.show_idle.emit()

    def stop(self):
        """Stop Jarvis."""
        Logger.info("App", "Stopping Jarvis...")
        self.jarvis.stop()

        if self.loop.is_running():
            self.loop.stop()


def main():
    """Main entry point."""
    print("="*60)
    print("JARVIS - Advanced AI Assistant")
    print("="*60)
    print()

    try:
        # Create Qt application
        app = QApplication(sys.argv)

        # Create Jarvis app
        jarvis_app = JarvisApp()

        # Setup GUI
        jarvis_app.setup_gui()

        # Start Jarvis core
        jarvis_app.start()

        print()
        print("="*60)
        print(f"[OK] Jarvis is ready!")
        print(f"  Wake word: 'Hey {Config.WAKE_WORD.capitalize()}'")
        print(f"  GUI: Floating window in bottom-right corner")
        print()
        print("  Say the wake word to activate Jarvis!")
        print("="*60)
        print()

        # Run Qt event loop
        exit_code = app.exec()

        # Cleanup
        jarvis_app.stop()

        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)

    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
