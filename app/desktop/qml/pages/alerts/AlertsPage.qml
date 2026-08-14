import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Item {
    id: control
    property var theme
    property var alertController

    property string severityFilter: "ALL"
    property string searchText: ""
    property int selectedIndex: 0

    // Live list from AlertController (fallback demo if empty)
    property var liveAlerts: []
    readonly property var fallbackAlerts: [
        { id: "ALRT-89214", title: "Unauthorized Access", priority: "CRITICAL", status: "OPEN", location: "Server Room A", camera_name: "CAM-SR-04", timestamp: "2024-05-20T14:22:01", description: "Unauthorized access detected" },
        { id: "ALRT-89210", title: "Unidentified Person", priority: "HIGH", status: "ACKNOWLEDGED", location: "Main Office", camera_name: "CAM-MO-01", timestamp: "2024-05-20T14:15:44", description: "Unidentified individual" }
    ]
    readonly property var alerts: {
        var src = (liveAlerts && liveAlerts.length) ? liveAlerts : fallbackAlerts
        var out = []
        for (var i = 0; i < src.length; i++) {
            var a = src[i]
            out.push({
                id: a.id || ("A-" + i),
                ts: a.timestamp || "",
                sev: a.priority || a.sev || "MEDIUM",
                detail: a.title || a.detail || "",
                status: (a.status === "OPEN" ? "Pending" : (a.status === "ACKNOWLEDGED" ? "Acknowledged" : (a.status === "RESOLVED" ? "Resolved" : (a.status || "Pending")))),
                conf: a.confidence || 90,
                threat: a.priority === "CRITICAL" ? "SEVERE" : (a.priority || "MEDIUM"),
                loc: a.location || "",
                cam: a.camera_name || a.camera_id || "",
                logic: "Vision-LLM-v4",
                raw: a
            })
        }
        return out
    }

    function reloadFromController() {
        if (alertController && alertController.alerts)
            liveAlerts = alertController.alerts
    }

    Connections {
        target: control.alertController
        function onAlertsChanged() { control.reloadFromController() }
        function onAlertReceived(p) { control.reloadFromController() }
    }
    Component.onCompleted: reloadFromController()

    function sevColor(s) {
        if (s === "CRITICAL") return theme ? theme.critical : "#EF4444"
        if (s === "HIGH") return theme ? theme.warning : "#F59E0B"
        if (s === "MEDIUM") return theme ? theme.info : "#06B6D4"
        return theme ? theme.textMuted : "#64748B"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16

        // Title row
        RowLayout {
            Layout.fillWidth: true
            Column {
                spacing: 4
                Text {
                    text: "Incidents & Alerts"
                    font.pixelSize: theme ? theme.fontSizeXXL : 20
                    font.weight: Font.Bold
                    color: theme ? theme.textPrimary : "#E5E7EB"
                }
                Text {
                    text: "SOC Real-time monitoring and threat management"
                    font.pixelSize: theme ? theme.fontSizeS : 12
                    color: theme ? theme.textSecondary : "#94A3B8"
                }
            }
            Item { Layout.fillWidth: true }
            AppButton { text: "Export CSV"; variant: "secondary"; theme: control.theme; iconName: "download" }
            AppButton { text: "Bulk Resolve"; variant: "primary"; theme: control.theme }
        }

        // Filters
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Text {
                text: "SEVERITY:"
                font.family: theme ? theme.fontFamilyMono : "monospace"
                font.pixelSize: 11
                color: theme ? theme.textMuted : "#64748B"
            }
            Repeater {
                model: ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
                Rectangle {
                    width: lab.implicitWidth + 20; height: 28; radius: 4
                    color: control.severityFilter === modelData
                           ? (theme ? theme.primary : "#2563EB")
                           : (theme ? theme.surface : "#151C28")
                    border.color: theme ? theme.border : "#1E293B"
                    border.width: 1
                    Text {
                        id: lab; anchors.centerIn: parent; text: modelData
                        font.pixelSize: 11; font.weight: Font.DemiBold
                        color: control.severityFilter === modelData ? "#FFF" : (theme ? theme.textSecondary : "#94A3B8")
                    }
                    MouseArea {
                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            control.severityFilter = modelData
                            if (control.alertController)
                                control.alertController.setFilterPriority(modelData)
                        }
                    }
                }
            }
            Item { Layout.fillWidth: true }
            AppInput {
                Layout.preferredWidth: 260; Layout.preferredHeight: 32
                theme: control.theme; placeholderText: "Search Incident IDs or Patterns…"; leadingIcon: "search"
                onTextChanged: {
                    control.searchText = text
                    if (control.alertController) control.alertController.setSearch(text)
                }
            }
            Rectangle {
                width: critLab.implicitWidth + 16; height: 28; radius: 14
                color: "#EF444422"; border.color: theme ? theme.critical : "#EF4444"; border.width: 1
                Text { id: critLab; anchors.centerIn: parent; text: "2 Critical"; font.pixelSize: 11; font.weight: Font.Bold; color: theme ? theme.critical : "#EF4444" }
            }
        }

        // Split: table + detail
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: theme ? theme.spacingM : 16

            // Table
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 1
                radius: 4
                color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"
                border.width: 1
                clip: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    // Header
                    Rectangle {
                        Layout.fillWidth: true; height: 36
                        color: theme ? theme.backgroundAlt : "#0F172A"
                        Row {
                            anchors.fill: parent; anchors.leftMargin: 12; spacing: 0
                            Text { width: 100; anchors.verticalCenter: parent.verticalCenter; text: "INCIDENT ID"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { width: 150; anchors.verticalCenter: parent.verticalCenter; text: "TIMESTAMP"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { width: 80; anchors.verticalCenter: parent.verticalCenter; text: "SEVERITY"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { width: 160; anchors.verticalCenter: parent.verticalCenter; text: "EVENT DETAILS"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { anchors.verticalCenter: parent.verticalCenter; text: "STATUS"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        }
                    }

                    ListView {
                        id: alertList
                        Layout.fillWidth: true; Layout.fillHeight: true
                        clip: true
                        model: control.alerts
                        currentIndex: control.selectedIndex
                        delegate: Rectangle {
                            width: alertList.width; height: 48
                            color: index === control.selectedIndex
                                   ? (theme ? theme.surfaceElevated : "#1E293B")
                                   : (index % 2 === 0 ? "transparent" : (theme ? theme.backgroundAlt : "#0F172A"))
                            border.color: index === control.selectedIndex ? (theme ? theme.primary : "#2563EB") : "transparent"
                            border.width: index === control.selectedIndex ? 1 : 0

                            // severity bar
                            Rectangle {
                                anchors.left: parent.left; anchors.top: parent.top; anchors.bottom: parent.bottom
                                width: 3; color: control.sevColor(modelData.sev)
                            }

                            Row {
                                anchors.fill: parent; anchors.leftMargin: 12; spacing: 0
                                Text { width: 100; anchors.verticalCenter: parent.verticalCenter; text: modelData.id; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textPrimary : "#E5E7EB" }
                                Text { width: 150; anchors.verticalCenter: parent.verticalCenter; text: modelData.ts; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textSecondary : "#94A3B8" }
                                Rectangle {
                                    width: 72; height: 20; radius: 4
                                    anchors.verticalCenter: parent.verticalCenter
                                    color: "transparent"
                                    border.color: control.sevColor(modelData.sev); border.width: 1
                                    Text { anchors.centerIn: parent; text: modelData.sev; font.pixelSize: 9; font.weight: Font.Bold; color: control.sevColor(modelData.sev) }
                                }
                                Item { width: 8; height: 1 }
                                Text { width: 152; anchors.verticalCenter: parent.verticalCenter; text: modelData.detail; font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB"; elide: Text.ElideRight }
                                Text {
                                    anchors.verticalCenter: parent.verticalCenter; text: modelData.status
                                    font.pixelSize: 11
                                    color: modelData.status === "Resolved" ? (theme ? theme.success : "#10B981")
                                         : modelData.status === "Acknowledged" ? (theme ? theme.info : "#06B6D4")
                                         : (theme ? theme.warning : "#F59E0B")
                                }
                            }
                            MouseArea {
                                anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                onClicked: control.selectedIndex = index
                            }
                        }
                    }

                    // Pagination footer
                    Rectangle {
                        Layout.fillWidth: true; height: 36
                        color: theme ? theme.backgroundAlt : "#0F172A"
                        Text {
                            anchors.left: parent.left; anchors.leftMargin: 12; anchors.verticalCenter: parent.verticalCenter
                            text: "Showing 6 of 48 active alerts"
                            font.pixelSize: 11; color: theme ? theme.textMuted : "#64748B"
                        }
                        Row {
                            anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter
                            spacing: 4
                            Repeater {
                                model: ["‹", "1", "2", "3", "›"]
                                Rectangle {
                                    width: 28; height: 24; radius: 4
                                    color: modelData === "1" ? (theme ? theme.primary : "#2563EB") : "transparent"
                                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                                    Text { anchors.centerIn: parent; text: modelData; font.pixelSize: 11; color: modelData === "1" ? "#FFF" : (theme ? theme.textSecondary : "#94A3B8") }
                                }
                            }
                        }
                    }
                }
            }

            // Detail panel
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: 1
                radius: 4
                color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"
                border.width: 1

                property var sel: control.alerts[control.selectedIndex]

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    // Live evidence
                    Rectangle {
                        Layout.fillWidth: true; Layout.preferredHeight: 140
                        radius: 4; color: "#0A0C10"; clip: true
                        Rectangle {
                            anchors.fill: parent
                            gradient: Gradient {
                                GradientStop { position: 0; color: "#0F172A" }
                                GradientStop { position: 1; color: "#1E293B" }
                            }
                        }
                        Row {
                            anchors.left: parent.left; anchors.top: parent.top; anchors.margins: 8; spacing: 6
                            Rectangle { width: 8; height: 8; radius: 4; color: "#EF4444"
                                SequentialAnimation on opacity { loops: Animation.Infinite; NumberAnimation { to: 0.3; duration: 600 }; NumberAnimation { to: 1; duration: 600 } }
                            }
                            Text { text: "LIVE EVIDENCE  ·  " + (parent.parent.parent.sel ? parent.parent.parent.sel.cam : ""); font.family: theme ? theme.fontFamilyMono : "monospace"; font.pixelSize: 10; color: "#E5E7EB"; anchors.verticalCenter: parent.verticalCenter }
                        }
                        AppButton {
                            anchors.bottom: parent.bottom; anchors.left: parent.left; anchors.margins: 8
                            text: "Playback Sequence"; variant: "primary"; theme: control.theme
                        }
                    }

                    Text {
                        text: "Unauthorized Access Detected"
                        font.pixelSize: theme ? theme.fontSizeL : 14; font.weight: Font.Bold
                        color: theme ? theme.textPrimary : "#E5E7EB"
                    }
                    Text {
                        text: (parent.parent.sel ? parent.parent.sel.id : "") + "  ·  Detection at " + (parent.parent.sel ? parent.parent.sel.ts : "")
                        font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"
                        color: theme ? theme.textMuted : "#64748B"
                    }

                    RowLayout {
                        Layout.fillWidth: true; spacing: 12
                        Rectangle {
                            Layout.fillWidth: true; height: 72; radius: 4
                            color: theme ? theme.backgroundAlt : "#0F172A"
                            Column {
                                anchors.centerIn: parent; spacing: 4
                                Text { anchors.horizontalCenter: parent.horizontalCenter; text: "AI CONFIDENCE"; font.pixelSize: 10; color: theme ? theme.textMuted : "#64748B" }
                                Text { anchors.horizontalCenter: parent.horizontalCenter; text: (parent.parent.parent.parent.sel ? parent.parent.parent.parent.sel.conf : 0) + "%"; font.pixelSize: 22; font.weight: Font.Bold; color: theme ? theme.info : "#06B6D4" }
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true; height: 72; radius: 4
                            color: theme ? theme.backgroundAlt : "#0F172A"
                            Column {
                                anchors.centerIn: parent; spacing: 4
                                Text { anchors.horizontalCenter: parent.horizontalCenter; text: "THREAT LEVEL"; font.pixelSize: 10; color: theme ? theme.textMuted : "#64748B" }
                                Text { anchors.horizontalCenter: parent.horizontalCenter; text: parent.parent.parent.parent.sel ? parent.parent.parent.parent.sel.threat : ""; font.pixelSize: 18; font.weight: Font.Bold; color: theme ? theme.critical : "#EF4444" }
                            }
                        }
                    }

                    Column {
                        Layout.fillWidth: true; spacing: 6
                        Text { text: "INCIDENT LOCATION"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { text: parent.parent.sel ? parent.parent.sel.loc : ""; font.pixelSize: 13; color: theme ? theme.textPrimary : "#E5E7EB" }
                        Text { text: "SOURCE CAMERA"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { text: parent.parent.sel ? parent.parent.sel.cam : ""; font.pixelSize: 13; color: theme ? theme.primary : "#2563EB" }
                        Text { text: "DESCRIPTION"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text {
                            width: parent.width
                            text: "AI engine detected unauthorized access. Pattern matches high-probability unauthorized entry vectors. Immediate manual verification required."
                            font.pixelSize: 12; wrapMode: Text.WordWrap; color: theme ? theme.textSecondary : "#94A3B8"
                        }
                    }

                    Item { Layout.fillHeight: true }

                    RowLayout {
                        Layout.fillWidth: true; spacing: 8
                        AppButton { Layout.fillWidth: true; text: "False Positive"; variant: "secondary"; theme: control.theme }
                        AppButton {
                            Layout.fillWidth: true; text: "Acknowledge"; variant: "primary"; theme: control.theme
                            onClicked: {
                                var a = control.alerts[control.selectedIndex]
                                if (a && control.alertController)
                                    control.alertController.acknowledgeAlert(a.id, "admin")
                            }
                        }
                    }
                    AppButton {
                        Layout.fillWidth: true; text: "Request Supervisor Review"; variant: "ghost"; theme: control.theme
                    }
                }
            }
        }
    }
}
