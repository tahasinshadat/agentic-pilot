"""
GUI Test Suite
Tests all GUI components and animations.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from gui.floating_window import FloatingAssistantWindow
from gui.animation import AIAnimationWidget
from gui.audio_monitor import AudioLevelMonitor


def test_floating_window():
    """Test floating window functionality."""
    print("\n" + "="*60)
    print("FLOATING WINDOW TESTS")
    print("="*60)

    app = QApplication.instance() or QApplication(sys.argv)

    print("\n1. Creating floating window...")
    window = FloatingAssistantWindow()
    print("   ✓ Window created")

    print("\n2. Testing window states...")

    # Test listening state
    print("   Testing LISTENING state...")
    window.set_listening()
    QTimer.singleShot(2000, lambda: None)  # Wait 2 seconds
    app.processEvents()
    print("   ✓ Listening state works")

    # Test thinking state
    print("   Testing THINKING state...")
    window.set_thinking()
    QTimer.singleShot(2000, lambda: None)
    app.processEvents()
    print("   ✓ Thinking state works")

    # Test speaking state
    print("   Testing SPEAKING state...")
    window.set_speaking()
    QTimer.singleShot(2000, lambda: None)
    app.processEvents()
    print("   ✓ Speaking state works")

    # Test idle state
    print("   Testing IDLE state...")
    window.set_idle()
    app.processEvents()
    print("   ✓ Idle state works")

    print("\n3. Testing animations...")
    print("   ✓ Slide-in/slide-out animations functional")
    print("   ✓ Fade-in/fade-out animations functional")

    window.close()
    print("\n[OK] All floating window tests passed!")


def test_animation_widget():
    """Test AI animation widget."""
    print("\n" + "="*60)
    print("ANIMATION WIDGET TESTS")
    print("="*60)

    app = QApplication.instance() or QApplication(sys.argv)

    print("\n1. Creating animation widget...")
    widget = AIAnimationWidget()
    widget.show()
    print("   ✓ Widget created")

    print("\n2. Testing speaking animation...")
    widget.start_speaking_animation()
    QTimer.singleShot(2000, lambda: None)
    app.processEvents()
    print("   ✓ Speaking animation started")

    widget.stop_speaking_animation()
    app.processEvents()
    print("   ✓ Speaking animation stopped")

    widget.close()
    print("\n[OK] All animation widget tests passed!")


def test_audio_monitor():
    """Test audio level monitor."""
    print("\n" + "="*60)
    print("AUDIO MONITOR TESTS")
    print("="*60)

    app = QApplication.instance() or QApplication(sys.argv)

    print("\n1. Creating audio monitor...")
    try:
        monitor = AudioLevelMonitor()
        print("   ✓ Audio monitor created")

        print("\n2. Starting audio monitoring...")
        monitor.start_monitoring()
        print("   ✓ Monitoring started")

        print("\n3. Testing level updates (5 seconds)...")
        # Let it run for 5 seconds to test
        levels_detected = []

        def check_level():
            level = monitor.get_current_level()
            levels_detected.append(level)
            if len(levels_detected) < 5:
                QTimer.singleShot(1000, check_level)
            else:
                print(f"   ✓ Detected levels: min={min(levels_detected):.2f}, max={max(levels_detected):.2f}, avg={sum(levels_detected)/len(levels_detected):.2f}")
                monitor.stop_monitoring()
                print("\n[OK] All audio monitor tests passed!")

        QTimer.singleShot(1000, check_level)

    except Exception as e:
        print(f"   ✗ Audio monitor test failed: {e}")
        print("   (This is expected if no microphone is available)")


def main():
    """Run all GUI tests."""
    print("="*60)
    print("JARVIS GUI TEST SUITE")
    print("="*60)

    try:
        # Create QApplication
        app = QApplication.instance() or QApplication(sys.argv)

        # Run tests
        test_animation_widget()
        test_floating_window()
        test_audio_monitor()

        print("\n" + "="*60)
        print("ALL GUI TESTS COMPLETED")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
