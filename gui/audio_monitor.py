"""
Audio Level Monitor
Monitors microphone input and provides real-time audio level data for visualization.
"""

import numpy as np
import pyaudio
import threading
import queue
from PySide6.QtCore import QObject, Signal, QTimer


class AudioLevelMonitor(QObject):
    """
    Monitors microphone input and emits audio level signals.
    Used for visualizing voice input level in the GUI.
    """

    # Signal emitted when audio level changes (0.0 to 1.0)
    level_changed = Signal(float)

    def __init__(self, rate=44100, chunk=1024):
        super().__init__()
        self.rate = rate
        self.chunk = chunk
        self.running = False
        self.current_level = 0.0

        # Audio setup
        self.p = None
        self.stream = None
        self.audio_thread = None

        # Level smoothing
        self.level_history = []
        self.history_size = 5  # Smooth over 5 samples

    def start_monitoring(self):
        """Start monitoring microphone input."""
        if self.running:
            return

        # Clean up any existing resources first
        self._cleanup_resources()

        self.running = True

        try:
            # Initialize PyAudio
            self.p = pyaudio.PyAudio()

            # Open stream
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
                stream_callback=self._audio_callback
            )

            self.stream.start_stream()
            print("[AudioMonitor] Monitoring started")

        except Exception as e:
            print(f"[AudioMonitor] Error starting: {e}")
            self.running = False
            self._cleanup_resources()

    def stop_monitoring(self):
        """Stop monitoring microphone input."""
        self.running = False
        self._cleanup_resources()
        print("[AudioMonitor] Monitoring stopped")

    def _cleanup_resources(self):
        """Clean up PyAudio resources safely."""
        try:
            if self.stream:
                try:
                    if self.stream.is_active():
                        self.stream.stop_stream()
                except:
                    pass
                try:
                    self.stream.close()
                except:
                    pass
                self.stream = None

            if self.p:
                try:
                    self.p.terminate()
                except:
                    pass
                self.p = None

            # Clear level history
            self.level_history = []
            self.current_level = 0.0

        except Exception as e:
            print(f"[AudioMonitor] Error during cleanup: {e}")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback - processes audio data."""
        if not self.running:
            return (None, pyaudio.paComplete)

        try:
            # Convert bytes to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16)

            # Convert to float to avoid overflow when squaring
            audio_data_float = audio_data.astype(np.float64)

            # Calculate RMS (root mean square) level
            # Use abs and max to ensure we never take sqrt of negative number
            mean_square = np.mean(audio_data_float**2)
            mean_square = max(0.0, mean_square)  # Ensure non-negative
            rms = np.sqrt(mean_square)

            # Normalize to 0.0 - 1.0 range
            # Max value for int16 is 32768
            normalized_level = min(rms / 32768.0, 1.0)

            # Validate the normalized level (check for NaN, inf, or invalid values)
            if not np.isfinite(normalized_level) or normalized_level < 0:
                normalized_level = 0.0
            elif normalized_level > 1.0:
                normalized_level = 1.0

            # Apply smoothing
            self.level_history.append(normalized_level)
            if len(self.level_history) > self.history_size:
                self.level_history.pop(0)

            # Calculate smoothed level
            smoothed_level = sum(self.level_history) / len(self.level_history)

            # Validate smoothed level as well
            if not np.isfinite(smoothed_level) or smoothed_level < 0:
                smoothed_level = 0.0
            elif smoothed_level > 1.0:
                smoothed_level = 1.0

            # Update current level
            self.current_level = smoothed_level

            # Debug: Print audio level (remove after testing)
            # if smoothed_level > 0.01:
            #     print(f"[AudioMonitor] Level: {smoothed_level:.3f}")

            # Emit signal (will be handled by Qt main thread)
            self.level_changed.emit(smoothed_level)

        except Exception as e:
            print(f"[AudioMonitor] Callback error: {e}")
            # Emit 0 on error to prevent GUI issues
            self.level_changed.emit(0.0)

        return (in_data, pyaudio.paContinue)

    def get_current_level(self):
        """Get current audio level (0.0 to 1.0)."""
        return self.current_level

    def cleanup(self):
        """Cleanup resources."""
        self.stop_monitoring()
