import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

Rectangle {
    id: control

    property var theme
    property string currentPage: "dashboard"
    property var icons: theme ? theme.iconsList : null

    implicitWidth: theme.sidebarWidth
    color: theme.surface

    Column {
        anchors.fill: parent
        spacing: 0

        // ---- Logo ----
        Rectangle {
            width: parent.width
            height: theme.headerHeight
            color: theme.surface

            Column {
                anchors.centerIn: parent
                spacing: 2
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "SENTINEL"
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeS
                    font.weight: theme.weightBold
                    font.letterSpacing: theme.letterSpacingL
                    color: theme.primary
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "AXYRIS SECURITY"
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeXS
                    font.letterSpacing: theme.letterSpacingL
                    color: theme.textMuted
                }
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: 1
                color: theme.border
            }
        }

        // ---- Navigation list ----
        Item {
            width: parent.width
            height: parent.height - logoFooterContainer.height - footerSpacer.height

            Column {
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: 2

                SidebarItem {
                    width: parent.width
                    title: "Dashboard"
                    glyph: control.icons ? control.icons.dashboard : "▣"
                    active: control.currentPage === "dashboard"
                    theme: control.theme
                    onClicked: control.pageChanged("dashboard")
                }
                SidebarItem {
                    width: parent.width
                    title: "Cameras"
                    glyph: control.icons ? control.icons.cameras : "□"
                    active: control.currentPage === "cameras"
                    theme: control.theme
                    onClicked: control.pageChanged("cameras")
                }
                SidebarItem {
                    width: parent.width
                    title: "Alerts"
                    glyph: control.icons ? control.icons.alerts : "⚠"
                    active: control.currentPage === "alerts" || control.currentPage === "incidents"
                    theme: control.theme
                    onClicked: control.pageChanged("alerts")
                }
                SidebarItem {
                    width: parent.width
                    title: "Events"
                    glyph: control.icons ? control.icons.events : "⧉"
                    active: control.currentPage === "events"
                    theme: control.theme
                    onClicked: control.pageChanged("events")
                }
                SidebarItem {
                    width: parent.width
                    title: "Users"
                    glyph: control.icons ? control.icons.users : "☰"
                    active: control.currentPage === "users"
                    theme: control.theme
                    onClicked: control.pageChanged("users")
                }
                SidebarItem {
                    width: parent.width
                    title: "AI Training"
                    glyph: control.icons ? control.icons.aiTraining : "⚙"
                    active: control.currentPage === "ai_training"
                    theme: control.theme
                    onClicked: control.pageChanged("ai_training")
                }
                SidebarItem {
                    width: parent.width
                    title: "Observability"
                    glyph: control.icons ? control.icons.observability : "⁂"
                    active: control.currentPage === "observability"
                    theme: control.theme
                    onClicked: control.pageChanged("observability")
                }
                SidebarItem {
                    width: parent.width
                    title: "System Health"
                    glyph: control.icons ? control.icons.systemHealth : "♥"
                    active: control.currentPage === "system_health" || control.currentPage === "health"
                    theme: control.theme
                    onClicked: control.pageChanged("system_health")
                }
                SidebarItem {
                    width: parent.width
                    title: "Settings"
                    glyph: control.icons ? control.icons.settings : "☸"
                    active: control.currentPage === "settings"
                    theme: control.theme
                    onClicked: control.pageChanged("settings")
                }
            }
        }

        // ---- Spacer pushes footer to the bottom ----
        Item {
            id: footerSpacer
            width: parent.width
            height: parent.height - logoFooterContainer.height
            visible: false
        }

        // ---- Footer: AXYRIS SECURITY ----
        Rectangle {
            id: logoFooterContainer
            width: parent.width
            height: 56
            color: theme.backgroundAlt

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                height: 1
                color: theme.border
            }

            Column {
                anchors.centerIn: parent
                spacing: 2

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 4
                    Rectangle { width: 6; height: 6; radius: 3; color: theme.success; anchors.verticalCenter: parent.verticalCenter }
                    Text {
                        text: "AXYRIS SECURITY"
                        font.family: theme.fontFamilyMono
                        font.pixelSize: theme.fontSizeXS
                        font.letterSpacing: theme.letterSpacingL
                        font.weight: theme.weightSemiBold
                        color: theme.textSecondary
                    }
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "v4.2.1-stable"
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeXS
                    color: theme.textMuted
                }
            }
        }
    }

    signal pageChanged(string page)
}