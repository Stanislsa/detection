import QtQuick 2.15
import QtQuick.Controls 2.15

CheckBox {
    id: control
    
    property var theme
    
    property color checkColor: theme ? theme.primary : "#0078d4"
    property color borderColor: theme ? theme.border : "#404040"
    property color textColor: theme ? theme.textPrimary : "#ffffff"
    
    implicitWidth: implicitIndicatorWidth + implicitContentWidth + leftPadding + rightPadding
    implicitHeight: Math.max(implicitIndicatorHeight, implicitContentHeight) + topPadding + bottomPadding
    
    spacing: theme ? theme.spacingS : 8
    
    indicator: Rectangle {
        implicitWidth: 20
        implicitHeight: 20
        x: control.leftPadding
        y: control.topPadding + control.availableHeight / 2 - height / 2
        width: implicitWidth
        height: implicitHeight
        color: control.checked ? control.checkColor : "transparent"
        border.color: control.borderColor
        border.width: 1
        radius: theme ? theme.radiusS : 4
        scale: control.pressed ? 0.9 : 1
        
        Behavior on color {
            ColorAnimation { duration: 150 }
        }
        
        Behavior on scale {
            NumberAnimation { duration: 150; easing.type: Easing.InOutQuad }
        }
        
        Rectangle {
            x: 5
            y: 5
            width: 10
            height: 10
            color: theme ? theme.textPrimary : "#ffffff"
            visible: control.checked
            scale: control.checked ? 1 : 0
            
            Behavior on scale {
                NumberAnimation { duration: 150; easing.type: Easing.InOutQuad }
            }
        }
    }
    
    contentItem: Text {
        text: control.text
        font: control.font
        color: control.textColor
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width + control.spacing
    }
}
