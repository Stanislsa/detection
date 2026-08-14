import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

AppDialog {
    id: control
    
    property var theme
    property var settingsController
    
    title: "Security Settings"
    width: 500
    dialogContentHeight: 500
    theme: control.theme
    
    Component.onCompleted: {
        if (settingsController) {
            sessionInput.text = settingsController.securitySettings.session_timeout || 30
            maxAttemptsInput.text = settingsController.securitySettings.max_login_attempts || 5
            lockoutInput.text = settingsController.securitySettings.lockout_duration || 15
            twoFactorCheck.checked = settingsController.securitySettings.two_factor_enabled !== undefined ? settingsController.securitySettings.two_factor_enabled : false
            passwordMinInput.text = settingsController.securitySettings.password_min_length || 8
            specialCheck.checked = settingsController.securitySettings.password_require_special !== undefined ? settingsController.securitySettings.password_require_special : true
            numberCheck.checked = settingsController.securitySettings.password_require_number !== undefined ? settingsController.securitySettings.password_require_number : true
            auditCheck.checked = settingsController.securitySettings.audit_logging !== undefined ? settingsController.securitySettings.audit_logging : true
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
                text: "Session Timeout (minutes)"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: sessionInput
                width: parent.width
                placeholderText: "30"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Max Login Attempts"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: maxAttemptsInput
                width: parent.width
                placeholderText: "5"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Lockout Duration (minutes)"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: lockoutInput
                width: parent.width
                placeholderText: "15"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            AppCheckBox {
                id: twoFactorCheck
                text: "Two-Factor Authentication"
                theme: control.theme
            }
            
            Text {
                text: "Enable 2FA for all users"
                font.pixelSize: theme ? theme.fontSizeXS : 10
                color: theme ? theme.textSecondary : "#a0a0a0"
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Password Min Length"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: passwordMinInput
                width: parent.width
                placeholderText: "8"
                theme: control.theme
            }
        }
        
        Row {
            spacing: theme ? theme.spacingM : 16
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: specialCheck
                    text: "Require Special"
                    theme: control.theme
                }
                
                Text {
                    text: "Require special characters"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
            
            Column {
                spacing: theme ? theme.spacingXS : 4
                
                AppCheckBox {
                    id: numberCheck
                    text: "Require Number"
                    theme: control.theme
                }
                
                Text {
                    text: "Require numbers"
                    font.pixelSize: theme ? theme.fontSizeXS : 10
                    color: theme ? theme.textSecondary : "#a0a0a0"
                }
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            AppCheckBox {
                id: auditCheck
                text: "Audit Logging"
                theme: control.theme
            }
            
            Text {
                text: "Enable security audit logging"
                font.pixelSize: theme ? theme.fontSizeXS : 10
                color: theme ? theme.textSecondary : "#a0a0a0"
            }
        }
        
        Item {
            width: parent.width
            height: parent.height - sessionInput.height - maxAttemptsInput.height - lockoutInput.height - passwordMinInput.height - parent.spacing * 7
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
                        settingsController.updateSecuritySettings(
                            parseInt(sessionInput.text) || 30,
                            parseInt(maxAttemptsInput.text) || 5,
                            parseInt(lockoutInput.text) || 15,
                            twoFactorCheck.checked,
                            parseInt(passwordMinInput.text) || 8,
                            specialCheck.checked,
                            numberCheck.checked,
                            auditCheck.checked
                        )
                        control.close()
                    }
                }
            }
        }
    }
}
