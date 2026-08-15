import QtQuick 2.15
import "../theme"

Rectangle {
    id: control
    
    property var theme
    property string label: ""
    property real confidence: 0
    property color color: theme ? theme.primary : "#0078d4"
    
    color: "transparent"
    border.color: control.color
    border.width: theme ? theme.borderWidth : 2
    radius: theme ? theme.radiusS : 4
    
    // Label background
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        width: labelText.width + (theme ? theme.spacingS : 8) * 2
        height: labelText.height + (theme ? theme.spacingXS : 4) * 2
        color: control.color
        radius: theme ? theme.radiusS : 4
        
        Text {
            id: labelText
            anchors.centerIn: parent
            text: control.label + (control.confidence > 0 ? " " + Math.round(control.confidence * 100) + "%" : "")
            font.pixelSize: theme ? theme.fontSizeS : 12
            font.bold: true
            color: "#ffffff"
        }
    }
    
    // Corner accents
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        width: theme ? theme.spacingS : 8
        height: theme ? theme.spacingS : 8
        color: control.color
    }
    
    Rectangle {
        anchors.top: parent.top
        anchors.right: parent.right
        width: theme ? theme.spacingS : 8
        height: theme ? theme.spacingS : 8
        color: control.color
    }
    
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        width: theme ? theme.spacingS : 8
        height: theme ? theme.spacingS : 8
        color: control.color
    }
    
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        width: theme ? theme.spacingS : 8
        height: theme ? theme.spacingS : 8
        color: control.color
    }
}
