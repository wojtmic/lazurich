import sys
from pathlib import Path

import qasync
from PySide6.QtGui import QGuiApplication, QIcon, QPixmap
from lazurich.gui.controllers.instances import InstanceController

from lazurich.gui import loader
from lazurich.gui.loader import init_qml, load_qml

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    pixmap = QPixmap(str(Path(__file__).resolve().parent / 'logo.png'))
    icon = QIcon()
    icon.addPixmap(pixmap)
    app.setWindowIcon(icon)

    loop = qasync.QEventLoop(app)
    qasync.asyncio.set_event_loop(loop)

    init_qml()

    instance_controller = InstanceController()
    loader.engine.rootContext().setContextProperty("instanceController", instance_controller)
    loader.engine.rootContext().setContextProperty("instanceModel", instance_controller.model)

    load_qml('listSlot', 'List.qml')

    with loop:
        sys.exit(loop.run_forever())