"""
Floating assistant window that appears in bottom-right corner.
Shows when Jarvis is speaking or listening.
Features voice level visualization with glowing border.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property, Signal, QPoint
from PySide6.QtGui import QFont, QScreen
from gui.animation import AIAnimationWidget
from gui.audio_monitor import AudioLevelMonitor
from gui.settings import get_settings


class FloatingAssistantWindow(QWidget):
    """
    Small floating window in bottom-right corner.
    Shows Jarvis animation and status text.
    """

    closed = Signal()

    def __init__(self):
        super().__init__()

        # Load settings
        self.settings = get_settings()

        self.setup_window()
        self.setup_ui()
        self.setup_animations()
        self.is_visible = False

        # Audio level monitoring for voice visualization
        self.audio_monitor = AudioLevelMonitor()
        self.audio_monitor.level_changed.connect(self._update_border_glow)
        self.current_audio_level = 0.0

    def setup_window(self):
        """Configure window properties."""
        # Frameless, always on top, transparent background
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Size
        self.setFixedSize(280, 200)

        # Position in bottom-right corner
        self.position_window()

    def position_window(self):
        """Position window in bottom-right corner with padding."""
        screen = QScreen.availableGeometry(self.screen())
        padding = 20
        x = screen.width() - self.width() - padding
        y = screen.height() - self.height() - padding
        self.move(x, y)

    def setup_ui(self):
        """Create UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Container widget for styling
        self.container = QWidget()
        self.container.setObjectName("container")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(8)

        # Animation widget (with color from settings)
        color_rgb = self.settings.get_color_rgb()
        self.animation_widget = AIAnimationWidget(color_rgb=color_rgb)
        self.animation_widget.setMinimumHeight(120)
        self.animation_widget.setMaximumHeight(120)
        container_layout.addWidget(self.animation_widget)

        # Status label
        self.status_label = QLabel("Listening...")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        container_layout.addWidget(self.status_label)

        # Name label (from settings)
        assistant_name = self.settings.get_assistant_name().upper()
        self.name_label = QLabel(assistant_name)
        self.name_label.setObjectName("name_label")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setFont(QFont("Segoe UI", 8))
        container_layout.addWidget(self.name_label)

        layout.addWidget(self.container)

        # Initial styling (will be updated dynamically for glow)
        self._update_stylesheet(0.0)

        # Drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

    def setup_animations(self):
        """Setup slide-in/slide-out animations."""
        self.slide_animation = QPropertyAnimation(self, b"pos")
        self.slide_animation.setDuration(500)
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)

        # Opacity animation for fade in/out
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(400)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Start hidden
        self.setWindowOpacity(0.0)

    def show_window(self):
        """Slide in from bottom-right with smooth fade."""
        if self.is_visible:
            return

        self.is_visible = True

        # Get final position
        screen = QScreen.availableGeometry(self.screen())
        padding = 20
        final_x = screen.width() - self.width() - padding
        final_y = screen.height() - self.height() - padding

        # Start position (off-screen)
        start_x = screen.width()
        start_y = final_y

        # Show window
        self.show()
        self.move(start_x, start_y)

        # Animate slide in
        self.slide_animation.setStartValue(self.pos())
        self.slide_animation.setEndValue(QPoint(final_x, final_y))
        self.slide_animation.start()

        # Fade in animation
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()

    def hide_window(self):
        """Slide out to bottom-right with smooth fade."""
        if not self.is_visible:
            return

        self.is_visible = False

        # Get off-screen position
        screen = QScreen.availableGeometry(self.screen())
        final_x = screen.width()
        final_y = self.y()

        # Animate slide out
        self.slide_animation.setStartValue(self.pos())
        self.slide_animation.setEndValue(QPoint(final_x, final_y))
        self.slide_animation.finished.connect(self._hide_complete)
        self.slide_animation.start()

        # Fade out animation (synchronized with slide)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.start()

    def _hide_complete(self):
        """Called when hide animation completes."""
        self.hide()
        try:
            self.slide_animation.finished.disconnect(self._hide_complete)
        except:
            pass  # Already disconnected

    def set_status(self, status: str):
        """Update status label."""
        self.status_label.setText(status)

    def reload_settings(self):
        """Reload settings and update GUI."""
        self.settings = get_settings()
        # Update name label
        assistant_name = self.settings.get_assistant_name().upper()
        self.name_label.setText(assistant_name)
        # Update glow effect with current audio level
        self._update_stylesheet(self.current_audio_level)
        # Update animation widget color and shape
        self.animation_widget.set_color(*self.settings.get_color_rgb())
        self.animation_widget.reload_settings()
        print(f"[GUI] Settings reloaded: {self.settings.settings}")

    def _update_stylesheet(self, audio_level):
        """Update stylesheet with dynamic border glow based on audio level."""
        try:
            # Get color from settings
            r, g, b = self.settings.get_color_rgb()

            # Amplify audio level for more visible effect (boost by 3x)
            # This makes quieter sounds more visible
            amplified_level = min(audio_level * 3.0, 1.0)

            # Get glow effect type from settings
            glow_effect = self.settings.get("glow_effect", "inward")

            if glow_effect == "inward":
                # Inward glow - border gets brighter and thicker
                self._apply_inward_glow(r, g, b, amplified_level)
            else:
                # Outward glow - shadow expands outward
                self._apply_outward_glow(r, g, b, amplified_level)

        except (ValueError, TypeError) as e:
            print(f"[GUI] Error updating stylesheet with audio_level={audio_level}: {e}")
            # Fallback to default style with no glow
            r, g, b = self.settings.get_color_rgb()
            self.setStyleSheet(f"""
                QWidget#container {{
                    background-color: rgba(15, 20, 35, 220);
                    border: 2px solid rgba({r}, {g}, {b}, 180);
                    border-radius: 15px;
                }}
                QLabel#status_label {{
                    color: rgba({int(r*0.7)}, {int(g*0.7+50)}, {int(b*0.7+50)}, 255);
                    background: transparent;
                }}
                QLabel#name_label {{
                    color: rgba({int(r*0.8)}, {int(g*0.8+50)}, {int(b*0.8)}, 200);
                    background: transparent;
                }}
            """)

    def _apply_inward_glow(self, r, g, b, amplified_level):
        """Apply inward glow effect - border gets brighter and thicker."""
        # Calculate glow intensity (100 to 255 - wider range)
        base_alpha = 100
        glow_alpha = int(base_alpha + (255 - base_alpha) * amplified_level)

        # Calculate border width (2px to 6px - more noticeable)
        border_width = int(2 + 4 * amplified_level)

        # Calculate glow spread using box-shadow simulation
        glow_blur = int(10 + 40 * amplified_level)  # 10px to 50px blur

        # Make border color brighter with audio
        border_r = int(r + (255 - r) * amplified_level * 0.4)
        border_g = int(g + (255 - g) * amplified_level * 0.4)
        border_b = int(b + (255 - b) * amplified_level * 0.4)

        self.setStyleSheet(f"""
            QWidget#container {{
                background-color: rgba(15, 20, 35, 220);
                border: {border_width}px solid rgba({border_r}, {border_g}, {border_b}, {glow_alpha});
                border-radius: 15px;
            }}
            QLabel#status_label {{
                color: rgba({int(r*0.7)}, {int(g*0.7+50)}, {int(b*0.7+50)}, 255);
                background: transparent;
            }}
            QLabel#name_label {{
                color: rgba({int(r*0.8)}, {int(g*0.8+50)}, {int(b*0.8)}, 200);
                background: transparent;
            }}
        """)

        # Update shadow effect for subtle outer glow
        shadow = self.container.graphicsEffect()
        if shadow:
            shadow.setBlurRadius(20 + glow_blur * 2)
            from PySide6.QtGui import QColor
            shadow_alpha = int(100 + 155 * amplified_level)
            shadow_color = QColor(r, g, b, shadow_alpha)
            shadow.setColor(shadow_color)

    def _apply_outward_glow(self, r, g, b, amplified_level):
        """Apply outward glow effect - shadow expands and radiates outward."""
        # Keep border minimal but slightly brighten with audio
        border_width = 2
        border_brightness = int(150 + 105 * amplified_level)  # 150 to 255

        self.setStyleSheet(f"""
            QWidget#container {{
                background-color: rgba(15, 20, 35, 220);
                border: {border_width}px solid rgba({r}, {g}, {b}, {border_brightness});
                border-radius: 15px;
            }}
            QLabel#status_label {{
                color: rgba({int(r*0.7)}, {int(g*0.7+50)}, {int(b*0.7+50)}, 255);
                background: transparent;
            }}
            QLabel#name_label {{
                color: rgba({int(r*0.8)}, {int(g*0.8+50)}, {int(b*0.8)}, 200);
                background: transparent;
            }}
        """)

        # Dramatic outward shadow expansion
        shadow = self.container.graphicsEffect()
        if shadow:
            # Shadow expands very dramatically (15px to 150px)
            # Using a more aggressive curve for visibility
            shadow_blur = int(15 + 135 * (amplified_level ** 0.7))
            shadow.setBlurRadius(shadow_blur)

            # Shadow gets much brighter as it expands (more visible)
            from PySide6.QtGui import QColor
            # More aggressive alpha increase for better visibility
            shadow_alpha = int(120 + 135 * amplified_level)  # 120 to 255
            shadow_color = QColor(r, g, b, shadow_alpha)
            shadow.setColor(shadow_color)

            # Centered glow for radial effect
            shadow.setOffset(0, 0)

    def _update_border_glow(self, level):
        """Called when audio level changes."""
        # Validate level to prevent NaN/inf errors
        import math
        if not math.isfinite(level) or level < 0:
            level = 0.0
        elif level > 1.0:
            level = 1.0

        # Debug: Print audio level (remove after testing)
        # if level > 0.01:  # Only print if there's actual audio
        #     print(f"[GUI] Audio level: {level:.3f}")

        self.current_audio_level = level
        self._update_stylesheet(level)

    def set_listening(self):
        """Set to listening mode."""
        self.set_status("Listening...")
        self.animation_widget.stop_speaking_animation()
        self.show_window()

        # Start audio monitoring for voice visualization
        try:
            self.audio_monitor.start_monitoring()
        except Exception as e:
            print(f"[GUI] Could not start audio monitoring: {e}")

    def set_thinking(self):
        """Set to thinking mode."""
        self.set_status("Thinking...")
        self.animation_widget.stop_speaking_animation()

        # Stop audio monitoring
        self.audio_monitor.stop_monitoring()
        self._update_stylesheet(0.0)  # Reset glow

    def set_speaking(self):
        """Set to speaking mode."""
        self.set_status("Speaking...")
        self.animation_widget.start_speaking_animation()
        self.show_window()

        # Stop audio monitoring (Jarvis is speaking, not listening)
        self.audio_monitor.stop_monitoring()
        self._update_stylesheet(0.0)  # Reset glow

    def set_idle(self):
        """Set to idle mode and hide."""
        self.animation_widget.stop_speaking_animation()

        # Stop audio monitoring
        self.audio_monitor.stop_monitoring()
        self._update_stylesheet(0.0)  # Reset glow

        QTimer.singleShot(2000, self.hide_window)  # Hide after 2 seconds

    def closeEvent(self, event):
        """Handle window close."""
        self.audio_monitor.cleanup()
        self.closed.emit()
        event.accept()
