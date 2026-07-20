import QtQuick
import QtQuick.Controls.Basic

Item {
    Component.onCompleted: instanceController.refresh()

    ListView {
        anchors.fill: parent
        model: instanceModel
        spacing: 4

        delegate: Rectangle {
            width: ListView.view.width
            // anchors.right: parent.right
            // anchors.left: parent.left

            height: 60
            color: "#2a2a2a"

            Column {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 12

                Text { text: name; color: "white"; font.pixelSize: 14 }
                Text { text: version + " · " + modloader; color: "#aaaaaa"; font.pixelSize: 11 }
            }

            Button {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.rightMargin: 12
                text: "Launch"
                onClicked: instanceController.launch(instanceId, version)
            }
        }
    }
}