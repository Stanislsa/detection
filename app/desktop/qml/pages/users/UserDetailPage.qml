import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"
import "../../cards"

Flickable {
    id: control
    
    property var theme
    property var userController
    property var router
    property string userId: ""
    
    contentWidth: parent.width
    contentHeight: contentColumn.height + (theme ? theme.spacingXL : 48)
    clip: true
    
    property var currentUser: null
    
    Component.onCompleted: {
        if (userController && userId) {
            currentUser = userController.getUser(userId)
        }
    }
    
    Connections {
        target: userController
        function onUsersChanged() {
            if (userController && userId) {
                currentUser = userController.getUser(userId)
            }
        }
    }
    
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
            
            AppButton {
                text: "← Back"
                backgroundColor: theme ? theme.surface : "#2d2d2d"
                theme: control.theme
                Layout.alignment: Qt.AlignLeft
                onClicked: {
                    if (router) {
                        router.navigateTo("users")
                    }
                }
            }
            
            Text {
                text: currentUser ? currentUser.username : "User Details"
                font.pixelSize: theme ? theme.fontSizeXXL : 32
                font.bold: true
                color: theme ? theme.textPrimary : "#ffffff"
                Layout.alignment: Qt.AlignLeft
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            Rectangle {
                width: theme ? theme.columnWidthS * 0.8 : 120
                height: theme ? theme.buttonHeight : 40
                radius: theme ? theme.radiusM : 8
                color: {
                    if (!currentUser) return theme ? theme.surface : "#2d2d2d"
                    if (currentUser.status === "active") return theme ? theme.success : "#107c10"
                    if (currentUser.status === "inactive") return theme ? theme.textDisabled : "#606060"
                    if (currentUser.status === "pending") return theme ? theme.warning : "#ff8c00"
                    if (currentUser.status === "suspended") return theme ? theme.danger : "#d13438"
                    return theme ? theme.surface : "#2d2d2d"
                }
                
                Text {
                    anchors.centerIn: parent
                    text: currentUser ? currentUser.status.toUpperCase() : "UNKNOWN"
                    font.pixelSize: theme ? theme.fontSizeS : 12
                    font.bold: true
                    color: "#ffffff"
                }
            }
            
            AppButton {
                text: "Edit"
                backgroundColor: theme ? theme.primary : "#0078d4"
                theme: control.theme
                Layout.alignment: Qt.AlignRight
                onClicked: {
                    // Open EditUserDialog
                }
            }
        }
        
        // User Info Card
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: theme ? theme.cardHeightL : 150
            theme: control.theme
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingL : 24
                spacing: theme ? theme.spacingL : 24
                
                // Avatar
                Rectangle {
                    width: theme ? theme.avatarSizeM : 100
                    height: theme ? theme.avatarSizeM : 100
                    radius: theme ? theme.avatarSizeM / 2 : 50
                    color: theme ? theme.surfaceElevated : "#3d3d3d"
                    Layout.alignment: Qt.AlignVCenter
                    
                    Text {
                        anchors.centerIn: parent
                        text: currentUser ? currentUser.username.substring(0, 2).toUpperCase() : "??"
                        font.pixelSize: theme ? theme.fontSizeXXL : 32
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                }
                
                // User Details
                Column {
                    Layout.fillWidth: true
                    spacing: theme ? theme.spacingS : 8
                    
                    Text {
                        text: currentUser ? currentUser.username : "Unknown"
                        font.pixelSize: theme ? theme.fontSizeXL : 24
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    Text {
                        text: currentUser ? currentUser.email : ""
                        font.pixelSize: theme ? theme.fontSizeM : 14
                        color: theme ? theme.textSecondary : "#a0a0a0"
                    }
                    
                    Row {
                        spacing: theme ? theme.spacingM : 16
                        
                        Column {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Role"
                                font.pixelSize: theme ? theme.fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: currentUser ? currentUser.role : "unknown"
                                font.pixelSize: theme ? theme.fontSizeM : 14
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                        }
                        
                        Column {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Status"
                                font.pixelSize: theme ? theme.fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: currentUser ? currentUser.status : "unknown"
                                font.pixelSize: theme ? theme.fontSizeM : 14
                                color: {
                                    if (!currentUser) return theme ? theme.textSecondary : "#a0a0a0"
                                    if (currentUser.status === "active") return theme ? theme.success : "#107c10"
                                    if (currentUser.status === "inactive") return theme ? theme.textDisabled : "#606060"
                                    if (currentUser.status === "pending") return theme ? theme.warning : "#ff8c00"
                                    if (currentUser.status === "suspended") return theme ? theme.danger : "#d13438"
                                    return theme ? theme.textSecondary : "#a0a0a0"
                                }
                            }
                        }
                        
                        Column {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Created"
                                font.pixelSize: theme ? theme.fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: currentUser ? currentUser.created_at_formatted : "N/A"
                                font.pixelSize: theme ? theme.fontSizeM : 14
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                        }
                        
                        Column {
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: "Last Login"
                                font.pixelSize: theme ? theme.fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: currentUser ? currentUser.last_login_formatted : "Never"
                                font.pixelSize: theme ? theme.fontSizeM : 14
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                        }
                    }
                }
            }
        }
        
        // Permissions Section
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Permissions"
            font.pixelSize: theme ? theme.fontSizeL : 16
            font.bold: true
            color: theme ? theme.textPrimary : "#ffffff"
        }
        
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: theme ? theme.cardHeightXL : 200
            theme: control.theme
            
            GridLayout {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                columns: 3
                columnSpacing: theme ? theme.spacingM : 16
                rowSpacing: theme ? theme.spacingS : 8
                
                Repeater {
                    model: currentUser ? currentUser.permissions : []
                    
                    Row {
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: "✓"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            color: theme ? theme.success : "#107c10"
                        }
                        
                        Text {
                            text: modelData.replace("_", " ").toUpperCase()
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                    }
                }
            }
        }
        
        // Activity Section
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Recent Activity"
            font.pixelSize: theme ? theme.fontSizeL : 16
            font.bold: true
            color: theme ? theme.textPrimary : "#ffffff"
        }
        
        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: theme ? theme.spacingM : 16
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            
            Repeater {
                model: currentUser ? currentUser.activities : []
                
                AppCard {
                    width: parent.width
                    height: theme ? theme.cardHeightS : 70
                    theme: control.theme
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: theme ? theme.spacingM : 16
                        spacing: theme ? theme.spacingM : 16
                        
                        Column {
                            Layout.fillWidth: true
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: modelData.action || "Unknown"
                                font.pixelSize: theme ? theme.fontSizeM : 14
                                font.bold: true
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                            
                            Text {
                                text: modelData.details || ""
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Text {
                            text: modelData.timestamp_formatted || "N/A"
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textDisabled : "#606060"
                            Layout.alignment: Qt.AlignVCenter
                        }
                    }
                }
            }
        }
    }
}
