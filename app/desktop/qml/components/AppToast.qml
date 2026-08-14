import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"

Rectangle {
    id: control
    
    property var theme
    property string message: ""
    property string type: "info" // info, success, warning, danger
    
    implicitWidth: Math.min(400, parent.width - theme.spacingXL * 2)
    implicitHeight: label.implicitHeight + theme.spacingM * 2
    
    color: {
        switch(control.type) {
            case "success": return theme.success
            case "warning": return theme.warning
            case "danger": return theme.danger
            default: return theme.info
        }
    }
    radius: theme.radiusM
    
    Row {
        anchors.fill: parent
        anchors.margins: theme.spacingM
        spacing: theme.spacingM
        
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: {
                switch(control.type) {
                    case "success": return "✓"
                    case "warning": return "⚠"
                    case "danger": return "✕"
                    default: return "ℹ"
                }
            }
            font.pixelSize: theme.fontSizeL
            color: theme.textPrimary
        }
        
        Text {
            id: label
            anchors.verticalCenter: parent.verticalCenter
            text: control.message
            font.pixelSize: theme.fontSizeM
            color: theme.textPrimary
        }
    }
    
    Timer {
        interval: 3000
        onTriggered: control.visible = false
        running: control.visible
    }
}
