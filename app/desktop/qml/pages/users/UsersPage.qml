import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Item {
    id: control
    property var theme
    property var userController

    readonly property var users: [
        { name: "Alex Rivers", email: "A.RIVERS@SENTINEL-AI.SYS", role: "SOC ANALYST", status: "Online", level: 8, last: "Now", initials: "AR" },
        { name: "Elena Vance", email: "E.VANCE@SENTINEL-AI.SYS", role: "SOC LEAD", status: "Online", level: 9, last: "Now", initials: "EV" },
        { name: "Marcus Thorne", email: "M.THORNE@SENTINEL-AI.SYS", role: "ADMINISTRATOR", status: "Away", level: 10, last: "12m ago", initials: "MT" },
        { name: "Sarah Jenkins", email: "S.JENKINS@SENTINEL-AI.SYS", role: "AUDITOR", status: "Offline", level: 4, last: "4h ago", initials: "SJ" },
        { name: "David Chen", email: "D.CHEN@SENTINEL-AI.SYS", role: "TECHNICIAN", status: "Suspended", level: 2, last: "3d ago", initials: "DC" }
    ]

    function statusColor(s) {
        if (s === "Online") return theme ? theme.success : "#10B981"
        if (s === "Away") return theme ? theme.warning : "#F59E0B"
        if (s === "Suspended") return theme ? theme.critical : "#EF4444"
        return theme ? theme.textMuted : "#64748B"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingL : 24
        spacing: theme ? theme.spacingM : 16

        RowLayout {
            Layout.fillWidth: true
            Column {
                spacing: 4
                Text { text: "User Directory"; font.pixelSize: theme ? theme.fontSizeXXL : 20; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
                Text { text: "Manage system access, roles, and security permissions for all personnel."; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8" }
            }
            Item { Layout.fillWidth: true }
            AppButton { text: "Export CSV"; variant: "secondary"; theme: control.theme }
            AppButton { text: "+ Add New User"; variant: "primary"; theme: control.theme }
        }

        RowLayout {
            Layout.fillWidth: true; spacing: 12
            Repeater {
                model: [
                    { t: "TOTAL USERS", v: "142" },
                    { t: "ACTIVE NOW", v: "38" },
                    { t: "SUSPENDED", v: "4" },
                    { t: "ADMINS", v: "12" }
                ]
                Rectangle {
                    Layout.fillWidth: true; height: 72; radius: 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"; border.width: 1
                    Column {
                        anchors.centerIn: parent; spacing: 4
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.t; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.v; font.pixelSize: 22; font.weight: Font.Bold; color: theme ? theme.textPrimary : "#E5E7EB" }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            AppInput { Layout.preferredWidth: 280; theme: control.theme; placeholderText: "Search by name, ID, or email…"; leadingIcon: "search" }
            AppButton { text: "Filters"; variant: "secondary"; theme: control.theme }
            Item { Layout.fillWidth: true }
            Text { text: "Showing 1-10 of 142"; font.pixelSize: 11; color: theme ? theme.textMuted : "#64748B" }
        }

        // User table
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
                        anchors.fill: parent; anchors.leftMargin: 16; spacing: 0
                        Text { width: 220; anchors.verticalCenter: parent.verticalCenter; text: "USER PROFILE"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { width: 140; anchors.verticalCenter: parent.verticalCenter; text: "ROLE & AUTHORITY"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { width: 90; anchors.verticalCenter: parent.verticalCenter; text: "STATUS"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { width: 100; anchors.verticalCenter: parent.verticalCenter; text: "ACCESS LEVEL"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        Text { anchors.verticalCenter: parent.verticalCenter; text: "LAST ACTIVITY"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    }
                }

                ListView {
                    Layout.fillWidth: true; Layout.fillHeight: true
                    model: control.users; clip: true
                    delegate: Rectangle {
                        width: ListView.view.width; height: 64
                        color: index % 2 === 0 ? "transparent" : (theme ? theme.backgroundAlt : "#0F172A")
                        Row {
                            anchors.fill: parent; anchors.leftMargin: 16; spacing: 0
                            // profile
                            Row {
                                width: 220; anchors.verticalCenter: parent.verticalCenter; spacing: 10
                                Rectangle {
                                    width: 36; height: 36; radius: 18
                                    color: theme ? theme.primary : "#2563EB"
                                    Text { anchors.centerIn: parent; text: modelData.initials; font.pixelSize: 12; font.weight: Font.Bold; color: "#FFF" }
                                }
                                Column {
                                    anchors.verticalCenter: parent.verticalCenter; spacing: 2
                                    Text { text: modelData.name; font.pixelSize: 13; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                                    Text { text: modelData.email; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                                }
                            }
                            // role
                            Rectangle {
                                width: 120; height: 22; radius: 4
                                anchors.verticalCenter: parent.verticalCenter
                                color: theme ? theme.surfaceElevated : "#1E293B"
                                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                                Text { anchors.centerIn: parent; text: modelData.role; font.pixelSize: 9; font.weight: Font.Bold; color: theme ? theme.textSecondary : "#94A3B8" }
                            }
                            Item { width: 20; height: 1 }
                            // status
                            Row {
                                width: 90; anchors.verticalCenter: parent.verticalCenter; spacing: 6
                                Rectangle { width: 8; height: 8; radius: 4; color: control.statusColor(modelData.status); anchors.verticalCenter: parent.verticalCenter }
                                Text { text: modelData.status; font.pixelSize: 12; color: control.statusColor(modelData.status); anchors.verticalCenter: parent.verticalCenter }
                            }
                            // level
                            Column {
                                width: 100; anchors.verticalCenter: parent.verticalCenter; spacing: 4
                                Text { text: "LVL " + modelData.level; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textSecondary : "#94A3B8" }
                                Rectangle {
                                    width: 80; height: 4; radius: 2; color: theme ? theme.backgroundAlt : "#0F172A"
                                    Rectangle { width: parent.width * (modelData.level / 10); height: parent.height; radius: 2; color: theme ? theme.primary : "#2563EB" }
                                }
                            }
                            Text { anchors.verticalCenter: parent.verticalCenter; text: modelData.last; font.pixelSize: 12; color: theme ? theme.textMuted : "#64748B" }
                        }
                    }
                }
            }
        }

        // Bottom: Active Sessions + Audit Log
        RowLayout {
            Layout.fillWidth: true; Layout.preferredHeight: 180; spacing: 16

            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true
                radius: 4; color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                Column {
                    anchors.fill: parent; anchors.margins: 16; spacing: 10
                    Text { text: "Active Sessions"; font.pixelSize: 13; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                    Repeater {
                        model: [
                            { n: "Alex Rivers", ip: "192.168.1.42", loc: "HQ - Room 4B" },
                            { n: "Elena Vance", ip: "192.168.1.101", loc: "Remote VPN" },
                            { n: "Marcus Thorne", ip: "10.0.4.15", loc: "Data Center 1" }
                        ]
                        Row {
                            width: parent.width; spacing: 8
                            Text { text: modelData.n; width: 110; font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB" }
                            Text { text: modelData.ip; width: 110; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { text: modelData.loc; font.pixelSize: 11; color: theme ? theme.textSecondary : "#94A3B8" }
                            Item { width: 8; height: 1 }
                            Rectangle {
                                width: 48; height: 16; radius: 8; color: "#10B98122"
                                Text { anchors.centerIn: parent; text: "ACTIVE"; font.pixelSize: 9; font.weight: Font.Bold; color: theme ? theme.success : "#10B981" }
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true
                radius: 4; color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                Column {
                    anchors.fill: parent; anchors.margins: 16; spacing: 8
                    Text { text: "Security Governance Log"; font.pixelSize: 13; font.weight: Font.DemiBold; color: theme ? theme.textPrimary : "#E5E7EB" }
                    Repeater {
                        model: [
                            { ts: "2024-05-24 14:22:01", act: "PERMISSION_CHANGE", who: "M. Thorne", tgt: "A. Rivers" },
                            { ts: "2024-05-24 13:45:12", act: "USER_LOGIN_FAILED", who: "SYSTEM", tgt: "D. Chen" },
                            { ts: "2024-05-24 11:10:55", act: "NEW_USER_CREATED", who: "E. Vance", tgt: "S. Jenkins" },
                            { ts: "2024-05-24 09:30:22", act: "ROLE_UPGRADE", who: "M. Thorne", tgt: "E. Vance" }
                        ]
                        Row {
                            width: parent.width; spacing: 8
                            Text { text: modelData.ts; width: 140; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                            Text { text: modelData.act; width: 140; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; font.weight: Font.Bold; color: theme ? theme.warning : "#F59E0B" }
                            Text { text: modelData.who; width: 70; font.pixelSize: 10; color: theme ? theme.textSecondary : "#94A3B8" }
                            Text { text: modelData.tgt; font.pixelSize: 10; color: theme ? theme.textSecondary : "#94A3B8" }
                        }
                    }
                }
            }
        }
    }
}
