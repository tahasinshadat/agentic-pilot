"""
Jarvis Settings & Test Application
Standalone application for configuring and testing Jarvis assistant.
Run this to customize and preview your assistant without starting Jarvis.

Usage:
    python settings_app.py 
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                                QWidget, QPushButton, QLabel, QComboBox, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt, QTimer
from gui.floating_window import FloatingAssistantWindow
from gui.settings import get_settings


class SettingsApp(QMainWindow):
    """
    Combined settings and test application with live preview.
    All-in-one window with inline settings and test controls.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis Settings & Test Manager")
        # 3:2 aspect ratio (900x600)
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(900, 600)

        # Preview window (shows how Jarvis will look)
        self.preview_window = FloatingAssistantWindow()
        self.preview_window.show()
        self.preview_window.set_listening()

        # Settings
        self.settings = get_settings()

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Create the main UI with horizontal layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # LEFT SIDE - Settings Panel
        settings_panel = self.create_settings_panel()
        main_layout.addWidget(settings_panel, stretch=2)

        # RIGHT SIDE - Test Controls Panel
        test_panel = self.create_test_panel()
        main_layout.addWidget(test_panel, stretch=1)

        # Window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QWidget {
                background-color: #1a1a2e;
                color: white;
            }
            QLabel {
                color: white;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #0096FF;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)

    def create_settings_panel(self):
        """Create left panel with all settings."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Title
        title = QLabel("⚙️ JARVIS SETTINGS")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #0096FF;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Assistant Identity Group
        identity_group = QGroupBox("Assistant Identity")
        identity_layout = QFormLayout()
        identity_layout.setSpacing(10)

        self.name_combo = self.create_combo(["Jarvis", "Sarah"], self.settings.get("assistant_name"))
        self.name_combo.currentTextChanged.connect(self.on_name_changed)
        identity_layout.addRow("Name:", self.name_combo)

        self.voice_combo = self.create_combo(
            ["English", "Australian", "British", "Indian", "African"],
            self.settings.get("voice_accent")
        )
        self.voice_combo.currentTextChanged.connect(self.on_voice_changed)
        identity_layout.addRow("Voice Accent:", self.voice_combo)

        identity_group.setLayout(identity_layout)
        layout.addWidget(identity_group)

        # Visual Effects Group
        visual_group = QGroupBox("Visual Effects")
        visual_layout = QFormLayout()
        visual_layout.setSpacing(10)

        self.glow_combo = self.create_combo(
            ["Inward", "Outward"],
            self.settings.get("glow_effect", "inward").capitalize()
        )
        self.glow_combo.currentTextChanged.connect(self.on_glow_changed)
        visual_layout.addRow("Glow Effect:", self.glow_combo)

        self.color_combo = self.create_combo(
            ["Blue", "Green", "Purple", "Red", "Cyan", "Yellow", "Orange", "Pink"],
            self.settings.get("gui_color", "blue").capitalize()
        )
        self.color_combo.currentTextChanged.connect(self.on_color_changed)
        visual_layout.addRow("GUI Color:", self.color_combo)

        self.shape_combo = self.create_combo(
            ["Sphere", "Icosahedron"],
            self.settings.get("animation_shape", "sphere").capitalize()
        )
        self.shape_combo.currentTextChanged.connect(self.on_shape_changed)
        visual_layout.addRow("Animation Shape:", self.shape_combo)

        visual_group.setLayout(visual_layout)
        layout.addWidget(visual_group)

        # Current Config Display
        self.config_display = QLabel()
        self.config_display.setStyleSheet("""
            font-size: 11px;
            color: #888;
            background-color: #252540;
            border: 2px solid #0096FF;
            border-radius: 8px;
            padding: 12px;
        """)
        self.update_config_display()
        layout.addWidget(self.config_display)

        layout.addStretch()

        return panel

    def create_test_panel(self):
        """Create right panel with test controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        # Title
        title = QLabel("🎬 TEST CONTROLS")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #0096FF;
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Test different GUI states.\n"
            "Watch the floating window!"
        )
        instructions.setStyleSheet("padding: 8px; color: #AAA; font-size: 12px;")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        layout.addSpacing(10)

        # State buttons
        btn_listening = self.create_test_button("🎤 LISTENING", "#4CAF50", self.test_listening)
        layout.addWidget(btn_listening)

        btn_thinking = self.create_test_button("🤔 THINKING", "#FF9800", self.test_thinking)
        layout.addWidget(btn_thinking)

        btn_speaking = self.create_test_button("🗣️ SPEAKING", "#2196F3", self.test_speaking)
        layout.addWidget(btn_speaking)

        btn_idle = self.create_test_button("💤 IDLE", "#9E9E9E", self.test_idle)
        layout.addWidget(btn_idle)

        layout.addSpacing(15)

        # Auto test
        btn_auto = QPushButton("🎬 Run Auto Test")
        btn_auto.clicked.connect(self.run_auto_test)
        btn_auto.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7b1fa2;
            }
        """)
        layout.addWidget(btn_auto)

        layout.addSpacing(15)

        # Status label
        self.status_label = QLabel("Ready to test!")
        self.status_label.setStyleSheet("""
            padding: 10px;
            background-color: #252540;
            border: 1px solid #0096FF;
            border-radius: 5px;
            font-family: 'Courier New';
            font-size: 11px;
            color: #0096FF;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        layout.addStretch()

        return panel

    def create_combo(self, items, current):
        """Create styled combo box."""
        combo = QComboBox()
        combo.addItems(items)
        combo.setCurrentText(current)
        combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d44;
                color: white;
                border: 2px solid #0096FF;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QComboBox:hover {
                border: 2px solid #00AAFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d44;
                color: white;
                selection-background-color: #0096FF;
                border: 2px solid #0096FF;
            }
        """)
        return combo

    def create_test_button(self, text, color, callback):
        """Create styled test button."""
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """)
        return btn

    def update_config_display(self):
        """Update the current configuration display."""
        self.config_display.setText(
            f"Current Configuration:\n\n"
            f"Name: {self.settings.get_assistant_name()}\n"
            f"Voice: {self.settings.get('voice_accent')}\n"
            f"Color: {self.settings.get('gui_color').capitalize()}\n"
            f"Glow: {self.settings.get('glow_effect').capitalize()}\n"
            f"Shape: {self.settings.get('animation_shape').capitalize()}\n\n"
            f"Settings saved to:\nconfig/settings.json"
        )

    # Settings change handlers
    def on_name_changed(self, name):
        self.settings.set("assistant_name", name)
        self.preview_window.reload_settings()
        self.update_config_display()

    def on_voice_changed(self, voice):
        self.settings.set("voice_accent", voice)
        self.update_config_display()

    def on_glow_changed(self, glow):
        self.settings.set("glow_effect", glow.lower())
        self.preview_window.reload_settings()
        self.update_config_display()

    def on_color_changed(self, color):
        self.settings.set("gui_color", color.lower())
        self.preview_window.reload_settings()
        self.update_config_display()

    def on_shape_changed(self, shape):
        self.settings.set("animation_shape", shape.lower())
        self.preview_window.reload_settings()
        self.update_config_display()

    # Test control handlers
    def test_listening(self):
        self.status_label.setText("Testing LISTENING mode...\n🎤 Speak to see border glow!")
        self.preview_window.set_listening()

    def test_thinking(self):
        self.status_label.setText("Testing THINKING mode...")
        self.preview_window.set_thinking()

    def test_speaking(self):
        self.status_label.setText("Testing SPEAKING mode...\n🗣️ Watch the animation!")
        self.preview_window.set_speaking()

    def test_idle(self):
        self.status_label.setText("Testing IDLE mode...\n💤 Window will hide in 2s")
        self.preview_window.set_idle()

    def run_auto_test(self):
        """Run automated test sequence."""
        self.status_label.setText("🎬 AUTO TEST: Starting sequence...")

        QTimer.singleShot(0, lambda: (
            self.preview_window.set_listening(),
            self.status_label.setText("🎤 LISTENING (4s)")
        ))

        QTimer.singleShot(4000, lambda: (
            self.preview_window.set_thinking(),
            self.status_label.setText("🤔 THINKING (4s)")
        ))

        QTimer.singleShot(8000, lambda: (
            self.preview_window.set_speaking(),
            self.status_label.setText("🗣️ SPEAKING (4s)")
        ))

        QTimer.singleShot(12000, lambda: (
            self.preview_window.set_idle(),
            self.status_label.setText("💤 IDLE (hides in 2s)")
        ))

        QTimer.singleShot(15000, lambda: self.status_label.setText(
            "✅ AUTO TEST COMPLETE!\n\n"
            "All states tested:\n"
            "• Listening ✓\n"
            "• Thinking ✓\n"
            "• Speaking ✓\n"
            "• Idle ✓"
        ))

    def closeEvent(self, event):
        """Clean up when closing."""
        if self.preview_window:
            self.preview_window.close()
        event.accept()


def main():
    """Run the settings application."""
    print("="*70)
    print("  JARVIS SETTINGS & TEST MANAGER")
    print("="*70)
    print("\nCombined settings and testing application")
    print("Configure and preview your assistant")
    print("\nSettings saved to: config/settings.json")
    print("Changes apply when Jarvis starts")
    print("="*70)

    app = QApplication(sys.argv)
    window = SettingsApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
