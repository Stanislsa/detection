import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

/*
 * PushPermissionDialog — consentement notifications push OS.
 *
 * Usage:
 *   PushPermissionDialog {
 *       id: pushDialog
 *       theme: root.theme
 *       pushService: PushService
 *   }
 *   // pushDialog.open()
 */
Popup {
    id: control

    property var theme
    property var pushService: typeof PushService !== "undefined" ? PushService : null

    signal granted()
    signal denied()

    modal: true
    dim: true
    focus: true
    padding: 0
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    width: Math.min(460, (parent ? parent.width : 460) - 32)
    height: body.implicitHeight + 24

    // Center on Overlay
    parent: Overlay.overlay
    x: parent ? Math.round((parent.width - width) / 2) : 0
    y: parent ? Math.round((parent.height - height) / 2) : 0

    enter: Transition {
        ParallelAnimation {
            NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 180; easing.type: Easing.OutCubic }
            NumberAnimation { property: "scale"; from: 0.92; to: 1; duration: 220; easing.type: Easing.OutBack }
        }
    }
    exit: Transition {
        ParallelAnimation {
            NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 140; easing.type: Easing.InCubic }
            NumberAnimation { property: "scale"; from: 1; to: 0.96; duration: 140; easing.type: Easing.InCubic }
        }
    }

    background: Rectangle {
        id: bg
        radius: theme ? (theme.radiusL || 8) : 8
        color: theme ? theme.surfaceElevated : "#1E293B"
        border.color: theme ? theme.border : "#1E293B"
        border.width: 1

        // Soft shadow via second rect (no GraphicalEffects dependency)
        Rectangle {
            z: -1
            anchors.fill: parent
            anchors.margins: -1
            anchors.topMargin: 4
            radius: parent.radius
            color: "#00000055"
        }
    }

    Overlay.modal: Rectangle {
        color: "#0B0E14CC"
        Behavior on opacity { NumberAnimation { duration: 160 } }
    }

    ColumnLayout {
        id: body
        width: control.width
        spacing: 0

        // ---- Header ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 56
            color: theme ? theme.surface : "#151C28"
            radius: theme ? (theme.radiusL || 8) : 8

            // square bottom corners
            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: parent.radius
                color: parent.color
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 8
                spacing: 12

                Rectangle {
                    width: 36
                    height: 36
                    radius: 18
                    color: theme ? theme.primary : "#2563EB"
                    AppIcon {
                        anchors.centerIn: parent
                        width: 18
                        height: 18
                        iconName: "bell"
                        iconColor: "#FFFFFF"
                    }
                }

                Column {
                    Layout.fillWidth: true
                    spacing: 1
                    Text {
                        text: "Push notifications"
                        font.family: theme ? theme.fontFamily : "Inter"
                        font.pixelSize: theme ? theme.fontSizeL : 14
                        font.weight: Font.DemiBold
                        color: theme ? theme.textPrimary : "#E5E7EB"
                    }
                    Text {
                        text: "Permission required"
                        font.pixelSize: 11
                        color: theme ? theme.textMuted : "#64748B"
                    }
                }

                AppIconButton {
                    Layout.preferredWidth: 32
                    Layout.preferredHeight: 32
                    iconName: "x"
                    theme: control.theme
                    onClicked: {
                        // Close without changing state (still unknown)
                        control.close()
                    }
                }
            }
        }

        // ---- Body ----
        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            Layout.topMargin: 16
            Layout.bottomMargin: 8
            spacing: 14

            Text {
                Layout.fillWidth: true
                text: "Allow SentinelAI to send critical security alerts to your desktop?"
                font.pixelSize: 14
                font.weight: Font.DemiBold
                color: theme ? theme.textPrimary : "#E5E7EB"
                wrapMode: Text.WordWrap
            }

            Text {
                Layout.fillWidth: true
                text: (pushService && pushService.isAndroid)
                      ? "On Android 13+, the system will also ask for the POST_NOTIFICATIONS permission after you tap Allow."
                      : "You will be notified of CRITICAL and HIGH severity events even when the application window is in the background."
                font.pixelSize: 13
                color: theme ? theme.textSecondary : "#94A3B8"
                wrapMode: Text.WordWrap
            }

            // Info card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: infoInner.implicitHeight + 24
                radius: 6
                color: theme ? theme.backgroundAlt : "#0F172A"
                border.color: theme ? theme.border : "#1E293B"
                border.width: 1

                Column {
                    id: infoInner
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 12
                    spacing: 8

                    Text {
                        text: "INCLUDED EVENTS"
                        font.pixelSize: 10
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        font.weight: Font.Bold
                        color: theme ? theme.textMuted : "#64748B"
                    }

                    Repeater {
                        model: [
                            { icon: "alert-triangle", label: "Intrusion & unauthorized access" },
                            { icon: "camera", label: "Camera offline / signal loss" },
                            { icon: "shield", label: "High-confidence AI detections" }
                        ]
                        Row {
                            spacing: 8
                            width: infoInner.width
                            AppIcon {
                                width: 14
                                height: 14
                                iconName: modelData.icon
                                iconColor: theme ? theme.primary : "#2563EB"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: modelData.label
                                font.pixelSize: 12
                                color: theme ? theme.textPrimary : "#E5E7EB"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 1
                        color: theme ? theme.border : "#1E293B"
                    }

                    Text {
                        width: parent.width
                        text: pushService
                              ? ("Backend: " + pushService.platformHint)
                              : "Backend: system tray"
                        font.pixelSize: 10
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        color: theme ? theme.textMuted : "#64748B"
                        wrapMode: Text.WordWrap
                    }
                }
            }

            Text {
                Layout.fillWidth: true
                text: "You can change this later in Settings → Alerts → Push permission."
                font.pixelSize: 11
                color: theme ? theme.textMuted : "#64748B"
                wrapMode: Text.WordWrap
            }
        }

        // ---- Footer ----
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 64
            color: theme ? theme.surface : "#151C28"

            // square top
            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                height: 8
                color: parent.color
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 10

                AppButton {
                    Layout.fillWidth: true
                    text: "Don't allow"
                    variant: "secondary"
                    theme: control.theme
                    onClicked: {
                        if (pushService)
                            pushService.denyPermission()
                        control.denied()
                        control.close()
                    }
                }

                AppButton {
                    Layout.fillWidth: true
                    text: "Allow notifications"
                    variant: "primary"
                    theme: control.theme
                    onClicked: {
                        if (pushService)
                            pushService.grantPermission()
                        control.granted()
                        control.close()
                    }
                }
            }
        }
    }

    onOpened: {
        // Force layout height after open
        control.height = body.implicitHeight
    }
}
