"""Auto-test language switching."""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Import test window
from test_canvas import TestCanvasWindow


def auto_toggle_language(window, clicks_left):
    """Auto-click language toggle button."""
    if clicks_left <= 0:
        print("\n" + "="*60)
        print("AUTO-TEST DONE: Closing window...")
        print("="*60 + "\n")
        window.close()
        return
    
    print("\n" + "="*60)
    print(f"AUTO-TEST: Clicking language toggle button... ({clicks_left} left)")
    print("="*60 + "\n")
    window.lang_toggle_btn.click()
    
    # Schedule another click in 3 seconds
    QTimer.singleShot(3000, lambda: auto_toggle_language(window, clicks_left - 1))


def main():
    """Run auto-test."""
    # Set UTF-8 encoding
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = TestCanvasWindow()
    window.show()
    
    # Auto-click 4 times (3 sec each = 12 sec total) then close
    QTimer.singleShot(3000, lambda: auto_toggle_language(window, 4))
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

