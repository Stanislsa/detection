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
                text: "User Directory"
                font.pixelSize: theme ? theme.fontSizeXXL : 32
                font.bold: true
                color: theme ? theme.textPrimary : "#ffffff"
                Layout.alignment: Qt.AlignLeft
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            AppButton {
                text: "Add User"
                backgroundColor: theme ? theme.primary : "#0078d4"
                theme: control.theme
                Layout.alignment: Qt.AlignRight
                onClicked: {
                    // Open CreateUserDialog
                    createUserLoader.source = "CreateUserDialog.qml"
                    if (createUserLoader.item) {
                        createUserLoader.item.open()
                    }
                }
            }
        }
        
        // KPI Cards
        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: theme ? theme.spacingM : 16
            
            KpiCard {
                title: "Total Users"
                value: userController ? userController.userCount : 0
                icon: "👥"
                theme: control.theme
                Layout.preferredWidth: theme ? theme.columnWidthS : 150
            }
            
            KpiCard {
                title: "Active"
                value: userController ? userController.userStatistics.active : 0
                icon: "✅"
                theme: control.theme
                Layout.preferredWidth: theme ? theme.columnWidthS : 150
            }
            
            KpiCard {
                title: "Inactive"
                value: userController ? userController.userStatistics.inactive : 0
                icon: "⚪"
                theme: control.theme
                Layout.preferredWidth: theme ? theme.columnWidthS : 150
            }
            
            KpiCard {
                title: "Pending"
                value: userController ? userController.userStatistics.pending : 0
                icon: "⏳"
                theme: control.theme
                Layout.preferredWidth: theme ? theme.columnWidthS : 150
            }
        }
        
        // Search and Filters
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: theme ? theme.cardHeightM : 80
            theme: control.theme
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingM : 16
                
                Column {
                    width: theme ? theme.columnWidthM : 200
                    spacing: theme ? theme.spacingXS : 4
                    
                    Text {
                        text: "Search"
                        font.pixelSize: theme ? theme.fontSizeXS : 10
                        color: theme ? theme.textSecondary : "#a0a0a0"
                    }
                    
                    AppInput {
                        id: searchInput
                        width: parent.width
                        placeholderText: "Search users..."
                        theme: control.theme
                        onTextChanged: {
                            if (userController && text.length > 2) {
                                filteredUsers = userController.searchUsers(text)
                            } else {
                                filteredUsers = userController ? userController.users : []
                            }
                        }
                    }
                }
                
                Column {
                    width: theme ? theme.columnWidthS : 150
                    spacing: theme ? theme.spacingXS : 4
                    
                    Text {
                        text: "Role"
                        font.pixelSize: theme ? theme.fontSizeXS : 10
                        color: theme ? theme.textSecondary : "#a0a0a0"
                    }
                    
                    AppComboBox {
                        id: roleFilter
                        width: parent.width
                        theme: control.theme
                        model: ["All", "Admin", "Operator", "Viewer", "Analyst"]
                        currentIndex: 0
                        onCurrentTextChanged: {
                            applyFilters()
                        }
                    }
                }
                
                Column {
                    width: theme ? theme.columnWidthS : 150
                    spacing: theme ? theme.spacingXS : 4
                    
                    Text {
                        text: "Status"
                        font.pixelSize: theme ? theme.fontSizeXS : 10
                        color: theme ? theme.textSecondary : "#a0a0a0"
                    }
                    
                    AppComboBox {
                        id: statusFilter
                        width: parent.width
                        theme: control.theme
                        model: ["All", "Active", "Inactive", "Pending", "Suspended"]
                        currentIndex: 0
                        onCurrentTextChanged: {
                            applyFilters()
                        }
                    }
                }
                
                Item {
                    Layout.fillWidth: true
                }
                
                AppButton {
                    text: "Clear Filters"
                    theme: control.theme
                    Layout.alignment: Qt.AlignVCenter
                    onClicked: {
                        searchInput.text = ""
                        roleFilter.currentIndex = 0
                        statusFilter.currentIndex = 0
                        filteredUsers = userController ? userController.users : []
                    }
                }
            }
        }
        
        // Users Table
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Users"
            font.pixelSize: theme ? theme.fontSizeL : 16
            font.bold: true
            color: theme ? theme.textPrimary : "#ffffff"
        }
        
        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: theme ? theme.spacingM : 16
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            
            Repeater {
                model: filteredUsers.length > 0 ? filteredUsers : (userController ? userController.users : [])
                
                AppCard {
                    width: parent.width
                    height: theme ? theme.cardHeightM : 80
                    theme: control.theme
                    border.color: {
                        if (modelData.status === "active") return theme ? theme.success : "#107c10"
                        if (modelData.status === "inactive") return theme ? theme.textDisabled : "#606060"
                        if (modelData.status === "pending") return theme ? theme.warning : "#ff8c00"
                        if (modelData.status === "suspended") return theme ? theme.danger : "#d13438"
                        return theme ? theme.border : "#404040"
                    }
                    border.width: theme ? theme.borderWidth : 2
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: theme ? theme.spacingM : 16
                        spacing: theme ? theme.spacingM : 16
                        
                        // Avatar/Initials
                        Rectangle {
                            width: theme ? theme.avatarSizeS : 50
                            height: theme ? theme.avatarSizeS : 50
                            radius: theme ? theme.avatarSizeS / 2 : 25
                            color: theme ? theme.surfaceElevated : "#3d3d3d"
                            Layout.alignment: Qt.AlignVCenter
                            
                            Text {
                                anchors.centerIn: parent
                                text: modelData.username ? modelData.username.substring(0, 2).toUpperCase() : "??"
                                font.pixelSize: theme ? theme.fontSizeL : 16
                                font.bold: true
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                        }
                        
                        // User info
                        Column {
                            Layout.fillWidth: true
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: modelData.username || "Unknown"
                                font.pixelSize: theme ? theme.fontSizeM : 14
                                font.bold: true
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                            
                            Text {
                                text: modelData.email || ""
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        // Role and Status
                        Column {
                            spacing: theme ? theme.spacingXS : 4
                            Layout.alignment: Qt.AlignVCenter
                            
                            Text {
                                text: modelData.role || "unknown"
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: modelData.status || "unknown"
                                font.pixelSize: theme ? theme.fontSizeXS : 10
                                color: {
                                    if (modelData.status === "active") return theme ? theme.success : "#107c10"
                                    if (modelData.status === "inactive") return theme ? theme.textDisabled : "#606060"
                                    if (modelData.status === "pending") return theme ? theme.warning : "#ff8c00"
                                    if (modelData.status === "suspended") return theme ? theme.danger : "#d13438"
                                    return theme ? theme.textSecondary : "#a0a0a0"
                                }
                            }
                        }
                        
                        // Last Login
                        Text {
                            text: "Last: " + (modelData.last_login_formatted || "Never")
                            font.pixelSize: theme ? theme.fontSizeXS : 10
                            color: theme ? theme.textDisabled : "#606060"
                            Layout.alignment: Qt.AlignVCenter
                        }
                        
                        // Actions
                        Row {
                            spacing: theme ? theme.spacingXS : 4
                            Layout.alignment: Qt.AlignVCenter
                            
                            AppButton {
                                text: "View"
                                backgroundColor: theme ? theme.surface : "#2d2d2d"
                                theme: control.theme
                                onClicked: {
                                    if (router) {
                                        router.navigateTo("user_detail", {"userId": modelData.id})
                                    }
                                }
                            }
                            
                            AppButton {
                                text: "Edit"
                                backgroundColor: theme ? theme.primary : "#0078d4"
                                theme: control.theme
                                onClicked: {
                                    // Open EditUserDialog
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    property var filteredUsers: []
    
    function applyFilters() {
        if (!userController) return
        
        var users = userController.users
        var role = roleFilter.currentText.toLowerCase()
        var status = statusFilter.currentText.toLowerCase()
        
        if (role !== "all") {
            users = users.filter(function(u) { return u.role === role })
        }
        if (status !== "all") {
            users = users.filter(function(u) { return u.status === status })
        }
        
        filteredUsers = users
    }
    
    Component.onCompleted: {
        filteredUsers = userController ? userController.users : []
    }
    
    // Loader for CreateUserDialog
    Loader {
        id: createUserLoader
        sourceComponent: Component {
            CreateUserDialog {
                theme: control.theme
                userController: control.userController
            }
        }
    }
}
