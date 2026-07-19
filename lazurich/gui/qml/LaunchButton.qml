import QtQuick
import QtQuick.Controls.Basic

Button {
    id: launchButton
    objectName: "launchButton"
    text: "Launch the fucking game"

    onClicked: eventBridge.trigger(launchButton.objectName)
}