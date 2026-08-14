import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: control
    
    property var theme
    
    property color backgroundColor: "transparent"
    property color hoverColor: theme ? theme.surfaceElevated : "#3d3d3d"
    property color pressedColor: theme ? theme.surface : "#2d2d2d"
    property color iconColor: theme ? theme.textPrimary : "#ffffff"
    
    implicitWidth: theme ? theme.iconSizeXL + theme.spacingM : 48
    implicitHeight: theme ? theme.iconSizeXL + theme.spacingM : 48
    
    background: Rectangle {
        implicitWidth: theme ? theme.iconSizeXL + theme.spacingM : 48
        implicitHeight: theme ? theme.iconSizeXL + theme.spacingM : 48
        color: control.pressed ? control.pressedColor :
               control.hovered ? control.hoverColor :
               control.backgroundColor
        radius: theme ? theme.radiusM : 8
        
        Behavior on color {
            ColorAnimation { duration: 150 }
        }
    }
    
    contentItem: Text {
        text: control.text
        color: control.iconColor
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.pixelSize: theme ? theme.iconSizeL : 24
    }
}
