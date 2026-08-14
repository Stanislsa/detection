import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"
import "../../video"
import "../../cards"

Flickable {
    id: control
    
    property var theme
    property string cameraId: pageParams.cameraId || ""
    property string cameraName: pageParams.cameraName || "Camera 1"
    
    contentWidth: parent.width
    contentHeight: contentColumn.height + (theme ? theme.spacingXL : 48)
    clip: true
    
    Column {
        id: contentColumn
        width: parent.width
        spacing: theme ? theme.spacingL : 24
        anchors.top: parent.top
        anchors.topMargin: theme ? theme.spacingL : 24
        
        // Header
        RowLayout {
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: theme ? theme.spacingM : 16
            
            Text {
                text: control.cameraName
                font.pixelSize: theme ? theme.fontSizeXXL : 32
                font.bold: true
                color: theme ? theme.textPrimary : "#ffffff"
                Layout.alignment: Qt.AlignLeft
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            AppButton {
                text: "← Back"
                backgroundColor: theme ? theme.surface : "#2d2d2d"
                theme: control.theme
                Layout.alignment: Qt.AlignRight
                onClicked: control.backRequested()
            }
        }
        
        // Video player
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: 480
            theme: control.theme
            
            VideoPlayer {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                theme: control.theme
                cameraId: control.cameraId
                showOverlay: true
            }
        }
        
        // Camera info
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: 150
            theme: control.theme
            
            Column {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingM : 16
                
                Row {
                    spacing: theme ? theme.spacingM : 16
                    
                    Text {
                        text: "Camera Information"
                        font.pixelSize: theme ? theme.fontSizeL : 16
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    Item {
                        width: parent.width - infoText.width - settingsButton.width
                        height: 1
                    }
                    
                    AppButton {
                        id: settingsButton
                        text: "⚙️ Settings"
                        backgroundColor: theme ? theme.surface : "#2d2d2d"
                        theme: control.theme
                        onClicked: Router.navigate_to("camera_settings")
                    }
                }
                
                Rectangle {
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#404040"
                }
                
                Row {
                    spacing: theme ? theme.spacingXL : 48
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Status"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: "Online"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.success : "#44ff44"
                        }
                    }
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Location"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: "Zone A - Entrance"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Resolution"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: "1920x1080"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "FPS"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                        
                        Text {
                            text: "30"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                }
            }
        }
        
        // Recent detections
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: 200
            theme: control.theme
            
            Column {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingM : 16
                
                Text {
                    text: "Recent Detections"
                    font.pixelSize: theme ? theme.fontSizeL : 16
                    font.bold: true
                    color: theme ? theme.textPrimary : "#ffffff"
                }
                
                Rectangle {
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#404040"
                }
                
                Text {
                    text: "Person detected - 2 min ago (Confidence: 95%)"
                    font.pixelSize: theme ? theme.fontSizeM : 14
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
                
                Text {
                    text: "Person detected - 5 min ago (Confidence: 87%)"
                    font.pixelSize: theme ? theme.fontSizeM : 14
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
                
                Text {
                    text: "Motion detected - 10 min ago"
                    font.pixelSize: theme ? theme.fontSizeM : 14
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
        }
    }
    
    signal backRequested()
}
