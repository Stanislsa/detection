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

    contentWidth: width
    contentHeight: contentColumn.implicitHeight + (theme ? theme.spacingXXL : 48)
    clip: true
    boundsBehavior: Flickable.StopAtBounds
    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

    Column {
        id: contentColumn
        width: parent.width
        spacing: theme ? theme.spacingL : 24
        topPadding: theme ? theme.spacingL : 24
        bottomPadding: theme ? theme.spacingXL : 32
        leftPadding: theme ? theme.spacingL : 24
        rightPadding: theme ? theme.spacingL : 24

        GridLayout {
            width: parent.width - parent.leftPadding - parent.rightPadding
            columns: width > 900 ? 4 : (width > 500 ? 2 : 1)
            rowSpacing: theme ? theme.spacingM : 16
            columnSpacing: theme ? theme.spacingM : 16

            Repeater {
                model: [
                    { title: "Active Threats", value: "12", delta: "-12% VS LAST 24H", positive: false, accent: "critical", icon: "shield" },
                    { title: "AI Inference Load", value: "42.8%", delta: "+5% VS LAST 24H", positive: true, accent: "primary", icon: "cpu" },
                    { title: "Live Nodes", value: "128 / 130", delta: "+6% VS LAST 24H", positive: true, accent: "success", icon: "activity" },
                    { title: "Events / Sec", value: "1,422", delta: "+24% VS LAST 24H", positive: true, accent: "info", icon: "zap" }
                ]
                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 96
                    radius: theme ? theme.radiusM : 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: theme ? theme.spacingM : 16
                        spacing: 6
                        Row {
                            width: parent.width
                            spacing: 8
                            AppIcon {
                                width: 16; height: 16
                                iconName: modelData.icon
                                iconColor: theme ? theme.textMuted : "#64748B"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Text {
                                text: modelData.title.toUpperCase()
                                font.family: theme ? theme.fontFamilyMono : "monospace"
                                font.pixelSize: theme ? theme.fontSizeXS : 11
                                font.letterSpacing: 1
                                color: theme ? theme.textMuted : "#64748B"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                        Text {
                            text: modelData.value
                            font.family: theme ? theme.fontFamily : "sans-serif"
                            font.pixelSize: theme ? theme.fontSizeXXL : 20
                            font.weight: Font.Bold
                            color: {
                                if (modelData.accent === "critical") return theme ? theme.critical : "#EF4444"
                                if (modelData.accent === "success") return theme ? theme.success : "#10B981"
                                if (modelData.accent === "info") return theme ? theme.info : "#06B6D4"
                                return theme ? theme.textPrimary : "#E5E7EB"
                            }
                        }
                        Text {
                            text: modelData.delta
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            font.pixelSize: 10
                            color: modelData.positive
                                   ? (theme ? theme.success : "#10B981")
                                   : (theme ? theme.critical : "#EF4444")
                        }
                    }
                }
            }
        }

        Rectangle {
            width: parent.width - parent.leftPadding - parent.rightPadding
            height: matrixCol.implicitHeight + 32
            radius: theme ? theme.radiusM : 4
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"
            border.width: 1

            Column {
                id: matrixCol
                width: parent.width
                padding: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingM : 16

                RowLayout {
                    width: parent.width - parent.padding * 2
                    spacing: 12
                    AppIcon { width: 16; height: 16; iconName: "video"; iconColor: theme ? theme.textSecondary : "#94A3B8" }
                    Text {
                        text: "Live Surveillance Matrix"
                        font.pixelSize: theme ? theme.fontSizeL : 14
                        font.weight: Font.DemiBold
                        color: theme ? theme.textPrimary : "#E5E7EB"
                    }
                    Rectangle {
                        width: syncLabel.implicitWidth + 16
                        height: 22
                        radius: 11
                        color: "#10B98122"
                        border.color: theme ? theme.success : "#10B981"
                        border.width: 1
                        Text {
                            id: syncLabel
                            anchors.centerIn: parent
                            text: "SYNC_STABLE"
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: theme ? theme.success : "#10B981"
                        }
                    }
                    Item { Layout.fillWidth: true }
                }

                GridLayout {
                    width: parent.width - parent.padding * 2
                    columns: width > 700 ? 3 : (width > 400 ? 2 : 1)
                    rowSpacing: 8
                    columnSpacing: 8

                    Repeater {
                        model: [
                            { name: "LOBBY_EAST_01", loc: "MAIN ENTRANCE / LOBBY", live: true, alert: false },
                            { name: "WH_DOCK_07", loc: "WAREHOUSE / LOADING DOCK B", live: true, alert: true },
                            { name: "SERVER_COR_04", loc: "DATA CENTER / AISLE 4", live: true, alert: false },
                            { name: "PARK_EXT_12", loc: "PARKING LOT / NORTH PERIMETER", live: true, alert: false },
                            { name: "RETAIL_FLR_02", loc: "LEVEL 1 / ELECTRONICS", live: true, alert: false },
                            { name: "PERIM_FNC_09", loc: "EXTERIOR / SOUTH FENCE", live: false, alert: false }
                        ]
                        delegate: Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 150
                            radius: 4
                            color: "#0A0C10"
                            border.color: modelData.alert ? (theme ? theme.critical : "#EF4444") : (theme ? theme.border : "#1E293B")
                            border.width: modelData.alert ? 2 : 1
                            clip: true

                            Rectangle {
                                anchors.fill: parent
                                gradient: Gradient {
                                    GradientStop { position: 0.0; color: "#0F172A" }
                                    GradientStop { position: 1.0; color: "#1E293B" }
                                }
                            }

                            Row {
                                anchors.left: parent.left
                                anchors.top: parent.top
                                anchors.margins: 8
                                spacing: 6
                                Rectangle {
                                    width: 8; height: 8; radius: 4
                                    color: modelData.live ? "#EF4444" : "#64748B"
                                    anchors.verticalCenter: parent.verticalCenter
                                    SequentialAnimation on opacity {
                                        running: modelData.live
                                        loops: Animation.Infinite
                                        NumberAnimation { to: 0.3; duration: 700 }
                                        NumberAnimation { to: 1.0; duration: 700 }
                                    }
                                }
                                Text {
                                    text: "REC  //  " + modelData.name
                                    font.family: theme ? theme.fontFamilyMono : "monospace"
                                    font.pixelSize: 10
                                    color: "#E5E7EB"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }

                            Rectangle {
                                visible: modelData.alert
                                anchors.centerIn: parent
                                width: 130; height: 28
                                radius: 2
                                color: "#EF4444AA"
                                border.color: "#EF4444"
                                Text {
                                    anchors.centerIn: parent
                                    text: "UNAUTHORIZED_PERSON"
                                    font.family: theme ? theme.fontFamilyMono : "monospace"
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                    color: "#FFFFFF"
                                }
                            }

                            Rectangle {
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.bottom: parent.bottom
                                height: 26
                                color: "#00000099"
                                Text {
                                    anchors.left: parent.left
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.leftMargin: 8
                                    text: modelData.loc
                                    font.pixelSize: 10
                                    color: "#CBD5E1"
                                    elide: Text.ElideRight
                                    width: parent.width - 16
                                }
                            }
                        }
                    }
                }
            }
        }

        // Inference + Event log
        GridLayout {
            width: parent.width - parent.leftPadding - parent.rightPadding
            columns: width > 800 ? 2 : 1
            columnSpacing: theme ? theme.spacingM : 16
            rowSpacing: theme ? theme.spacingM : 16

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 180
                radius: theme ? theme.radiusM : 4
                color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"
                border.width: 1
                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12
                    Text {
                        text: "INFERENCE RESOURCES"
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        font.pixelSize: 11
                        color: theme ? theme.textMuted : "#64748B"
                    }
                    Column {
                        width: parent.width; spacing: 4
                        Row {
                            width: parent.width
                            Text { text: "ENGINE ALPHA"; font.pixelSize: 11; color: theme ? theme.textSecondary : "#94A3B8"; width: parent.width - 40 }
                            Text { text: "72%"; font.family: theme ? theme.fontFamilyMono : "monospace"; font.pixelSize: 11; color: theme ? theme.textPrimary : "#E5E7EB" }
                        }
                        Rectangle {
                            width: parent.width; height: 6; radius: 3
                            color: theme ? theme.backgroundAlt : "#0F172A"
                            Rectangle { width: parent.width * 0.72; height: parent.height; radius: 3; color: theme ? theme.primary : "#2563EB" }
                        }
                    }
                    Column {
                        width: parent.width; spacing: 4
                        Row {
                            width: parent.width
                            Text { text: "BUFFER STREAM"; font.pixelSize: 11; color: theme ? theme.textSecondary : "#94A3B8"; width: parent.width - 40 }
                            Text { text: "18%"; font.family: theme ? theme.fontFamilyMono : "monospace"; font.pixelSize: 11; color: theme ? theme.textPrimary : "#E5E7EB" }
                        }
                        Rectangle {
                            width: parent.width; height: 6; radius: 3
                            color: theme ? theme.backgroundAlt : "#0F172A"
                            Rectangle { width: parent.width * 0.18; height: parent.height; radius: 3; color: theme ? theme.info : "#06B6D4" }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 180
                radius: theme ? theme.radiusM : 4
                color: theme ? theme.surface : "#151C28"
                border.color: theme ? theme.border : "#1E293B"
                border.width: 1
                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 8
                    Text {
                        text: "LIVE EVENT LOG"
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        font.pixelSize: 11
                        color: theme ? theme.textMuted : "#64748B"
                    }
                    Repeater {
                        model: [
                            { sev: "CRITICAL", msg: "Unauthorized Person Detected", cam: "WH_DOCK_07", time: "14:41:02", c: "c" },
                            { sev: "WARNING", msg: "Thermal Threshold Warning", cam: "SERVER_COR_04", time: "14:39:55", c: "w" },
                            { sev: "CRITICAL", msg: "Camera Signal Interrupted", cam: "PERIM_FNC_09", time: "14:35:12", c: "c" },
                            { sev: "INFO", msg: "AI Inference Engine Latency", cam: "SYS_HEALTH", time: "14:30:44", c: "i" }
                        ]
                        delegate: Row {
                            width: parent.width
                            spacing: 8
                            Text {
                                text: modelData.sev
                                width: 70
                                font.family: theme ? theme.fontFamilyMono : "monospace"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: modelData.c === "c" ? "#EF4444" : (modelData.c === "w" ? "#F59E0B" : "#06B6D4")
                            }
                            Column {
                                width: parent.width - 150
                                Text { text: modelData.msg; font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB"; elide: Text.ElideRight; width: parent.width }
                                Text { text: modelData.cam; font.family: theme ? theme.fontFamilyMono : "monospace"; font.pixelSize: 10; color: theme ? theme.textMuted : "#64748B" }
                            }
                            Text { text: modelData.time; font.family: theme ? theme.fontFamilyMono : "monospace"; font.pixelSize: 10; color: theme ? theme.textMuted : "#64748B" }
                        }
                    }
                }
            }
        }
    }
}
