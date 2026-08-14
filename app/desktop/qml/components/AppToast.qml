import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"

Rectangle {
    id: control

    property var theme
    property string message: ""
    property string type: "info" // info, success, warning, danger
    property int durationMs: 4000

    implicitWidth: Math.min(380, (parent ? parent.width : 400) - 48)
    implicitHeight: Math.max(48, contentRow.implicitHeight + 20)

    radius: theme ? theme.radiusM : 4
    border.width: 1
    border.color: {
        switch(control.type) {
            case "success": return theme ? theme.success : "#10B981"
            case "warning": return theme ? theme.warning : "#F59E0B"
            case "danger":  return theme ? theme.critical : "#EF4444"
            default:        return theme ? theme.info : "#06B6D4"
        }
    }
    color: theme ? theme.surfaceElevated : "#1E293B"

    // Slide + fade entrance
    opacity: 0
    x: 40

    Component.onCompleted: {
        opacity = 1
        x = 0
    }

    Behavior on opacity {
        NumberAnimation { duration: 220; easing.type: Easing.OutCubic }
    }
    Behavior on x {
        NumberAnimation { duration: 260; easing.type: Easing.OutCubic }
    }

    // Left accent bar
    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 4
        radius: 2
        color: {
            switch(control.type) {
                case "success": return theme ? theme.success : "#10B981"
                case "warning": return theme ? theme.warning : "#F59E0B"
                case "danger":  return theme ? theme.critical : "#EF4444"
                default:        return theme ? theme.info : "#06B6D4"
            }
        }
    }

    Row {
        id: contentRow
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 12
        anchors.topMargin: 10
        anchors.bottomMargin: 10
        spacing: 12

        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: {
                switch(control.type) {
                    case "success": return "✓"
                    case "warning": return "⚠"
                    case "danger":  return "✕"
                    default:        return "ℹ"
                }
            }
            font.pixelSize: theme ? theme.fontSizeL : 14
            color: {
                switch(control.type) {
                    case "success": return theme ? theme.success : "#10B981"
                    case "warning": return theme ? theme.warning : "#F59E0B"
                    case "danger":  return theme ? theme.critical : "#EF4444"
                    default:        return theme ? theme.info : "#06B6D4"
                }
            }
        }

        Text {
            id: label
            width: parent.width - 60
            anchors.verticalCenter: parent.verticalCenter
            text: control.message
            font.family: theme ? theme.fontFamily : "sans-serif"
            font.pixelSize: theme ? theme.fontSizeM : 13
            color: theme ? theme.textPrimary : "#E5E7EB"
            wrapMode: Text.WordWrap
        }

        // Close button
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: "×"
            font.pixelSize: 18
            color: theme ? theme.textMuted : "#64748B"
            MouseArea {
                anchors.fill: parent
                anchors.margins: -6
                cursorShape: Qt.PointingHandCursor
                onClicked: control.dismiss()
            }
        }
    }

    // Auto dismiss
    Timer {
        id: dismissTimer
        interval: control.durationMs
        running: true
        onTriggered: control.dismiss()
    }

    function dismiss() {
        opacity = 0
        x = 40
        dismissCompleteTimer.start()
    }

    Timer {
        id: dismissCompleteTimer
        interval: 240
        onTriggered: control.visible = false
    }
}
