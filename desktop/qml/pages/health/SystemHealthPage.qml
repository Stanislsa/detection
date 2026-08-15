import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Item {
    id: control
    property var theme
    readonly property bool isNarrow: width < 960
    readonly property bool isMobile: width < 720
    readonly property int pageMargin: isMobile ? 10 : (isNarrow ? 14 : 24)
    property var healthController
    property var serviceHealthController

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
                Text { text: "System Health & Infrastructure"; font.pixelSize: theme ? theme.fontSizeXXL : 20; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
                Text { text: "Monitoring core service telemetry and neural engine performance."; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8" }
            }
            Item { Layout.fillWidth: true }
            AppButton { text: "Refresh Status"; variant: "secondary"; theme: control.theme }
            AppButton { text: "View Full Logs"; variant: "primary"; theme: control.theme }
        }

        // Banner
        Rectangle {
            Layout.fillWidth: true; height: 100; radius: 6
            gradient: Gradient {
                GradientStop { position: 0; color: "#0F172A" }
                GradientStop { position: 1; color: "#1E3A5F" }
            }
            border.color: theme ? theme.border : "#1E293B"; border.width: 1
            Column {
                anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; anchors.leftMargin: 24; spacing: 6
                Rectangle {
                    width: st.implicitWidth + 16; height: 20; radius: 10
                    color: "#10B98133"
                    Text { id: st; anchors.centerIn: parent; text: "System: Verified Stable"; font.pixelSize: 10; font.weight: Font.Bold; color: theme ? theme.success : "#10B981" }
                }
                Text { text: "AI Cluster \"Sentient-A\" is Processing Live"; font.pixelSize: 18; font.weight: Font.Bold; color: "#E5E7EB" }
                Text { text: "All 512 edge nodes are communicating successfully. Current throughput is at 84% efficiency."; font.pixelSize: 12; color: "#94A3B8" }
            }
        }

        // KPI
        RowLayout {
            Layout.fillWidth: true; spacing: 12
            Repeater {
                model: [
                    { t: "OVERALL SYSTEM STATUS", v: "Operational", c: "success" },
                    { t: "UPTIME", v: "99.98%", c: "primary" },
                    { t: "ACTIVE SERVICES", v: "42 / 44", c: "warning" },
                    { t: "SECURITY THREATS BLOCKED", v: "1,284", c: "info" }
                ]
                Rectangle {
                    Layout.fillWidth: true; height: 80; radius: 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                    Column {
                        anchors.centerIn: parent; spacing: 4
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.t; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter; text: modelData.v
                            font.pixelSize: 20; font.weight: Font.Bold
                            color: modelData.c === "success" ? "#10B981" : (modelData.c === "warning" ? "#F59E0B" : (theme ? theme.textPrimary : "#E5E7EB"))
                        }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 16

            // Core services table
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 2
                radius: 4; color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                clip: true

                ColumnLayout {
                    anchors.fill: parent; spacing: 0
                    Rectangle {
                        Layout.fillWidth: true; height: 40
                        Text { anchors.left: parent.left; anchors.leftMargin: 16; anchors.verticalCenter: parent.verticalCenter; text: "Core Services Status"; font.pixelSize: 13; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                        Rectangle {
                            anchors.right: parent.right; anchors.rightMargin: 16; anchors.verticalCenter: parent.verticalCenter
                            width: svcT.implicitWidth + 12; height: 20; radius: 10; color: "#10B98122"
                            Text { id: svcT; anchors.centerIn: parent; text: "SERVICES: 44 ACTIVE"; font.pixelSize: 9; font.weight: Font.Bold; color: "#10B981" }
                        }
                    }
                    Rectangle {
                        Layout.fillWidth: true; height: 28
                        color: theme ? theme.backgroundAlt : "#0F172A"
                        Row {
                            anchors.fill: parent; anchors.leftMargin: 16
                            Text { width: 180; anchors.verticalCenter: parent.verticalCenter; text: "SERVICE NAME"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { width: 70; anchors.verticalCenter: parent.verticalCenter; text: "TYPE"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { width: 100; anchors.verticalCenter: parent.verticalCenter; text: "STATUS"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { width: 70; anchors.verticalCenter: parent.verticalCenter; text: "LATENCY"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { anchors.verticalCenter: parent.verticalCenter; text: "UPTIME"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        }
                    }
                    ListView {
                        Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                        model: [
                            { n: "Neural Threat Engine", id: "ai-engine-01", type: "Core", s: "OPERATIONAL", lat: "12ms", up: "100%" },
                            { n: "Event Log Database", id: "db-cluster-01", type: "Storage", s: "OPERATIONAL", lat: "45ms", up: "99.95%" },
                            { n: "Video Stream Processor", id: "stream-proc-02", type: "Media", s: "DEGRADED", lat: "156ms", up: "98.2%" },
                            { n: "Identity Provider", id: "auth-svc-01", type: "Security", s: "OPERATIONAL", lat: "8ms", up: "100%" },
                            { n: "SDN Controller", id: "net-mgr-03", type: "Network", s: "CRITICAL", lat: "N/A", up: "84.1%" }
                        ]
                        delegate: Rectangle {
                            width: ListView.view.width; height: 48
                            color: index % 2 ? (theme ? theme.backgroundAlt : "#0F172A") : "transparent"
                            Row {
                                anchors.fill: parent; anchors.leftMargin: 16
                                Column {
                                    width: 180; anchors.verticalCenter: parent.verticalCenter
                                    Text { text: modelData.n; font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB" }
                                    Text { text: modelData.id; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                }
                                Text { width: 70; anchors.verticalCenter: parent.verticalCenter; text: modelData.type; font.pixelSize: 11; color: theme ? theme.textSecondary : "#94A3B8" }
                                Rectangle {
                                    width: 95; height: 20; radius: 4; anchors.verticalCenter: parent.verticalCenter
                                    color: modelData.s === "OPERATIONAL" ? "#10B98122" : (modelData.s === "DEGRADED" ? "#F59E0B22" : "#EF444422")
                                    Text { anchors.centerIn: parent; text: modelData.s; font.pixelSize: 9; font.weight: Font.Bold
                                        color: modelData.s === "OPERATIONAL" ? "#10B981" : (modelData.s === "DEGRADED" ? "#F59E0B" : "#EF4444") }
                                }
                                Item { width: 5; height: 1 }
                                Text { width: 70; anchors.verticalCenter: parent.verticalCenter; text: modelData.lat; font.pixelSize: 12; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textSecondary : "#94A3B8" }
                                Text { anchors.verticalCenter: parent.verticalCenter; text: modelData.up; font.pixelSize: 12; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textSecondary : "#94A3B8" }
                            }
                        }
                    }
                }
            }

            // Right: performance + events
            ColumnLayout {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 1; spacing: 12

                Rectangle {
                    Layout.fillWidth: true; Layout.preferredHeight: 160
                    radius: 4; color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                    Column {
                        anchors.fill: parent; anchors.margins: 14; spacing: 8
                        Text { text: "System Performance"; font.pixelSize: 12; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                        Canvas {
                            width: parent.width; height: 100
                            onPaint: {
                                var ctx = getContext("2d"); ctx.clearRect(0,0,width,height)
                                ctx.strokeStyle = "#10B981"; ctx.lineWidth = 2; ctx.beginPath()
                                var pts = [0.5,0.55,0.5,0.6,0.7,0.9,0.85,0.6,0.5,0.45,0.4]
                                for (var i=0;i<pts.length;i++){ var x=i/(pts.length-1)*width; var y=height-pts[i]*height; if(i===0)ctx.moveTo(x,y); else ctx.lineTo(x,y) }
                                ctx.stroke()
                                ctx.strokeStyle = "#06B6D4"; ctx.beginPath()
                                pts = [0.3,0.35,0.4,0.45,0.5,0.55,0.5,0.45,0.4,0.35,0.3]
                                for (var j=0;j<pts.length;j++){ var x2=j/(pts.length-1)*width; var y2=height-pts[j]*height; if(j===0)ctx.moveTo(x2,y2); else ctx.lineTo(x2,y2) }
                                ctx.stroke()
                            }
                            Component.onCompleted: requestPaint()
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true; Layout.fillHeight: true
                    radius: 4; color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                    Column {
                        anchors.fill: parent; anchors.margins: 14; spacing: 8
                        Text { text: "Recent System Events"; font.pixelSize: 12; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                        Repeater {
                            model: [
                                { s: "CRITICAL", m: "Network link loss on SDN-Gateway-03", t: "14:22:15" },
                                { s: "WARNING", m: "Thermal Threshold Reached: Rack B-12", t: "13:58:04" },
                                { s: "INFO", m: "Database Backup Successful", t: "12:30:11" }
                            ]
                            Column {
                                width: parent.width; spacing: 2
                                Row {
                                    spacing: 8
                                    Text { text: modelData.s; font.pixelSize: 10; font.weight: Font.Bold; font.family: theme ? theme.fontFamilyMono : "monospace"
                                        color: modelData.s === "CRITICAL" ? "#EF4444" : (modelData.s === "WARNING" ? "#F59E0B" : "#06B6D4") }
                                    Text { text: modelData.t; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                }
                                Text { text: modelData.m; font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB"; width: parent.width; wrapMode: Text.WordWrap }
                            }
                        }
                    }
                }
            }
        }

        // Resource cards
        RowLayout {
            Layout.fillWidth: true; spacing: 12
            Repeater {
                model: [
                    { t: "CPU Clusters", v: "42%", s: "Avg Load" },
                    { t: "Memory Pool", v: "68%", s: "Utilized" },
                    { t: "Data Storage", v: "91%", s: "Capacity" },
                    { t: "Network I/O", v: "1.2", s: "Gbps" }
                ]
                Rectangle {
                    Layout.fillWidth: true; height: 80; radius: 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                    Column {
                        anchors.centerIn: parent; spacing: 4
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.t; font.pixelSize: 11; color: theme ? theme.textMuted : "#64748B" }
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.v; font.pixelSize: 20; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.s; font.pixelSize: 10; color: theme ? theme.textSecondary : "#94A3B8" }
                    }
                }
            }
        }
    }
}
}
