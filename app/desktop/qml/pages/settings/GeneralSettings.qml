import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

AppDialog {
    id: control
    
    property var theme
    property var settingsController
    
    title: "General Settings"
    width: 500
    dialogContentHeight: 400
    theme: control.theme
    
    Component.onCompleted: {
        if (settingsController) {
            nameInput.text = settingsController.generalSettings.application_name || ""
            themeCombo.currentIndex = themeCombo.find(settingsController.generalSettings.theme || "dark")
            languageCombo.currentIndex = languageCombo.find(settingsController.generalSettings.language || "en")
            autoUpdateCheck.checked = settingsController.generalSettings.auto_update !== undefined ? settingsController.generalSettings.auto_update : true
            debugModeCheck.checked = settingsController.generalSettings.debug_mode !== undefined ? settingsController.generalSettings.debug_mode : false
            logLevelCombo.currentIndex = logLevelCombo.find(settingsController.generalSettings.log_level || "info")
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
                text: "Application Name"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: nameInput
                width: parent.width
                placeholderText: "Enter application name"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Theme"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppComboBox {
                id: themeCombo
                width: parent.width
                theme: control.theme
                model: ["dark", "light"]
                currentIndex: 0
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Language"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppComboBox {
                id: languageCombo
                width: parent.width
                theme: control.theme
                model: ["en", "fr", "es", "de"]
                currentIndex: 0
            }
        }
        
        Row {
            spacing: theme ? theme.spacingM : 16
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: autoUpdateCheck
                    text: "Auto Update"
                    theme: control.theme
                }
                
                Text {
                    text: "Automatically update application"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: debugModeCheck
                    text: "Debug Mode"
                    theme: control.theme
                }
                
                Text {
                    text: "Enable debug logging"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Log Level"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppComboBox {
                id: logLevelCombo
                width: parent.width
                theme: control.theme
                model: ["debug", "info", "warning", "error"]
                currentIndex: 1
            }
        }
        
        Item {
            width: parent.width
            height: parent.height - nameInput.height - themeCombo.height - languageCombo.height - logLevelCombo.height - parent.spacing * 5
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
                        settingsController.updateGeneralSettings(
                            nameInput.text,
                            themeCombo.currentText,
                            languageCombo.currentText,
                            autoUpdateCheck.checked,
                            debugModeCheck.checked,
                            logLevelCombo.currentText
                        )
                        control.close()
                    }
                }
            }
        }
    }
}
