import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

/*
 * PushPermissionDialog — consentement notifications push OS.
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
    height: body.implicitHeight

    parent: Overlay.overlay
    x: parent ? Math.round((parent.width - width) / 2) : 0
    y: parent ? Math.round((parent.height - height) / 2) : 0

    enter: Transition {
        ParallelAnimation {
            NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 180; easing.type: Easing.OutCubic }
            NumberAnimation { property: "scale"; from: 0.94; to: 1; duration: 220; easing.type: Easing.OutCubic }
        }
    }
    exit: Transition {
        ParallelAnimation {
            NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 140; easing.type: Easing.InCubic }
            NumberAnimation { property: "scale"; from: 1; to: 0.96; duration: 140; easing.type: Easing.InCubic }
        }
    }

    background: Rectangle {
        radius: 10
        color: theme ? theme.surfaceElevated : "#1E293B"
        border.color: theme ? theme.border : "#334155"
        border.width: 1
    }

    Overlay.modal: Rectangle {
        color: "#0B0E14CC"
    }

    function iconSource(name) {
        if (typeof AppPaths !== "undefined" && AppPaths) {
            var u = AppPaths.iconUrl(name)
            if (u && u.length > 0)
                return u
        }
        return Qt.resolvedUrl("../../assets/icons/" + name + ".svg")
    }

    ColumnLayout {
        id: body
        width: control.width
        spacing: 0

        // ---- Header ----
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 60

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 18
                anchors.rightMargin: 10
                spacing: 12

                Rectangle {
                    width: 40
                    height: 40
                    radius: 20
                    color: theme ? theme.primary : "#2563EB"

                    Image {
                        anchors.centerIn: parent
                        width: 20
                        height: 20
                        source: control.iconSource("bell")
                        sourceSize.width: 40
                        sourceSize.height: 40
                        fillMode: Image.PreserveAspectFit
                        // Tint white via layer if available; fallback visible as-is
                        opacity: 0.95
                    }
                }

                Column {
                    Layout.fillWidth: true
                    spacing: 2
                    Text {
                        text: (typeof I18n !== "undefined" && I18n) ? I18n.t("push.title") : "Push notifications"
                        font.family: theme ? theme.fontFamily : "Inter"
                        font.pixelSize: 15
                        font.weight: Font.DemiBold
                        color: theme ? theme.textPrimary : "#E5E7EB"
                    }
                    Text {
                        text: (typeof I18n !== "undefined" && I18n) ? I18n.t("push.permission_required") : "Permission required"
                        font.pixelSize: 12
                        color: theme ? theme.textMuted : "#64748B"
                    }
                }

                Item {
                    Layout.preferredWidth: 32
                    Layout.preferredHeight: 32
                    Rectangle {
                        anchors.fill: parent
                        radius: 6
                        color: closeMa.containsMouse ? (theme ? theme.surfaceAlt : "#1B2433") : "transparent"
                    }
                    Text {
                        anchors.centerIn: parent
                        text: "✕"
                        font.pixelSize: 14
                        color: theme ? theme.textSecondary : "#94A3B8"
                    }
                    MouseArea {
                        id: closeMa
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: control.close()
                    }
                }
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: 1
                color: theme ? theme.border : "#1E293B"
            }
        }

        // ---- Body ----
        ColumnLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 20
            Layout.rightMargin: 20
            Layout.topMargin: 18
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
                lineHeight: 1.25
            }

            // Info card
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: infoInner.implicitHeight + 24
                radius: 8
                color: theme ? theme.backgroundAlt : "#0F172A"
                border.color: theme ? theme.border : "#1E293B"
                border.width: 1

                Column {
                    id: infoInner
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 14
                    spacing: 10

                    Text {
                        text: "INCLUDED EVENTS"
                        font.pixelSize: 10
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        font.weight: Font.Bold
                        font.letterSpacing: 0.6
                        color: theme ? theme.textMuted : "#64748B"
                    }

                    Repeater {
                        model: [
                            {
                                icon: "alert-triangle",
                                accent: "#EF4444",
                                label: "Intrusion & unauthorized access"
                            },
                            {
                                icon: "camera",
                                accent: "#06B6D4",
                                label: "Camera offline / signal loss"
                            },
                            {
                                icon: "shield",
                                accent: "#2563EB",
                                label: "High-confidence AI detections"
                            }
                        ]

                        RowLayout {
                            width: infoInner.width
                            spacing: 10

                            // Icon badge — never falls back to icon filename text
                            Rectangle {
                                width: 28
                                height: 28
                                radius: 6
                                color: modelData.accent + "22"
                                border.color: modelData.accent + "55"
                                border.width: 1

                                Image {
                                    id: rowIcon
                                    anchors.centerIn: parent
                                    width: 14
                                    height: 14
                                    source: control.iconSource(modelData.icon)
                                    sourceSize.width: 28
                                    sourceSize.height: 28
                                    fillMode: Image.PreserveAspectFit
                                    visible: status !== Image.Error && status !== Image.Null
                                }

                                // Fallback glyph if SVG fails (no filename text)
                                Text {
                                    anchors.centerIn: parent
                                    visible: rowIcon.status === Image.Error || rowIcon.status === Image.Null
                                    text: modelData.icon === "alert-triangle" ? "⚠"
                                          : modelData.icon === "camera" ? "◉"
                                          : "◈"
                                    font.pixelSize: 12
                                    color: modelData.accent
                                }
                            }

                            Text {
                                Layout.fillWidth: true
                                text: modelData.label
                                font.pixelSize: 13
                                color: theme ? theme.textPrimary : "#E5E7EB"
                                elide: Text.ElideRight
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
                        font.pixelSize: 11
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
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 68

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                height: 1
                color: theme ? theme.border : "#1E293B"
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 10

                AppButton {
                    Layout.fillWidth: true
                    text: (typeof I18n !== "undefined" && I18n) ? I18n.t("push.dont_allow") : "Don't allow"
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
                    text: (typeof I18n !== "undefined" && I18n) ? I18n.t("push.allow") : "Allow notifications"
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

    onOpened: control.height = body.implicitHeight
}
