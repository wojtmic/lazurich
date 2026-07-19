import sys

from PySide6.QtGui import QGuiApplication, QIcon, QPixmap

from lazurich.gui.loader import init_qml

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    pixmap = QPixmap("./logo.png")
    icon = QIcon()
    icon.addPixmap(pixmap)
    app.setWindowIcon(icon)

    init_qml()
    sys.exit(app.exec())