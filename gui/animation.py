"""
3D Animated widget for Jarvis / SARAH.

Modes:
- "sphere"      : pulsing point sphere (QPainter)
- "icosahedron" : wireframe icosahedron (QPainter)
- "humanoid"    : baked PCA hologram head (Three.js via QWebEngineView)

Features:
- Pulses when speaking (all modes)
- Continuous rotation (all modes)
- Deep blue-black background
- Color customizable via set_color() / reload_settings()
"""

import math
import json

from PySide6.QtCore import Qt, QTimer, QUrl, QSize
from PySide6.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QPen,
    QVector3D,
    QMatrix4x4,
)
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView

from gui.settings import get_settings
from gui.humanoid_data import BASE_POINTS, BAND_POINTS


# ============================================================
# Helpers
# ============================================================

def _rgb_to_hex(rgb):
    r, g, b = rgb
    r = max(0, min(int(r), 255))
    g = max(0, min(int(g), 255))
    b = max(0, min(int(b), 255))
    return f"#{r:02x}{g:02x}{b:02x}"


def build_html(base_points, band_points, base_color_rgb) -> str:
    """
    Build the Three.js hologram head scene as inline HTML/JS.
    Uses baked BASE_POINTS / BAND_POINTS (no h5py at runtime).
    Head is lowered so the neck lines up behind the UI "Listening..." text.
    """
    base_json = json.dumps(base_points, separators=(",", ":"))
    band_json = json.dumps(band_points, separators=(",", ":"))
    base_color_hex = _rgb_to_hex(base_color_rgb)

    # Important: double {{ }} for JS object literals inside f-string.
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #020814;
        }}
        canvas {{
            display: block;
        }}
    </style>
</head>
<body>
<script type="module">
    import * as THREE from "https://unpkg.com/three@0.164.0/build/three.module.js?module";
    import {{ OrbitControls }} from "https://unpkg.com/three@0.164.0/examples/jsm/controls/OrbitControls.js?module";

    const basePoints = {base_json};
    const bandPoints = {band_json};

    const jarvisState = {{
        speaking: false,
        pulse: 0.0,
        color: "{base_color_hex}"
    }};

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x020814);

    const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.01, 100.0);
    camera.position.set(0.0, 0.0, 2.0);

    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setPixelRatio(window.devicePixelRatio || 1);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x020814, 1.0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    document.body.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.enablePan = false;
    controls.enableZoom = false;
    controls.enabled = false;

    const ambient = new THREE.AmbientLight(0x8899ff, 0.7);
    scene.add(ambient);

    const pinkLight = new THREE.PointLight(0xff88ff, 1.0, 6.0);
    pinkLight.position.set(1.6, 1.4, 2.0);
    scene.add(pinkLight);

    const cyanLight = new THREE.PointLight(0x66ffff, 0.8, 6.0);
    cyanLight.position.set(-1.8, 0.4, -2.0);
    scene.add(cyanLight);

    const headGroup = new THREE.Group();
    scene.add(headGroup);

    function createPointsCloud(points, size, opacity) {{
        const count = points.length;
        const positions = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {{
            const p = points[i];
            positions[i * 3 + 0] = p[0];
            positions[i * 3 + 1] = p[1];
            positions[i * 3 + 2] = p[2];
        }}
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        const material = new THREE.PointsMaterial({{
            size: size,
            transparent: true,
            opacity: opacity,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        }});
        material.color = new THREE.Color(jarvisState.color);
        return new THREE.Points(geometry, material);
    }}

    const baseCloud = createPointsCloud(basePoints, 0.010, 0.22);
    const bandCloud = createPointsCloud(bandPoints, 0.014, 0.30);
    headGroup.add(baseCloud);
    headGroup.add(bandCloud);

    const HEAD_SCALE_BASE = 0.6;
    const HEAD_BASE_Y = -0.10;  // lowered so neck sits behind UI label
    headGroup.scale.set(HEAD_SCALE_BASE, HEAD_SCALE_BASE, HEAD_SCALE_BASE);
    headGroup.position.y = HEAD_BASE_Y;

    window.setJarvisState = function(update) {{
        if (!update) return;
        if (typeof update.speaking === "boolean") {{
            jarvisState.speaking = update.speaking;
        }}
        if (typeof update.pulse === "number") {{
            jarvisState.pulse = update.pulse;
        }}
        if (typeof update.color === "string") {{
            jarvisState.color = update.color;
            const c = new THREE.Color(update.color);
            baseCloud.material.color.copy(c);
            bandCloud.material.color.copy(c);
        }}
    }};

    const clock = new THREE.Clock();

    function animate() {{
        const t = clock.getElapsedTime();

        headGroup.rotation.y = t * 0.7;

        const speakingPulse = jarvisState.speaking
            ? 1.0 + 0.08 * Math.sin(t * 9.0)
            : 1.0;
        const externalPulse = 1.0 + 0.25 * jarvisState.pulse;
        const finalScale = HEAD_SCALE_BASE * speakingPulse * externalPulse;
        headGroup.scale.set(finalScale, finalScale, finalScale);

        const glow = 0.18 + 0.40 * jarvisState.pulse;
        baseCloud.material.opacity = 0.16 + glow * 0.6;
        bandCloud.material.opacity = 0.24 + glow * 0.7;

        controls.update();
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
    }}

    animate();

    window.addEventListener("resize", () => {{
        const w = window.innerWidth || 1;
        const h = window.innerHeight || 1;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
    }});
</script>
</body>
</html>
"""


# ============================================================
# AIAnimationWidget
# ============================================================

class AIAnimationWidget(QWidget):
    """
    Drop-in animated widget.

    Modes controlled by settings["animation_shape"]:
      - "sphere"
      - "icosahedron"
      - "humanoid"   (baked hologram head)

    Public API:
      - start_speaking_animation()
      - stop_speaking_animation()
      - set_color(r, g, b)
      - reload_settings()
    """

    def __init__(self, parent=None, color_rgb=(255, 200, 0)):
        super().__init__(parent)

        self.settings = get_settings()
        self.shape_type = str(
            self.settings.get("animation_shape", "sphere")
        ).lower()

        # Shared animation state
        self.is_speaking = False
        self.pulse_angle = 0.0
        self.target_pulse = 0.0
        self.current_pulse = 0.0
        self.pulse_smoothing = 0.15

        # Rotation (for painter modes)
        self.angle_y = 0.0
        self.angle_x = 0.0

        # Color (default; can be overridden by settings)
        self.base_color = color_rgb
        if hasattr(self.settings, "get_color_rgb"):
            try:
                self.base_color = self.settings.get_color_rgb()
            except Exception:
                pass

        # Painter geometry
        self.sphere_points = self._create_sphere_points()
        self.icosahedron_vertices, self.icosahedron_edges = self._create_icosahedron_wireframe()

        # Humanoid / web state
        self.head_loaded = False
        self._load_error = None
        self.page_ready = False

        self.webview = QWebEngineView(self)
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.setStyleSheet("background: #020814; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.webview)

        # Initialize mode-specific visuals
        self._setup_humanoid_if_needed()
        self._apply_shape_mode()

        # Timer (~60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

        # Background matches holo theme for all modes
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #020814; border: none;")

    # ===========================
    # Public control API
    # ===========================

    def start_speaking_animation(self):
        self.is_speaking = True
        if self.shape_type == "humanoid":
            self._push_state_to_js()

    def stop_speaking_animation(self):
        self.is_speaking = False
        self.pulse_angle = 0.0
        self.target_pulse = 0.0
        if self.shape_type == "humanoid":
            self._push_state_to_js()

    def set_color(self, r, g, b):
        self.base_color = (r, g, b)
        if self.shape_type == "humanoid":
            self._push_state_to_js(force=True)
        else:
            self.update()

    def reload_settings(self):
        self.settings = get_settings()

        # Color from settings (if available)
        if hasattr(self.settings, "get_color_rgb"):
            try:
                self.base_color = self.settings.get_color_rgb()
            except Exception:
                pass

        # Shape mode
        new_shape = str(self.settings.get("animation_shape", self.shape_type)).lower()
        if new_shape not in ("sphere", "icosahedron", "humanoid"):
            new_shape = "sphere"

        if new_shape != self.shape_type:
            self.shape_type = new_shape
            self._apply_shape_mode()

        if self.shape_type == "humanoid":
            self._push_state_to_js(force=True)
        else:
            self.update()

    # ===========================
    # Internal: geometry (painter)
    # ===========================

    def _create_sphere_points(self, radius=40, num_points_lat=15, num_points_lon=30):
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

    def _create_icosahedron_wireframe(self, radius=45):
        phi = (1 + math.sqrt(5)) / 2

        vertices = [
            QVector3D(-1, phi, 0), QVector3D(1, phi, 0),
            QVector3D(-1, -phi, 0), QVector3D(1, -phi, 0),
            QVector3D(0, -1, phi), QVector3D(0, 1, phi),
            QVector3D(0, -1, -phi), QVector3D(0, 1, -phi),
            QVector3D(phi, 0, -1), QVector3D(phi, 0, 1),
            QVector3D(-phi, 0, -1), QVector3D(-phi, 0, 1),
        ]

        normalized = []
        for v in vertices:
            length = math.sqrt(v.x() ** 2 + v.y() ** 2 + v.z() ** 2)
            normalized.append(QVector3D(
                v.x() / length * radius,
                v.y() / length * radius,
                v.z() / length * radius
            ))

        edges = [
            (0, 1), (0, 5), (0, 7), (0, 10), (0, 11),
            (1, 5), (5, 11), (11, 10), (10, 7), (7, 1),
            (1, 8), (5, 9), (11, 4), (10, 2), (7, 6),
            (3, 2), (3, 4), (3, 6), (3, 8), (3, 9),
            (2, 4), (4, 9), (9, 8), (8, 6), (6, 2)
        ]
        return normalized, edges

    # ===========================
    # Internal: mode handling
    # ===========================

    def _setup_humanoid_if_needed(self):
        """Prepare HTML for humanoid mode once, using baked data."""
        if self.head_loaded or self._load_error:
            return

        try:
            html = build_html(BASE_POINTS, BAND_POINTS, self.base_color)
            self.webview.setHtml(html, QUrl("about:blank"))
            self.webview.loadFinished.connect(self._on_page_loaded)
            self.head_loaded = True
        except Exception as e:
            self._load_error = str(e)
            error_html = f"""
            <html><body style="margin:0;padding:8px;
                   background:#020814;color:#ff88aa;
                   font-family:system-ui;font-size:10px;">
            <b>Hologram avatar error</b><br/>
            <code>{self._load_error}</code>
            </body></html>
            """
            self.webview.setHtml(error_html, QUrl("about:blank"))
            self.webview.show()

    def _apply_shape_mode(self):
        """Show/hide WebEngine vs painter depending on mode."""
        if self.shape_type == "humanoid":
            self._setup_humanoid_if_needed()
            self.webview.show()
        else:
            self.webview.hide()  # painter uses this widget surface
        self.update()

    # ===========================
    # Qt overrides
    # ===========================

    def sizeHint(self) -> QSize:
        return QSize(260, 260)

    def paintEvent(self, event):
        # Humanoid is rendered fully by QWebEngineView
        if self.shape_type == "humanoid":
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#020814"))

        w, h = self.width(), self.height()
        painter.translate(w / 2, h / 2)

        # Pulse factor
        pulse_amplitude = 0.25
        pulse_factor = 1.0 + (self.current_pulse * pulse_amplitude)

        # Rotation
        rotation_y = QMatrix4x4()
        rotation_y.rotate(self.angle_y, 0, 1, 0)
        rotation_x = QMatrix4x4()
        rotation_x.rotate(self.angle_x, 1, 0, 0)
        rotation = rotation_y * rotation_x

        if self.shape_type == "icosahedron":
            self._draw_icosahedron_wireframe(painter, rotation, pulse_factor)
        else:  # default sphere
            self._draw_sphere(painter, rotation, pulse_factor)

    # ===========================
    # Painter mode drawing
    # ===========================

    def _draw_sphere(self, painter, rotation, pulse_factor):
        projected_points = []
        for point in self.sphere_points:
            rotated_point = rotation.map(point)

            z_factor = 200 / (200 + rotated_point.z())
            x = (rotated_point.x() * z_factor) * pulse_factor
            y = (rotated_point.y() * z_factor) * pulse_factor

            size = (rotated_point.z() + 40) / 80
            alpha = int(50 + 205 * size)
            point_size = 1 + size * 2.5
            projected_points.append((x, y, point_size, alpha))

        projected_points.sort(key=lambda p: p[2])

        r, g, b = self.base_color
        for x, y, point_size, alpha in projected_points:
            if self.is_speaking:
                color = QColor(
                    min(int(r + (255 - r) * 0.4), 255),
                    min(int(g + (255 - g) * 0.4), 255),
                    min(int(b + (255 - b) * 0.4), 255),
                    alpha,
                )
            else:
                color = QColor(r, g, b, alpha)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(x), int(y), int(point_size), int(point_size))

    def _draw_icosahedron_wireframe(self, painter, rotation, pulse_factor):
        projected_vertices = []
        for vertex in self.icosahedron_vertices:
            rotated = rotation.map(vertex)
            z_factor = 200 / (200 + rotated.z())
            x = (rotated.x() * z_factor) * pulse_factor
            y = (rotated.y() * z_factor) * pulse_factor
            projected_vertices.append((x, y, rotated.z()))

        r, g, b = self.base_color

        # Edges
        for v1_idx, v2_idx in self.icosahedron_edges:
            x1, y1, z1 = projected_vertices[v1_idx]
            x2, y2, z2 = projected_vertices[v2_idx]
            avg_z = (z1 + z2) / 2
            depth_factor = (avg_z + 45) / 90

            alpha = int(80 + 175 * depth_factor)
            base_width = 1.5 + depth_factor * 1.5
            line_width = base_width * (1.0 + 0.3 * self.current_pulse) if self.is_speaking else base_width

            if self.is_speaking:
                color = QColor(
                    min(int(r + (255 - r) * 0.4), 255),
                    min(int(g + (255 - g) * 0.4), 255),
                    min(int(b + (255 - b) * 0.4), 255),
                    alpha,
                )
            else:
                color = QColor(r, g, b, alpha)

            pen = QPen(color)
            pen.setWidthF(line_width)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Vertices
        for x, y, z in projected_vertices:
            depth_factor = (z + 45) / 90
            alpha = int(100 + 155 * depth_factor)
            point_size = 2 + depth_factor * 2

            if self.is_speaking:
                color = QColor(
                    min(int(r + (255 - r) * 0.5), 255),
                    min(int(g + (255 - g) * 0.5), 255),
                    min(int(b + (255 - b) * 0.5), 255),
                    alpha,
                )
            else:
                color = QColor(r, g, b, alpha)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(x), int(y), int(point_size), int(point_size))

    # ===========================
    # Animation driver
    # ===========================

    def _on_page_loaded(self, ok: bool):
        self.page_ready = ok
        if ok:
            self._push_state_to_js(force=True)

    def update_animation(self):
        # Pulse state (shared)
        if self.is_speaking:
            self.pulse_angle += 0.25
            if self.pulse_angle > math.tau:
                self.pulse_angle -= math.tau
            self.target_pulse = (1.0 + math.sin(self.pulse_angle)) / 2.0
        else:
            self.target_pulse = 0.0

        self.current_pulse += (self.target_pulse - self.current_pulse) * self.pulse_smoothing

        if self.shape_type == "humanoid":
            self._push_state_to_js()
        else:
            # Rotate painter shapes
            self.angle_y = (self.angle_y + 0.8) % 360
            self.angle_x = (self.angle_x + 0.2) % 360
            self.update()

    # ===========================
    # JS bridge for humanoid
    # ===========================

    def _push_state_to_js(self, force: bool = False):
        if not (self.shape_type == "humanoid" and self.page_ready):
            return

        color_hex = _rgb_to_hex(self.base_color)
        speaking_str = "true" if self.is_speaking else "false"
        pulse_val = float(self.current_pulse)

        js = (
            "if (window.setJarvisState) {"
            f"window.setJarvisState({{"
            f"speaking: {speaking_str}, "
            f"pulse: {pulse_val}, "
            f"color: '{color_hex}'"
            f"}});"
            "}"
        )
        self.webview.page().runJavaScript(js)
