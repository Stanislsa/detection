import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"
import "../components"

Rectangle {
    id: control
    property var theme
    property string title: ""
    property string glyph: ""
    property string icon: ""
    property bool active: false
    property bool hovered: false
    property bool collapsed: false

    implicitHeight: 40
    color: control.active ? (theme ? theme.surfaceElevated : "#1E293B")
         : control.hovered ? (theme ? theme.surfaceAlt : "#1B2433")
         : "transparent"

    Behavior on color { ColorAnimation { duration: 150 } }

    // Left rail for active item
    Rectangle {
        visible: control.active
        width: 3
        height: parent.height
        color: theme ? theme.primary : "#2563EB"
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Tooltip when collapsed
    ToolTip {
        visible: control.collapsed && control.hovered
        text: control.title
        delay: 200
        timeout: 3000
    }

    Item {
        anchors.fill: parent
        anchors.leftMargin: control.collapsed ? 0 : (theme ? theme.spacingM : 16)
        anchors.rightMargin: control.collapsed ? 0 : (theme ? theme.spacingM : 16)

        // Collapsed: centered icon only
        AppIcon {
            anchors.centerIn: parent
            visible: control.collapsed
            width: theme ? theme.iconSizeM : 16
            height: theme ? theme.iconSizeM : 16
            iconName: control.glyph !== "" ? control.glyph : control.icon
            iconColor: control.active ? (theme ? theme.primary : "#2563EB")
                 : (control.hovered ? (theme ? theme.textPrimary : "#E5E7EB")
                                    : (theme ? theme.textSecondary : "#94A3B8"))
            Behavior on iconColor { ColorAnimation { duration: 150 } }
        }

        // Expanded: icon + text
        Row {
            anchors.fill: parent
            spacing: theme ? theme.spacingM : 16
            visible: !control.collapsed
            opacity: control.collapsed ? 0 : 1
            Behavior on opacity { NumberAnimation { duration: 140 } }

            AppIcon {
                anchors.verticalCenter: parent.verticalCenter
                width: theme ? theme.iconSizeM : 16
                height: theme ? theme.iconSizeM : 16
                iconName: control.glyph !== "" ? control.glyph : control.icon
                iconColor: control.active ? (theme ? theme.primary : "#2563EB")
                     : (control.hovered ? (theme ? theme.textPrimary : "#E5E7EB")
                                        : (theme ? theme.textSecondary : "#94A3B8"))
                Behavior on iconColor { ColorAnimation { duration: 150 } }
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: control.title
                font.family: theme ? theme.fontFamily : "Inter"
                font.pixelSize: theme ? theme.fontSizeM : 13
                font.weight: control.active && theme ? theme.weightSemiBold : Font.Normal
                color: control.active ? (theme ? theme.textPrimary : "#E5E7EB")
                     : (control.hovered ? (theme ? theme.textPrimary : "#E5E7EB")
                                        : (theme ? theme.textSecondary : "#94A3B8"))
                Behavior on color { ColorAnimation { duration: 150 } }
                elide: Text.ElideRight
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onEntered: control.hovered = true
        onExited: control.hovered = false
        onClicked: control.clicked()
    }

    signal clicked()
}
