import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QScreen
from PySide6.QtCore import QTimer

app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

# Take screenshot after 1 second
def take_screenshot():
    screen = QApplication.primaryScreen()
    screenshot = screen.grabWindow(0)
    screenshot.save('C:/MaxManager/screenshot_ui.png')
    print("Screenshot saved to C:/MaxManager/screenshot_ui.png")
    QApplication.quit()

QTimer.singleShot(1000, take_screenshot)
app.exec()

