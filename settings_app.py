"""
Jarvis Settings & Test Application
Futuristic control hub for configuring and testing the Jarvis assistant.

Usage:
    python settings_app.py
"""

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QComboBox,
    QGroupBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
)

from gui.floating_window import FloatingAssistantWindow
from gui.settings import get_settings


class SettingsApp(QMainWindow):
    """
    Jarvis Settings & Test Manager

    Layout:
        - Top: Futuristic header with title, tagline, AI orb & state indicator.
        - Left: Glass panel for identity / visual configuration.
        - Right: Glass panel for test controls & system status.

    Visual style:
        - Dark, layered background with neon cyan / blue / purple accents.
        - Panels feel like holographic cards.
        - Buttons mimic game/HUD controls.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIS · Control Hub")
        self.setGeometry(100, 100, 1000, 620)
        self.setMinimumSize(960, 580)

        # Core models
        self.settings = get_settings()

        # Live preview (existing floating Jarvis window)
        self.preview_window = FloatingAssistantWindow()
        self.preview_window.show()
        self.preview_window.set_listening()

        # Internal
        self.ai_state_label = None
        self.status_label = None
        self.config_display = None

        self._setup_ui()

    # -------------------------------------------------------------------------
    # UI SETUP
    # -------------------------------------------------------------------------

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setSpacing(18)
        root.setContentsMargins(26, 22, 26, 22)

        header = self._create_header()
        body = self._create_body()

        root.addWidget(header)
        root.addLayout(body)

        self._apply_global_style()

    def _create_header(self) -> QWidget:
        """
        Futuristic top bar:
            - Left: Title + subtitle
            - Center: Thin divider / HUD line
            - Right: AI orb + dynamic state label
        """
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 4)

        # Left: Title
        title_block = QWidget()
        title_layout = QVBoxLayout(title_block)
        title_layout.setSpacing(2)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("JARVIS CONTROL HUB")
        title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 0.15em;
            color: #38bdf8;
            """
        )
        title_layout.addWidget(title)

        subtitle = QLabel("Configure identity, visuals & behavior · Live-synced with your AI assistant")
        subtitle.setStyleSheet(
            """
            font-size: 10px;
            color: #9ca3af;
            """
        )
        title_layout.addWidget(subtitle)

        layout.addWidget(title_block, stretch=3, alignment=Qt.AlignVCenter)

        # Middle: HUD line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: rgba(56,189,248,0.22);")
        layout.addWidget(line, stretch=2, alignment=Qt.AlignVCenter)

        # Right: AI orb + state
        orb_container = QWidget()
        orb_layout = QHBoxLayout(orb_container)
        orb_layout.setSpacing(8)
        orb_layout.setContentsMargins(0, 0, 0, 0)

        orb = QLabel()
        orb.setFixedSize(30, 30)
        orb.setObjectName("aiOrb")

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(28)
        glow.setColor(Qt.cyan)
        glow.setOffset(0, 0)
        orb.setGraphicsEffect(glow)

        self.ai_state_label = QLabel("ONLINE · LISTENING")
        self.ai_state_label.setStyleSheet(
            """
            font-size: 9px;
            color: #a5b4fc;
            """
        )

        orb_layout.addWidget(orb, alignment=Qt.AlignRight | Qt.AlignVCenter)
        orb_layout.addWidget(self.ai_state_label, alignment=Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(orb_container, stretch=1, alignment=Qt.AlignRight | Qt.AlignVCenter)

        # Simple pulse animation for the orb
        self._start_orb_pulse(orb)

        return header

    def _create_body(self) -> QHBoxLayout:
        """
        Two main glass panels:
            - Left: Settings
            - Right: Test controls
        """
        body_layout = QHBoxLayout()
        body_layout.setSpacing(18)

        settings_panel = self._create_settings_panel()
        controls_panel = self._create_test_panel()

        body_layout.addWidget(settings_panel, stretch=2)
        body_layout.addWidget(controls_panel, stretch=1)

        return body_layout

    def _apply_global_style(self):
        """
        Global futuristic style:
            - Layered gradient background
            - Neon outlines
            - Glass panels (semi-transparent)
        """
        self.setStyleSheet(
            """
            * {
                font-family: "Segoe UI", "SF Pro Text", "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
            }

            QMainWindow {
                background-color: #01030a;
                background-image: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #020817,
                    stop:0.35 #020817,
                    stop:1 #020617
                );
            }

            QWidget {
                background-color: transparent;
                color: #e5e7eb;
            }

            #GlassPanel {
                background-color: rgba(6, 12, 30, 0.96);
                border-radius: 18px;
                border: 1px solid rgba(56, 189, 248, 0.18);
            }

            #GlassPanelRight {
                background-color: rgba(4, 7, 20, 0.98);
                border-radius: 18px;
                border: 1px solid rgba(168, 85, 247, 0.26);
            }

            QGroupBox {
                font-size: 11px;
                font-weight: 600;
                color: #9ca3af;
                border: 1px solid rgba(56, 189, 248, 0.20);
                border-radius: 12px;
                margin-top: 14px;
                padding: 12px;
                background-color: rgba(5, 10, 25, 0.98);
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: #38bdf8;
                font-size: 10px;
                letter-spacing: 0.08em;
            }

            QLabel {
                font-size: 10px;
            }

            QComboBox {
                background-color: rgba(3, 7, 18, 0.98);
                color: #e5e7eb;
                border: 1px solid rgba(129, 140, 248, 0.9);
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 10px;
            }

            QComboBox:hover {
                border: 1px solid #38bdf8;
            }

            QComboBox::drop-down {
                border: none;
                width: 16px;
            }

            QComboBox QAbstractItemView {
                background-color: #020817;
                color: #e5e7eb;
                selection-background-color: #1d4ed8;
                border: 1px solid #38bdf8;
            }

            QPushButton {
                font-size: 11px;
                font-weight: 600;
            }

            /* AI Orb */
            #aiOrb {
                border-radius: 15px;
                background-color: qradialgradient(
                    cx:0.3, cy:0.3, radius:0.9,
                    fx:0.3, fy:0.3,
                    stop:0 #e0f2fe,
                    stop:0.3 #38bdf8,
                    stop:0.7 #1d4ed8,
                    stop:1 transparent
                );
            }
            """
        )

    # -------------------------------------------------------------------------
    # LEFT PANEL: SETTINGS
    # -------------------------------------------------------------------------

    def _create_settings_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("GlassPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        # Panel header
        header = QLabel("ASSISTANT PROFILE")
        header.setStyleSheet(
            """
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.18em;
            color: #6ee7ff;
            """
        )
        layout.addWidget(header)

        caption = QLabel("Define how Jarvis appears, sounds, and visualizes itself.")
        caption.setStyleSheet("font-size: 9px; color: #9ca3af;")
        layout.addWidget(caption)

        # Identity Group
        identity_group = QGroupBox("IDENTITY")
        identity_layout = QFormLayout()
        identity_layout.setSpacing(8)

        name_label = self._field_label("Display Name")
        self.name_combo = self._create_combo(
            ["Jarvis", "Sarah"],
            self.settings.get("assistant_name", "Jarvis"),
        )
        self.name_combo.currentTextChanged.connect(self.on_name_changed)
        identity_layout.addRow(name_label, self.name_combo)

        voice_label = self._field_label("Voice Accent")
        self.voice_combo = self._create_combo(
            ["English", "Australian", "British", "Indian", "African"],
            self.settings.get("voice_accent", "English"),
        )
        self.voice_combo.currentTextChanged.connect(self.on_voice_changed)
        identity_layout.addRow(voice_label, self.voice_combo)

        identity_group.setLayout(identity_layout)
        layout.addWidget(identity_group)

        # Visual Group
        visual_group = QGroupBox("VISUAL SIGNATURE")
        visual_layout = QFormLayout()
        visual_layout.setSpacing(8)

        glow_label = self._field_label("Glow Mode")
        self.glow_combo = self._create_combo(
            ["Inward", "Outward"],
            self._cap(self.settings.get("glow_effect", "inward")),
        )
        self.glow_combo.currentTextChanged.connect(self.on_glow_changed)
        visual_layout.addRow(glow_label, self.glow_combo)

        color_label = self._field_label("Primary Accent")
        self.color_combo = self._create_combo(
            ["Blue", "Cyan", "Purple", "Neon Green", "Red", "Orange", "Pink"],
            self._map_color_value(self.settings.get("gui_color", "blue")),
        )
        self.color_combo.currentTextChanged.connect(self.on_color_changed)
        visual_layout.addRow(color_label, self.color_combo)

        shape_label = self._field_label("Orb Geometry")
        self.shape_combo = self._create_combo(
            ["Sphere", "Icosahedron", "Humanoid"],
            self._cap(self.settings.get("animation_shape", "sphere")),
        )
        self.shape_combo.currentTextChanged.connect(self.on_shape_changed)
        visual_layout.addRow(shape_label, self.shape_combo)

        visual_group.setLayout(visual_layout)
        layout.addWidget(visual_group)

        # Config summary / system log style
        self.config_display = QLabel()
        self.config_display.setWordWrap(True)
        self.config_display.setStyleSheet(
            """
            font-family: "JetBrains Mono", "Consolas", monospace;
            font-size: 9px;
            color: #9ca3af;
            background-color: rgba(2, 6, 23, 0.98);
            border-radius: 10px;
            border: 1px solid rgba(56, 189, 248, 0.26);
            padding: 9px 10px;
            """
        )
        self._update_config_display()
        layout.addWidget(self.config_display)

        layout.addStretch()
        return panel

    # -------------------------------------------------------------------------
    # RIGHT PANEL: TEST CONTROLS
    # -------------------------------------------------------------------------

    def _create_test_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("GlassPanelRight")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QLabel("STATE SIMULATION")
        header.setStyleSheet(
            """
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.18em;
            color: #c4b5fd;
            """
        )
        layout.addWidget(header)

        caption = QLabel("Trigger Jarvis UI states and observe behavior in the floating preview.")
        caption.setWordWrap(True)
        caption.setStyleSheet("font-size: 9px; color: #9ca3af;")
        layout.addWidget(caption)

        # Buttons
        layout.addWidget(
            self._create_state_button("LISTENING", "#22c55e", self.test_listening)
        )
        layout.addWidget(
            self._create_state_button("THINKING", "#38bdf8", self.test_thinking)
        )
        layout.addWidget(
            self._create_state_button("SPEAKING", "#6366f1", self.test_speaking)
        )
        layout.addWidget(
            self._create_state_button("IDLE", "#6b7280", self.test_idle)
        )

        # Auto test button
        auto_btn = QPushButton("RUN NEURAL CYCLE")
        auto_btn.clicked.connect(self.run_auto_test)
        auto_btn.setCursor(Qt.PointingHandCursor)
        auto_btn.setStyleSheet(
            """
            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a855f7,
                    stop:1 #38bdf8
                );
                color: #f9fafb;
                border-radius: 10px;
                padding: 9px 14px;
                font-weight: 700;
                letter-spacing: 0.08em;
            }
            QPushButton:hover {
                border: 1px solid rgba(148, 163, 253, 0.9);
            }
            QPushButton:pressed {
                background-color: #4c1d95;
            }
            """
        )
        layout.addWidget(auto_btn)

        # Status / log
        self.status_label = QLabel("Ready. Jarvis systems nominal.")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            """
            font-family: "JetBrains Mono", "Consolas", monospace;
            font-size: 9px;
            padding: 8px;
            margin-top: 6px;
            border-radius: 9px;
            background-color: rgba(2,6,23,0.98);
            border: 1px solid rgba(75,85,99,0.85);
            color: #9ca3af;
            """
        )
        layout.addWidget(self.status_label)

        layout.addStretch()
        return panel

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def _create_combo(self, items, current) -> QComboBox:
        combo = QComboBox()
        combo.addItems(items)
        if current in items:
            combo.setCurrentText(current)
        combo.setCursor(Qt.PointingHandCursor)
        return combo

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(
            """
            font-size: 8px;
            font-weight: 600;
            letter-spacing: 0.12em;
            color: #6b7280;
            """
        )
        return lbl

    def _create_state_button(self, text: str, color: str, callback) -> QPushButton:
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: rgba(1, 6, 18, 0.98);
                color: {color};
                border-radius: 10px;
                padding: 9px 12px;
                border: 1px solid {color};
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: rgba(10, 18, 35, 0.98);
            }}
            QPushButton:pressed {{
                background-color: {color};
                color: #020817;
            }}
            """
        )
        return btn

    @staticmethod
    def _cap(value: str) -> str:
        return (value or "").capitalize()

    @staticmethod
    def _map_color_value(stored: str) -> str:
        """Map old simple values to nicer labels without breaking behavior."""
        if not stored:
            return "Blue"
        v = stored.lower()
        if v == "cyan":
            return "Cyan"
        if v in ("green", "neon", "neon_green", "neongreen"):
            return "Neon Green"
        return v.capitalize()

    def _start_orb_pulse(self, orb_label: QLabel):
        """Subtle pulsing via alternating stylesheet (fake 'breathing' effect)."""
        base = (
            """
            border-radius: 15px;
            background-color: qradialgradient(
                cx:0.3, cy:0.3, radius:0.9,
                fx:0.3, fy:0.3,
                stop:0 #e0f2fe,
                stop:0.3 #38bdf8,
                stop:0.7 #1d4ed8,
                stop:1 transparent
            );
            """
        )
        alt = (
            """
            border-radius: 15px;
            background-color: qradialgradient(
                cx:0.4, cy:0.4, radius:1.0,
                fx:0.4, fy:0.4,
                stop:0 #bae6fd,
                stop:0.35 #22c55e,
                stop:0.8 #1d4ed8,
                stop:1 transparent
            );
            """
        )

        def toggle():
            orb_label.setStyleSheet(alt if orb_label.property("state") != 1 else base)
            orb_label.setProperty("state", 0 if orb_label.property("state") == 1 else 1)

        timer = QTimer(self)
        timer.timeout.connect(toggle)
        timer.start(900)

    # -------------------------------------------------------------------------
    # CONFIG DISPLAY
    # -------------------------------------------------------------------------

    def _update_config_display(self):
        self.config_display.setText(
            "CONFIG SNAPSHOT\n"
            "────────────────\n"
            f"assistant_name      = {self.settings.get_assistant_name()}\n"
            f"voice_accent        = {self.settings.get('voice_accent')}\n"
            f"gui_color           = {self.settings.get('gui_color')}\n"
            f"glow_effect         = {self.settings.get('glow_effect')}\n"
            f"animation_shape     = {self.settings.get('animation_shape')}\n\n"
            "Storage: config/settings.json"
        )

    # -------------------------------------------------------------------------
    # SETTINGS CHANGE HANDLERS
    # -------------------------------------------------------------------------

    def on_name_changed(self, name: str):
        self.settings.set("assistant_name", name)
        self.preview_window.reload_settings()
        self._update_config_display()

    def on_voice_changed(self, voice: str):
        self.settings.set("voice_accent", voice)
        self._update_config_display()

    def on_glow_changed(self, glow: str):
        self.settings.set("glow_effect", glow.lower())
        self.preview_window.reload_settings()
        self._update_config_display()

    def on_color_changed(self, color: str):
        # Map display label back to simple key
        key = color.lower().replace(" ", "_")
        if key == "neon_green":
            key = "green"
        self.settings.set("gui_color", key)
        self.preview_window.reload_settings()
        self._update_config_display()

    def on_shape_changed(self, shape: str):
        self.settings.set("animation_shape", shape.lower())
        self.preview_window.reload_settings()
        self._update_config_display()

    # -------------------------------------------------------------------------
    # TEST CONTROL HANDLERS
    # -------------------------------------------------------------------------

    def _set_ai_state(self, label: str):
        if self.ai_state_label:
            self.ai_state_label.setText(label)

    def test_listening(self):
        self.status_label.setText("Listening mode engaged. Awaiting input...")
        self._set_ai_state("ONLINE · LISTENING")
        self.preview_window.set_listening()

    def test_thinking(self):
        self.status_label.setText("Thinking mode engaged. Processing signals...")
        self._set_ai_state("ONLINE · THINKING")
        self.preview_window.set_thinking()

    def test_speaking(self):
        self.status_label.setText("Speaking mode engaged. Rendering response...")
        self._set_ai_state("ONLINE · SPEAKING")
        self.preview_window.set_speaking()

    def test_idle(self):
        self.status_label.setText("Idle mode engaged. Preview will auto-hide.")
        self._set_ai_state("STANDBY · IDLE")
        self.preview_window.set_idle()

    def run_auto_test(self):
        self.status_label.setText("Running neural state cycle...")
        self._set_ai_state("ONLINE · TESTING")

        QTimer.singleShot(0, lambda: (self.preview_window.set_listening(),
                                      self.status_label.setText("Phase 1/4: LISTENING (4s)")))
        QTimer.singleShot(4000, lambda: (self.preview_window.set_thinking(),
                                         self.status_label.setText("Phase 2/4: THINKING (4s)")))
        QTimer.singleShot(8000, lambda: (self.preview_window.set_speaking(),
                                         self.status_label.setText("Phase 3/4: SPEAKING (4s)")))
        QTimer.singleShot(12000, lambda: (self.preview_window.set_idle(),
                                          self.status_label.setText("Phase 4/4: IDLE (3s)")))
        QTimer.singleShot(15000, lambda: (
            self.status_label.setText("Neural cycle complete. All visual states verified."),
            self._set_ai_state("ONLINE · LISTENING"),
        ))

    # -------------------------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------------------------

    def closeEvent(self, event):
        if self.preview_window:
            self.preview_window.close()
        event.accept()


def main():
    print("=" * 70)
    print("  JARVIS · CONTROL HUB")
    print("=" * 70)
    print("Futuristic settings & test console for your AI assistant.")
    print("Settings saved to: config/settings.json")
    print("Changes apply when Jarvis starts.")
    print("=" * 70)

    app = QApplication(sys.argv)
    # Optional: slight font hinting
    app.setFont(QFont("Segoe UI", 9))
    window = SettingsApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()