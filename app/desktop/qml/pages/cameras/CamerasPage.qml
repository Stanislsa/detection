import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"
import "../../dialogs"

Item {
    id: control
    property var theme
    property var cameraController

    property string viewMode: "grid"  // grid | list
    property string locFilter: "All"
    readonly property bool isNarrow: width < 960
    readonly property bool isMobile: width < 720
    readonly property int pageMargin: isMobile ? 10 : (isNarrow ? 14 : 24)
    readonly property int camCols: width >= 1200 ? 3 : (width >= 800 ? 2 : 1)

    readonly property var cameras: [
        { name: "MAIN LOBBY ENTRY", loc: "Building A - North", res: "4K", rec: true, live: true, offline: false },
        { name: "WAREHOUSE LOADING DOCK", loc: "Building B - Logistics", res: "1080P", rec: true, live: true, offline: false },
        { name: "SERVER ROOM CORRIDOR", loc: "Building A - Data Center", res: "2K", rec: false, live: true, offline: false },
        { name: "PARKING WEST ENTRANCE", loc: "Exterior - Zone 4", res: "1080P", rec: true, live: true, offline: false },
        { name: "PERIMETER FENCE LINE", loc: "Exterior - East Wall", res: "720P", rec: false, live: false, offline: true },
        { name: "OFFICE CORRIDOR 4C", loc: "Building C - Floor 4", res: "1080P", rec: true, live: true, offline: false }
    ]

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
            Text {
                text: "Camera Management"
                font.pixelSize: theme ? theme.fontSizeXXL : 20
                font.weight: Font.Bold
                color: theme ? theme.textPrimary : "#E5E7EB"
            }
            Rectangle {
                width: devLab.implicitWidth + 14; height: 22; radius: 11
                color: theme ? theme.surfaceElevated : "#1E293B"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1
                Text { id: devLab; anchors.centerIn: parent; text: "6 Devices"; font.pixelSize: 11; color: theme ? theme.textSecondary : "#94A3B8" }
            }
            Item { Layout.fillWidth: true }
            AppInput {
                Layout.preferredWidth: 200; Layout.preferredHeight: 32
                theme: control.theme; placeholderText: "Filter streams…"; leadingIcon: "search"
            }
            AppIconButton { iconName: "grid"; theme: control.theme; onClicked: control.viewMode = "grid" }
            AppIconButton { iconName: "list"; theme: control.theme; onClicked: control.viewMode = "list" }
            AppButton { text: "FILTER"; variant: "secondary"; theme: control.theme; }
            AppButton { text: "ACTIONS"; variant: "primary"; theme: control.theme }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: theme ? theme.spacingM : 16

            // Left metrics sidebar
            Rectangle {
                Layout.preferredWidth: 200
                Layout.fillHeight: true
                radius: 4
                color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"; border.width: 1

                Column {
                    anchors.fill: parent; anchors.margins: 12; spacing: 16

                    Text { text: "SYSTEM METRICS"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }

                    Column {
                        width: parent.width; spacing: 6
                        Row {
                            width: parent.width
                            AppIcon { width: 14; height: 14; iconName: "cpu"; iconColor: theme ? theme.textSecondary : "#94A3B8"; anchors.verticalCenter: parent.verticalCenter }
                            Text { text: "  AI Load"; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8"; anchors.verticalCenter: parent.verticalCenter; width: parent.width - 50 }
                            Text { text: "24%"; font.pixelSize: 12; font.weight: Font.Bold; color: theme ? theme.success : "#10B981"; anchors.verticalCenter: parent.verticalCenter }
                        }
                        Rectangle {
                            width: parent.width; height: 4; radius: 2; color: theme ? theme.backgroundAlt : "#0F172A"
                            Rectangle { width: parent.width * 0.24; height: parent.height; radius: 2; color: theme ? theme.success : "#10B981" }
                        }
                    }
                    Column {
                        width: parent.width; spacing: 6
                        Row {
                            width: parent.width
                            AppIcon { width: 14; height: 14; iconName: "hard-drive"; iconColor: theme ? theme.textSecondary : "#94A3B8"; anchors.verticalCenter: parent.verticalCenter }
                            Text { text: "  Storage"; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8"; anchors.verticalCenter: parent.verticalCenter; width: parent.width - 50 }
                            Text { text: "82%"; font.pixelSize: 12; font.weight: Font.Bold; color: theme ? theme.warning : "#F59E0B"; anchors.verticalCenter: parent.verticalCenter }
                        }
                        Rectangle {
                            width: parent.width; height: 4; radius: 2; color: theme ? theme.backgroundAlt : "#0F172A"
                            Rectangle { width: parent.width * 0.82; height: parent.height; radius: 2; color: theme ? theme.warning : "#F59E0B" }
                        }
                    }

                    Text { text: "LOCATIONS"; font.pixelSize: 10; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    Repeater {
                        model: [
                            { n: "Building A", c: 12 }, { n: "Building B", c: 8 },
                            { n: "Building C", c: 4 }, { n: "Exterior", c: 15 }, { n: "Data Center", c: 6 }
                        ]
                        Row {
                            width: parent.width
                            Text { text: modelData.n; font.pixelSize: 12; color: theme ? theme.textSecondary : "#94A3B8"; width: parent.width - 30 }
                            Text { text: "" + modelData.c; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                        }
                    }

                    Text {
                        text: "STATUS"
                        font.pixelSize: 10
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        color: theme ? theme.textMuted : "#64748B"
                    }
                    Column {
                        spacing: 6
                        Row {
                            spacing: 6
                            Rectangle {
                                width: 8; height: 8; radius: 4
                                color: theme ? theme.success : "#10B981"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: "Operational  32"
                                font.pixelSize: 12
                                color: theme ? theme.textSecondary : "#94A3B8"
                            }
                        }
                        Row {
                            spacing: 6
                            Rectangle {
                                width: 8; height: 8; radius: 4
                                color: theme ? theme.critical : "#EF4444"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: "Alert Triggered  2"
                                font.pixelSize: 12
                                color: theme ? theme.textSecondary : "#94A3B8"
                            }
                        }
                        Row {
                            spacing: 6
                            Rectangle {
                                width: 8; height: 8; radius: 4
                                color: theme ? theme.textMuted : "#64748B"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: "Offline  5"
                                font.pixelSize: 12
                                color: theme ? theme.textSecondary : "#94A3B8"
                            }
                        }
                    }

                    Item { height: 20; width: 1 }
                    AppButton { width: parent.width; text: "FLEET SETTINGS"; variant: "secondary"; theme: control.theme }
                }
            }

            // Camera grid
            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: width > 700 ? 3 : 2
                rowSpacing: 10; columnSpacing: 10

                Repeater {
                    model: control.cameras
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: 140
                        radius: 4
                        color: "#0A0C10"
                        border.color: modelData.offline ? (theme ? theme.textMuted : "#64748B") : (theme ? theme.border : "#1E293B")
                        border.width: 1
                        clip: true

                        Rectangle {
                            anchors.fill: parent
                            gradient: Gradient {
                                GradientStop { position: 0; color: modelData.offline ? "#1E293B" : "#0F172A" }
                                GradientStop { position: 1; color: "#1E293B" }
                            }
                            opacity: modelData.offline ? 0.5 : 1
                        }

                        // top badges
                        Row {
                            anchors.left: parent.left; anchors.top: parent.top; anchors.margins: 8; spacing: 6
                            Rectangle {
                                width: 8; height: 8; radius: 4
                                color: modelData.offline ? "#64748B" : (modelData.live ? "#10B981" : "#F59E0B")
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: modelData.name
                                font.pixelSize: 11; font.weight: Font.DemiBold; color: "#E5E7EB"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                        Row {
                            anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 8; spacing: 4
                            Rectangle {
                                visible: modelData.rec; width: recT.implicitWidth + 10; height: 18; radius: 3
                                color: "#EF4444"; Text { id: recT; anchors.centerIn: parent; text: "REC"; font.pixelSize: 9; font.weight: Font.Bold; color: "#FFF" }
                            }
                            Rectangle {
                                width: resT.implicitWidth + 10; height: 18; radius: 3
                                color: "#00000088"; border.color: "#FFFFFF44"; border.width: 1
                                Text { id: resT; anchors.centerIn: parent; text: modelData.res; font.pixelSize: 9; color: "#E5E7EB" }
                            }
                        }

                        // offline overlay
                        Column {
                            visible: modelData.offline
                            anchors.centerIn: parent; spacing: 6
                            AppIcon { anchors.horizontalCenter: parent.horizontalCenter; width: 28; height: 28; iconName: "wifi-off"; iconColor: "#64748B" }
                            Text { anchors.horizontalCenter: parent.horizontalCenter; text: "CONNECTION LOST"; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: "#94A3B8" }
                        }

                        // footer
                        Rectangle {
                            anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
                            height: 28; color: "#00000099"
                            Text {
                                anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; anchors.leftMargin: 8
                                text: modelData.loc; font.pixelSize: 10; color: "#CBD5E1"; elide: Text.ElideRight; width: parent.width - 16
                            }
                        }
                    }
                }

                // Mount new stream tile
                Rectangle {
                    Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 140
                    radius: 4; color: "transparent"
                    border.color: theme ? theme.borderStrong : "#334155"; border.width: 1
                    
                    Column {
                        anchors.centerIn: parent; spacing: 8
                        AppIcon { anchors.horizontalCenter: parent.horizontalCenter; width: 28; height: 28; iconName: "plus"; iconColor: theme ? theme.textMuted : "#64748B" }
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: "MOUNT NEW STREAM"; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textMuted : "#64748B" }
                    }
                    MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: addCamDialog.open() }
                }
            }
        }

        // Footer status
        Row {
            spacing: 16
            Rectangle { width: 8; height: 8; radius: 4; color: theme ? theme.success : "#10B981"; anchors.verticalCenter: parent.verticalCenter }
            Text { text: "LIVE STREAM ACTIVE"; font.pixelSize: 11; font.family: theme ? theme.fontFamilyMono : "monospace"; color: theme ? theme.textSecondary : "#94A3B8"; anchors.verticalCenter: parent.verticalCenter }
            Text { text: "AI Detection: Enabled"; font.pixelSize: 11; color: theme ? theme.textMuted : "#64748B"; anchors.verticalCenter: parent.verticalCenter }
            Text { text: "Latency: 142ms"; font.pixelSize: 11; color: theme ? theme.textMuted : "#64748B"; anchors.verticalCenter: parent.verticalCenter }
        }
    }

    AddCameraDialog {
        id: addCamDialog
        theme: control.theme
    }
}
}
