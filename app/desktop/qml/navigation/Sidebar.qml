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
    property bool collapsed: false

    implicitWidth: collapsed ? (theme ? theme.sidebarCollapsedWidth : 64)
                             : (theme ? theme.sidebarWidth : 240)
    color: theme.surface

    Behavior on color {
        ColorAnimation { duration: 280; easing.type: Easing.InOutQuad }
    }

    Column {
        anchors.fill: parent
        spacing: 0

        // ---- Logo ----
        Rectangle {
            width: parent.width
            height: theme.headerHeight
            color: theme.surface

            Behavior on color { ColorAnimation { duration: 280 } }

            // Expanded logo
            Column {
                anchors.centerIn: parent
                spacing: 2
                visible: !control.collapsed
                opacity: control.collapsed ? 0 : 1
                Behavior on opacity { NumberAnimation { duration: 160 } }

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

            // Collapsed icon
            Rectangle {
                anchors.centerIn: parent
                width: 28
                height: 28
                radius: 6
                color: theme.primary
                visible: control.collapsed
                opacity: control.collapsed ? 1 : 0
                Behavior on opacity { NumberAnimation { duration: 160 } }

                Text {
                    anchors.centerIn: parent
                    text: "S"
                    font.family: theme.fontFamilyMono
                    font.pixelSize: 14
                    font.weight: theme.weightBold
                    color: "#FFFFFF"
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
        Flickable {
            width: parent.width
            height: parent.height - theme.headerHeight - 56
            contentHeight: navColumn.height
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            Column {
                id: navColumn
                width: parent.width
                spacing: 2
                topPadding: 8
                bottomPadding: 8

                SidebarItem {
                    width: parent.width
                    title: "Dashboard"
                    glyph: control.icons ? control.icons.dashboard : "▣"
                    active: control.currentPage === "dashboard"
                    theme: control.theme
                    collapsed: control.collapsed
                    onClicked: control.pageChanged("dashboard")
                }
                SidebarItem {
                    width: parent.width
                    title: "Cameras"
                    glyph: control.icons ? control.icons.cameras : "□"
                    active: control.currentPage === "cameras"
                    theme: control.theme
                    collapsed: control.collapsed
                    onClicked: control.pageChanged("cameras")
                }
                SidebarItem {
                    width: parent.width
                    title: "Alerts"
                    glyph: control.icons ? control.icons.alerts : "⚠"
                    active: control.currentPage === "alerts" || control.currentPage === "incidents"
                    theme: control.theme
                    collapsed: control.collapsed
                    onClicked: control.pageChanged("alerts")
                }
                SidebarItem {
                    width: parent.width
                    title: "Events"
                    glyph: control.icons ? control.icons.events : "⧉"
                    active: control.currentPage === "events"
                    theme: control.theme
                    collapsed: control.collapsed
                    onClicked: control.pageChanged("events")
                }
                SidebarItem {
                    width: parent.width
                    title: "Users"
                    glyph: control.icons ? control.icons.users : "☰"
                    active: control.currentPage === "users"
                    theme: control.theme
                    collapsed: control.collapsed
                    onClicked: control.pageChanged("users")
                }
                SidebarItem {
                    width: parent.width
                    title: "AI Training"
                    glyph: control.icons ? control.icons.aiTraining : "⚙"
                    active: control.currentPage === "ai_training"
                    theme: control.theme
                    collapsed: control.collapsed
                    onClicked: control.pageChanged("ai_training")
                }
                SidebarItem {
                    width: parent.width
                    title: "Observability"
                    glyph: control.icons ? control.icons.observability : "⁂"
                    active: control.currentPage === "observability"
                    theme: control.theme
                    collapsed: control.collapsed
                    onClicked: control.pageChanged("observability")
                }
                SidebarItem {
                    width: parent.width
                    title: "System Health"
                    glyph: control.icons ? control.icons.systemHealth : "♥"
                    active: control.currentPage === "system_health" || control.currentPage === "health"
                    theme: control.theme
                    collapsed: control.collapsed
                    onClicked: control.pageChanged("system_health")
                }
                SidebarItem {
                    width: parent.width
                    title: "Settings"
                    glyph: control.icons ? control.icons.settings : "☸"
                    active: control.currentPage === "settings"
                    theme: control.theme
                    collapsed: control.collapsed
                    onClicked: control.pageChanged("settings")
                }
            }
        }

        // ---- Footer ----
        Rectangle {
            width: parent.width
            height: 56
            color: theme.backgroundAlt

            Behavior on color { ColorAnimation { duration: 280 } }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                height: 1
                color: theme.border
            }

            // Expanded footer
            Column {
                anchors.centerIn: parent
                spacing: 2
                visible: !control.collapsed
                opacity: control.collapsed ? 0 : 1

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 4
                    Rectangle {
                        width: 6; height: 6; radius: 3
                        color: theme.success
                        anchors.verticalCenter: parent.verticalCenter
                    }
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

            // Collapsed footer indicator
            Rectangle {
                anchors.centerIn: parent
                width: 8; height: 8; radius: 4
                color: theme.success
                visible: control.collapsed
            }
        }
    }

    signal pageChanged(string page)
}
