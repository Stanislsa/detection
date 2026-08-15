import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"
import "../../charts"

Item {
    id: control
    property var theme
    readonly property bool isNarrow: width < 960
    readonly property bool isMobile: width < 720
    readonly property int pageMargin: isMobile ? 10 : (isNarrow ? 14 : 24)

    Flickable {
        id: pageScroll
        anchors.fill: parent
        contentWidth: width
        contentHeight: pageCol.implicitHeight + 32
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

    ColumnLayout {
        id: pageCol
        width: pageScroll.width - (pageScroll.width < 900 ? 24 : 48)
        x: pageScroll.width < 900 ? 12 : 24
        // top margin

        spacing: theme ? theme.spacingM : 16

        RowLayout {
            Layout.fillWidth: true
            Column {
                spacing: 4
                Text { text: "Infrastructure Observability"; font.pixelSize: theme ? theme.fontSizeXXL : 20; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
                Text { text: "Real-time hardware telemetry and system performance metrics."; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8" }
            }
            Item { Layout.fillWidth: true }
            Rectangle {
                width: liveT.implicitWidth + 20; height: 26; radius: 13
                color: "#10B98122"; border.color: theme ? theme.success : "#10B981"; border.width: 1
                Row {
                    anchors.centerIn: parent; spacing: 6
                    Rectangle { width: 6; height: 6; radius: 3; color: theme ? theme.success : "#10B981"; anchors.verticalCenter: parent.verticalCenter }
                    Text { id: liveT; text: "LIVE TELEMETRY"; font.pixelSize: 10; font.weight: Font.Bold; color: theme ? theme.success : "#10B981" }
                }
            }
            AppButton { text: "REFRESH DATA"; variant: "secondary"; theme: control.theme }
            AppButton { text: "SYSTEM LOGS"; variant: "primary"; theme: control.theme }
        }

        // KPI metrics
        RowLayout {
            Layout.fillWidth: true; spacing: 12
            Repeater {
                model: [
                    { t: "CPU LOAD", v: "64.2%", d: "+4.2%", up: true },
                    { t: "MEMORY USAGE", v: "12.8GB", d: "-1.1%", up: false },
                    { t: "GPU UTILIZATION", v: "88.5%", d: "+12.4%", up: true },
                    { t: "NETWORK THROUGHPUT", v: "420 Mb/s", d: "+15%", up: true }
                ]
                Rectangle {
                    Layout.fillWidth: true; height: 90; radius: 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                    Column {
                        anchors.fill: parent; anchors.margins: 14; spacing: 4
                        Text { text: modelData.t; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { text: modelData.v; font.pixelSize: 22; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
                        Text { text: modelData.d; font.pixelSize: 11; color: modelData.up ? (theme ? theme.success : "#10B981") : (theme ? theme.critical : "#EF4444") }
                    }
                }
            }
        }

        // Chart + services
        RowLayout {
            Layout.fillWidth: true; Layout.preferredHeight: 240; spacing: 16

            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 2
                radius: 4; color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                Column {
                    anchors.fill: parent; anchors.margins: 16; spacing: 8
                    Text { text: "SYSTEM PERFORMANCE TIMELINE"; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    // Simple sparkline placeholder
                    Canvas {
                        id: perfCanvas
                        width: parent.width; height: 160
                        onPaint: {
                            var ctx = getContext("2d")
                            ctx.clearRect(0, 0, width, height)
                            function drawLine(pts, color) {
                                ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.beginPath()
                                for (var i = 0; i < pts.length; i++) {
                                    var x = (i / (pts.length - 1)) * width
                                    var y = height - pts[i] * height
                                    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y)
                                }
                                ctx.stroke()
                            }
                            drawLine([0.3,0.4,0.55,0.7,0.65,0.5,0.45,0.6,0.75,0.7,0.55], "#2563EB")
                            drawLine([0.2,0.35,0.5,0.8,0.85,0.6,0.4,0.5,0.7,0.9,0.6], "#F59E0B")
                            drawLine([0.6,0.62,0.65,0.68,0.7,0.72,0.7,0.68,0.7,0.72,0.7], "#10B981")
                        }
                        Component.onCompleted: requestPaint()
                    }
                    Row {
                        spacing: 16
                        Row {
                            spacing: 6
                            Rectangle {
                                width: 10
                                height: 3
                                color: "#2563EB"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: "CPU"
                                font.pixelSize: 10
                                color: theme ? theme.textMuted : "#64748B"
                            }
                        }
                        Row {
                            spacing: 6
                            Rectangle {
                                width: 10
                                height: 3
                                color: "#F59E0B"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: "GPU"
                                font.pixelSize: 10
                                color: theme ? theme.textMuted : "#64748B"
                            }
                        }
                        Row {
                            spacing: 6
                            Rectangle {
                                width: 10
                                height: 3
                                color: "#10B981"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: "RAM"
                                font.pixelSize: 10
                                color: theme ? theme.textMuted : "#64748B"
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 1
                radius: 4; color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                Column {
                    anchors.fill: parent; anchors.margins: 16; spacing: 8
                    Text { text: "CORE AI SERVICE HEALTH"; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    Repeater {
                        model: [
                            { n: "Vision Engine Pro", s: "ACTIVE" },
                            { n: "Anomaly Detector", s: "ACTIVE" },
                            { n: "Vector DB Cluster", s: "DEGRADED" },
                            { n: "Stream Processor", s: "ACTIVE" },
                            { n: "Authentication API", s: "ACTIVE" },
                            { n: "Log Aggregator", s: "ACTIVE" }
                        ]
                        Row {
                            width: parent.width
                            Text { text: modelData.n; width: parent.width - 80; font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB" }
                            Rectangle {
                                width: 70; height: 18; radius: 9
                                color: modelData.s === "ACTIVE" ? "#10B98122" : "#F59E0B22"
                                Text { anchors.centerIn: parent; text: modelData.s; font.pixelSize: 9; font.weight: Font.Bold; color: modelData.s === "ACTIVE" ? "#10B981" : "#F59E0B" }
                            }
                        }
                    }
                }
            }
        }

        // Node inventory
        Rectangle {
            Layout.fillWidth: true; Layout.fillHeight: true
            radius: 4; color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"; border.width: 1
            clip: true

            ColumnLayout {
                anchors.fill: parent; spacing: 0
                Rectangle {
                    Layout.fillWidth: true; height: 40
                    color: "transparent"
                    Text { anchors.left: parent.left; anchors.leftMargin: 16; anchors.verticalCenter: parent.verticalCenter; text: "COMPUTE NODE INVENTORY"; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    AppInput { anchors.right: parent.right; anchors.rightMargin: 16; anchors.verticalCenter: parent.verticalCenter; width: 180; height: 28; theme: control.theme; placeholderText: "Filter nodes…"; leadingIcon: "search" }
                }
                Rectangle {
                    Layout.fillWidth: true; height: 32
                    color: theme ? theme.backgroundAlt : "#0F172A"
                    Row {
                        anchors.fill: parent; anchors.leftMargin: 16
                        Text { width: 180; anchors.verticalCenter: parent.verticalCenter; text: "NODE IDENTITY"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { width: 100; anchors.verticalCenter: parent.verticalCenter; text: "STATUS"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { width: 80; anchors.verticalCenter: parent.verticalCenter; text: "LATENCY"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { width: 80; anchors.verticalCenter: parent.verticalCenter; text: "UPTIME"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { anchors.verticalCenter: parent.verticalCenter; text: "LOAD DISTRIBUTION"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    }
                }
                ListView {
                    Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                    model: [
                        { n: "Core-Node-01", id: "0xeddd64", s: "Operational", lat: "12ms", up: "99.98%", load: 0.45 },
                        { n: "AI-Compute-X1", id: "0xdfc89", s: "High Load", lat: "45ms", up: "98.50%", load: 0.88 },
                        { n: "Storage-Array-A", id: "0xe2ec3", s: "Operational", lat: "8ms", up: "100.00%", load: 0.32 },
                        { n: "Edge-Gateway-04", id: "0x2f7cb", s: "Warning", lat: "156ms", up: "94.20%", load: 0.76 },
                        { n: "DB-Sentinel-Primary", id: "0x3b8ad", s: "Operational", lat: "5ms", up: "99.99%", load: 0.58 }
                    ]
                    delegate: Rectangle {
                        width: ListView.view.width; height: 44
                        color: index % 2 ? (theme ? theme.backgroundAlt : "#0F172A") : "transparent"
                        Row {
                            anchors.fill: parent; anchors.leftMargin: 16
                            Column {
                                width: 180; anchors.verticalCenter: parent.verticalCenter
                                Text { text: modelData.n; font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB" }
                                Text { text: "ID: " + modelData.id; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            }
                            Rectangle {
                                width: 90; height: 20; radius: 4; anchors.verticalCenter: parent.verticalCenter
                                color: modelData.s === "Operational" ? "#10B98122" : (modelData.s === "High Load" ? "#F59E0B22" : "#EF444422")
                                Text { anchors.centerIn: parent; text: modelData.s; font.pixelSize: 10; font.weight: Font.Bold
                                    color: modelData.s === "Operational" ? "#10B981" : (modelData.s === "High Load" ? "#F59E0B" : "#EF4444") }
                            }
                            Item { width: 10; height: 1 }
                            Text { width: 80; anchors.verticalCenter: parent.verticalCenter; text: modelData.lat; font.pixelSize: 12; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textSecondary : "#94A3B8" }
                            Text { width: 80; anchors.verticalCenter: parent.verticalCenter; text: modelData.up; font.pixelSize: 12; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textSecondary : "#94A3B8" }
                            Rectangle {
                                width: 120; height: 6; radius: 3; anchors.verticalCenter: parent.verticalCenter
                                color: theme ? theme.backgroundAlt : "#0F172A"
                                Rectangle { width: parent.width * modelData.load; height: parent.height; radius: 3; color: theme ? theme.primary : "#2563EB" }
                            }
                        }
                    }
                }
            }
        }
    }
}
}
