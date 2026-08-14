import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

AppDialog {
    id: control
    
    property var theme
    property var settingsController
    
    title: "Notification Settings"
    width: 500
    dialogContentHeight: 550
    theme: control.theme
    
    Component.onCompleted: {
        if (settingsController) {
            emailCheck.checked = settingsController.notificationSettings.email_enabled !== undefined ? settingsController.notificationSettings.email_enabled : true
            emailInput.text = settingsController.notificationSettings.email_address || ""
            smsCheck.checked = settingsController.notificationSettings.sms_enabled !== undefined ? settingsController.notificationSettings.sms_enabled : false
            smsInput.text = settingsController.notificationSettings.sms_number || ""
            pushCheck.checked = settingsController.notificationSettings.push_enabled !== undefined ? settingsController.notificationSettings.push_enabled : true
            criticalCheck.checked = settingsController.notificationSettings.critical_only !== undefined ? settingsController.notificationSettings.critical_only : false
            quietCheck.checked = settingsController.notificationSettings.quiet_hours_enabled !== undefined ? settingsController.notificationSettings.quiet_hours_enabled : false
            quietStartInput.text = settingsController.notificationSettings.quiet_hours_start || "22:00"
            quietEndInput.text = settingsController.notificationSettings.quiet_hours_end || "08:00"
        }
    }
    
    Column {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16
        
        Row {
            spacing: theme ? theme.spacingM : 16
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: emailCheck
                    text: "Email"
                    theme: control.theme
                }
                
                Text {
                    text: "Enable email notifications"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: smsCheck
                    text: "SMS"
                    theme: control.theme
                }
                
                Text {
                    text: "Enable SMS notifications"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: pushCheck
                    text: "Push"
                    theme: control.theme
                }
                
                Text {
                    text: "Enable push notifications"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Email Address"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: emailInput
                width: parent.width
                placeholderText: "email@example.com"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "SMS Number"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: smsInput
                width: parent.width
                placeholderText: "+1234567890"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            AppCheckBox {
                id: criticalCheck
                text: "Critical Only"
                theme: control.theme
            }
            
            Text {
                text: "Only send critical notifications"
                font.pixelSize: theme ? theme.fontSizeXS : 10
                color: theme ? theme.textSecondary : "#a0a0a0"
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            AppCheckBox {
                id: quietCheck
                text: "Quiet Hours"
                theme: control.theme
            }
            
            Text {
                text: "Enable quiet hours"
                font.pixelSize: theme ? theme.fontSizeXS : 10
                color: theme ? theme.textSecondary : "#a0a0a0"
            }
        }
        
        Row {
            spacing: theme ? theme.spacingM : 16
            
            Column {
                width: 120
                spacing: theme ? theme.spacingS : 8
                
                Text {
                    text: "Start Time"
                    font.pixelSize: theme ? theme.fontSizeM : 14
                    color: theme ? theme.textPrimary : "#ffffff"
                }
                
                AppInput {
                    id: quietStartInput
                    width: parent.width
                    placeholderText: "22:00"
                    theme: control.theme
                }
            }
            
            Column {
                width: 120
                spacing: theme ? theme.spacingS : 8
                
                Text {
                    text: "End Time"
                    font.pixelSize: theme ? theme.fontSizeM : 14
                    color: theme ? theme.textPrimary : "#ffffff"
                }
                
                AppInput {
                    id: quietEndInput
                    width: parent.width
                    placeholderText: "08:00"
                    theme: control.theme
                }
            }
        }
        
        Item {
            width: parent.width
            height: parent.height - emailInput.height - smsInput.height - quietStartInput.height - quietEndInput.height - parent.spacing * 7
        }
        
        Row {
            anchors.right: parent.right
            spacing: theme ? theme.spacingS : 8
            
            AppButton {
                text: "Cancel"
                backgroundColor: theme ? theme.surface : "#2d2d2d"
                theme: control.theme
                onClicked: control.close()
            }
            
            AppButton {
                text: "Save"
                backgroundColor: theme ? theme.primary : "#0078d4"
                theme: control.theme
                onClicked: {
                    if (settingsController) {
                        settingsController.updateNotificationSettings(
                            emailCheck.checked,
                            emailInput.text,
                            smsCheck.checked,
                            smsInput.text,
                            pushCheck.checked,
                            criticalCheck.checked,
                            quietCheck.checked,
                            quietStartInput.text,
                            quietEndInput.text
                        )
                        control.close()
                    }
                }
            }
        }
    }
}
