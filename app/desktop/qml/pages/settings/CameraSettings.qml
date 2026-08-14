import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

AppDialog {
    id: control
    
    property var theme
    property var settingsController
    
    title: "Camera Settings"
    width: 500
    dialogContentHeight: 450
    theme: control.theme
    
    Component.onCompleted: {
        if (settingsController) {
            resolutionCombo.currentIndex = resolutionCombo.find(settingsController.cameraSettings.default_resolution || "1080p")
            fpsInput.text = settingsController.cameraSettings.default_fps || 30
            autoReconnectCheck.checked = settingsController.cameraSettings.auto_reconnect !== undefined ? settingsController.cameraSettings.auto_reconnect : true
            reconnectInput.text = settingsController.cameraSettings.reconnect_interval || 30
            recordingCheck.checked = settingsController.cameraSettings.recording_enabled !== undefined ? settingsController.cameraSettings.recording_enabled : true
            retentionInput.text = settingsController.cameraSettings.retention_days || 30
        }
    }
    
    Column {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Default Resolution"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppComboBox {
                id: resolutionCombo
                width: parent.width
                theme: control.theme
                model: ["720p", "1080p", "4K"]
                currentIndex: 1
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Default FPS"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: fpsInput
                width: parent.width
                placeholderText: "30"
                theme: control.theme
            }
        }
        
        Row {
            spacing: theme ? theme.spacingM : 16
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: autoReconnectCheck
                    text: "Auto Reconnect"
                    theme: control.theme
                }
                
                Text {
                    text: "Automatically reconnect cameras"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: recordingCheck
                    text: "Recording"
                    theme: control.theme
                }
                
                Text {
                    text: "Enable video recording"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Reconnect Interval (seconds)"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: reconnectInput
                width: parent.width
                placeholderText: "30"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Retention Days"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: retentionInput
                width: parent.width
                placeholderText: "30"
                theme: control.theme
            }
        }
        
        Item {
            width: parent.width
            height: parent.height - resolutionCombo.height - fpsInput.height - reconnectInput.height - retentionInput.height - parent.spacing * 5
        }
        
        Row {
            anchors.right: parent.right
            spacing: theme ? theme.spacingS : 8
            
            AppButton {
                text: "Cancel"
                variant: "secondary"
                theme: control.theme
                onClicked: control.close()
            }
            
            AppButton {
                text: "Save"
                variant: "primary"
                theme: control.theme
                onClicked: {
                    if (settingsController) {
                        settingsController.updateCameraSettings(
                            resolutionCombo.currentText,
                            parseInt(fpsInput.text) || 30,
                            autoReconnectCheck.checked,
                            parseInt(reconnectInput.text) || 30,
                            recordingCheck.checked,
                            parseInt(retentionInput.text) || 30
                        )
                        control.close()
                    }
                }
            }
        }
    }
}
