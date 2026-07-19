from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine, QmlElement, QQmlComponent
from PySide6.QtQuick import QQuickItem

QML_IMPORT_NAME = "Lazurich"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class GuiSlot(QQuickItem):
    pass


SCRIPT_DIR = Path(__file__).resolve().parent
QML_DIR = SCRIPT_DIR / "qml"

engine: QQmlApplicationEngine | None = None


def init_qml(entry_file: str = "main.qml") -> QQmlApplicationEngine:
    global engine
    engine = QQmlApplicationEngine()
    engine.addImportPath(str(QML_DIR))

    entry = QML_DIR / entry_file
    engine.load(str(entry))

    if not engine.rootObjects():
        raise RuntimeError(f"Failed to load QML: {entry}")

    return engine


def load_qml(slot_id: str, file: str) -> QQuickItem:
    if engine is None:
        raise RuntimeError("Call init_qml() before load_qml()")

    slot = None
    for root in engine.rootObjects():
        slot = root.findChild(QQuickItem, slot_id)
        if slot is not None:
            break

    if slot is None:
        raise ValueError(f"No GuiSlot found with objectName '{slot_id}'")

    component = QQmlComponent(engine, QUrl.fromLocalFile(str(QML_DIR / file)))

    if component.status() == QQmlComponent.Error:
        raise RuntimeError(f"Failed to load {file}: {component.errorString()}")

    item = component.create()

    if item is None:
        raise RuntimeError(f"Failed to create item from {file}: {component.errorString()}")

    item.setParentItem(slot)
    item.setParent(slot)

    return item