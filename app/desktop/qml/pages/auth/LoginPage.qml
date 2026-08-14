import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Rectangle {
    id: control
    
    property var theme
    property var authController
    
    color: control.theme.background
    
    Column {
        anchors.centerIn: parent
        spacing: control.theme ? control.theme.spacingXL : 32
        
        // Logo
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "SentinelAI"
            font.pixelSize: control.theme ? control.theme.fontSizeDisplay : 48
            font.bold: true
            color: control.theme ? control.theme.primary : "#0078d4"
        }
        
        // Login Card
        AppCard {
            id: loginCard
            anchors.horizontalCenter: parent.horizontalCenter
            width: theme ? theme.loginCardWidth : 400
            theme: control.theme
            
            Column {
                anchors.fill: parent
                anchors.margins: control.theme ? control.theme.spacingXL : 32
                spacing: control.theme ? control.theme.spacingL : 24
                
                Text {
                    text: "Sign In"
                    font.pixelSize: control.theme ? control.theme.fontSizeXXL : 24
                    font.bold: true
                    color: control.theme ? control.theme.textPrimary : "#ffffff"
                }
                
                Text {
                    text: "Enter your credentials to access the system"
                    font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                    color: control.theme ? control.theme.textSecondary : "#a0a0a0"
                }
                
                Column {
                    width: parent.width
                    spacing: control.theme ? control.theme.spacingM : 16
                    
                    Text {
                        text: "Email"
                        font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                        font.bold: true
                        color: control.theme ? control.theme.textPrimary : "#ffffff"
                    }
                    
                    AppInput {
                        id: emailInput
                        width: parent.width
                        theme: control.theme
                        placeholderText: "admin@sentinelai.local"
                    }
                    
                    Text {
                        text: "Password"
                        font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                        font.bold: true
                        color: control.theme ? control.theme.textPrimary : "#ffffff"
                    }
                    
                    AppInput {
                        id: passwordInput
                        width: parent.width
                        theme: control.theme
                        placeholderText: "********"
                        echoMode: TextInput.Password
                    }
                }
                
                AppButton {
                    id: loginButton
                    width: parent.width
                    text: "Sign In"
                    theme: control.theme
                    enabled: emailInput.text !== "" && passwordInput.text !== ""
                    
                    onClicked: {
                        control.authController.login(emailInput.text, passwordInput.text)
                    }
                }
                
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "Forgot password?"
                    font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                    color: control.theme ? control.theme.primary : "#0078d4"
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: control.forgotPasswordRequested()
                    }
                }
            }
        }
    }
    
    signal forgotPasswordRequested()
}
