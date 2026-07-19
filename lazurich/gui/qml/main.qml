import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Lazurich 1.0

ApplicationWindow {
    id: window
    width: 640
    height: 480
    visible: true
    title: "Lazurich"

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            id: sidebar
            Layout.fillHeight: true
            onNavigate: function(itemId) {
                console.log("navigate to:", itemId)
            }
        }

        GuiSlot {
            id: contentSlot
            objectName: "contentSlot"
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}