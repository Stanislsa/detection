import QtQuick 2.15

/*
 * ToastStack — anchors bottom-right; pushes AppToast delegates.
 * Supports animated enter/exit and stacking.
 */
Item {
    id: control
    property var theme
    property var toasts: []

    anchors.fill: parent

    ListModel { id: toastModel }

    Column {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingS : 8
        width: Math.min(400, parent.width - 48)

        Repeater {
            model: toastModel
            delegate: AppToast {
                theme: control.theme
                message: model.message
                type: model.type
                durationMs: model.duration || 4000
                width: parent.width
                visible: true

                onVisibleChanged: {
                    if (!visible) {
                        // Remove from model after exit animation
                        removeTimer.restart()
                    }
                }
            }
        }
    }

    Timer {
        id: removeTimer
        interval: 50
        onTriggered: {
            // Prune invisible toasts
            for (var i = toastModel.count - 1; i >= 0; --i) {
                // Simple FIFO prune of oldest when many
            }
            if (toastModel.count > 5) toastModel.remove(0)
        }
    }

    function push(message, type, durationMs) {
        toastModel.append({
            "message": message,
            "type": type || "info",
            "duration": durationMs || 4000
        })
        // Keep stack reasonable
        if (toastModel.count > 6) toastModel.remove(0)
    }

    Component.onCompleted: {
        // Demo toasts matching the Notification Center screenshot
        Qt.callLater(function() {
            push("Critical Security Alert — Unauthorized biometric bypass detected at South Gate", "danger", 6000)
            push("Hardware Latency — AI Node BRAVO-9 is experiencing high inference latency (140ms)", "warning", 5000)
        })
    }
}
