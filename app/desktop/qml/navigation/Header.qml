import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

Rectangle {
    id: control

    property var theme
    property string title: "Dashboard"
    property var crumbs: ["SentinelAI", "Dashboard"]
    property string searchQuery: ""
    property int unreadCount: 0

    signal searchSubmitted(string query)
    signal breadcrumbClicked(int index)
    signal notificationClicked()

    implicitHeight: theme.headerHeight
    color: theme.surface

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 1
        color: theme.border
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: theme.spacingM
        anchors.rightMargin: theme.spacingM
        spacing: theme.spacingM

        // Breadcrumb
        Breadcrumb {
            anchors.verticalCenter: parent.verticalCenter
            theme: control.theme
            items: control.crumbs
            onItemClicked: (index) => control.breadcrumbClicked(index)
        }

        Item { width: 1; height: parent.height }

        // Global search (center)
        Item {
            width: 360
            height: theme.buttonHeight
            anchors.verticalCenter: parent.verticalCenter

            AppInput {
                anchors.fill: parent
                theme: control.theme
                placeholderText: "Search alerts, cameras, logs…"
                leadingIcon: "⌕"
                mono: false
                onAccepted: control.searchSubmitted(text)
            }
        }

        Item { width: 1; height: parent.height }

        // Right-side icons
        Row {
            anchors.verticalCenter: parent.verticalCenter
            spacing: theme.spacingS

            Item {
                width: 32
                height: 32
                anchors.verticalCenter: parent.verticalCenter

                AppIconButton {
                    anchors.fill: parent
                    text: "⌕"
                    theme: control.theme
                    onClicked: control.searchSubmitted("")
                }
            }

            Item {
                width: 32
                height: 32
                anchors.verticalCenter: parent.verticalCenter

                AppIconButton {
                    anchors.fill: parent
                    text: "ⓘ"
                    theme: control.theme
                    onClicked: control.notificationClicked()
                }

                // Badge
                Rectangle {
                    visible: control.unreadCount > 0
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: -2
                    width: badgeLabel.implicitWidth + 8
                    height: 16
                    radius: 8
                    color: theme.critical
                    border.color: theme.surface
                    border.width: 1

                    Text {
                        id: badgeLabel
                        anchors.centerIn: parent
                        text: control.unreadCount > 99 ? "99+" : control.unreadCount.toString()
                        font.family: theme.fontFamilyMono
                        font.pixelSize: theme.fontSizeXS
                        font.weight: theme.weightBold
                        color: "#FFFFFF"
                    }
                }
            }

            // Avatar chip
            AvatarChip {
                theme: control.theme
                name: "Alex Rivers"
                role: "SOC Analyst"
                initials: "AR"
            }
        }
    }
}