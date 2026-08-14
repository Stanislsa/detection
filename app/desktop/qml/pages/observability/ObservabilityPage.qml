import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"
import "../../cards"
import "../../charts"

Flickable {
    id: control
    
    property var theme
    property var healthController
    
    contentWidth: parent.width
    contentHeight: contentColumn.height + (theme ? theme.spacingXL : 48)
    clip: true
    
    Column {
        id: contentColumn
        width: parent.width
        spacing: theme ? theme.spacingL : 24
        anchors.top: parent.top
        anchors.topMargin: theme ? theme.spacingL : 24
        
        // Header with Navigation Buttons
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            spacing: theme ? theme.spacingM : 16
            
            Text {
                text: "Infrastructure Observability"
                font.pixelSize: theme ? theme.fontSizeXXL : 32
                font.bold: true
                color: theme ? theme.textPrimary : "#ffffff"
                anchors.verticalCenter: parent.verticalCenter
            }
            
            Item {
                width: 1
                height: parent.height
            }
            
            Row {
                spacing: theme ? theme.spacingXS : 4
                
                Rectangle {
                    width: 120
                    height: 32
                    radius: theme ? theme.radiusS : 4
                    color: theme ? theme.primary : "#2563EB"
                    
                    Text {
                        anchors.centerIn: parent
                        text: "SYSTEM HEALTH"
                        font.pixelSize: theme ? fontSizeXS : 10
                        font.bold: true
                        color: "#ffffff"
                    }
                }
                
                Rectangle {
                    width: 100
                    height: 32
                    radius: theme ? theme.radiusS : 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"
                    border.width: 1
                    
                    Text {
                        anchors.centerIn: parent
                        text: "PERFORMANCE"
                        font.pixelSize: theme ? fontSizeXS : 10
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                }
                
                Rectangle {
                    width: 60
                    height: 32
                    radius: theme ? theme.radiusS : 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"
                    border.width: 1
                    
                    Text {
                        anchors.centerIn: parent
                        text: "LOGS"
                        font.pixelSize: theme ? fontSizeXS : 10
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                }
                
                Rectangle {
                    width: 60
                    height: 32
                    radius: theme ? theme.radiusS : 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"
                    border.width: 1
                    
                    Text {
                        anchors.centerIn: parent
                        text: "ALERTS"
                        font.pixelSize: theme ? fontSizeXS : 10
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                }
            }
            
            // Overall status indicator
            Rectangle {
                width: 120
                height: 32
                radius: theme ? theme.radiusS : 4
                color: theme ? theme.success : "#10B981"
                
                Text {
                    anchors.centerIn: parent
                    text: "HEALTHY"
                    font.pixelSize: theme ? fontSizeXS : 10
                    font.bold: true
                    color: "#ffffff"
                }
            }
        }
        
        // Component status cards
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Component Status"
            font.pixelSize: theme ? theme.fontSizeL : 16
            font.bold: true
            color: theme ? theme.textPrimary : "#ffffff"
        }
        
        GridLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            columns: Math.max(1, Math.floor(width / (theme ? theme.columnWidthM : 200 + (theme ? theme.spacingM : 16))))
            columnSpacing: theme ? theme.spacingM : 16
            rowSpacing: theme ? theme.spacingM : 16
            
            Repeater {
                model: healthController ? healthController.components : []
                
                AppCard {
                    width: theme ? theme.columnWidthM : 200
                    height: theme ? theme.cardHeightL : 120
                    theme: control.theme
                    border.color: {
                        if (modelData.status === "healthy") return theme ? theme.success : "#107c10"
                        if (modelData.status === "degraded") return theme ? theme.warning : "#ff8c00"
                        if (modelData.status === "unhealthy") return theme ? theme.danger : "#d13438"
                        return theme ? theme.border : "#404040"
                    }
                    border.width: 2
                    
                    Column {
                        anchors.fill: parent
                        anchors.margins: theme ? theme.spacingM : 16
                        spacing: theme ? theme.spacingXS : 4
                        
                        Text {
                            text: modelData.name || "Component"
                            font.pixelSize: theme ? theme.fontSizeM : 14
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                        
                        Text {
                            text: modelData.status || "unknown"
                            font.pixelSize: theme ? theme.fontSizeS : 12
                            color: {
                                if (modelData.status === "healthy") return theme ? theme.success : "#107c10"
                                if (modelData.status === "degraded") return theme ? theme.warning : "#ff8c00"
                                if (modelData.status === "unhealthy") return theme ? theme.danger : "#d13438"
                                return theme ? theme.textSecondary : "#a0a0a0"
                            }
                        }
                        
                        Item {
                            width: parent.width
                            height: parent.height - parent.height
                        }
                        
                        // Latest metric value
                        Text {
                            text: {
                                if (modelData.metrics && modelData.metrics.length > 0) {
                                    const metric = modelData.metrics[modelData.metrics.length - 1]
                                    return metric.value.toFixed(1) + " " + metric.unit
                                }
                                return "N/A"
                            }
                            font.pixelSize: theme ? theme.fontSizeXL : 24
                            font.bold: true
                            color: theme ? theme.textPrimary : "#ffffff"
                        }
                    }
                }
            }
        }
        
        // Charts section
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Resource Usage"
            font.pixelSize: theme ? theme.fontSizeL : 16
            font.bold: true
            color: theme ? theme.textPrimary : "#ffffff"
        }
        
        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: theme ? theme.spacingM : 16
            
            // CPU Gauge
            AppCard {
                width: 250
                height: 250
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingS : 8
                    
                    Text {
                        text: "CPU Usage"
                        font.pixelSize: theme ? theme.fontSizeM : 14
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    Gauge {
                        width: 180
                        height: 180
                        anchors.horizontalCenter: parent.horizontalCenter
                        value: {
                            if (healthController) {
                                const cpu = healthController.getComponent("cpu")
                                if (cpu && cpu.metrics && cpu.metrics.length > 0) {
                                    return cpu.metrics[cpu.metrics.length - 1].value
                                }
                            }
                            return 0
                        }
                        maxValue: 100
                        unit: "%"
                        theme: control.theme
                    }
                }
            }
            
            // RAM Gauge
            AppCard {
                width: 250
                height: 250
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingS : 8
                    
                    Text {
                        text: "Memory Usage"
                        font.pixelSize: theme ? theme.fontSizeM : 14
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    Gauge {
                        width: 180
                        height: 180
                        anchors.horizontalCenter: parent.horizontalCenter
                        value: {
                            if (healthController) {
                                const ram = healthController.getComponent("ram")
                                if (ram && ram.metrics && ram.metrics.length > 0) {
                                    return ram.metrics[ram.metrics.length - 1].value
                                }
                            }
                            return 0
                        }
                        maxValue: 100
                        unit: "%"
                        theme: control.theme
                    }
                }
            }
            
            // GPU Gauge
            AppCard {
                width: 250
                height: 250
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingS : 8
                    
                    Text {
                        text: "GPU Usage"
                        font.pixelSize: theme ? theme.fontSizeM : 14
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    Gauge {
                        width: 180
                        height: 180
                        anchors.horizontalCenter: parent.horizontalCenter
                        value: {
                            if (healthController) {
                                const gpu = healthController.getComponent("gpu")
                                if (gpu && gpu.metrics && gpu.metrics.length > 0) {
                                    return gpu.metrics[gpu.metrics.length - 1].value
                                }
                            }
                            return 0
                        }
                        maxValue: 100
                        unit: "%"
                        theme: control.theme
                    }
                }
            }
        }
        
        // Latency charts
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Performance Metrics"
            font.pixelSize: theme ? theme.fontSizeL : 16
            font.bold: true
            color: theme ? theme.textPrimary : "#ffffff"
        }
        
        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: theme ? theme.spacingM : 16
            
            // Inference Latency
            AppCard {
                width: 400
                height: 200
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingS : 8
                    
                    Text {
                        text: "AI Inference Latency"
                        font.pixelSize: theme ? theme.fontSizeM : 14
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    LineChart {
                        width: parent.width
                        height: parent.height - parent.height
                        data: {
                            if (healthController) {
                                const history = healthController.getMetricHistory("ai_inference", 30)
                                return history.map(m => m.value)
                            }
                            return []
                        }
                        theme: control.theme
                    }
                }
            }
            
            // API Latency
            AppCard {
                width: 400
                height: 200
                theme: control.theme
                
                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingS : 8
                    
                    Text {
                        text: "API Latency"
                        font.pixelSize: theme ? theme.fontSizeM : 14
                        font.bold: true
                        color: theme ? theme.textPrimary : "#ffffff"
                    }
                    
                    LineChart {
                        width: parent.width
                        height: parent.height - parent.height
                        data: {
                            if (healthController) {
                                const history = healthController.getMetricHistory("api_latency", 30)
                                return history.map(m => m.value)
                            }
                            return []
                        }
                        theme: control.theme
                    }
                }
            }
        }
        
        // Events/sec chart
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: 200
            theme: control.theme
            
            Column {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingS : 8
                
                Text {
                    text: "Event Bus Throughput"
                    font.pixelSize: theme ? theme.fontSizeM : 14
                    font.bold: true
                    color: theme ? theme.textPrimary : "#ffffff"
                }
                
                LineChart {
                    width: parent.width
                    height: parent.height - parent.height
                    data: {
                        if (healthController) {
                            const history = healthController.getMetricHistory("event_bus", 50)
                            return history.map(m => m.value)
                        }
                        return []
                    }
                    theme: control.theme
                }
            }
        }
    }
    
    Connections {
        target: healthController
        function onMetricsChanged() {
            // Force refresh when metrics update
        }
        function onHealthStatusChanged() {
            // Force refresh when health status changes
        }
    }
}
