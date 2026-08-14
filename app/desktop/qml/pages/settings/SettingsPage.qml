import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Item {
    id: control
    property var theme
    property var settingsController

    property string activeTab: "General"  // General | Camera | AI Engine | Storage | Security | Appearance

    readonly property var tabs: ["General", "Camera", "AI Engine", "Storage", "Security", "Alerts", "Telegram", "Appearance"]

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16

        Column {
            spacing: 4
            Text { text: "SYSTEM CONFIGURATION"; font.pixelSize: theme ? theme.fontSizeXXL : 20; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
            Text { text: "Manage enterprise security policies, hardware acceleration, and data retention parameters."; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8" }
        }

        // Tabs
        Rectangle {
            Layout.fillWidth: true; height: 40
            radius: 4; color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"; border.width: 1

            Row {
                anchors.fill: parent; anchors.margins: 4; spacing: 4
                Repeater {
                    model: control.tabs
                    Rectangle {
                        width: tabLab.implicitWidth + 24; height: parent.height
                        radius: 4
                        color: control.activeTab === modelData ? (theme ? theme.primary : "#2563EB") : "transparent"
                        Text {
                            id: tabLab; anchors.centerIn: parent; text: modelData
                            font.pixelSize: 12; font.weight: control.activeTab === modelData ? Font.DemiBold : Font.Normal
                            color: control.activeTab === modelData ? "#FFF" : (theme ? theme.textSecondary : "#94A3B8")
                        }
                        MouseArea {
                            anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                            onClicked: control.activeTab = modelData
                        }
                    }
                }
            }
        }

        // Content
        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 16

            // Main form
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 2
                radius: 4; color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                clip: true

                Flickable {
                    anchors.fill: parent; anchors.margins: 20
                    contentHeight: formCol.height; clip: true
                    boundsBehavior: Flickable.StopAtBounds

                    Column {
                        id: formCol; width: parent.width; spacing: 20

                        // ---- GENERAL ----
                        Column {
                            width: parent.width; spacing: 12
                            visible: control.activeTab === "General"
                            Text { text: "System Information"; font.pixelSize: 14; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                            GridLayout {
                                width: parent.width; columns: 2; columnSpacing: 16; rowSpacing: 12
                                Column {
                                    Layout.fillWidth: true; spacing: 4
                                    Text { text: "NODE IDENTIFIER"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                    AppInput { width: parent.width; theme: control.theme; text: "SENTINEL-HQ-01" }
                                }
                                Column {
                                    Layout.fillWidth: true; spacing: 4
                                    Text { text: "ORGANIZATION"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                    AppInput { width: parent.width; theme: control.theme; text: "Axyris Enterprise Security" }
                                }
                                Column {
                                    Layout.fillWidth: true; spacing: 4
                                    Text { text: "SYSTEM TIMEZONE"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                    AppInput { width: parent.width; theme: control.theme; text: "UTC (Coordinated Universal Time)" }
                                }
                                Column {
                                    Layout.fillWidth: true; spacing: 4
                                    Text { text: "INTERFACE LANGUAGE"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                    AppInput { width: parent.width; theme: control.theme; text: "English (US)" }
                                }
                            }
                            Text { text: "Network & Connectivity"; font.pixelSize: 14; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                            Row {
                                spacing: 12
                                Text { text: "Static IP Configuration"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; anchors.verticalCenter: parent.verticalCenter }
                                AppSwitch { theme: control.theme; checked: true }
                            }
                            GridLayout {
                                width: parent.width; columns: 2; columnSpacing: 16; rowSpacing: 12
                                Column {
                                    Layout.fillWidth: true; spacing: 4
                                    Text { text: "IP ADDRESS"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                    AppInput { width: parent.width; theme: control.theme; text: "10.0.4.122"; mono: true }
                                }
                                Column {
                                    Layout.fillWidth: true; spacing: 4
                                    Text { text: "SUBNET MASK"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                    AppInput { width: parent.width; theme: control.theme; text: "255.255.255.0"; mono: true }
                                }
                            }
                        }

                        // ---- TELEGRAM ----
                        Column {
                            width: parent.width
                            spacing: 8
                            visible: control.activeTab === "Telegram"
                            TelegramSettings {
                                width: parent.width
                                theme: control.theme
                                telegramController: typeof TelegramController !== "undefined" ? TelegramController : null
                            }
                        }

                        // ---- ALERTS (real-time) ----
                        Column {
                            width: parent.width
                            spacing: 8
                            visible: control.activeTab === "Alerts"
                            NotificationSettings {
                                width: parent.width
                                theme: control.theme
                                alertController: typeof AlertController !== "undefined" ? AlertController : null
                            }
                        }

                        // ---- APPEARANCE / THEME ----
                        Column {
                            width: parent.width; spacing: 16
                            visible: control.activeTab === "Appearance"

                            Text { text: "Theme Mode"; font.pixelSize: 14; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                            Text { text: "Choose between dark and light interface themes. Changes apply instantly."; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8"; width: parent.width; wrapMode: Text.WordWrap }

                            Row {
                                spacing: 16
                                // Dark card
                                Rectangle {
                                    width: 160; height: 120; radius: 8
                                    color: "#0B0E14"
                                    border.color: theme && theme.isDark ? (theme.primary) : "#334155"
                                    border.width: theme && theme.isDark ? 2 : 1
                                    Column {
                                        anchors.centerIn: parent; spacing: 8
                                        AppIcon { anchors.horizontalCenter: parent.horizontalCenter; width: 28; height: 28; iconName: "moon"; iconColor: "#94A3B8" }
                                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: "Dark"; font.pixelSize: 13; font.weight: Font.DemiBold; color: "#E5E7EB" }
                                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: "Default SOC mode"; font.pixelSize: 10; color: "#64748B" }
                                    }
                                    MouseArea {
                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                        onClicked: if (theme) theme.setDark(true)
                                    }
                                }
                                // Light card
                                Rectangle {
                                    width: 160; height: 120; radius: 8
                                    color: "#F1F5F9"
                                    border.color: theme && !theme.isDark ? "#2563EB" : "#CBD5E1"
                                    border.width: theme && !theme.isDark ? 2 : 1
                                    Column {
                                        anchors.centerIn: parent; spacing: 8
                                        AppIcon { anchors.horizontalCenter: parent.horizontalCenter; width: 28; height: 28; iconName: "sun"; iconColor: "#475569" }
                                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: "Light"; font.pixelSize: 13; font.weight: Font.DemiBold; color: "#0F172A" }
                                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: "Day operations"; font.pixelSize: 10; color: "#64748B" }
                                    }
                                    MouseArea {
                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                        onClicked: if (theme) theme.setDark(false)
                                    }
                                }
                            }

                            Text { text: "Accent Color"; font.pixelSize: 14; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                            Row {
                                spacing: 10
                                Repeater {
                                    model: ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4"]
                                    Rectangle {
                                        width: 32; height: 32; radius: 16; color: modelData
                                        border.color: "#FFFFFF44"; border.width: 2
                                    }
                                }
                            }

                            Row {
                                spacing: 12
                                Text { text: "Reduce motion / animations"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; anchors.verticalCenter: parent.verticalCenter }
                                AppSwitch { theme: control.theme; checked: false }
                            }
                            Row {
                                spacing: 12
                                Text { text: "Compact density"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; anchors.verticalCenter: parent.verticalCenter }
                                AppSwitch { theme: control.theme; checked: false }
                            }
                        }

                        // ---- SECURITY ----
                        Column {
                            width: parent.width; spacing: 12
                            visible: control.activeTab === "Security"
                            Text { text: "Security Policies"; font.pixelSize: 14; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                            Row { spacing: 12; Text { text: "Enforce MFA for all operators"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; anchors.verticalCenter: parent.verticalCenter }; AppSwitch { theme: control.theme; checked: true } }
                            Row { spacing: 12; Text { text: "Session timeout (30 min)"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; anchors.verticalCenter: parent.verticalCenter }; AppSwitch { theme: control.theme; checked: true } }
                            Row { spacing: 12; Text { text: "Audit log retention (90 days)"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; anchors.verticalCenter: parent.verticalCenter }; AppSwitch { theme: control.theme; checked: true } }
                        }

                        // ---- CAMERA / AI / STORAGE placeholders ----
                        Column {
                            width: parent.width; spacing: 12
                            visible: control.activeTab === "Camera" || control.activeTab === "AI Engine" || control.activeTab === "Storage"
                            Text {
                                text: control.activeTab + " Settings"
                                font.pixelSize: 14; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB"
                            }
                            Text {
                                text: "Configure " + control.activeTab.toLowerCase() + " parameters for the SentinelAI node."
                                font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8"
                            }
                            Row { spacing: 12; Text { text: "Enable " + control.activeTab + " module"; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB"; anchors.verticalCenter: parent.verticalCenter }; AppSwitch { theme: control.theme; checked: true } }
                        }
                    }
                }
            }

            // Right sidebar
            ColumnLayout {
                Layout.preferredWidth: 260; Layout.fillHeight: true; spacing: 12

                Rectangle {
                    Layout.fillWidth: true; Layout.preferredHeight: 160
                    radius: 4; color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                    Column {
                        anchors.fill: parent; anchors.margins: 16; spacing: 8
                        Text { text: "SYSTEM HEALTH SUMMARY"; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; font.weight: Font.Bold; color: theme ? theme.primary : "#2563EB" }
                        Row { width: parent.width; Text { text: "Software Version"; width: parent.width - 90; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8" }; Text { text: "v4.2.8-stable"; font.pixelSize: 12; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textPrimary : "#E5E7EB" } }
                        Row { width: parent.width; Text { text: "Last Update"; width: parent.width - 110; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8" }; Text { text: "2024-05-12"; font.pixelSize: 12; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textPrimary : "#E5E7EB" } }
                        Row { width: parent.width; Text { text: "System Uptime"; width: parent.width - 110; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8" }; Text { text: "142 days"; font.pixelSize: 12; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textPrimary : "#E5E7EB" } }
                        AppButton { width: parent.width; text: "Check for Updates"; variant: "secondary"; theme: control.theme }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true; Layout.preferredHeight: 120
                    radius: 4; color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                    Column {
                        anchors.fill: parent; anchors.margins: 16; spacing: 10
                        Text { text: "MAINTENANCE ACTIONS"; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; font.weight: Font.Bold; color: theme ? theme.critical : "#EF4444" }
                        AppButton { width: parent.width; text: "Restart Web Service"; variant: "secondary"; theme: control.theme }
                        AppButton { width: parent.width; text: "Purge System Logs"; variant: "danger"; theme: control.theme }
                    }
                }

                Item { Layout.fillHeight: true }

                RowLayout {
                    Layout.fillWidth: true
                    AppButton { Layout.fillWidth: true; text: "Discard Changes"; variant: "secondary"; theme: control.theme }
                    AppButton { Layout.fillWidth: true; text: "Commit Changes"; variant: "primary"; theme: control.theme }
                }
            }
        }
    }
}
