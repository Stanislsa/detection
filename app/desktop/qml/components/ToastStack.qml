import QtQuick 2.15

/*
 * ToastStack — anchors bottom-right; pushes AppToast delegates.
 * Use from the Notifications page to surface floating toasts.
 */
Item {
    id: control
    property var theme
    property var toasts: []   // [{message, type, durationMs}]

    anchors.fill: parent

    ListModel { id: toastModel }

    Column {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingS : 8

        Repeater {
            model: toastModel
            delegate: AppToast {
                theme: control.theme
                message: model.message
                type: model.type
                visible: true
            }
        }
    }

    function push(message, type, durationMs) {
        toastModel.append({ "message": message, "type": type || "info" })
        // Auto-prune after duration
        timer.interval = durationMs || 4000
        timer.restart()
    }

    Timer {
        id: timer
        repeat: false
        onTriggered: {
            if (toastModel.count > 0) toastModel.remove(0)
        }
    }

    Component.onCompleted: {
        // seed two demo toasts to match the spec screenshot
        toastModel.append({ "message": "Critical Security Alert — Unauthorized biometric bypass", "type": "danger" })
        toastModel.append({ "message": "Hardware Latency — 880ms on SATELLITE UPLINK", "type": "warning" })
    }
}