import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"
import "../../cards"
import "../../video"
import "../../dialogs"

Flickable {
    id: control
    
    property var theme
    property var cameraController
    
    contentWidth: parent.width
    contentHeight: contentColumn.height + (theme ? theme.spacingXL : 48)
    clip: true
    
    Column {
        id: contentColumn
        width: parent.width
        spacing: theme ? theme.spacingL : 24
        anchors.top: parent.top
        anchors.topMargin: theme ? theme.spacingL : 24
        
        // Header row
        RowLayout {
            width: parent.width
            spacing: theme ? theme.spacingM : 16
            
            Text {
                id: camerasText
                text: "Cameras"
                font.pixelSize: theme ? theme.fontSizeXXL : 32
                font.bold: true
                color: theme ? theme.textPrimary : "#ffffff"
                Layout.alignment: Qt.AlignLeft
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            AppButton {
                id: addButton
                text: "+ Add Camera"
                backgroundColor: theme ? theme.primary : "#0078d4"
                theme: control.theme
                Layout.alignment: Qt.AlignRight
                onClicked: addCameraDialog.open()
            }
        }
        
        // Sidebar with Metrics and Filters
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            spacing: theme ? theme.spacingM : 16
            
            // Left Sidebar
            AppCard {
                width: 200
                height: theme ? theme.cardHeightXL : 400
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    // Metrics
                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingS : 8
                        
                        Text {
                            text: "AI Load"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: "24%"
                            font.pixelSize: theme ? theme.fontSizeL : 16
                            font.bold: true
                            color: theme ? theme.success : "#10B981"
                        }
                        
                        Rectangle {
                            width: parent.width
                            height: 4
                            radius: 2
                            color: theme ? theme.surface : "#151C28"
                            
                            Rectangle {
                                width: parent.width * 0.24
                                height: parent.height
                                radius: 2
                                color: theme ? theme.success : "#10B981"
                            }
                        }
                    }
                    
                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingS : 8
                        
                        Text {
                            text: "Storage"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: "82%"
                            font.pixelSize: theme ? theme.fontSizeL : 16
                            font.bold: true
                            color: theme ? theme.warning : "#F59E0B"
                        }
                        
                        Rectangle {
                            width: parent.width
                            height: 4
                            radius: 2
                            color: theme ? theme.surface : "#151C28"
                            
                            Rectangle {
                                width: parent.width * 0.82
                                height: parent.height
                                radius: 2
                                color: theme ? theme.warning : "#F59E0B"
                            }
                        }
                    }
                    
                    Rectangle {
                        width: parent.width
                        height: 1
                        color: theme ? theme.border : "#1E293B"
                    }
                    
                    // Location Filters
                    Text {
                        text: "Locations"
                        font.pixelSize: theme ? theme.fontSizeS : 12
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingXS : 4
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Building A"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Rectangle {
                                width: 20
                                height: 16
                                radius: 2
                                color: theme ? theme.surface : "#151C28"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "12"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: theme ? theme.textPrimary : "#ffffff"
                                }
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Building B"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Rectangle {
                                width: 20
                                height: 16
                                radius: 2
                                color: theme ? theme.surface : "#151C28"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "8"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: theme ? theme.textPrimary : "#ffffff"
                                }
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Building C"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Rectangle {
                                width: 20
                                height: 16
                                radius: 2
                                color: theme ? theme.surface : "#151C28"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "4"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: theme ? theme.textPrimary : "#ffffff"
                                }
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Exterior"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Rectangle {
                                width: 20
                                height: 16
                                radius: 2
                                color: theme ? theme.surface : "#151C28"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "15"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: theme ? theme.textPrimary : "#ffffff"
                                }
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Data Center"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Rectangle {
                                width: 20
                                height: 16
                                radius: 2
                                color: theme ? theme.surface : "#151C28"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "6"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: theme ? theme.textPrimary : "#ffffff"
                                }
                            }
                        }
                    }
                    
                    Rectangle {
                        width: parent.width
                        height: 1
                        color: theme ? theme.border : "#1E293B"
                    }
                    
                    // Status Filter
                    Text {
                        text: "Status Filter"
                        font.pixelSize: theme ? theme.fontSizeS : 12
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingXS : 4
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 8
                                height: 8
                                radius: 4
                                color: theme ? theme.success : "#10B981"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            
                            Text {
                                text: "Operational"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Item {
                                width: 1
                                height: parent.height
                            }
                            
                            Text {
                                text: "32"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 8
                                height: 8
                                radius: 4
                                color: theme ? theme.danger : "#EF4444"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            
                            Text {
                                text: "Alert Triggered"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Item {
                                width: 1
                                height: parent.height
                            }
                            
                            Text {
                                text: "2"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                        }
                        
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Rectangle {
                                width: 8
                                height: 8
                                radius: 4
                                color: theme ? theme.textDisabled : "#606060"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            
                            Text {
                                text: "Offline"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Item {
                                width: 1
                                height: parent.height
                            }
                            
                            Text {
                                text: "5"
                                font.pixelSize: theme ? fontSizeXS : 10
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                        }
                    }
                }
            }
            
            // Camera Grid
            AppCard {
                Layout.fillWidth: true
                height: theme ? theme.cardHeightXL : 400
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    GridLayout {
                        width: parent.width
                        height: parent.height - 60
                        columns: 3
                        columnSpacing: theme ? theme.spacingS : 8
                        rowSpacing: theme ? theme.spacingS : 8
                        
                        // 5 Active Cameras
                        Repeater {
                            model: 5
                            
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: theme ? theme.surfaceElevated : "#1E293B"
                                radius: theme ? theme.radiusS : 4
                                border.color: theme ? theme.border : "#1E293B"
                                border.width: 1
                                
                                Column {
                                    anchors.fill: parent
                                    spacing: theme ? theme.spacingXS : 4
                                    
                                    Row {
                                        width: parent.width
                                        spacing: theme ? theme.spacingXS : 4
                                        
                                        Rectangle {
                                            width: 30
                                            height: 16
                                            radius: 2
                                            color: theme ? theme.danger : "#EF4444"
                                            
                                            Text {
                                                anchors.centerIn: parent
                                                text: "REC"
                                                font.pixelSize: theme ? fontSizeXS : 8
                                                font.bold: true
                                                color: "#ffffff"
                                            }
                                        }
                                        
                                        Item {
                                            width: 1
                                            height: parent.height
                                        }
                                        
                                        Text {
                                            text: ["4K", "1080p", "720p", "4K", "1080p"][index]
                                            font.pixelSize: theme ? fontSizeXS : 10
                                            font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                            color: theme ? theme.textSecondary : "#a0a0a0"
                                        }
                                    }
                                    
                                    Rectangle {
                                        width: parent.width
                                        height: parent.height - 40
                                        color: "#000000"
                                        radius: theme ? theme.radiusS : 4
                                    }
                                    
                                    Text {
                                        text: ["LOBBY_EAST_01", "WH_DOCK_07", "SERVER_COR_04", "PARK_EXT_12", "RETAIL_FLR_02"][index]
                                        font.pixelSize: theme ? fontSizeXS : 10
                                        font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                        color: theme ? theme.textSecondary : "#a0a0a0"
                                    }
                                }
                            }
                        }
                        
                        // 1 Offline Camera
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: theme ? theme.surface : "#151C28"
                            radius: theme ? theme.radiusS : 4
                            border.color: theme ? theme.border : "#1E293B"
                            border.width: 1
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: theme ? theme.spacingS : 8
                                
                                Text {
                                    text: "📡"
                                    font.pixelSize: theme ? fontSizeXL : 32
                                    color: theme ? theme.textDisabled : "#606060"
                                }
                                
                                Text {
                                    text: "PERIMETER FENCE LINE"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                                    color: theme ? theme.textDisabled : "#606060"
                                }
                                
                                Text {
                                    text: "SIGNAL LOST"
                                    font.pixelSize: theme ? fontSizeXS : 10
                                    color: theme ? theme.textDisabled : "#606060"
                                }
                            }
                        }
                        
                        // 1 Empty Camera Slot
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: theme ? theme.surface : "#151C28"
                            radius: theme ? theme.radiusS : 4
                            border.color: theme ? theme.border : "#1E293B"
                            border.width: 1
                            border.style: Qt.DashLine
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: theme ? theme.spacingS : 8
                                
                                Text {
                                    text: "+"
                                    font.pixelSize: theme ? fontSizeXXL : 32
                                    color: theme ? theme.textDisabled : "#606060"
                                }
                                
                                AppButton {
                                    text: "MOUNT NEW STREAM"
                                    theme: control.theme
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Action Bar
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: theme ? theme.cardHeightS : 60
            theme: control.theme
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingM : 16
                
                AppButton {
                    text: "FLEET SETTINGS"
                    theme: control.theme
                    Layout.alignment: Qt.AlignLeft
                }
                
                Item {
                    Layout.fillWidth: true
                }
                
                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: theme ? theme.success : "#10B981"
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                Text {
                    text: "LIVE STREAM ACTIVE"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                    color: theme ? theme.textSecondary : "#a0a0a0"
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                Item {
                    width: 20
                }
                
                Text {
                    text: "AI Detection:"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: theme ? theme.success : "#10B981"
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                Text {
                    text: "Enabled"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                Item {
                    width: 20
                }
                
                Text {
                    text: "Latency: 142ms"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    font.family: theme ? theme.fontFamilyCode : "JetBrains Mono"
                    color: theme ? theme.textSecondary : "#a0a0a0"
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                Item {
                    width: 20
                }
                
                AppButton {
                    text: "🔊"
                    theme: control.theme
                    Layout.alignment: Qt.AlignRight
                }
                
                AppButton {
                    text: "⛶"
                    theme: control.theme
                    Layout.alignment: Qt.AlignRight
                }
            }
        }
    }
    
    // Dialogs
    AddCameraDialog {
        id: addCameraDialog
        theme: control.theme
        onCameraAdded: function(name, url, location) {
            // Handle camera addition
            console.log("Camera added:", name, url, location)
        }
    }
    
    EditCameraDialog {
        id: editCameraDialog
        theme: control.theme
        cameraId: "cam1"
        cameraName: "Camera 1"
        cameraUrl: "rtsp://example.com/stream"
        location: "Zone A"
        onCameraUpdated: function(id, name, url, location) {
            console.log("Camera updated:", id, name, url, location)
        }
        onCameraDeleted: function(id) {
            console.log("Camera deleted:", id)
        }
    }
}
