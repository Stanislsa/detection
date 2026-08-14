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
    property bool isDark: true

    signal searchSubmitted(string query)
    signal breadcrumbClicked(int index)
    signal notificationClicked()
    signal themeToggleRequested()
    signal menuToggleRequested()

    implicitHeight: theme.headerHeight
    color: theme.surface

    Behavior on color {
        ColorAnimation { duration: 280; easing.type: Easing.InOutQuad }
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 1
        color: theme.border
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: theme.spacingM
        anchors.rightMargin: theme.spacingM
        spacing: theme.spacingM

        // Hamburger / menu toggle (always visible for responsiveness)
        AppIconButton {
            Layout.preferredWidth: 32
            Layout.preferredHeight: 32
            iconName: "menu"
            theme: control.theme
            onClicked: control.menuToggleRequested()
        }

        // Breadcrumb
        Breadcrumb {
            Layout.fillWidth: false
            Layout.maximumWidth: 280
            theme: control.theme
            items: control.crumbs
            onItemClicked: (index) => control.breadcrumbClicked(index)
        }

        Item { Layout.fillWidth: true }

        // Global search
        Item {
            Layout.preferredWidth: Math.min(360, parent.width * 0.28)
            Layout.preferredHeight: theme.buttonHeight
            Layout.minimumWidth: 160

            AppInput {
                anchors.fill: parent
                theme: control.theme
                placeholderText: "Search alerts, cameras, logs…"
                leadingIcon: "search"
                mono: false
                onAccepted: control.searchSubmitted(text)
            }
        }

        // Theme toggle
        AppIconButton {
            Layout.preferredWidth: 32
            Layout.preferredHeight: 32
            iconName: control.isDark ? "sun" : "moon"
            theme: control.theme
            ToolTip.visible: hovered
            ToolTip.text: control.isDark ? "Switch to Light mode" : "Switch to Dark mode"
            onClicked: control.themeToggleRequested()
        }

        // Notification bell
        Item {
            Layout.preferredWidth: 32
            Layout.preferredHeight: 32

            AppIconButton {
                anchors.fill: parent
                iconName: "bell"
                theme: control.theme
                onClicked: control.notificationClicked()
            }

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
                z: 2

                Text {
                    id: badgeLabel
                    anchors.centerIn: parent
                    text: control.unreadCount > 99 ? "99+" : control.unreadCount.toString()
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeXS
                    font.weight: theme.weightBold
                    color: "#FFFFFF"
                }

                // Pulse animation on badge
                SequentialAnimation on scale {
                    running: control.unreadCount > 0
                    loops: Animation.Infinite
                    NumberAnimation { to: 1.15; duration: 600; easing.type: Easing.InOutQuad }
                    NumberAnimation { to: 1.0; duration: 600; easing.type: Easing.InOutQuad }
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
