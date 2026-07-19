import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QIcon, QPixmap

from lazurich.gui.loader import init_qml

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    pixmap = QPixmap(str(Path(__file__).resolve().parent) + "/logo.png")
    icon = QIcon()
    icon.addPixmap(pixmap)
    app.setWindowIcon(icon)

    init_qml()
    sys.exit(app.exec())