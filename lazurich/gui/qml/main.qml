import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Lazurich 1.0

ApplicationWindow {
    id: window
    width: 720
    height: 480
    visible: true
    title: "Lazurich"

    // Tab order must match the StackLayout children below.
    readonly property var tabIds: ["home", "list", "skin", "accounts", "settings"]

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            id: sidebar
            objectName: "sidebar"
            Layout.fillHeight: true
            z: 100
        }

        StackLayout {
            id: tabs
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: Math.max(0, window.tabIds.indexOf(sidebar.activeItem))

            GuiSlot { objectName: "homeSlot" }
            GuiSlot { objectName: "listSlot" }
            GuiSlot { objectName: "skinSlot" }
            GuiSlot { objectName: "accountsSlot" }
            GuiSlot { objectName: "settingsSlot" }
        }
    }
}