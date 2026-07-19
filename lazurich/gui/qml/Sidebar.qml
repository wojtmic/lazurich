import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Rectangle {
    id: sidebar

    property bool expanded: false
    property string activeItem: "home"
    property int collapsedWidth: 56
    property int expandedWidth: 180

    width: expanded ? expandedWidth : collapsedWidth
    Behavior on width { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }

    color: "#1e1e1e"

    signal navigate(string itemId)

    ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: 8
        anchors.bottomMargin: 8
        spacing: 4

        SidebarButton {
            Layout.fillWidth: true
            expanded: sidebar.expanded
            active: sidebar.activeItem === "home"
            glyph: "\u2302"
            label: "Home"
            onClicked: { sidebar.activeItem = "home"; sidebar.navigate("home") }
        }

        SidebarButton {
            Layout.fillWidth: true
            expanded: sidebar.expanded
            active: sidebar.activeItem === "list"
            glyph: "\u2261"
            label: "List"
            onClicked: { sidebar.activeItem = "list"; sidebar.navigate("list") }
        }

        SidebarButton {
            Layout.fillWidth: true
            expanded: sidebar.expanded
            active: sidebar.activeItem === "skin"
            glyph: "\u25A0"
            label: "Skin"
            onClicked: { sidebar.activeItem = "skin"; sidebar.navigate("skin") }
        }

        Item { Layout.fillHeight: true } // spacer

        SidebarButton {
            Layout.fillWidth: true
            expanded: sidebar.expanded
            active: sidebar.activeItem === "accounts"
            glyph: "\u263A"
            label: "Accounts"
            onClicked: { sidebar.activeItem = "accounts"; sidebar.navigate("accounts") }
        }

        SidebarButton {
            Layout.fillWidth: true
            expanded: sidebar.expanded
            active: sidebar.activeItem === "settings"
            glyph: "\u2699"
            label: "Settings"
            onClicked: { sidebar.activeItem = "settings"; sidebar.navigate("settings") }
        }

        SidebarButton {
            Layout.fillWidth: true
            expanded: sidebar.expanded
            active: false
            glyph: sidebar.expanded ? "\u276E" : "\u276F"
            label: "Collapse"
            onClicked: sidebar.expanded = !sidebar.expanded
        }
    }
}