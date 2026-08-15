import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"
import "../../cards"

Flickable {
    id: control
    
    property var theme
    readonly property bool isNarrow: width < 960
    readonly property bool isMobile: width < 720
    readonly property int pageMargin: isMobile ? 10 : (isNarrow ? 14 : 24)
    property var notificationController
    
    contentWidth: parent.width
    contentHeight: contentColumn.height + (theme ? theme.spacingXL : 48)
    clip: true
    
    Column {
        id: contentColumn
        width: parent.width
        spacing: theme ? theme.spacingL : 24
        anchors.top: parent.top
        anchors.topMargin: theme ? theme.spacingL : 24
        
        // Filters Header
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            spacing: theme ? theme.spacingM : 16
            
            Row {
                spacing: theme ? theme.spacingXS : 4
                
                Rectangle {
                    width: 60
                    height: 32
                    radius: theme ? theme.radiusS : 4
                    color: theme ? theme.primary : "#2563EB"
                    
                    Text {
                        anchors.centerIn: parent
                        text: "All"
                        font.pixelSize: theme ? theme.fontSizeXS : 10
                        font.bold: true
                        color: theme ? theme.onAccent : "#ffffff"
                    }
                }
                
                Rectangle {
                    width: 80
                    height: 32
                    radius: theme ? theme.radiusS : 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"
                    border.width: 1
                    
                    Text {
                        anchors.centerIn: parent
                        text: "Unread"
                        font.pixelSize: theme ? theme.fontSizeXS : 10
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                }
                
                Rectangle {
                    width: 150
                    height: 32
                    radius: theme ? theme.radiusS : 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"
                    border.width: 1
                    
                    Text {
                        anchors.centerIn: parent
                        text: "Mark all as read"
                        font.pixelSize: theme ? theme.fontSizeXS : 10
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                }
            }
            
            Item {
                width: 1
                height: parent.height
            }
            
            AppInput {
                width: 200
                placeholderText: "Search..."
                theme: control.theme
            }
        }
        
        // Notification Cards with Colored Borders
        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            spacing: theme ? theme.spacingS : 8
            
            // Critical Notification
            Rectangle {
                width: parent.width
                height: 80
                color: theme ? theme.surface : "#151C28"
                radius: theme ? theme.radiusS : 4
                border.color: theme ? theme.danger : "#EF4444"
                border.width: 3
                
                Row {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Rectangle {
                        width: 4
                        height: parent.height
                        color: theme ? theme.danger : "#EF4444"
                    }
                    
                    Column {
                        width: parent.width - 100
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Critical Security Alert"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "Unauthorized biometric bypass detected in Server Room A"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: "2 min ago"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                            color: theme ? theme.textDisabled : "#606060"
                        }
                    }
                }
            }
            
            // Warning Notification
            Rectangle {
                width: parent.width
                height: 80
                color: theme ? theme.surface : "#151C28"
                radius: theme ? theme.radiusS : 4
                border.color: theme ? theme.warning : "#F59E0B"
                border.width: 3
                
                Row {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Rectangle {
                        width: 4
                        height: parent.height
                        color: theme ? theme.warning : "#F59E0B"
                    }
                    
                    Column {
                        width: parent.width - 100
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Hardware Latency Warning"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "Camera Cam-SR-04 experiencing high latency (450ms)"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: "15 min ago"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                            color: theme ? theme.textDisabled : "#606060"
                        }
                    }
                }
            }
            
            // Success Notification
            Rectangle {
                width: parent.width
                height: 80
                color: theme ? theme.surface : "#151C28"
                radius: theme ? theme.radiusS : 4
                border.color: theme ? theme.success : "#10B981"
                border.width: 3
                
                Row {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Rectangle {
                        width: 4
                        height: parent.height
                        color: theme ? theme.success : "#10B981"
                    }
                    
                    Column {
                        width: parent.width - 100
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "System Update Complete"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "AI Model Vision-LLM-v4 updated successfully"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: "1 hour ago"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                            color: theme ? theme.textDisabled : "#606060"
                        }
                    }
                }
            }
            
            // Info Notification
            Rectangle {
                width: parent.width
                height: 80
                color: theme ? theme.surface : "#151C28"
                radius: theme ? theme.radiusS : 4
                border.color: theme ? theme.info : "#06B6D4"
                border.width: 3
                
                Row {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Rectangle {
                        width: 4
                        height: parent.height
                        color: theme ? theme.info : "#06B6D4"
                    }
                    
                    Column {
                        width: parent.width - 100
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "New Camera Added"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "Cam-PK-12 successfully provisioned and online"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: "2 hours ago"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                            color: theme ? theme.textDisabled : "#606060"
                        }
                    }
                }
            }
        }
        
        // Upcoming Maintenance Calendar Block
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: theme ? theme.cardHeightM : 120
            theme: control.theme
            
            Column {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingM : 16
                
                Row {
                    spacing: theme ? theme.spacingS : 8
                    
                    Text {
                        text: "📅"
                        font.pixelSize: theme ? theme.fontSizeL : 16
                    }
                    
                    Text {
                        text: "Upcoming Maintenance"
                        font.pixelSize: theme ? theme.fontSizeL : 16
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                }
                
                Rectangle {
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#1E293B"
                }
                
                Row {
                    spacing: theme ? theme.spacingM : 16
                    
                    Column {
                        width: 80
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "JAN 18"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            font.bold: true
                            color: theme ? theme.primary : "#2563EB"
                        }
                        
                        Text {
                            text: "02:00 UTC"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    Column {
                        // Width is derived from the outer Column (grandparent of
                        // this Column), not from the parent Row, to break the
                        // polish loop (Row width depends on children → child
                        // width reads parent width → re-polish forever).
                        width: parent.parent.width - 96 - (theme ? theme.spacingM : 16)
                        spacing: theme ? theme.spacingXS : 4

                        Text {
                            text: "Server Room A - Zone 4"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "Scheduled camera firmware update - 4 cameras affected"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                }
            }
        }
    }
    
    function formatTimestamp(timestamp) {
        if (!timestamp) return ""
        const date = new Date(timestamp)
        const now = new Date()
        const diff = now - date
        
        const minutes = Math.floor(diff / 60000)
        const hours = Math.floor(diff / 3600000)
        const days = Math.floor(diff / 86400000)
        
        if (minutes < 1) return "Just now"
        if (minutes < 60) return minutes + " min ago"
        if (hours < 24) return hours + " hours ago"
        return days + " days ago"
    }
}
