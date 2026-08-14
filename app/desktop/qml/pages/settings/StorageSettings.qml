import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

AppDialog {
    id: control
    
    property var theme
    property var settingsController
    
    title: "Storage Settings"
    width: 500
    dialogContentHeight: 500
    theme: control.theme
    
    Component.onCompleted: {
        if (settingsController) {
            pathInput.text = settingsController.storageSettings.storage_path || "/var/lib/sentinelai/storage"
            maxStorageInput.text = settingsController.storageSettings.max_storage_gb || 1000
            autoCleanupCheck.checked = settingsController.storageSettings.auto_cleanup !== undefined ? settingsController.storageSettings.auto_cleanup : true
            cleanupInput.text = settingsController.storageSettings.cleanup_threshold || 90
            backupCheck.checked = settingsController.storageSettings.backup_enabled !== undefined ? settingsController.storageSettings.backup_enabled : true
            backupPathInput.text = settingsController.storageSettings.backup_path || "/var/lib/sentinelai/backups"
            backupCombo.currentIndex = backupCombo.find(settingsController.storageSettings.backup_schedule || "daily")
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
                text: "Storage Path"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: pathInput
                width: parent.width
                placeholderText: "/var/lib/sentinelai/storage"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Max Storage (GB)"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: maxStorageInput
                width: parent.width
                placeholderText: "1000"
                theme: control.theme
            }
        }
        
        Row {
            spacing: theme ? theme.spacingM : 16
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: autoCleanupCheck
                    text: "Auto Cleanup"
                    theme: control.theme
                }
                
                Text {
                    text: "Automatically clean old files"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: backupCheck
                    text: "Backup"
                    theme: control.theme
                }
                
                Text {
                    text: "Enable automatic backups"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Cleanup Threshold (%)"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: cleanupInput
                width: parent.width
                placeholderText: "90"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Backup Path"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: backupPathInput
                width: parent.width
                placeholderText: "/var/lib/sentinelai/backups"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Backup Schedule"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppComboBox {
                id: backupCombo
                width: parent.width
                theme: control.theme
                model: ["hourly", "daily", "weekly"]
                currentIndex: 1
            }
        }
        
        Item {
            width: parent.width
            height: parent.height - pathInput.height - maxStorageInput.height - cleanupInput.height - backupPathInput.height - backupCombo.height - parent.spacing * 6
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
                        settingsController.updateStorageSettings(
                            pathInput.text,
                            parseInt(maxStorageInput.text) || 1000,
                            autoCleanupCheck.checked,
                            parseInt(cleanupInput.text) || 90,
                            backupCheck.checked,
                            backupPathInput.text,
                            backupCombo.currentText
                        )
                        control.close()
                    }
                }
            }
        }
    }
}
