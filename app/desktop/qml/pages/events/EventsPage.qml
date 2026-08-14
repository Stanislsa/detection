import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Item {
    id: control
    property var theme
    property var eventController

    property int page: 1
    property int pageSize: 7
    property var sevFilters: ({ Critical: true, Warning: true, Information: true })
    property string searchText: ""
    property real minConfidence: 0.75

    readonly property var allEvents: [
        { time: "14:22:31", sev: "Critical", title: "Restricted Area Intrusion", cat: "PERSONNEL", conf: 98.4, desc: "Human detected in Zone B-4 (Vault Perimeter) during", cam: "CAM-VLT-02", node: "Processing Node Alpha-1" },
        { time: "14:18:12", sev: "Warning", title: "Unrecognized Vehicle Detect", cat: "VEHICLE", conf: 82.1, desc: "Black SUV (Plate: unknown) lingering at loading dock for >5", cam: "CAM-EXT-L1", node: "Processing Node Alpha-1" },
        { time: "14:15:00", sev: "Information", title: "Server Cabinet Door Open", cat: "ACCESS", conf: 99.9, desc: "Cabinet 04-A opened by authorized user (ID: 4421).", cam: "CAM-SRV-01", node: "Processing Node Alpha-1" },
        { time: "14:02:45", sev: "Critical", title: "Network Interface Down", cat: "HARDWARE", conf: 100.0, desc: "Physical link loss detected on Core Switch 02 - Port 24.", cam: "SYS-MON-02", node: "Processing Node Alpha-1" },
        { time: "13:58:33", sev: "Warning", title: "Crowd Density Warning", cat: "AI ANALYTICS", conf: 76.5, desc: "Estimated occupancy in Lobby exceeds threshold (Current: 42).", cam: "CAM-LOB-04", node: "Processing Node Alpha-1" },
        { time: "13:45:10", sev: "Information", title: "Backup Completed Successfully", cat: "SYSTEM", conf: 100.0, desc: "Daily cold storage backup for site 01 finished in 14 minutes.", cam: "SYS-MON-01", node: "Processing Node Alpha-1" },
        { time: "13:30:00", sev: "Information", title: "Shift Change Registered", cat: "PERSONNEL", conf: 100.0, desc: "Team Bravo assumed control of SOC station 12.", cam: "CAM-SOC-MAIN", node: "Processing Node Alpha-1" },
        { time: "13:12:00", sev: "Warning", title: "Thermal Threshold", cat: "HARDWARE", conf: 88.0, desc: "Rack B-12 chassis sensor reports 48°C.", cam: "SYS-THERM", node: "Node Beta-2" },
        { time: "12:55:00", sev: "Critical", title: "Unauthorized Badge", cat: "ACCESS", conf: 95.2, desc: "Badge ID 7781 used at restricted door after hours.", cam: "CAM-DR-09", node: "Node Alpha-1" }
    ]

    function sevColor(s) {
        if (s === "Critical") return theme ? theme.critical : "#EF4444"
        if (s === "Warning") return theme ? theme.warning : "#F59E0B"
        return theme ? theme.info : "#06B6D4"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16

        RowLayout {
            Layout.fillWidth: true
            Column {
                spacing: 4
                Text { text: "Event History"; font.pixelSize: theme ? theme.fontSizeXXL : 20; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
                Text { text: "Historical timeline of all system and AI-detected security events."; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8" }
            }
            Item { Layout.fillWidth: true }
            AppButton { text: "Export CSV"; variant: "secondary"; theme: control.theme }
            AppButton { text: "Hide Filters"; variant: "ghost"; theme: control.theme }
        }

        // KPI strip
        RowLayout {
            Layout.fillWidth: true; spacing: 12
            Repeater {
                model: [
                    { t: "TOTAL EVENTS", v: "1,284", icon: "inbox" },
                    { t: "CRITICAL ERRORS", v: "12", icon: "alert-triangle" },
                    { t: "AI DETECTIONS", v: "243", icon: "bot" },
                    { t: "AVG CONFIDENCE", v: "89.4%", icon: "gauge" }
                ]
                Rectangle {
                    Layout.fillWidth: true; height: 72; radius: 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                    Column {
                        anchors.centerIn: parent; spacing: 4
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.t; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.v; font.pixelSize: 20; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 16

            // Filters panel
            Rectangle {
                Layout.preferredWidth: 240; Layout.fillHeight: true
                radius: 4; color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1

                Column {
                    anchors.fill: parent; anchors.margins: 16; spacing: 14

                    Text { text: "Granular Filters"; font.pixelSize: 14; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }

                    AppInput {
                        width: parent.width; theme: control.theme
                        placeholderText: "Event ID, camera name…"; leadingIcon: "search"
                        onTextChanged: control.searchText = text
                    }

                    Text { text: "SEVERITY"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    Repeater {
                        model: ["Critical", "Warning", "Information"]
                        Row {
                            spacing: 8
                            Rectangle {
                                width: 16; height: 16; radius: 3
                                color: control.sevFilters[modelData] ? (theme ? theme.primary : "#2563EB") : "transparent"
                                border.color: theme ? theme.borderStrong : "#334155"; border.width: 1
                                Text { anchors.centerIn: parent; text: control.sevFilters[modelData] ? "✓" : ""; font.pixelSize: 11; color: "#FFF" }
                                MouseArea {
                                    anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        var f = Object.assign({}, control.sevFilters)
                                        f[modelData] = !f[modelData]
                                        control.sevFilters = f
                                    }
                                }
                            }
                            Text { text: modelData; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8"; anchors.verticalCenter: parent.verticalCenter }
                        }
                    }

                    Text { text: "CATEGORY"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    Repeater {
                        model: ["Personnel", "Vehicle", "Access", "Hardware", "AI Analytics", "System"]
                        Row {
                            spacing: 8
                            Rectangle {
                                width: 16; height: 16; radius: 3
                                color: "transparent"; border.color: theme ? theme.borderStrong : "#334155"; border.width: 1
                            }
                            Text { text: modelData; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8"; anchors.verticalCenter: parent.verticalCenter }
                        }
                    }

                    Text { text: "AI CONFIDENCE  > " + Math.round(control.minConfidence * 100) + "%"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    Rectangle {
                        width: parent.width; height: 6; radius: 3; color: theme ? theme.backgroundAlt : "#0F172A"
                        Rectangle { width: parent.width * control.minConfidence; height: parent.height; radius: 3; color: theme ? theme.primary : "#2563EB" }
                        MouseArea {
                            anchors.fill: parent
                            onClicked: control.minConfidence = Math.max(0.1, Math.min(1.0, mouse.x / width))
                        }
                    }

                    Text { text: "TIMEFRAME"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    Rectangle {
                        width: parent.width; height: 32; radius: 4
                        color: theme ? theme.surfaceAlt : "#1B2433"
                        border.color: theme ? theme.border : "#1E293B"; border.width: 1
                        Text { anchors.left: parent.left; anchors.leftMargin: 10; anchors.verticalCenter: parent.verticalCenter; text: "Last 24 Hours"; font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB" }
                        AppIcon { anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter; width: 14; height: 14; iconName: "chevron-down"; iconColor: theme ? theme.textMuted : "#64748B" }
                    }

                    AppButton { width: parent.width; text: "Apply Filters"; variant: "primary"; theme: control.theme }
                }
            }

            // Event list
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true
                radius: 4; color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                clip: true

                ColumnLayout {
                    anchors.fill: parent; spacing: 0

                    Rectangle {
                        Layout.fillWidth: true; height: 36
                        color: theme ? theme.backgroundAlt : "#0F172A"
                        Row {
                            anchors.fill: parent; anchors.leftMargin: 16; spacing: 12
                            Text { anchors.verticalCenter: parent.verticalCenter; text: "OCT 24, 2023"; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Rectangle { width: 6; height: 6; radius: 3; color: theme ? theme.success : "#10B981"; anchors.verticalCenter: parent.verticalCenter }
                            Text { anchors.verticalCenter: parent.verticalCenter; text: "REAL-TIME STREAM ACTIVE"; font.pixelSize: 11; color: theme ? theme.success : "#10B981" }
                        }
                    }

                    ListView {
                        Layout.fillWidth: true; Layout.fillHeight: true
                        clip: true
                        model: control.allEvents
                        spacing: 0
                        delegate: Rectangle {
                            width: ListView.view.width; height: 72
                            color: index % 2 === 0 ? "transparent" : (theme ? theme.backgroundAlt : "#0F172A")

                            RowLayout {
                                anchors.fill: parent; anchors.leftMargin: 16; anchors.rightMargin: 16; spacing: 12
                                Text {
                                    text: modelData.time; width: 60
                                    font.family: theme ? theme.fontFamilyMono : "monospace"; font.pixelSize: 12
                                    color: theme ? theme.textMuted : "#64748B"
                                }
                                Rectangle { width: 8; height: 8; radius: 4; color: control.sevColor(modelData.sev) }
                                Column {
                                    Layout.fillWidth: true; spacing: 2
                                    Row {
                                        spacing: 8
                                        Text { text: modelData.title; font.pixelSize: 13; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                                        Rectangle {
                                            width: catT.implicitWidth + 10; height: 16; radius: 3
                                            color: theme ? theme.surfaceElevated : "#1E293B"
                                            Text { id: catT; anchors.centerIn: parent; text: modelData.cat; font.pixelSize: 9; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                        }
                                        Text { text: "AI: " + modelData.conf + "%"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.info : "#06B6D4" }
                                    }
                                    Text { text: modelData.desc; font.pixelSize: 11; color: theme ? theme.textSecondary : "#94A3B8"; elide: Text.ElideRight; width: parent.width }
                                    Text { text: modelData.cam + "  ·  " + modelData.node; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true; height: 40
                        color: theme ? theme.backgroundAlt : "#0F172A"
                        Text {
                            anchors.left: parent.left; anchors.leftMargin: 16; anchors.verticalCenter: parent.verticalCenter
                            text: "Showing 7 of 1,284 events"
                            font.pixelSize: 11; color: theme ? theme.textMuted : "#64748B"
                        }
                        Row {
                            anchors.right: parent.right; anchors.rightMargin: 16; anchors.verticalCenter: parent.verticalCenter
                            spacing: 4
                            Repeater {
                                model: ["Previous", "1", "2", "3", "…", "128", "Next"]
                                Rectangle {
                                    width: Math.max(28, t.implicitWidth + 12); height: 26; radius: 4
                                    color: modelData === "1" ? (theme ? theme.primary : "#2563EB") : "transparent"
                                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                                    Text { id: t; anchors.centerIn: parent; text: modelData; font.pixelSize: 11; color: modelData === "1" ? "#FFF" : (theme ? theme.textSecondary : "#94A3B8") }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
