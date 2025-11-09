"""
Settings Window
GUI for configuring Jarvis assistant preferences.
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QComboBox, QPushButton, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt, Signal
from gui.settings import get_settings


class SettingsWindow(QMainWindow):
    """Settings configuration window."""

    # Signal emitted when settings change
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        self.setWindowTitle("Jarvis Settings")
        self.setGeometry(200, 200, 500, 600)
        self.setup_ui()

    def setup_ui(self):
        """Create the settings UI."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("⚙️ Assistant Settings")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #0096FF;
            padding: 15px;
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Assistant Identity Group
        identity_group = QGroupBox("Assistant Identity")
        identity_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #0096FF;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        identity_layout = QFormLayout()
        identity_layout.setSpacing(10)

        # Name selector
        self.name_combo = QComboBox()
        self.name_combo.addItems(["Jarvis", "Sarah"])
        self.name_combo.setCurrentText(self.settings.get("assistant_name"))
        self.name_combo.currentTextChanged.connect(self.on_name_changed)
        self.name_combo.setStyleSheet(self._combo_style())
        identity_layout.addRow("Name:", self.name_combo)

        # Voice accent selector
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["English", "Australian", "British", "Indian", "African"])
        self.voice_combo.setCurrentText(self.settings.get("voice_accent"))
        self.voice_combo.currentTextChanged.connect(self.on_voice_changed)
        self.voice_combo.setStyleSheet(self._combo_style())
        identity_layout.addRow("Voice Accent:", self.voice_combo)

        identity_group.setLayout(identity_layout)
        main_layout.addWidget(identity_group)

        # Visual Effects Group
        visual_group = QGroupBox("Visual Effects")
        visual_group.setStyleSheet(identity_group.styleSheet())
        visual_layout = QFormLayout()
        visual_layout.setSpacing(10)

        # Glow effect selector
        self.glow_combo = QComboBox()
        self.glow_combo.addItems(["Inward", "Outward"])
        current_glow = self.settings.get("glow_effect", "inward")
        self.glow_combo.setCurrentText(current_glow.capitalize())
        self.glow_combo.currentTextChanged.connect(self.on_glow_changed)
        self.glow_combo.setStyleSheet(self._combo_style())
        visual_layout.addRow("Glow Effect:", self.glow_combo)

        # Color selector
        self.color_combo = QComboBox()
        self.color_combo.addItems(["Blue", "Green", "Purple", "Red", "Cyan", "Yellow", "Orange", "Pink"])
        current_color = self.settings.get("gui_color", "blue")
        self.color_combo.setCurrentText(current_color.capitalize())
        self.color_combo.currentTextChanged.connect(self.on_color_changed)
        self.color_combo.setStyleSheet(self._combo_style())
        visual_layout.addRow("GUI Color:", self.color_combo)

        visual_group.setLayout(visual_layout)
        main_layout.addWidget(visual_group)

        # Animation Group
        animation_group = QGroupBox("Animation Style")
        animation_group.setStyleSheet(identity_group.styleSheet())
        animation_layout = QFormLayout()
        animation_layout.setSpacing(10)

        # Shape selector
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Sphere", "Icosahedron", "Humanoid"])
        current_shape = self.settings.get("animation_shape", "sphere")
        self.shape_combo.setCurrentText(current_shape.capitalize())
        self.shape_combo.currentTextChanged.connect(self.on_shape_changed)
        self.shape_combo.setStyleSheet(self._combo_style())
        animation_layout.addRow("Shape:", self.shape_combo)

        animation_group.setLayout(animation_layout)
        main_layout.addWidget(animation_group)

        # Buttons
        button_layout = QHBoxLayout()

        # Save & Close button
        save_btn = QPushButton("💾 Save & Close")
        save_btn.clicked.connect(self.save_and_close)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0096FF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0080DD;
            }
            QPushButton:pressed {
                background-color: #006ACC;
            }
        """)

        # Cancel button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #777;
            }
            QPushButton:pressed {
                background-color: #555;
            }
        """)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        main_layout.addLayout(button_layout)

        main_layout.addStretch()

        # Apply window style
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
        """)

    def _combo_style(self):
        """Get combo box stylesheet."""
        return """
            QComboBox {
                background-color: #2d2d44;
                color: white;
                border: 2px solid #0096FF;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 2px solid #00AAFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid white;
                width: 8px;
                height: 8px;
                border-top: none;
                border-left: none;
                transform: rotate(45deg);
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d44;
                color: white;
                selection-background-color: #0096FF;
                border: 2px solid #0096FF;
            }
        """

    def on_name_changed(self, name):
        """Handle name change."""
        self.settings.set("assistant_name", name)
        self.settings_changed.emit()

    def on_voice_changed(self, voice):
        """Handle voice accent change."""
        self.settings.set("voice_accent", voice)
        self.settings_changed.emit()

    def on_glow_changed(self, glow):
        """Handle glow effect change."""
        self.settings.set("glow_effect", glow.lower())
        self.settings_changed.emit()

    def on_color_changed(self, color):
        """Handle color change."""
        self.settings.set("gui_color", color.lower())
        self.settings_changed.emit()

    def on_shape_changed(self, shape):
        """Handle shape change."""
        self.settings.set("animation_shape", shape.lower())
        self.settings_changed.emit()

    def save_and_close(self):
        """Save settings and close window."""
        self.settings.save_settings()
        self.settings_changed.emit()
        self.close()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())
