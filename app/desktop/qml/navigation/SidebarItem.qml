import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"
import "../components"

Rectangle {
    id: control
    property var theme
    property string title: ""
    property string glyph: ""     // new — single-character symbol from Icons registry
    property string icon: ""      // legacy alias for glyph (back-compat)
    property bool active: false
    property bool hovered: false

    implicitHeight: 40
    color: control.active ? (theme ? theme.surfaceElevated : "#1E293B")
         : control.hovered ? (theme ? theme.surfaceAlt : "#1B2433")
         : "transparent"

    Behavior on color { ColorAnimation { duration: 150 } }

    // Left rail (4px) for active item
    Rectangle {
        visible: control.active
        width: 3
        height: parent.height
        color: theme ? theme.primary : "#2563EB"

        Behavior on color { ColorAnimation { duration: 150 } }
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: theme ? theme.spacingM : 16
        anchors.rightMargin: theme ? theme.spacingM : 16
        spacing: theme ? theme.spacingM : 16

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
        }

        Item { width: 1; height: parent.height }
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