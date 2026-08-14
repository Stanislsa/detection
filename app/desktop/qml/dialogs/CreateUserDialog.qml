import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

AppDialog {
    id: control
    
    property var theme
    property string username: ""
    property string email: ""
    property string role: "operator"
    
    signal userCreated(string username, string email, string role)
    
    title: "Create User"
    width: theme ? theme.dialogWidthM : 500
    dialogContentHeight: theme ? theme.dialogContentHeightL : 450
    theme: control.theme
    
    Column {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Username"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: usernameInput
                width: parent.width
                placeholderText: "Enter username"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Email"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: emailInput
                width: parent.width
                placeholderText: "Enter email address"
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Role"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppComboBox {
                id: roleInput
                width: parent.width
                theme: control.theme
                model: ["Operator", "Supervisor", "Admin"]
                currentIndex: 0
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Password"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: passwordInput
                width: parent.width
                placeholderText: "Enter password"
                echoMode: TextInput.Password
                theme: control.theme
            }
        }
        
        Column {
            width: parent.width
            spacing: theme ? theme.spacingS : 8
            
            Text {
                text: "Confirm Password"
                font.pixelSize: theme ? theme.fontSizeM : 14
                color: theme ? theme.textPrimary : "#ffffff"
            }
            
            AppInput {
                id: confirmPasswordInput
                width: parent.width
                placeholderText: "Confirm password"
                echoMode: TextInput.Password
                theme: control.theme
            }
        }
        
        Item {
            width: parent.width
            height: parent.height - usernameInput.height - emailInput.height - roleInput.height - passwordInput.height - confirmPasswordInput.height - parent.spacing * 5
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
                text: "Create User"
                variant: "primary"
                theme: control.theme
                onClicked: {
                    if (usernameInput.text && emailInput.text && passwordInput.text) {
                        if (passwordInput.text === confirmPasswordInput.text) {
                            control.state = "loading"
                            // Simulate API call
                            Qt.callLater(function() {
                                control.userCreated(usernameInput.text, emailInput.text, roleInput.currentText)
                                control.state = "success"
                                Qt.callLater(function() {
                                    control.close()
                                }, 1000)
                            })
                        }
                    }
                }
            }
        }
    }
}
