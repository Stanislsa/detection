import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Rectangle {
    id: control
    
    property var theme
    readonly property bool isCompact: height < 700 || width < 640
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
        
        // Forgot Password Card
        AppCard {
            id: forgotPasswordCard
            anchors.horizontalCenter: parent.horizontalCenter
            width: 400
            theme: control.theme
            
            Column {
                anchors.fill: parent
                anchors.margins: control.theme ? control.theme.spacingXL : 32
                spacing: control.theme ? control.theme.spacingLG : 24
                
                Text {
                    text: "Reset Password"
                    font.pixelSize: control.theme ? control.theme.fontSizeXXL : 24
                    font.bold: true
                    color: control.theme ? control.theme.textPrimary : "#ffffff"
                }
                
                Text {
                    text: "Enter your email address and we'll send you a link to reset your password"
                    font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                    color: control.theme ? control.theme.textSecondary : "#a0a0a0"
                    wrapMode: Text.WordWrap
                }
                
                Column {
                    width: parent.width
                    spacing: control.theme ? control.theme.spacingMD : 16
                    
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
                }
                
                AppButton {
                    id: sendButton
                    width: parent.width
                    text: "Send Reset Link"
                    theme: control.theme
                    enabled: emailInput.text !== ""
                    
                    onClicked: {
                        control.authController.request_password_reset(emailInput.text)
                    }
                }
                
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "Back to Sign In"
                    font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                    color: control.theme ? control.theme.primary : "#0078d4"
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: control.backToLogin()
                    }
                }
            }
        }
    }
    
    signal backToLogin()
}
