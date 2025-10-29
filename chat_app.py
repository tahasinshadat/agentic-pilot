# Chat App - Text-based interface for Jarvis
# A floating chat window for silent environments (like Claude for Chrome but for entire computer).

import sys
import asyncio
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread
from PySide6.QtGui import QFont, QColor, QPalette

from config.config import Config
from agent.gemini import GeminiCore
from gui.settings import Settings, get_settings
from utils.logger import Logger


class ChatSignals(QObject):
    # Signals for thread-safe GUI updates.
    add_message = Signal(str, str)  # role, content
    set_status = Signal(str)  # status text
    clear_chat = Signal()


class ChatWorker(QThread):
    # Worker thread for Gemini processing.

    def __init__(self, gemini_core: GeminiCore):
        super().__init__()
        self.gemini_core = gemini_core
        self.current_message = None
        self.running = True
        self.signals = ChatSignals()
        self.loop = None

    def run(self):
        # Run async event loop in thread.
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Keep loop running
        while self.running:
            if self.current_message:
                message = self.current_message
                self.current_message = None
                self.loop.run_until_complete(self._handle_message(message))
            else:
                # Sleep briefly to avoid busy waiting
                import time
                time.sleep(0.1)

    async def _handle_message(self, user_text: str):
        # Handle a user message.
        from google.genai import types
        import base64
        import io

        try:
            self.signals.set_status.emit("Thinking...")

            # Capture screen
            screenshot_result = await self.gemini_core.screen_capture.capture_screen()

            # Build contents
            contents = []
            user_parts = [types.Part(text=user_text)]

            # Add screenshot
            if screenshot_result:
                screenshot_image, _ = screenshot_result
                image_io = io.BytesIO()
                screenshot_image.save(image_io, format="JPEG", quality=85)
                image_bytes = image_io.getvalue()

                user_parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/jpeg",
                            data=base64.b64encode(image_bytes).decode('utf-8')
                        )
                    )
                )

            contents.append(types.Content(role="user", parts=user_parts))

            # Call Gemini
            def _call():
                return self.gemini_core.client.models.generate_content(
                    model=Config.MODEL,
                    contents=contents,
                    config=self.gemini_core._g_config,
                )

            # Retry logic
            max_retries = 3
            retry_delay = 2
            response = None

            for attempt in range(max_retries):
                try:
                    response = await asyncio.to_thread(_call)
                    break
                except Exception as e:
                    error_msg = str(e)
                    if "503" in error_msg or "overloaded" in error_msg.lower():
                        if attempt < max_retries - 1:
                            self.signals.set_status.emit(f"API busy, retrying... ({attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2
                        else:
                            raise
                    else:
                        raise

            # Handle tool calls
            max_iterations = 5
            for iteration in range(max_iterations):
                function_calls = []
                if getattr(response, "candidates", None):
                    model_content = response.candidates[0].content
                    if getattr(model_content, "parts", None):
                        for part in model_content.parts:
                            fc = getattr(part, "function_call", None)
                            if fc:
                                function_calls.append(fc)

                if not function_calls:
                    break

                self.signals.set_status.emit(f"Using tools... (step {iteration + 1})")

                # Execute tools
                function_responses = await self.gemini_core._handle_tool_calls(function_calls)

                # Append model response and function results
                contents.append(response.candidates[0].content)

                fr_parts = []
                for fr in function_responses:
                    fr_obj = types.FunctionResponse(
                        name=fr["name"],
                        response=fr["response"],
                    )
                    fr_parts.append(types.Part(function_response=fr_obj))

                contents.append(types.Content(role="user", parts=fr_parts))

                # Get next response with retry
                for attempt in range(max_retries):
                    try:
                        response = await asyncio.to_thread(_call)
                        break
                    except Exception as e:
                        error_msg = str(e)
                        if "503" in error_msg or "overloaded" in error_msg.lower():
                            if attempt < max_retries - 1:
                                current_delay = 2 * (2 ** attempt)
                                self.signals.set_status.emit(f"API busy, retrying... ({attempt + 1}/{max_retries})")
                                await asyncio.sleep(current_delay)
                            else:
                                raise
                        else:
                            raise

            # Extract response text
            response_text = getattr(response, "text", "") or ""
            import re
            response_text = re.sub(r"```.*?```", "", response_text, flags=re.DOTALL).strip()

            if response_text:
                self.signals.add_message.emit("assistant", response_text)
            else:
                self.signals.add_message.emit("assistant", "[Action completed]")

            self.signals.set_status.emit("Ready")

        except Exception as e:
            Logger.error("ChatWorker", f"Error handling message: {e}")
            import traceback
            traceback.print_exc()
            self.signals.add_message.emit("system", f"Error: {str(e)}")
            self.signals.set_status.emit("Ready")

    def send_message(self, message: str):
        # Queue a message for processing.
        self.current_message = message

    def stop(self):
        # Stop the worker thread.
        self.running = False


class ChatWindow(QMainWindow):
    # Main chat window.

    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.setup_gemini()
        self.setup_ui()
        self.setup_worker()

    def setup_gemini(self):
        # Initialize Gemini core.
        Logger.info("ChatApp", "Initializing Gemini...")
        self.gemini_core = GeminiCore(
            gemini_api_key=Config.GEMINI_API_KEY,
            wake_word=self.settings.get("assistant_name", "Jarvis").lower()
        )
        Logger.info("ChatApp", "Gemini ready!")

    def setup_worker(self):
        # Setup worker thread.
        self.worker = ChatWorker(self.gemini_core)
        self.worker.signals.add_message.connect(self.add_message)
        self.worker.signals.set_status.connect(self.set_status)
        self.worker.signals.clear_chat.connect(self.clear_chat)
        self.worker.start()

    def setup_ui(self):
        # Create the chat UI.
        self.setWindowTitle(f"{self.settings.get('assistant_name', 'Jarvis')} Chat")
        self.setGeometry(100, 100, 650, 850)

        # Make window stay on top
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)

        # Get user's theme color
        color_rgb = self.settings.get_color_rgb()
        self.theme_color = QColor(*color_rgb)
        self.theme_hex = self.theme_color.name()

        # Set dark theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background: #1e1e1e;
            }}
            QWidget {{
                background: #1e1e1e;
                color: #ffffff;
            }}
        """)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Header with theme color
        header = QLabel(f"💬 {self.settings.get('assistant_name', 'Jarvis')} Chat")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"color: {self.theme_hex}; padding: 10px;")
        layout.addWidget(header)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("""
            color: #888;
            padding: 8px;
            background: #2d2d2d;
            border-radius: 8px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Chat history (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 2px solid #2d2d2d;
                border-radius: 12px;
                background: #252525;
            }}
            QScrollBar:vertical {{
                background: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.theme_hex};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.theme_color.lighter(120).name()};
            }}
        """)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)

        scroll.setWidget(self.chat_container)
        layout.addWidget(scroll, stretch=1)

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 12px;
                padding: 8px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(8, 8, 8, 8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.setFont(QFont("Segoe UI", 12))
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 10px;
                background: transparent;
                color: #ffffff;
            }
            QLineEdit::placeholder {
                color: #888;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)

        send_btn = QPushButton("Send")
        send_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.theme_hex};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
            }}
            QPushButton:hover {{
                background: {self.theme_color.lighter(120).name()};
            }}
            QPushButton:pressed {{
                background: {self.theme_color.darker(120).name()};
            }}
        """)
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field, stretch=1)
        input_layout.addWidget(send_btn)

        layout.addWidget(input_frame)

        # Clear button
        clear_btn = QPushButton("Clear Chat")
        clear_btn.setFont(QFont("Segoe UI", 10))
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                padding: 8px;
                color: #888;
            }
            QPushButton:hover {
                background: #3d3d3d;
                color: #aaa;
            }
        """)
        clear_btn.clicked.connect(self.clear_chat)
        layout.addWidget(clear_btn)

        # Add welcome message
        self.add_message("assistant", f"Hello! I'm {self.settings.get('assistant_name', 'Jarvis')}. I can see your screen and help you with anything. What can I do for you?")

    def add_message(self, role: str, content: str):
        # Add a message to chat history.
        # Create message bubble
        bubble = QFrame()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(14, 10, 14, 10)
        bubble_layout.setSpacing(6)

        # Role label
        role_label = QLabel("You" if role == "user" else self.settings.get('assistant_name', 'Jarvis'))
        role_label.setFont(QFont("Segoe UI", 10, QFont.Bold))

        # Message text
        msg_label = QLabel(content)
        msg_label.setFont(QFont("Segoe UI", 12))
        msg_label.setWordWrap(True)
        msg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        bubble_layout.addWidget(role_label)
        bubble_layout.addWidget(msg_label)

        # Style based on role with theme color
        if role == "user":
            bubble.setStyleSheet(f"""
                QFrame {{
                    background: {self.theme_hex};
                    border-radius: 16px;
                    margin-left: 60px;
                }}
                QLabel {{
                    color: white;
                    background: transparent;
                }}
            """)
        elif role == "system":
            bubble.setStyleSheet("""
                QFrame {
                    background: #4d2020;
                    border-radius: 16px;
                    border: 2px solid #803030;
                }
                QLabel {
                    color: #ff8080;
                    background: transparent;
                }
            """)
        else:  # assistant
            bubble.setStyleSheet("""
                QFrame {
                    background: #2d2d2d;
                    border-radius: 16px;
                    border: 2px solid #3d3d3d;
                    margin-right: 60px;
                }
                QLabel {
                    color: #ffffff;
                    background: transparent;
                }
            """)

        self.chat_layout.addWidget(bubble)

        # Smooth scroll to bottom
        QTimer.singleShot(50, lambda: self.scroll_to_bottom())

    def scroll_to_bottom(self):
        # Scroll chat to bottom.
        scroll = self.chat_container.parent()
        if isinstance(scroll, QScrollArea):
            scroll.verticalScrollBar().setValue(
                scroll.verticalScrollBar().maximum()
            )

    def send_message(self):
        # Send user message.
        text = self.input_field.text().strip()
        if not text:
            return

        # Add to chat
        self.add_message("user", text)

        # Clear input
        self.input_field.clear()

        # Set status
        self.set_status("Processing...")

        # Send to worker
        self.worker.send_message(text)

    def set_status(self, status: str):
        # Update status label.
        self.status_label.setText(status)

    def clear_chat(self):
        # Clear all chat messages.
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add welcome message again
        self.add_message("assistant", f"Chat cleared. How can I help you?")

    def closeEvent(self, event):
        # Handle window close.
        self.worker.stop()
        self.worker.wait(1000)  # Wait up to 1 second
        event.accept()


def main():
    # Run the chat app.
    app = QApplication(sys.argv)

    # Set app style
    app.setStyle("Fusion")

    window = ChatWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
