import QtQuick
import QtQuick.Controls
import Lazurich 1.0

ApplicationWindow {
    id: window
    width: 640
    height: 480
    visible: true
    title: "Lazurich"

    GuiSlot {
        id: contentSlot
        objectName: "contentSlot"
        anchors.fill: parent
    }
}