import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

/*
 * Configuration des alertes temps réel + canaux de notification.
 */
Flickable {
    id: control
    property var theme
    property var alertController: typeof AlertController !== "undefined" ? AlertController : null

    contentWidth: width
    contentHeight: col.implicitHeight + 48
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    function cfg(key, fallback) {
        if (!alertController) return fallback
        var c = alertController.config
        return c && c[key] !== undefined ? c[key] : fallback
    }

    function setCfg(key, value) {
        if (!alertController) return
        var patch = {}
        patch[key] = value
        alertController.updateConfig(patch)
    }

    Column {
        id: col
        width: parent.width
        spacing: theme ? theme.spacingL : 20
        leftPadding: 4
        rightPadding: 4

        // ---- Realtime engine ----
        Rectangle {
            width: parent.width - 8
            height: engineCol.implicitHeight + 32
            radius: 4
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"
            border.width: 1

            Column {
                id: engineCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 16
                spacing: 14

                RowLayout {
                    width: parent.width
                    Text {
                        text: "Real-time Alert Engine"
                        font.pixelSize: 15
                        font.weight: Font.DemiBold
                        color: theme ? theme.textPrimary : "#E5E7EB"
                        Layout.fillWidth: true
                    }
                    Rectangle {
                        width: statusLab.implicitWidth + 16
                        height: 22
                        radius: 11
                        color: (alertController && alertController.realtimeRunning) ? "#10B98122" : "#64748B22"
                        border.color: (alertController && alertController.realtimeRunning) ? "#10B981" : "#64748B"
                        border.width: 1
                        Text {
                            id: statusLab
                            anchors.centerIn: parent
                            text: (alertController && alertController.realtimeRunning) ? "RUNNING" : "STOPPED"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: (alertController && alertController.realtimeRunning) ? "#10B981" : "#64748B"
                        }
                    }
                }

                Text {
                    width: parent.width
                    text: "Simulates / polls security detections and pushes critical events to the notification stack and Alerts page."
                    font.pixelSize: 12
                    color: theme ? theme.textSecondary : "#94A3B8"
                    wrapMode: Text.WordWrap
                }

                RowLayout {
                    width: parent.width
                    Text {
                        text: "Enable real-time stream"
                        font.pixelSize: 13
                        color: theme ? theme.textPrimary : "#E5E7EB"
                        Layout.fillWidth: true
                    }
                    AppSwitch {
                        theme: control.theme
                        checked: control.cfg("enabled", true)
                        onToggled: {
                            control.setCfg("enabled", checked)
                            if (checked && alertController) alertController.startRealtime()
                            else if (alertController) alertController.stopRealtime()
                        }
                    }
                }

                RowLayout {
                    width: parent.width
                    Text {
                        text: "Poll interval"
                        font.pixelSize: 13
                        color: theme ? theme.textPrimary : "#E5E7EB"
                        Layout.fillWidth: true
                    }
                    Text {
                        text: Math.round(control.cfg("poll_interval_ms", 5000) / 1000) + "s"
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        font.pixelSize: 12
                        color: theme ? theme.textSecondary : "#94A3B8"
                    }
                }
                // Simple interval selector
                Row {
                    spacing: 8
                    Repeater {
                        model: [
                            { label: "2s", ms: 2000 },
                            { label: "5s", ms: 5000 },
                            { label: "10s", ms: 10000 },
                            { label: "30s", ms: 30000 }
                        ]
                        Rectangle {
                            width: lab.implicitWidth + 16
                            height: 28
                            radius: 4
                            color: control.cfg("poll_interval_ms", 5000) === modelData.ms
                                   ? (theme ? theme.primary : "#2563EB") : (theme ? theme.surfaceAlt : "#1B2433")
                            border.color: theme ? theme.border : "#1E293B"
                            border.width: 1
                            Text {
                                id: lab
                                anchors.centerIn: parent
                                text: modelData.label
                                font.pixelSize: 11
                                color: control.cfg("poll_interval_ms", 5000) === modelData.ms
                                       ? "#FFF" : (theme ? theme.textSecondary : "#94A3B8")
                            }
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: control.setCfg("poll_interval_ms", modelData.ms)
                            }
                        }
                    }
                }

                Row {
                    spacing: 10
                    AppButton {
                        text: alertController && alertController.realtimeRunning ? "Stop stream" : "Start stream"
                        variant: alertController && alertController.realtimeRunning ? "danger" : "primary"
                        theme: control.theme
                        onClicked: if (alertController) alertController.toggleRealtime()
                    }
                    AppButton {
                        text: "Inject test CRITICAL"
                        variant: "secondary"
                        theme: control.theme
                        onClicked: {
                            if (alertController)
                                alertController.injectTestAlert(
                                    "Test Critical Alert",
                                    "Manually injected from Notification Settings",
                                    "CRITICAL", "INTRUSION", "CAM-TEST", "Test Cam", "Lab Zone"
                                )
                        }
                    }
                    AppButton {
                        text: "Simulate 3 CRITICAL"
                        variant: "danger"
                        theme: control.theme
                        onClicked: {
                            if (alertController)
                                alertController.simulateCriticalBurst(3)
                        }
                    }
                }
            }
        }

        
        // ---- Push permission ----
        Rectangle {
            width: parent.width - 8
            height: permCol.implicitHeight + 32
            radius: 4
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"
            border.width: 1

            Column {
                id: permCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 16
                spacing: 12

                Text {
                    text: "Push permission"
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                    color: theme ? theme.textPrimary : "#E5E7EB"
                }

                RowLayout {
                    width: parent.width
                    Text {
                        text: "Status"
                        font.pixelSize: 13
                        color: theme ? theme.textPrimary : "#E5E7EB"
                        Layout.fillWidth: true
                    }
                    Rectangle {
                        width: permLab.implicitWidth + 16
                        height: 22
                        radius: 11
                        color: {
                            if (typeof PushService === "undefined" || !PushService) return "#64748B22"
                            if (PushService.isGranted) return "#10B98122"
                            if (PushService.isDenied) return "#EF444422"
                            return "#F59E0B22"
                        }
                        border.color: {
                            if (typeof PushService === "undefined" || !PushService) return "#64748B"
                            if (PushService.isGranted) return "#10B981"
                            if (PushService.isDenied) return "#EF4444"
                            return "#F59E0B"
                        }
                        border.width: 1
                        Text {
                            id: permLab
                            anchors.centerIn: parent
                            text: {
                                if (typeof PushService === "undefined" || !PushService) return "N/A"
                                if (PushService.isGranted) return "GRANTED"
                                if (PushService.isDenied) return "DENIED"
                                return "UNKNOWN"
                            }
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: {
                                if (typeof PushService === "undefined" || !PushService) return "#64748B"
                                if (PushService.isGranted) return "#10B981"
                                if (PushService.isDenied) return "#EF4444"
                                return "#F59E0B"
                            }
                        }
                    }
                }

                Text {
                    width: parent.width
                    text: typeof PushService !== "undefined" && PushService
                          ? PushService.platformHint
                          : "Push service not available"
                    font.pixelSize: 11
                    font.family: theme ? theme.fontFamilyMono : "monospace"
                    color: theme ? theme.textMuted : "#64748B"
                    wrapMode: Text.WordWrap
                }


                RowLayout {
                    width: parent.width
                    visible: typeof PushService !== "undefined" && PushService && PushService.isAndroid
                    Text {
                        text: "Android OS permission"
                        font.pixelSize: 13
                        color: theme ? theme.textPrimary : "#E5E7EB"
                        Layout.fillWidth: true
                    }
                    Text {
                        text: {
                            if (typeof AndroidPermissions === "undefined" || !AndroidPermissions)
                                return "—"
                            var s = AndroidPermissions.statusSnapshot()
                            return s.postNotifications ? "POST_NOTIFICATIONS ✓" : "POST_NOTIFICATIONS ✗"
                        }
                        font.pixelSize: 11
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        color: theme ? theme.textSecondary : "#94A3B8"
                    }
                }
                AppButton {
                    visible: typeof PushService !== "undefined" && PushService && PushService.isAndroid
                    text: "Request Android POST_NOTIFICATIONS"
                    variant: "secondary"
                    theme: control.theme
                    onClicked: {
                        if (typeof AndroidPermissions !== "undefined" && AndroidPermissions)
                            AndroidPermissions.requestPushPermissions()
                    }
                }

                Row {
                    spacing: 10
                    AppButton {
                        text: "Request permission"
                        variant: "primary"
                        theme: control.theme
                        onClicked: {
                            if (typeof PushService !== "undefined" && PushService)
                                PushService.requestPermission()
                        }
                    }
                    AppButton {
                        text: "Reset"
                        variant: "secondary"
                        theme: control.theme
                        onClicked: {
                            if (typeof PushService !== "undefined" && PushService)
                                PushService.resetPermission()
                        }
                    }
                    AppButton {
                        text: "Revoke"
                        variant: "danger"
                        theme: control.theme
                        visible: typeof PushService !== "undefined" && PushService && PushService.isGranted
                        onClicked: {
                            if (typeof PushService !== "undefined" && PushService)
                                PushService.denyPermission()
                        }
                    }
                }
            }
        }

        // ---- Event types ----
        Rectangle {
            width: parent.width - 8
            height: typesCol.implicitHeight + 32
            radius: 4
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"
            border.width: 1

            Column {
                id: typesCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 16
                spacing: 12

                Text {
                    text: "Detection types"
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                    color: theme ? theme.textPrimary : "#E5E7EB"
                }

                Repeater {
                    model: [
                        { key: "enable_person", label: "Person / face detection" },
                        { key: "enable_vehicle", label: "Vehicle detection" },
                        { key: "enable_intrusion", label: "Intrusion / tailgating" },
                        { key: "enable_motion", label: "Motion in restricted zones" },
                        { key: "enable_system", label: "System / camera health" }
                    ]
                    RowLayout {
                        width: parent.width
                        Text {
                            text: modelData.label
                            font.pixelSize: 13
                            color: theme ? theme.textPrimary : "#E5E7EB"
                            Layout.fillWidth: true
                        }
                        AppSwitch {
                            theme: control.theme
                            checked: control.cfg(modelData.key, true)
                            onToggled: control.setCfg(modelData.key, checked)
                        }
                    }
                }

                Text {
                    text: "Minimum AI confidence: " + Math.round(control.cfg("min_confidence", 0.7) * 100) + "%"
                    font.pixelSize: 12
                    color: theme ? theme.textSecondary : "#94A3B8"
                }
                Row {
                    spacing: 8
                    Repeater {
                        model: [
                            { label: "60%", v: 0.60 },
                            { label: "70%", v: 0.70 },
                            { label: "80%", v: 0.80 },
                            { label: "90%", v: 0.90 }
                        ]
                        Rectangle {
                            width: t.implicitWidth + 14
                            height: 26
                            radius: 4
                            color: Math.abs(control.cfg("min_confidence", 0.7) - modelData.v) < 0.01
                                   ? (theme ? theme.primary : "#2563EB") : (theme ? theme.surfaceAlt : "#1B2433")
                            border.color: theme ? theme.border : "#1E293B"
                            border.width: 1
                            Text {
                                id: t
                                anchors.centerIn: parent
                                text: modelData.label
                                font.pixelSize: 11
                                color: Math.abs(control.cfg("min_confidence", 0.7) - modelData.v) < 0.01
                                       ? "#FFF" : (theme ? theme.textSecondary : "#94A3B8")
                            }
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: control.setCfg("min_confidence", modelData.v)
                            }
                        }
                    }
                }
            }
        }

        // ---- Local notifications ----
        Rectangle {
            width: parent.width - 8
            height: notifCol.implicitHeight + 32
            radius: 4
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"
            border.width: 1

            Column {
                id: notifCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 16
                spacing: 12

                Text {
                    text: "Local notifications"
                    font.pixelSize: 15
                    font.weight: Font.DemiBold
                    color: theme ? theme.textPrimary : "#E5E7EB"
                }

                RowLayout {
                    width: parent.width
                    Text { text: "Show toast popups"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; Layout.fillWidth: true }
                    AppSwitch {
                        theme: control.theme
                        checked: control.cfg("toast_enabled", true)
                        onToggled: control.setCfg("toast_enabled", checked)
                    }
                }
                RowLayout {
                    width: parent.width
                    Text { text: "Toasts for CRITICAL only"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; Layout.fillWidth: true }
                    AppSwitch {
                        theme: control.theme
                        checked: control.cfg("toast_critical_only", false)
                        onToggled: control.setCfg("toast_critical_only", checked)
                    }
                }
                RowLayout {
                    width: parent.width
                    Text { text: "Header badge (critical open count)"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; Layout.fillWidth: true }
                    AppSwitch {
                        theme: control.theme
                        checked: control.cfg("badge_enabled", true)
                        onToggled: control.setCfg("badge_enabled", checked)
                    }
                }
                RowLayout {
                    width: parent.width
                    Text { text: "Sound alerts (reserved)"; font.pixelSize: 13; color: theme ? theme.textMuted : "#64748B"; Layout.fillWidth: true }
                    AppSwitch {
                        theme: control.theme
                        checked: control.cfg("sound_enabled", false)
                        onToggled: control.setCfg("sound_enabled", checked)
                    }
                }
                RowLayout {
                    width: parent.width
                    Text { text: "OS push notifications (tray / notify-send)"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; Layout.fillWidth: true }
                    AppSwitch {
                        id: pushSwitch
                        theme: control.theme
                        checked: typeof PushService !== "undefined" && PushService
                                 ? PushService.userEnabled && PushService.isGranted
                                 : false
                        onToggled: {
                            if (typeof PushService !== "undefined" && PushService)
                                PushService.set_enabled(checked)
                        }
                    }
                }
                Text {
                    width: parent.width
                    text: "Critical alerts also appear as desktop notifications via the system tray."
                    font.pixelSize: 11
                    color: theme ? theme.textMuted : "#64748B"
                    wrapMode: Text.WordWrap
                }
            }
        }
    }
}
