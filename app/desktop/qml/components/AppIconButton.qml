import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: control

    property var theme
    // Prefer iconName (SVG from assets/icons). Falls back to text glyph.
    property string iconName: ""
    property color backgroundColor: "transparent"
    property color hoverColor: theme ? theme.surfaceElevated : "#3d3d3d"
    property color pressedColor: theme ? theme.surface : "#2d2d2d"
    property color iconColor: theme ? theme.textPrimary : "#ffffff"

    implicitWidth: 32
    implicitHeight: 32

    background: Rectangle {
        implicitWidth: 32
        implicitHeight: 32
        color: control.pressed ? control.pressedColor :
               control.hovered ? control.hoverColor :
               control.backgroundColor
        radius: theme ? theme.radiusM : 6

        Behavior on color {
            ColorAnimation { duration: 150 }
        }
    }

    contentItem: Item {
        anchors.fill: parent

        AppIcon {
            anchors.centerIn: parent
            width: theme ? theme.iconSizeM : 18
            height: theme ? theme.iconSizeM : 18
            visible: control.iconName !== ""
            iconName: control.iconName
            iconColor: control.iconColor
            theme: control.theme
        }

        Text {
            anchors.centerIn: parent
            visible: control.iconName === ""
            text: control.text
            color: control.iconColor
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: theme ? theme.iconSizeM : 18
        }
    }
}
