import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Flickable {
    id: control
    
    property var theme
    property var settingsController
    
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
            width: parent.width
            spacing: theme ? theme.spacingM : 16
            
            Text {
                text: "System Configuration"
                font.pixelSize: theme ? theme.fontSizeXXL : 32
                font.bold: true
                color: theme ? theme.textPrimary : "#ffffff"
                Layout.alignment: Qt.AlignLeft
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            AppButton {
                text: "Reset to Defaults"
                backgroundColor: theme ? theme.danger : "#d13438"
                theme: control.theme
                Layout.alignment: Qt.AlignRight
                onClicked: {
                    if (settingsController) {
                        settingsController.resetToDefaults()
                    }
                }
            }
        }
        
        // Settings categories
        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: theme ? theme.spacingM : 16
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            
            // General Settings
            AppCard {
                width: parent.width
                height: theme ? theme.cardHeightS : 60
                theme: control.theme
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Text {
                        text: "⚙️"
                        font.pixelSize: theme ? theme.fontSizeXXL : 32
                        Layout.alignment: Qt.AlignVCenter
                    }
                    
                    Column {
                        Layout.fillWidth: true
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "General"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "Application settings, theme, language"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    AppButton {
                        text: "Configure"
                        backgroundColor: theme ? theme.primary : "#0078d4"
                        theme: control.theme
                        Layout.alignment: Qt.AlignVCenter
                        onClicked: {
                            generalSettingsLoader.source = "GeneralSettings.qml"
                            generalSettingsLoader.item.open()
                        }
                    }
                }
            }
            
            // Camera Settings
            AppCard {
                width: parent.width
                height: theme ? theme.cardHeightS : 60
                theme: control.theme
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Text {
                        text: "📹"
                        font.pixelSize: theme ? theme.fontSizeXXL : 32
                        Layout.alignment: Qt.AlignVCenter
                    }
                    
                    Column {
                        Layout.fillWidth: true
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Camera"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "Resolution, FPS, recording, retention"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    AppButton {
                        text: "Configure"
                        backgroundColor: theme ? theme.primary : "#0078d4"
                        theme: control.theme
                        Layout.alignment: Qt.AlignVCenter
                        onClicked: {
                            cameraSettingsLoader.source = "CameraSettings.qml"
                            cameraSettingsLoader.item.open()
                        }
                    }
                }
            }
            
            // AI Settings
            AppCard {
                width: parent.width
                height: theme ? theme.cardHeightS : 60
                theme: control.theme
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Text {
                        text: "🤖"
                        font.pixelSize: theme ? theme.fontSizeXXL : 32
                        Layout.alignment: Qt.AlignVCenter
                    }
                    
                    Column {
                        Layout.fillWidth: true
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "AI & Inference"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "Model, confidence, detection settings"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    AppButton {
                        text: "Configure"
                        backgroundColor: theme ? theme.primary : "#0078d4"
                        theme: control.theme
                        Layout.alignment: Qt.AlignVCenter
                        onClicked: {
                            aiSettingsLoader.source = "AISettings.qml"
                            aiSettingsLoader.item.open()
                        }
                    }
                }
            }
            
            // Notification Settings
            AppCard {
                width: parent.width
                height: theme ? theme.cardHeightS : 60
                theme: control.theme
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Text {
                        text: "🔔"
                        font.pixelSize: theme ? theme.fontSizeXXL : 32
                        Layout.alignment: Qt.AlignVCenter
                    }
                    
                    Column {
                        Layout.fillWidth: true
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Notifications"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "Email, SMS, push, quiet hours"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    AppButton {
                        text: "Configure"
                        backgroundColor: theme ? theme.primary : "#0078d4"
                        theme: control.theme
                        Layout.alignment: Qt.AlignVCenter
                        onClicked: {
                            notificationSettingsLoader.source = "NotificationSettings.qml"
                            notificationSettingsLoader.item.open()
                        }
                    }
                }
            }
            
            // Storage Settings
            AppCard {
                width: parent.width
                height: theme ? theme.cardHeightS : 60
                theme: control.theme
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Text {
                        text: "💾"
                        font.pixelSize: theme ? theme.fontSizeXXL : 32
                        Layout.alignment: Qt.AlignVCenter
                    }
                    
                    Column {
                        Layout.fillWidth: true
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Storage"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "Storage path, limits, backup"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    AppButton {
                        text: "Configure"
                        backgroundColor: theme ? theme.primary : "#0078d4"
                        theme: control.theme
                        Layout.alignment: Qt.AlignVCenter
                        onClicked: {
                            storageSettingsLoader.source = "StorageSettings.qml"
                            storageSettingsLoader.item.open()
                        }
                    }
                }
            }
            
            // Security Settings
            AppCard {
                width: parent.width
                height: theme ? theme.cardHeightS : 60
                theme: control.theme
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16
                    
                    Text {
                        text: "🔒"
                        font.pixelSize: theme ? theme.fontSizeXXL : 32
                        Layout.alignment: Qt.AlignVCenter
                    }
                    
                    Column {
                        Layout.fillWidth: true
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "Security"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: "Session, authentication, passwords"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            color: theme ? theme.textSecondary : "#a0a0a0"
                        }
                    }
                    
                    AppButton {
                        text: "Configure"
                        backgroundColor: theme ? theme.primary : "#0078d4"
                        theme: control.theme
                        Layout.alignment: Qt.AlignVCenter
                        onClicked: {
                            securitySettingsLoader.source = "SecuritySettings.qml"
                            securitySettingsLoader.item.open()
                        }
                    }
                }
            }
        }
    }
    
    // Loaders for settings dialogs
    Loader {
        id: generalSettingsLoader
        sourceComponent: Component {
            GeneralSettings {
                theme: control.theme
                settingsController: control.settingsController
            }
        }
    }
    
    Loader {
        id: cameraSettingsLoader
        sourceComponent: Component {
            CameraSettings {
                theme: control.theme
                settingsController: control.settingsController
            }
        }
    }
    
    Loader {
        id: aiSettingsLoader
        sourceComponent: Component {
            AISettings {
                theme: control.theme
                settingsController: control.settingsController
            }
        }
    }
    
    Loader {
        id: notificationSettingsLoader
        sourceComponent: Component {
            NotificationSettings {
                theme: control.theme
                settingsController: control.settingsController
            }
        }
    }
    
    Loader {
        id: storageSettingsLoader
        sourceComponent: Component {
            StorageSettings {
                theme: control.theme
                settingsController: control.settingsController
            }
        }
    }
    
    Loader {
        id: securitySettingsLoader
        sourceComponent: Component {
            SecuritySettings {
                theme: control.theme
                settingsController: control.settingsController
            }
        }
    }
}
