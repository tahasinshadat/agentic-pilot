"""
3D Animated widget for Jarvis.
Supports sphere and wireframe icosahedron shapes.
Pulses when speaking, rotates continuously with smooth animations.
"""

import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QVector3D, QMatrix4x4
from gui.settings import get_settings


class AIAnimationWidget(QWidget):
    """
    3D animated widget that supports sphere and wireframe icosahedron.
    Shape is determined by settings.
    """

    def __init__(self, parent=None, color_rgb=(0, 150, 255)):
        super().__init__(parent)
        self.angle_y = 0
        self.angle_x = 0
        self.is_speaking = False
        self.pulse_angle = 0

        # Load settings to determine shape
        self.settings = get_settings()
        self.shape_type = self.settings.get("animation_shape", "sphere")

        # Create geometry
        self.sphere_points = self.create_sphere_points()
        self.icosahedron_vertices, self.icosahedron_edges = self.create_icosahedron_wireframe()

        # Color customization
        self.base_color = color_rgb  # RGB tuple

        # Smooth pulse interpolation
        self.target_pulse = 0.0
        self.current_pulse = 0.0
        self.pulse_smoothing = 0.15

        # Animation timer - 60 FPS for smoothness
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

        # Transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)

    def start_speaking_animation(self):
        """Activates the speaking animation (pulsing shape)."""
        self.is_speaking = True

    def stop_speaking_animation(self):
        """Deactivates the speaking animation."""
        self.is_speaking = False
        self.pulse_angle = 0
        self.target_pulse = 0.0
        self.update()

    def set_color(self, r, g, b):
        """Change the animation color."""
        self.base_color = (r, g, b)
        self.update()

    def reload_settings(self):
        """Reload settings and update shape and color if changed."""
        self.settings = get_settings()
        new_shape = self.settings.get("animation_shape", "sphere")

        # Update shape type
        if new_shape != self.shape_type:
            self.shape_type = new_shape
            print(f"[Animation] Shape changed to: {self.shape_type}")

        # Update color
        color_rgb = self.settings.get_color_rgb()
        self.base_color = color_rgb
        print(f"[Animation] Color updated to RGB{color_rgb}")

        self.update()

    def create_sphere_points(self, radius=40, num_points_lat=15, num_points_lon=30):
        """Creates 3D points on a sphere surface."""
        points = []
        for i in range(num_points_lat + 1):
            lat = math.pi * (-0.5 + i / num_points_lat)
            y = radius * math.sin(lat)
            xy_radius = radius * math.cos(lat)

            for j in range(num_points_lon):
                lon = 2 * math.pi * (j / num_points_lon)
                x = xy_radius * math.cos(lon)
                z = xy_radius * math.sin(lon)
                points.append(QVector3D(x, y, z))
        return points

    def create_icosahedron_wireframe(self, radius=45):
        """Creates wireframe icosahedron - clean 30 edges showing all 20 triangular faces."""
        # Golden ratio
        phi = (1 + math.sqrt(5)) / 2

        # 12 vertices of icosahedron
        vertices = [
            QVector3D(-1, phi, 0), QVector3D(1, phi, 0),
            QVector3D(-1, -phi, 0), QVector3D(1, -phi, 0),
            QVector3D(0, -1, phi), QVector3D(0, 1, phi),
            QVector3D(0, -1, -phi), QVector3D(0, 1, -phi),
            QVector3D(phi, 0, -1), QVector3D(phi, 0, 1),
            QVector3D(-phi, 0, -1), QVector3D(-phi, 0, 1),
        ]

        # Normalize vertices to sphere
        normalized = []
        for v in vertices:
            length = math.sqrt(v.x()**2 + v.y()**2 + v.z()**2)
            normalized.append(QVector3D(
                v.x() / length * radius,
                v.y() / length * radius,
                v.z() / length * radius
            ))

        # Define all 30 edges that form the 20 triangular faces
        edges = [
            # Top pentagon
            (0, 1), (0, 5), (0, 7), (0, 10), (0, 11),
            # Middle ring
            (1, 5), (5, 11), (11, 10), (10, 7), (7, 1),
            # Diagonal connections
            (1, 8), (5, 9), (11, 4), (10, 2), (7, 6),
            # Bottom pentagon
            (3, 2), (3, 4), (3, 6), (3, 8), (3, 9),
            # Lower ring
            (2, 4), (4, 9), (9, 8), (8, 6), (6, 2)
        ]

        return normalized, edges

    def update_animation(self):
        """Update rotation and pulse angles with smooth interpolation."""
        # Smooth rotation
        self.angle_y += 0.8
        self.angle_x += 0.2

        # Smooth pulse animation
        if self.is_speaking:
            self.pulse_angle += 0.25  # Smooth pulse speed
            if self.pulse_angle > math.pi * 2:
                self.pulse_angle -= math.pi * 2

            # Calculate target pulse
            self.target_pulse = (1 + math.sin(self.pulse_angle)) / 2
        else:
            self.target_pulse = 0.0

        # Smooth interpolation to target pulse
        self.current_pulse += (self.target_pulse - self.current_pulse) * self.pulse_smoothing

        if self.angle_y >= 360:
            self.angle_y -= 360
        if self.angle_x >= 360:
            self.angle_x -= 360

        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Draw the 3D shape with pulsing effect."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.transparent)

        w, h = self.width(), self.height()
        painter.translate(w / 2, h / 2)

        # Smooth pulse effect when speaking
        pulse_amplitude = 0.25  # 25% pulse
        pulse_factor = 1.0 + (self.current_pulse * pulse_amplitude)

        # Rotation matrices
        rotation_y = QMatrix4x4()
        rotation_y.rotate(self.angle_y, 0, 1, 0)
        rotation_x = QMatrix4x4()
        rotation_x.rotate(self.angle_x, 1, 0, 0)
        rotation = rotation_y * rotation_x

        # Draw based on shape type
        if self.shape_type == "icosahedron":
            self._draw_icosahedron_wireframe(painter, rotation, pulse_factor)
        else:  # Default to sphere
            self._draw_sphere(painter, rotation, pulse_factor)

    def _draw_sphere(self, painter, rotation, pulse_factor):
        """Draw the original sphere with points."""
        # Project 3D points to 2D
        projected_points = []
        for point in self.sphere_points:
            rotated_point = rotation.map(point)

            # Perspective projection
            z_factor = 200 / (200 + rotated_point.z())
            x = (rotated_point.x() * z_factor) * pulse_factor
            y = (rotated_point.y() * z_factor) * pulse_factor

            # Size and alpha based on Z depth
            size = (rotated_point.z() + 40) / 80
            alpha = int(50 + 205 * size)
            point_size = 1 + size * 2.5

            projected_points.append((x, y, point_size, alpha))

        # Sort by size for depth effect
        projected_points.sort(key=lambda p: p[2])

        # Draw points
        for x, y, point_size, alpha in projected_points:
            # Lighter when speaking, darker otherwise
            r, g, b = self.base_color
            if self.is_speaking:
                # Brighten color when speaking
                color = QColor(
                    min(int(r + (255 - r) * 0.4), 255),
                    min(int(g + (255 - g) * 0.4), 255),
                    min(int(b + (255 - b) * 0.4), 255),
                    alpha
                )
            else:
                color = QColor(r, g, b, alpha)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(x), int(y), int(point_size), int(point_size))

    def _draw_icosahedron_wireframe(self, painter, rotation, pulse_factor):
        """Draw wireframe icosahedron - only edges."""
        # Project vertices
        projected_vertices = []
        for vertex in self.icosahedron_vertices:
            rotated = rotation.map(vertex)

            # Perspective projection
            z_factor = 200 / (200 + rotated.z())
            x = (rotated.x() * z_factor) * pulse_factor
            y = (rotated.y() * z_factor) * pulse_factor

            projected_vertices.append((x, y, rotated.z()))

        # Draw edges
        r, g, b = self.base_color
        for v1_idx, v2_idx in self.icosahedron_edges:
            x1, y1, z1 = projected_vertices[v1_idx]
            x2, y2, z2 = projected_vertices[v2_idx]

            # Calculate depth for this edge (average Z)
            avg_z = (z1 + z2) / 2
            depth_factor = (avg_z + 45) / 90  # Normalize to 0-1

            # Alpha based on depth
            alpha = int(80 + 175 * depth_factor)

            # Line width based on depth (and pulse)
            base_width = 1.5 + depth_factor * 1.5
            if self.is_speaking:
                line_width = base_width * (1.0 + 0.3 * self.current_pulse)
            else:
                line_width = base_width

            # Color - brighter when speaking
            if self.is_speaking:
                color = QColor(
                    min(int(r + (255 - r) * 0.4), 255),
                    min(int(g + (255 - g) * 0.4), 255),
                    min(int(b + (255 - b) * 0.4), 255),
                    alpha
                )
            else:
                color = QColor(r, g, b, alpha)

            # Draw line
            pen = QPen(color)
            pen.setWidthF(line_width)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Draw all 12 vertices as small points
        for x, y, z in projected_vertices:
            depth_factor = (z + 45) / 90
            alpha = int(100 + 155 * depth_factor)
            point_size = 2 + depth_factor * 2

            if self.is_speaking:
                color = QColor(
                    min(int(r + (255 - r) * 0.5), 255),
                    min(int(g + (255 - g) * 0.5), 255),
                    min(int(b + (255 - b) * 0.5), 255),
                    alpha
                )
            else:
                color = QColor(r, g, b, alpha)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(x), int(y), int(point_size), int(point_size))
