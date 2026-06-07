import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from StreamLabsTikTokStreamKeyGenerator import StreamApp

def capture_screenshot():
    app = QApplication(sys.argv + ['-platform', 'offscreen'])
    window = StreamApp()
    window.show()

    # Give it a moment to render
    QTimer.singleShot(1000, lambda: (
        window.grab().save("screenshot.png"),
        app.quit()
    ))

    sys.exit(app.exec())

if __name__ == "__main__":
    capture_screenshot()
