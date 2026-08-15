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
        
        // 2FA Card
        AppCard {
            id: twoFactorCard
            anchors.horizontalCenter: parent.horizontalCenter
            width: 400
            theme: control.theme
            
            Column {
                anchors.fill: parent
                anchors.margins: control.theme ? control.theme.spacingXL : 32
                spacing: control.theme ? control.theme.spacingLG : 24
                
                Text {
                    text: "Two-Factor Authentication"
                    font.pixelSize: control.theme ? control.theme.fontSizeXXL : 24
                    font.bold: true
                    color: control.theme ? control.theme.textPrimary : "#ffffff"
                }
                
                Text {
                    text: "Enter the 6-digit verification code sent to your device"
                    font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                    color: control.theme ? control.theme.textSecondary : "#a0a0a0"
                    wrapMode: Text.WordWrap
                }
                
                Column {
                    width: parent.width
                    spacing: control.theme ? control.theme.spacingMD : 16
                    
                    Text {
                        text: "Verification Code"
                        font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                        font.bold: true
                        color: control.theme ? control.theme.textPrimary : "#ffffff"
                    }
                    
                    AppInput {
                        id: codeInput
                        width: parent.width
                        theme: control.theme
                        placeholderText: "000000"
                        maximumLength: 6
                        validator: IntValidator { bottom: 0; top: 999999 }
                    }
                }
                
                AppButton {
                    id: verifyButton
                    width: parent.width
                    text: "Verify"
                    theme: control.theme
                    enabled: codeInput.text.length === 6
                    
                    onClicked: {
                        control.authController.verify_two_factor(codeInput.text)
                    }
                }
                
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: "Resend code"
                    font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                    color: control.theme ? control.theme.primary : "#0078d4"
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            // Resend logic would go here
                            console.log("Resend code")
                        }
                    }
                }
            }
        }
    }
}
