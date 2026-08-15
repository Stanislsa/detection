import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"
import "../../cards"

Flickable {
    id: control
    
    property var theme
    property var alertController
    property string alertId: ""
    
    contentWidth: parent.width
    contentHeight: contentColumn.height + (theme ? theme.spacingXL : 48)
    clip: true
    
    Component.onCompleted: {
        if (alertId) {
            alertController.selectAlert(alertId)
        }
    }
    
    Column {
        id: contentColumn
        width: parent.width
        spacing: theme ? theme.spacingL : 24
        anchors.top: parent.top
        anchors.topMargin: theme ? theme.spacingL : 24
        
        // Back button
        AppButton {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "← Back to Alerts"
            theme: control.theme
            onClicked: control.backRequested()
        }
        
        // Alert Detail Card
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: detailColumn.height + (theme ? theme.spacingM : 16) * 2
            theme: control.theme
            
            Column {
                id: detailColumn
                width: parent.width
                anchors.margins: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingM : 16
                
                // Header
                Row {
                    width: parent.width
                    spacing: theme ? theme.spacingM : 16
                    
                    Column {
                        width: parent.width - 200
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: alertController.selectedAlert.title || "Alert Details"
                            font.pixelSize: theme ? theme.fontSizeXXL : 24
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: alertController.selectedAlert.camera_name || "Unknown Camera"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    Item {
                        width: 1
                        height: parent.height
                    }
                    
                    AppBadge {
                        text: alertController.selectedAlert.priority || "UNKNOWN"
                        theme: control.theme
                        color: getPriorityColor(alertController.selectedAlert.priority)
                    }
                    
                    AppBadge {
                        text: alertController.selectedAlert.status || "UNKNOWN"
                        theme: control.theme
                        color: getStatusColor(alertController.selectedAlert.status)
                    }
                }
                
                Rectangle {
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#404040"
                }
                
                // Description
                Column {
                    width: parent.width
                    spacing: theme ? theme.spacingXS : 4
                    
                    Text {
                        text: "Description"
                        font.pixelSize: theme ? theme.fontSizeS : 12
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    Text {
                        text: alertController.selectedAlert.description || "No description available"
                        font.pixelSize: theme ? theme.fontSizeM : 14
                        color: theme ? theme.textSecondary : "#a0a0a0"
                        width: parent.width
                        wrapMode: Text.WordWrap
                    }
                }
                
                // Details Grid
                GridLayout {
                    width: parent.width
                    columns: 2
                    columnSpacing: theme ? theme.spacingLG : 24
                    rowSpacing: theme ? theme.spacingM : 16
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Location"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: alertController.selectedAlert.location || "Unknown"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                    }
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Timestamp"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: formatTimestamp(alertController.selectedAlert.timestamp)
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                    }
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Alert Type"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: alertController.selectedAlert.alert_type || "Unknown"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                    }
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Camera ID"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: alertController.selectedAlert.camera_id || "N/A"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                    }
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Acknowledged By"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: alertController.selectedAlert.acknowledged_by || "Not acknowledged"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                    }
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Acknowledged At"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: formatTimestamp(alertController.selectedAlert.acknowledged_at)
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                    }
                }
                
                Rectangle {
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#404040"
                }
                
                // Actions
                Row {
                    width: parent.width
                    spacing: theme ? theme.spacingM : 16
                    
                    AppButton {
                        text: "Acknowledge"
                        theme: control.theme
                        enabled: alertController.selectedAlert.status === "OPEN"
                        onClicked: alertController.acknowledgeAlert(alertController.selectedAlertId)
                    }
                    
                    AppButton {
                        text: "Investigating"
                        theme: control.theme
                        onClicked: alertController.updateAlertStatus(alertController.selectedAlertId, "INVESTIGATING")
                    }
                    
                    AppButton {
                        text: "Resolve"
                        theme: control.theme
                        onClicked: alertController.updateAlertStatus(alertController.selectedAlertId, "RESOLVED")
                    }
                    
                    Item {
                        width: 1
                        height: parent.height
                    }
                    
                    AppButton {
                        text: "View Camera"
                        theme: control.theme
                        onClicked: control.cameraViewRequested(alertController.selectedAlert.camera_id)
                    }
                }
            }
        }
    }
    
    signal backRequested()
    signal cameraViewRequested(string cameraId)
    
    function getPriorityColor(priority) {
        switch(priority) {
            case "CRITICAL": return theme ? theme.danger : "#d13438"
            case "HIGH": return theme ? theme.warning : "#ff8c00"
            case "MEDIUM": return theme ? theme.info : "#0078d4"
            case "LOW": return theme ? theme.success : "#107c10"
            default: return theme ? theme.border : "#404040"
        }
    }
    
    function getStatusColor(status) {
        switch(status) {
            case "OPEN": return theme ? theme.danger : "#d13438"
            case "ACKNOWLEDGED": return theme ? theme.warning : "#ff8c00"
            case "INVESTIGATING": return theme ? theme.info : "#0078d4"
            case "RESOLVED": return theme ? theme.success : "#107c10"
            default: return theme ? theme.border : "#404040"
        }
    }
    
    function formatTimestamp(timestamp) {
        if (!timestamp) return "N/A"
        var date = new Date(timestamp)
        return date.toLocaleString()
    }
}
