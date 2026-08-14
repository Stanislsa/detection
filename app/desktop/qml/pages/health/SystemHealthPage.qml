import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"
import "../../cards"

Flickable {
    id: control
    
    property var theme
    property var serviceHealthController
    
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
                text: "System Health & Infrastructure"
                font.pixelSize: theme ? theme.fontSizeXXL : 32
                font.bold: true
                color: theme ? theme.textPrimary : "#ffffff"
                Layout.alignment: Qt.AlignLeft
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            // Overall status indicator
            Rectangle {
                width: theme ? theme.columnWidthS : 120
                height: theme ? theme.buttonHeight : 40
                radius: theme ? theme.radiusM : 8
                color: {
                    if (serviceHealthController && serviceHealthController.overallStatus === "healthy") return theme ? theme.success : "#107c10"
                    if (serviceHealthController && serviceHealthController.overallStatus === "warning") return theme ? theme.warning : "#ff8c00"
                    if (serviceHealthController && serviceHealthController.overallStatus === "critical") return theme ? theme.danger : "#d13438"
                    return theme ? theme.surface : "#2d2d2d"
                }
                
                Text {
                    anchors.centerIn: parent
                    text: serviceHealthController ? serviceHealthController.overallStatus.toUpperCase() : "UNKNOWN"
                    font.pixelSize: theme ? theme.fontSizeS : 12
                    font.bold: true
                    color: "#ffffff"
                }
            }
            
            AppButton {
                text: "Refresh"
                backgroundColor: theme ? theme.primary : "#0078d4"
                theme: control.theme
                Layout.alignment: Qt.AlignRight
                onClicked: {
                    if (serviceHealthController) {
                        serviceHealthController.refreshHealth()
                    }
                }
            }
        }
        
        // KPI Cards
        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            spacing: theme ? theme.spacingM : 16
            
            KpiCard {
                title: "Total Services"
                value: serviceHealthController ? serviceHealthController.healthStatistics.total : 0
                icon: "📊"
                theme: control.theme
                Layout.fillWidth: true
                Layout.preferredWidth: theme ? theme.columnWidthS : 150
            }
            
            KpiCard {
                title: "Healthy"
                value: serviceHealthController ? serviceHealthController.healthStatistics.healthy : 0
                icon: "✅"
                theme: control.theme
                Layout.fillWidth: true
                Layout.preferredWidth: theme ? theme.columnWidthS : 150
            }
            
            KpiCard {
                title: "Warning"
                value: serviceHealthController ? serviceHealthController.healthStatistics.warning : 0
                icon: "⚠️"
                theme: control.theme
                Layout.fillWidth: true
                Layout.preferredWidth: theme ? theme.columnWidthS : 150
            }
            
            KpiCard {
                title: "Critical"
                value: serviceHealthController ? serviceHealthController.healthStatistics.critical : 0
                icon: "🔴"
                theme: control.theme
                Layout.fillWidth: true
                Layout.preferredWidth: theme ? theme.columnWidthS : 150
            }
        }
        
        // Services list
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Services Status"
            font.pixelSize: theme ? theme.fontSizeL : 16
            font.bold: true
            color: theme ? theme.textPrimary : "#ffffff"
        }
        
        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: theme ? theme.spacingM : 16
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            
            Repeater {
                model: serviceHealthController ? serviceHealthController.services : []
                
                AppCard {
                    width: parent.width
                    height: theme ? theme.cardHeightM : 140
                    theme: control.theme
                    border.color: {
                        if (modelData.status === "healthy") return theme ? theme.success : "#107c10"
                        if (modelData.status === "warning") return theme ? theme.warning : "#ff8c00"
                        if (modelData.status === "critical") return theme ? theme.danger : "#d13438"
                        if (modelData.status === "offline") return theme ? theme.textDisabled : "#606060"
                        return theme ? theme.border : "#404040"
                    }
                    border.width: 2
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: theme ? theme.spacingM : 16
                        spacing: theme ? theme.spacingM : 16
                        
                        // Status icon
                        Text {
                            text: {
                                if (modelData.status === "healthy") return "✅"
                                if (modelData.status === "warning") return "⚠️"
                                if (modelData.status === "critical") return "🔴"
                                if (modelData.status === "offline") return "⚫"
                                return "❓"
                            }
                            font.pixelSize: theme ? theme.fontSizeXXL : 32
                            Layout.alignment: Qt.AlignVCenter
                        }
                        
                        // Service info
                        Column {
                            Layout.fillWidth: true
                            spacing: theme ? theme.spacingXS : 4
                            
                            Text {
                                text: modelData.name || "Service"
                                font.pixelSize: theme ? theme.fontSizeM : 14
                                font.bold: true
                                color: theme ? theme.textPrimary : "#ffffff"
                            }
                            
                            Text {
                                text: modelData.status || "unknown"
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                color: {
                                    if (modelData.status === "healthy") return theme ? theme.success : "#107c10"
                                    if (modelData.status === "warning") return theme ? theme.warning : "#ff8c00"
                                    if (modelData.status === "critical") return theme ? theme.danger : "#d13438"
                                    if (modelData.status === "offline") return theme ? theme.textDisabled : "#606060"
                                    return theme ? theme.textSecondary : "#a0a0a0"
                                }
                            }
                            
                            Text {
                                text: "Version: " + (modelData.version || "N/A")
                                font.pixelSize: theme ? theme.fontSizeXS : 10
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        // Metrics
                        Column {
                            spacing: theme ? theme.spacingXS : 4
                            Layout.alignment: Qt.AlignVCenter
                            
                            Text {
                                text: "Uptime: " + (modelData.uptime_formatted || "N/A")
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: "Latency: " + (modelData.latency ? modelData.latency.toFixed(1) + " ms" : "N/A")
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            
                            Text {
                                text: "Last Check: " + (modelData.last_check_formatted || "N/A")
                                font.pixelSize: theme ? theme.fontSizeXS : 10
                                color: theme ? theme.textDisabled : "#606060"
                            }
                        }
                    }
                }
            }
        }
    }
    
    Connections {
        target: serviceHealthController
        function onHealthChanged() {
            // Force refresh when health changes
        }
    }
}
