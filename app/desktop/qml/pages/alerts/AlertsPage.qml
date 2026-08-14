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
    
    contentWidth: parent.width
    contentHeight: contentColumn.height + (theme ? theme.spacingXL : 48)
    clip: true
    
    Column {
        id: contentColumn
        width: parent.width
        spacing: theme ? theme.spacingL : 24
        anchors.top: parent.top
        anchors.topMargin: theme ? theme.spacingL : 24
        
        // Split-Screen Layout
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            spacing: theme ? theme.spacingM : 16
            
            // Left Side - Incident Table
            AppCard {
                width: (parent.width - (theme ? theme.spacingM : 16)) / 2
                height: theme ? theme.cardHeightXXL : 600
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    // Severity Filter Bar
                    Row {
                        width: parent.width
                        spacing: theme ? theme.spacingXS : 4
                        
                        Repeater {
                            model: ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
                            
                            Rectangle {
                                width: (parent.width - (theme ? theme.spacingXS : 4) * 4) / 5
                                height: 32
                                radius: theme ? theme.radiusS : 4
                                color: {
                                    if (index === 0) return theme ? theme.primary : "#2563EB"
                                    if (modelData === "CRITICAL") return theme ? theme.danger : "#EF4444"
                                    if (modelData === "HIGH") return theme ? theme.warning : "#F59E0B"
                                    return theme ? theme.surface : "#151C28"
                                }
                                border.color: theme ? theme.border : "#1E293B"
                                border.width: 1
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: modelData
                                    font.pixelSize: theme ? theme.fontSizeXS : 10
                                    font.bold: true
                                    color: "#ffffff"
                                }
                            }
                        }
                    }
                    
                    Row {
                        width: parent.width
                        spacing: theme ? theme.spacingS : 8
                        
                        AppInput {
                            width: parent.width - 100
                            placeholderText: "Search incidents..."
                            theme: control.theme
                        }
                        
                        Text {
                            text: "2 Critical"
                            font.pixelSize: theme ? fontSizeXS : 10
                            font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                            color: theme ? theme.danger : "#EF4444"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        
                        Text {
                            text: "Queue: 14 Active"
                            font.pixelSize: theme ? fontSizeXS : 10
                            font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                            color: theme ? theme.textSecondary : "#a0a0a0"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                    
                    Rectangle {
                        width: parent.width
                        height: 1
                        color: theme ? theme.border : "#1E293B"
                    }
                    
                    // Incident Table Header
                    Row {
                        width: parent.width
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "ID"
                            font.pixelSize: theme ? fontSizeXS : 10
                            font.bold: true
                            color: theme ? theme.textSecondary : "#a0a0a0"
                            width: 80
                        }
                        
                        Text {
                            text: "Timestamp"
                            font.pixelSize: theme ? fontSizeXS : 10
                            font.bold: true
                            color: theme ? theme.textSecondary : "#a0a0a0"
                            width: 100
                        }
                        
                        Text {
                            text: "Severity"
                            font.pixelSize: theme ? fontSizeXS : 10
                            font.bold: true
                            color: theme ? theme.textSecondary : "#a0a0a0"
                            width: 80
                        }
                        
                        Text {
                            text: "Event Details"
                            font.pixelSize: theme ? fontSizeXS : 10
                            font.bold: true
                            color: theme ? theme.textSecondary : "#a0a0a0"
                            Layout.fillWidth: true
                        }
                        
                        Text {
                            text: "Status"
                            font.pixelSize: theme ? fontSizeXS : 10
                            font.bold: true
                            color: theme ? theme.textSecondary : "#a0a0a0"
                            width: 100
                        }
                    }
                    
                    // Incident List
                    ListView {
                        width: parent.width
                        height: parent.height - 120
                        model: [
                            {id: "ALRT-89214", timestamp: "2m ago", severity: "Critical", details: "Unauthorized Access", status: "Pending"},
                            {id: "ALRT-89213", timestamp: "5m ago", severity: "High", details: "Motion Detected", status: "Acknowledged"},
                            {id: "ALRT-89212", timestamp: "12m ago", severity: "Medium", details: "Zone Breach", status: "Resolved"},
                            {id: "ALRT-89211", timestamp: "18m ago", severity: "Low", details: "Sensor Alert", status: "Pending"}
                        ]
                        spacing: theme ? theme.spacingXS : 4
                        clip: true
                        
                        delegate: Row {
                            width: parent.width
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 20
                                height: 20
                                radius: 2
                                color: "transparent"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☐"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: theme ? theme.textSecondary : "#a0a0a0"
                                }
                            }
                            
                            Text {
                                text: modelData.id
                                font.pixelSize: theme ? fontSizeXS : 10
                                font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                color: theme ? theme.textSecondary : "#a0a0a0"
                                width: 80
                            }
                            
                            Text {
                                text: modelData.timestamp
                                font.pixelSize: theme ? fontSizeXS : 10
                                font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                color: theme ? theme.textSecondary : "#a0a0a0"
                                width: 100
                            }
                            
                            Rectangle {
                                width: 70
                                height: 20
                                radius: 2
                                color: {
                                    if (modelData.severity === "Critical") return theme ? theme.danger : "#EF4444"
                                    if (modelData.severity === "High") return theme ? theme.warning : "#F59E0B"
                                    if (modelData.severity === "Medium") return theme ? theme.info : "#06B6D4"
                                    return theme ? theme.success : "#10B981"
                                }
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.severity.toUpperCase()
                                    font.pixelSize: theme ? fontSizeXS : 8
                                    font.bold: true
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: modelData.details
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textPrimary : "#ffffff"
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                            
                            Text {
                                text: modelData.status
                                font.pixelSize: theme ? fontSizeXS : 10
                                font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                color: {
                                    if (modelData.status === "Pending") return theme ? theme.warning : "#F59E0B"
                                    if (modelData.status === "Acknowledged") return theme ? theme.info : "#06B6D4"
                                    return theme ? theme.success : "#10B981"
                                }
                                width: 100
                            }
                        }
                    }
                }
            }
            
            // Right Side - Inspection Panel
            AppCard {
                Layout.fillWidth: true
                height: theme ? theme.cardHeightXXL : 600
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    // Video Player
                    Rectangle {
                        width: parent.width
                        height: 200
                        color: "#000000"
                        radius: theme ? theme.radiusS : 4
                        
                        Column {
                            anchors.fill: parent
                            anchors.margins: theme ? theme.spacingS : 8
                            spacing: theme ? theme.spacingS : 8
                            
                            Row {
                                spacing: theme ? theme.spacingS : 8
                                
                                Text {
                                    text: "LIVE EVIDENCE"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    font.bold: true
                                    color: theme ? theme.textSecondary : "#a0a0a0"
                                }
                                
                                Text {
                                    text: "Cam-SR-04"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                    color: theme ? theme.textSecondary : "#a0a0a0"
                                }
                                
                                Item {
                                    width: 1
                                    height: parent.height
                                }
                                
                                AppButton {
                                    text: "Playback Sequence"
                                    theme: control.theme
                                }
                            }
                            
                            Rectangle {
                                width: parent.width
                                height: parent.height - 30
                                color: "#1a1a1a"
                                radius: theme ? theme.radiusS : 4
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "📷 VIDEO FEED"
                                    font.pixelSize: theme ? fontSizeL : 16
                                    color: theme ? theme.textDisabled : "#606060"
                                }
                            }
                        }
                    }
                    
                    // Alert Details
                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingS : 8
                        
                        Row {
                            spacing: theme ? theme.spacingS : 8
                            
                            Text {
                                text: "Unauthorized Access Detected"
                                font.pixelSize: theme ? fontSizeL : 16
                                font.bold: true
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                            
                            Text {
                                text: "ID: ALRT-89214"
                                font.pixelSize: theme ? fontSizeXS : 10
                                font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Text {
                            text: "Timestamp: 2024-01-15 14:32:45 UTC"
                            font.pixelSize: theme ? fontSizeXS : 10
                            font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    // Alert Metrics
                    Row {
                        width: parent.width
                        spacing: theme ? theme.spacingM : 16
                        
                        Column {
                            width: (parent.width - (theme ? theme.spacingM : 16)) / 2
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "AI Confidence"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Rectangle {
                                width: 80
                                height: 24
                                radius: 2
                                color: theme ? theme.success : "#10B981"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "98.4%"
                                    font.pixelSize: theme ? fontSizeS : 12
                                    font.bold: true
                                    color: "#ffffff"
                                }
                            }
                        }
                        
                        Column {
                            width: (parent.width - (theme ? theme.spacingM : 16)) / 2
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Threat Level"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: "SEVERE"
                                font.pixelSize: theme ? fontSizeXL : 18
                                font.bold: true
                                color: theme ? theme.danger : "#EF4444"
                            }
                        }
                    }
                    
                    // Tabs
                    Row {
                        width: parent.width
                        spacing: theme ? theme.spacingXS : 4
                        
                        Repeater {
                            model: ["OVERVIEW", "TELEMETRY", "AUDIT LOG"]
                            
                            Rectangle {
                                width: (parent.width - (theme ? theme.spacingXS : 4) * 2) / 3
                                height: 32
                                radius: theme ? theme.radiusS : 4
                                color: index === 0 ? theme ? theme.primary : "#2563EB" : theme ? theme.surface : "#151C28"
                                border.color: theme ? theme.border : "#1E293B"
                                border.width: 1
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: modelData
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    font.bold: true
                                    color: "#ffffff"
                                }
                            }
                        }
                    }
                    
                    // Info Card
                    Rectangle {
                        width: parent.width
                        height: 120
                        color: theme ? theme.surface : "#151C28"
                        radius: theme ? theme.radiusS : 4
                        border.color: theme ? theme.border : "#1E293B"
                        border.width: 1
                
                        Column {
                            anchors.fill: parent
                            anchors.margins: theme ? theme.spacingM : 16
                            spacing: theme ? theme.spacingS : 8
                            
                            Row {
                                spacing: theme ? theme.spacingS : 8
                                
                                Text {
                                    text: "Location:"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: theme ? theme.textSecondary : "#a0a0a0"
                                }
                                
                                Text {
                                    text: "Server Room A - Zone 4"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                    color: theme ? theme.textPrimary : "#ffffff"
                                }
                            }
                            
                            Row {
                                spacing: theme ? theme.spacingS : 8
                                
                                Text {
                                    text: "Source Camera:"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: theme ? theme.textSecondary : "#a0a0a0"
                                }
                                
                                Text {
                                    text: "Cam-SR-04"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                    color: theme ? theme.textPrimary : "#ffffff"
                                }
                            }
                            
                            Row {
                                spacing: theme ? theme.spacingS : 8
                                
                                Text {
                                    text: "Detection Logic:"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: theme ? theme.textSecondary : "#a0a0a0"
                                }
                                
                                Row {
                                    spacing: theme ? theme.spacingXS : 4
                                    
                                    Rectangle {
                                        width: 60
                                        height: 16
                                        radius: 2
                                        color: theme ? theme.primary : "#2563EB"
                                        
                                        Text {
                                            anchors.centerIn: parent
                                            text: "Vision-LLM-v4"
                                            font.pixelSize: theme ? fontSizeXS : 8
                                            color: "#ffffff"
                                        }
                                    }
                                    
                                    Rectangle {
                                        width: 60
                                        height: 16
                                        radius: 2
                                        color: theme ? theme.primary : "#2563EB"
                                        
                                        Text {
                                            anchors.centerIn: parent
                                            text: "Spatial_Guard"
                                            font.pixelSize: theme ? fontSizeXS : 8
                                            color: "#ffffff"
                                        }
                                    }
                                }
                            }
                            
                            Text {
                                text: "Unauthorized personnel detected in restricted server room area. No valid access credentials presented."
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                    
                    // Action Buttons
                    Row {
                        width: parent.width
                        spacing: theme ? theme.spacingS : 8
                        
                        AppButton {
                            text: "False Positive"
                            backgroundColor: theme ? theme.surface : "#151C28"
                            theme: control.theme
                            Layout.fillWidth: true
                        }
                        
                        AppButton {
                            text: "Acknowledge"
                            backgroundColor: theme ? theme.primary : "#2563EB"
                            theme: control.theme
                            Layout.fillWidth: true
                        }
                    }
                    
                    AppButton {
                        text: "Request Supervisor Review"
                        backgroundColor: theme ? theme.warning : "#F59E0B"
                        theme: control.theme
                        width: parent.width
                    }
                }
            }
        }
    }
    
    signal alertDetailRequested(string alertId)
    
    function formatTimestamp(timestamp) {
        var date = new Date(timestamp)
        var now = new Date()
        var diff = Math.floor((now - date) / 1000)
        
        if (diff < 60) return diff + " sec ago"
        if (diff < 3600) return Math.floor(diff / 60) + " min ago"
        if (diff < 86400) return Math.floor(diff / 3600) + " hours ago"
        return date.toLocaleDateString()
    }
}
