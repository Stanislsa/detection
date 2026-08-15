import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Rectangle {
    id: control

    property var theme
    readonly property bool isCompact: height < 700 || width < 640
    property var authController

    color: control.theme.background

    Behavior on color {
        ColorAnimation { duration: 280 }
    }

    // Subtle geometric background
    Item {
        anchors.fill: parent
        opacity: 0.15

        Repeater {
            model: 8
            Rectangle {
                x: (index % 4) * (parent.width / 3) - 40
                y: Math.floor(index / 4) * (parent.height / 2) + 60
                width: 180
                height: 180
                radius: 12
                rotation: 15 + index * 8
                color: "transparent"
                border.color: theme ? theme.primary : "#2563EB"
                border.width: 1
                opacity: 0.4
            }
        }
    }

    Column {
        anchors.centerIn: parent
        spacing: theme ? theme.spacingXL : 32
        width: Math.min(420, parent.width - 48)

        // Logo + brand
        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 8

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 48
                height: 48
                radius: 10
                color: theme ? theme.primary : "#2563EB"

                Text {
                    anchors.centerIn: parent
                    text: "🛡"
                    font.pixelSize: 22
                }
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "SentinelAI"
                font.family: theme ? theme.fontFamily : "sans-serif"
                font.pixelSize: theme ? theme.fontSizeXXXL : 28
                font.weight: theme ? theme.weightBold : Font.Bold
                color: theme ? theme.textPrimary : "#E5E7EB"
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "SECURE OPERATIONS GATEWAY"
                font.family: theme ? theme.fontFamilyMono : "monospace"
                font.pixelSize: theme ? theme.fontSizeXS : 11
                font.letterSpacing: 2
                color: theme ? theme.textMuted : "#64748B"
            }
        }

        // Platform Access Card
        Rectangle {
            width: parent.width
            radius: theme ? theme.radiusL : 6
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"
            border.width: 1

            Behavior on color { ColorAnimation { duration: 280 } }

            Column {
                id: cardContent
                width: parent.width
                padding: theme ? theme.spacingXL : 32
                spacing: theme ? theme.spacingL : 20

                Row {
                    width: parent.width - parent.padding * 2
                    spacing: 8

                    Text {
                        text: "Platform Access"
                        font.family: theme ? theme.fontFamily : "sans-serif"
                        font.pixelSize: theme ? theme.fontSizeXL : 16
                        font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                        color: theme ? theme.textPrimary : "#E5E7EB"
                    }

                    Item { width: 1; height: 1; Layout.fillWidth: true }

                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: statusText.implicitWidth + 12
                        height: 20
                        radius: 10
                        color: theme ? theme.success : "#10B981"
                        opacity: 0.15

                        Text {
                            id: statusText
                            anchors.centerIn: parent
                            text: "SYSTEM ONLINE"
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: theme ? theme.success : "#10B981"
                        }
                    }
                }

                Text {
                    width: parent.width - parent.padding * 2
                    text: "Enter your encrypted credentials to continue."
                    font.pixelSize: theme ? theme.fontSizeS : 12
                    color: theme ? theme.textSecondary : "#94A3B8"
                    wrapMode: Text.WordWrap
                }

                // Email
                Column {
                    width: parent.width - parent.padding * 2
                    spacing: 6

                    Text {
                        text: "OPERATOR EMAIL"
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        font.pixelSize: theme ? theme.fontSizeXS : 11
                        font.letterSpacing: 1
                        color: theme ? theme.textMuted : "#64748B"
                    }

                    AppInput {
                        id: emailInput
                        width: parent.width
                        theme: control.theme
                        placeholderText: "operator@axyris.security"
                    }
                }

                // Password
                Column {
                    width: parent.width - parent.padding * 2
                    spacing: 6

                    Row {
                        width: parent.width
                        Text {
                            text: "SYSTEM PASSWORD"
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            font.pixelSize: theme ? theme.fontSizeXS : 11
                            font.letterSpacing: 1
                            color: theme ? theme.textMuted : "#64748B"
                        }
                        Item { width: parent.width - 160; height: 1 }
                        Text {
                            text: "RESET CREDENTIAL"
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            font.pixelSize: theme ? theme.fontSizeXS : 11
                            color: theme ? theme.primary : "#2563EB"
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: control.forgotPasswordRequested()
                            }
                        }
                    }

                    AppInput {
                        id: passwordInput
                        width: parent.width
                        theme: control.theme
                        placeholderText: "••••••••••••"
                        echoMode: TextInput.Password
                    }
                }

                // Trust checkbox
                Row {
                    spacing: 8
                    AppCheckBox {
                        id: trustBox
                        theme: control.theme
                        checked: false
                    }
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Trust this workstation for 24 hours"
                        font.pixelSize: theme ? theme.fontSizeS : 12
                        color: theme ? theme.textSecondary : "#94A3B8"
                    }
                }

                // Authenticate button
                AppButton {
                    id: loginButton
                    width: parent.width - parent.padding * 2
                    text: "Authenticate  →"
                    theme: control.theme
                    enabled: emailInput.text !== "" && passwordInput.text !== ""

                    onClicked: {
                        if (control.authController)
                            control.authController.login(emailInput.text, passwordInput.text)
                    }
                }

                // Policy note
                Rectangle {
                    width: parent.width - parent.padding * 2
                    height: policyText.implicitHeight + 16
                    radius: 4
                    color: theme ? theme.backgroundAlt : "#0F172A"
                    border.color: theme ? theme.border : "#1E293B"
                    border.width: 1

                    Text {
                        id: policyText
                        anchors.fill: parent
                        anchors.margins: 8
                        text: "Session monitored under Axyris Security Policy v4.2. Unauthorized access attempt is a federal offense."
                        font.pixelSize: theme ? theme.fontSizeXS : 11
                        color: theme ? theme.textMuted : "#64748B"
                        wrapMode: Text.WordWrap
                    }
                }

                // Footer badges
                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 16
                    Text {
                        text: "🔒 AES-256"
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        font.pixelSize: 10
                        color: theme ? theme.textMuted : "#64748B"
                    }
                    Text {
                        text: "•"
                        color: theme ? theme.textMuted : "#64748B"
                    }
                    Text {
                        text: "FIDO2 Ready"
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        font.pixelSize: 10
                        color: theme ? theme.textMuted : "#64748B"
                    }
                }
            }

            // Dynamic height from content
            height: cardContent.implicitHeight
        }

        // Bottom links
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 16
            Text {
                text: "PRIVACY POLICY"
                font.family: theme ? theme.fontFamilyMono : "monospace"
                font.pixelSize: 10
                color: theme ? theme.textMuted : "#64748B"
            }
            Text { text: "•"; color: theme ? theme.textMuted : "#64748B" }
            Text {
                text: "COMPLIANCE"
                font.family: theme ? theme.fontFamilyMono : "monospace"
                font.pixelSize: 10
                color: theme ? theme.textMuted : "#64748B"
            }
            Text { text: "•"; color: theme ? theme.textMuted : "#64748B" }
            Text {
                text: "SUPPORT"
                font.family: theme ? theme.fontFamilyMono : "monospace"
                font.pixelSize: 10
                color: theme ? theme.textMuted : "#64748B"
            }
        }
    }

    // Version footer
    Text {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 16
        text: "SENTINELAI NODE: V2.4.0-BUILD.8821  //  AXYRIS SECURITY SYSTEMS"
        font.family: theme ? theme.fontFamilyMono : "monospace"
        font.pixelSize: 10
        color: theme ? theme.textDisabled : "#475569"
    }

    signal forgotPasswordRequested()
}
