import QtQuick
import QtQuick.Controls.Basic

Button {
    id: btn

    property bool expanded: false
    property bool active: false
    property string glyph: ""
    property string label: ""

    implicitHeight: 44
    flat: true

    background: Rectangle {
        color: btn.active ? "#333333" : (btn.hovered ? "#2a2a2a" : "transparent")
        Behavior on color { ColorAnimation { duration: 100 } }
    }

    contentItem: Row {
        spacing: 12
        leftPadding: 16
        anchors.verticalCenter: parent.verticalCenter

        Text {
            text: btn.glyph
            color: btn.active ? "#ffffff" : "#aaaaaa"
            font.pixelSize: 18
            width: 20
            horizontalAlignment: Text.AlignHCenter
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: btn.label
            color: btn.active ? "#ffffff" : "#aaaaaa"
            font.pixelSize: 13
            visible: btn.expanded
            opacity: btn.expanded ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 100 } }
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}