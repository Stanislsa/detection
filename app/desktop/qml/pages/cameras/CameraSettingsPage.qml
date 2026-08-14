import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

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
                text: control.cameraName + " Settings"
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
        
        // General settings
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: 250
            theme: control.theme
            
            Column {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingM : 16
                
                Text {
                    text: "General Settings"
                    font.pixelSize: theme ? theme.fontSizeL : 16
                    font.bold: true
                    color: theme ? theme.textPrimary : "#ffffff"
                }
                
                Rectangle {
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#404040"
                }
                
                Column {
                    width: parent.width
                    spacing: theme ? theme.spacingS : 8
                    
                    Text {
                        text: "Camera Name"
                        font.pixelSize: theme ? theme.fontSizeM : 14
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    AppInput {
                        width: parent.width
                        text: control.cameraName
                        theme: control.theme
                    }
                }
                
                Column {
                    width: parent.width
                    spacing: theme ? theme.spacingS : 8
                    
                    Text {
                        text: "Location"
                        font.pixelSize: theme ? theme.fontSizeM : 14
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    AppInput {
                        width: parent.width
                        text: "Zone A - Entrance"
                        theme: control.theme
                    }
                }
            }
        }
        
        // Detection settings
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: 300
            theme: control.theme
            
            Column {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingM : 16
                
                Text {
                    text: "Detection Settings"
                    font.pixelSize: theme ? theme.fontSizeL : 16
                    font.bold: true
                    color: theme ? theme.textPrimary : "#ffffff"
                }
                
                Rectangle {
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#404040"
                }
                
                Row {
                    spacing: theme ? theme.spacingM : 16
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Enable Person Detection"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        AppSwitch {
                            checked: true
                            theme: control.theme
                        }
                    }
                    
                    Column {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Enable Vehicle Detection"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        AppSwitch {
                            checked: true
                            theme: control.theme
                        }
                    }
                }
                
                Column {
                    width: parent.width
                    spacing: theme ? theme.spacingS : 8
                    
                    Text {
                        text: "Confidence Threshold"
                        font.pixelSize: theme ? theme.fontSizeM : 14
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    Slider {
                        width: parent.width
                        from: 0
                        to: 100
                        value: 70
                    }
                }
            }
        }
        
        // Save button
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: theme ? theme.spacingS : 8
            
            AppButton {
                text: "Cancel"
                backgroundColor: theme ? theme.surface : "#2d2d2d"
                theme: control.theme
                onClicked: control.backRequested()
            }
            
            AppButton {
                text: "Save Settings"
                backgroundColor: theme ? theme.primary : "#0078d4"
                theme: control.theme
                onClicked: {
                    console.log("Settings saved")
                    control.backRequested()
                }
            }
        }
    }
    
    signal backRequested()
}
