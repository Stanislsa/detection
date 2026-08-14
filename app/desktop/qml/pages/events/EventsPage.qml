import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"
import "../../cards"

Flickable {
    id: control
    
    property var theme
    property var eventController
    
    contentWidth: parent.width
    contentHeight: contentColumn.height + (theme ? theme.spacingXL : 48)
    clip: true
    
    Column {
        id: contentColumn
        width: parent.width
        spacing: theme ? theme.spacingL : 24
        anchors.top: parent.top
        anchors.topMargin: theme ? theme.spacingL : 24
        
        // Sidebar with Filters and Event List
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            spacing: theme ? theme.spacingM : 16
            
            // Left Sidebar - Filters
            AppCard {
                width: 250
                height: theme ? theme.cardHeightXXL : 600
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Text {
                        text: "Filters"
                        font.pixelSize: theme ? theme.fontSizeL : 16
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    Rectangle {
                        width: parent.width
                        height: 1
                        color: theme ? theme.border : "#1E293B"
                    }
                    
                    // Search
                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Search by ID / Camera"
                            font.pixelSize: theme ? fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        AppInput {
                            width: parent.width
                            placeholderText: "Search..."
                            theme: control.theme
                        }
                    }
                    
                    // Severity Checkboxes
                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Severity"
                            font.pixelSize: theme ? fontSizeS : 12
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 16
                                height: 16
                                radius: 2
                                color: theme ? theme.danger : "#EF4444"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☑"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: "Critical"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 16
                                height: 16
                                radius: 2
                                color: theme ? theme.warning : "#F59E0B"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☑"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: "High"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 16
                                height: 16
                                radius: 2
                                color: theme ? theme.info : "#06B6D4"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☑"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: "Medium"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 16
                                height: 16
                                radius: 2
                                color: theme ? theme.success : "#10B981"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☑"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: "Low"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                    }
                    
                    // Category Checkboxes
                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Categories"
                            font.pixelSize: theme ? fontSizeS : 12
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 16
                                height: 16
                                radius: 2
                                color: theme ? theme.primary : "#2563EB"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☑"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: "Personnel"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 16
                                height: 16
                                radius: 2
                                color: theme ? theme.primary : "#2563EB"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☑"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: "Vehicle"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 16
                                height: 16
                                radius: 2
                                color: theme ? theme.primary : "#2563EB"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☑"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: "Access"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 16
                                height: 16
                                radius: 2
                                color: theme ? theme.primary : "#2563EB"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☑"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: "Hardware"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 16
                                height: 16
                                radius: 2
                                color: theme ? theme.primary : "#2563EB"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☑"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: "AI Analytics"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 16
                                height: 16
                                radius: 2
                                color: theme ? theme.primary : "#2563EB"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "☑"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: "#ffffff"
                                }
                            }
                            
                            Text {
                                text: "System"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                    }
                    
                    // AI Confidence Slider
                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "AI Confidence > 75%"
                            font.pixelSize: theme ? fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Rectangle {
                            width: parent.width
                            height: 4
                            radius: 2
                            color: theme ? theme.surface : "#151C28"
                            
                            Rectangle {
                                width: parent.width * 0.75
                                height: parent.height
                                radius: 2
                                color: theme ? theme.primary : "#2563EB"
                            }
                        }
                        
                        Text {
                            text: "75%"
                            font.pixelSize: theme ? fontSizeXS : 10
                            font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    // Period Selector
                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Period"
                            font.pixelSize: theme ? fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        AppComboBox {
                            width: parent.width
                            theme: control.theme
                            model: ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Range"]
                            currentIndex: 0
                        }
                    }
                    
                    Item {
                        width: parent.width
                        height: 1
                    }
                    
                    AppButton {
                        text: "Apply Filters"
                        width: parent.width
                        theme: control.theme
                    }
                }
            }
            
            // Event List
            AppCard {
                Layout.fillWidth: true
                height: theme ? theme.cardHeightXXL : 600
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    // Metrics Header
                    Row {
                        width: parent.width
                        spacing: theme ? theme.spacingM : 16
                        
                        Column {
                            width: (parent.width - (theme ? theme.spacingM : 16) * 3) / 4
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Total Events"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: "1,284"
                                font.pixelSize: theme ? fontSizeL : 16
                                font.bold: true
                                font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                        }
                        
                        Column {
                            width: (parent.width - (theme ? theme.spacingM : 16) * 3) / 4
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Critical Errors"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: "12"
                                font.pixelSize: theme ? fontSizeL : 16
                                font.bold: true
                                font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                color: theme ? theme.danger : "#EF4444"
                            }
                        }
                        
                        Column {
                            width: (parent.width - (theme ? theme.spacingM : 16) * 3) / 4
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "AI Detections"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: "243"
                                font.pixelSize: theme ? fontSizeL : 16
                                font.bold: true
                                font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                color: theme ? theme.primary : "#2563EB"
                            }
                        }
                        
                        Column {
                            width: (parent.width - (theme ? theme.spacingM : 16) * 3) / 4
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Avg Confidence"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: "89.4%"
                                font.pixelSize: theme ? fontSizeL : 16
                                font.bold: true
                                font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                color: theme ? theme.success : "#10B981"
                            }
                        }
                    }
                    
                    Rectangle {
                        width: parent.width
                        height: 1
                        color: theme ? theme.border : "#1E293B"
                    }
                    
                    // Event Cards
                    ListView {
                        width: parent.width
                        height: parent.height - 80
                        model: [
                            {timestamp: "14:32:45", severity: "Critical", title: "Unauthorized Access", category: "Personnel", aiScore: "98.4%", camera: "Cam-SR-04", node: "WH_DOCK_07"},
                            {timestamp: "14:28:12", severity: "High", title: "Motion Detected", category: "Vehicle", aiScore: "87.2%", camera: "Cam-PK-12", node: "PARK_EXT_12"},
                            {timestamp: "14:15:33", severity: "Medium", title: "Zone Breach", category: "Access", aiScore: "92.1%", camera: "Cam-LO-01", node: "LOBBY_EAST_01"},
                            {timestamp: "14:02:18", severity: "Low", title: "Sensor Alert", category: "Hardware", aiScore: "N/A", camera: "Cam-SV-04", node: "SERVER_COR_04"}
                        ]
                        spacing: theme ? theme.spacingS : 8
                        clip: true
                        
                        delegate: Rectangle {
                            width: parent.width
                            height: 60
                            color: theme ? theme.surface : "#151C28"
                            radius: theme ? theme.radiusS : 4
                            border.color: theme ? theme.border : "#1E293B"
                            border.width: 1
                            
                            Row {
                                anchors.fill: parent
                                anchors.margins: theme ? theme.spacingS : 8
                                spacing: theme ? theme.spacingS : 8
                                
                                // Indicator Dot
                                Rectangle {
                                    width: 8
                                    height: 8
                                    radius: 4
                                    color: {
                                        if (modelData.severity === "Critical") return theme ? theme.danger : "#EF4444"
                                        if (modelData.severity === "High") return theme ? theme.warning : "#F59E0B"
                                        if (modelData.severity === "Medium") return theme ? theme.info : "#06B6D4"
                                        return theme ? theme.success : "#10B981"
                                    }
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                
                                // Timestamp
                                Text {
                                    text: modelData.timestamp
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                    color: theme ? theme.textSecondary : "#a0a0a0"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                
                                // Title
                                Text {
                                    text: modelData.title
                                    font.pixelSize: theme ? fontSizeS : 12
                                    font.bold: true
                                    color: theme ? theme.textPrimary : "#ffffff"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                
                                // Category Tag
                                Rectangle {
                                    width: 60
                                    height: 20
                                    radius: 2
                                    color: theme ? theme.primary : "#2563EB"
                                    anchors.verticalCenter: parent.verticalCenter
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData.category.toUpperCase()
                                        font.pixelSize: theme ? fontSizeXS : 8
                                        color: "#ffffff"
                                    }
                                }
                                
                                // AI Score
                                Text {
                                    text: "AI: " + modelData.aiScore
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                    color: theme ? theme.success : "#10B981"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                
                                Item {
                                    width: 1
                                    height: parent.height
                                }
                                
                                // Thumbnail placeholder
                                Rectangle {
                                    width: 40
                                    height: 30
                                    color: "#000000"
                                    radius: theme ? theme.radiusS : 4
                                    anchors.verticalCenter: parent.verticalCenter
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "📷"
                                        font.pixelSize: theme ? fontSizeXS : 10
                                        color: theme ? theme.textDisabled : "#606060"
                                    }
                                }
                                
                                // Camera ID
                                Text {
                                    text: modelData.camera
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                    color: theme ? theme.textSecondary : "#a0a0a0"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                
                                // Node
                                Text {
                                    text: modelData.node
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                    color: theme ? theme.textDisabled : "#606060"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    function formatEventType(type) {
        const names = {
            "person_detected": "Person Detected",
            "fall_detected": "Fall Detected",
            "motion_detected": "Motion Detected",
            "intrusion": "Intrusion",
            "camera_offline": "Camera Offline",
            "camera_online": "Camera Online"
        }
        return names[type] || type
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
