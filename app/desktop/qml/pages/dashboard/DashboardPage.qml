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

    contentWidth: parent.width
    contentHeight: contentColumn.height + (theme ? theme.spacingXL : 48)
    clip: true

    Column {
        id: contentColumn
        width: parent.width
        spacing: theme ? theme.spacingL : 24
        anchors.top: parent.top
        anchors.topMargin: theme ? theme.spacingL : 24

        // ---- KPI Row: 4 spec cards with deltas ----
        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            spacing: theme ? theme.spacingM : 16

            KpiCard {
                theme: control.theme
                Layout.fillWidth: true
                Layout.preferredWidth: 200
                title: "Active Threats"
                kpiValue: "12"
                unit: ""
                icon: Icons.alertGlyph
                cardColor: theme.critical
                accent: theme.critical
                delta: "+3"
                deltaPositive: false
                deltaColor: "critical"
            }

            KpiCard {
                theme: control.theme
                Layout.fillWidth: true
                Layout.preferredWidth: 200
                title: "AI Inference Load"
                kpiValue: "42.8"
                unit: "%"
                icon: Icons.aiTrainingGlyph
                cardColor: theme.primary
                accent: theme.primary
                delta: "+5.4%"
                deltaPositive: true
                deltaColor: "info"
            }

            KpiCard {
                theme: control.theme
                Layout.fillWidth: true
                Layout.preferredWidth: 200
                title: "Live Nodes"
                kpiValue: "128/130"
                unit: ""
                icon: Icons.observabilityGlyph
                cardColor: theme.success
                accent: theme.success
                delta: "-2"
                deltaPositive: false
                deltaColor: "warning"
            }

            KpiCard {
                theme: control.theme
                Layout.fillWidth: true
                Layout.preferredWidth: 200
                title: "Events / Sec"
                kpiValue: "1,422"
                unit: "ev/s"
                icon: Icons.eventsGlyph
                cardColor: theme.info
                accent: theme.info
                delta: "+12%"
                deltaPositive: true
                deltaColor: "success"
            }
        }

        // ---- Live Surveillance Matrix ----
        AppCard {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            height: theme ? theme.cardHeightXXL : 400
            theme: control.theme

            Column {
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                spacing: theme ? theme.spacingM : 16

                RowLayout {
                    width: parent.width
                    spacing: theme ? theme.spacingM : 16

                    Text {
                        text: "Live Surveillance Matrix"
                        font.pixelSize: theme ? theme.fontSizeL : 16
                        font.weight: theme.weightSemiBold
                        color: theme ? theme.textPrimary : "#ffffff"
                        Layout.alignment: Qt.AlignLeft
                    }

                    AppBadge {
                        theme: control.theme
                        variant: "subtle"
                        icon: Icons.successGlyph
                        text: "SYNC_STABLE"
                    }

                    Item { Layout.fillWidth: true }

                    AppButton {
                        theme: control.theme
                        variant: "secondary"
                        text: "CUSTOM VIEW"
                    }

                    AppButton {
                        theme: control.theme
                        variant: "secondary"
                        text: "TOGGLE AI LABELS"
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#1E293B"
                }

                // 2x3 Video Grid
                GridLayout {
                    width: parent.width
                    height: parent.height - 60
                    columns: 3
                    columnSpacing: theme ? theme.spacingS : 8
                    rowSpacing: theme ? theme.spacingS : 8

                    Repeater {
                        model: [
                            { id: "LOBBY_EAST_01", alert: false },
                            { id: "WH_DOCK_07",     alert: true  },
                            { id: "SERVER_COR_04",  alert: false },
                            { id: "PARK_EXT_12",    alert: false },
                            { id: "RETAIL_FLR_02",  alert: false },
                            { id: "PERIM_FNC_09",   alert: false }
                        ]

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: theme ? theme.surfaceElevated : "#1E293B"
                            radius: theme ? theme.radiusS : 4
                            border.color: modelData.alert
                                ? (theme ? theme.critical : "#EF4444")
                                : (theme ? theme.border : "#1E293B")
                            border.width: 1

                            Column {
                                anchors.fill: parent
                                anchors.margins: theme ? theme.spacingS : 8
                                spacing: theme ? theme.spacingXS : 4

                                Row {
                                    width: parent.width
                                    Text {
                                        text: modelData.id
                                        font.pixelSize: theme ? theme.fontSizeXS : 10
                                        font.family: theme ? theme.fontFamilyMono : "JetBrains Mono"
                                        font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                                        color: modelData.alert
                                            ? (theme ? theme.critical : "#EF4444")
                                            : (theme ? theme.success : "#10B981")
                                    }
                                    Item { width: 1; height: 1 }
                                }

                                Rectangle {
                                    width: parent.width
                                    height: parent.height - 20
                                    color: "#000000"
                                    radius: theme ? theme.radiusS : 4
                                    border.color: modelData.alert
                                        ? (theme ? theme.critical : "#EF4444")
                                        : "transparent"
                                    border.width: modelData.alert ? 2 : 0

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData.alert ? "UNAUTHORIZED_PERSON" : ""
                                        font.pixelSize: theme ? theme.fontSizeS : 12
                                        font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                                        color: theme ? theme.critical : "#EF4444"
                                    }

                                    // Bounding box overlay for the alert tile
                                    Rectangle {
                                        visible: modelData.alert
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: parent.width * 0.4
                                        height: parent.height * 0.55
                                        color: "transparent"
                                        border.color: theme ? theme.critical : "#EF4444"
                                        border.width: 2
                                        radius: 2
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // ---- Right sidebar row: Inference Resources + Live Event Log ----
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - (theme ? theme.spacingXL : 48) * 2
            spacing: theme ? theme.spacingM : 16

            // Inference Resources
            AppCard {
                width: (parent.width - (theme ? theme.spacingM : 16)) / 2
                height: theme ? theme.cardHeightL : 200
                theme: control.theme

                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16

                    Text {
                        text: "Inference Resources"
                        font.pixelSize: theme ? theme.fontSizeL : 16
                        font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                        color: theme ? theme.textPrimary : "#ffffff"
                    }

                    Rectangle {
                        width: parent.width
                        height: 1
                        color: theme ? theme.border : "#1E293B"
                    }

                    Column {
                        width: parent.width
                        spacing: theme ? theme.spacingS : 8

                        Row {
                            spacing: theme ? theme.spacingS : 8
                            Text {
                                text: "ENGINE ALPHA"
                                font.family: theme ? theme.fontFamilyMono : "JetBrains Mono"
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            Text {
                                text: "72%"
                                font.family: theme ? theme.fontFamilyMono : "JetBrains Mono"
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                                color: theme ? theme.success : "#10B981"
                            }
                        }

                        Rectangle {
                            width: parent.width
                            height: 8
                            radius: theme ? theme.radiusS : 4
                            color: theme ? theme.surface : "#151C28"
                            Rectangle {
                                width: parent.width * 0.72
                                height: parent.height
                                radius: theme ? theme.radiusS : 4
                                color: theme ? theme.primary : "#2563EB"
                            }
                        }

                        Row {
                            spacing: theme ? theme.spacingS : 8
                            Text {
                                text: "BUFFER STREAM"
                                font.family: theme ? theme.fontFamilyMono : "JetBrains Mono"
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                color: theme ? theme.textSecondary : "#a0a0a0"
                            }
                            Text {
                                text: "18%"
                                font.family: theme ? theme.fontFamilyMono : "JetBrains Mono"
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                                color: theme ? theme.warning : "#F59E0B"
                            }
                        }

                        Rectangle {
                            width: parent.width
                            height: 8
                            radius: theme ? theme.radiusS : 4
                            color: theme ? theme.surface : "#151C28"
                            Rectangle {
                                width: parent.width * 0.18
                                height: parent.height
                                radius: theme ? theme.radiusS : 4
                                color: theme ? theme.warning : "#F59E0B"
                            }
                        }
                    }
                }
            }

            // Live Event Log
            AppCard {
                width: (parent.width - (theme ? theme.spacingM : 16)) / 2
                height: theme ? theme.cardHeightL : 200
                theme: control.theme

                Column {
                    anchors.fill: parent
                    anchors.margins: theme ? theme.spacingM : 16
                    spacing: theme ? theme.spacingM : 16

                    Text {
                        text: "Live Event Log"
                        font.pixelSize: theme ? theme.fontSizeL : 16
                        font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                        color: theme ? theme.textPrimary : "#ffffff"
                    }

                    Rectangle {
                        width: parent.width
                        height: 1
                        color: theme ? theme.border : "#1E293B"
                    }

                    ListView {
                        width: parent.width
                        height: parent.height - 60
                        model: [
                            { severity: "critical", node: "WH_DOCK_07",     time: "2m ago"  },
                            { severity: "warning",  node: "SERVER_COR_04",  time: "5m ago"  },
                            { severity: "info",     node: "LOBBY_EAST_01",  time: "12m ago" },
                            { severity: "info",     node: "PARK_EXT_12",    time: "18m ago" },
                            { severity: "info",     node: "RETAIL_FLR_02",  time: "24m ago" }
                        ]
                        spacing: theme ? theme.spacingS : 8
                        clip: true

                        delegate: Row {
                            width: parent.width
                            spacing: theme ? theme.spacingS : 8

                            Rectangle {
                                width: 8
                                height: 8
                                radius: 4
                                anchors.verticalCenter: parent.verticalCenter
                                color: {
                                    if (modelData.severity === "critical") return theme ? theme.critical : "#EF4444"
                                    if (modelData.severity === "warning")  return theme ? theme.warning  : "#F59E0B"
                                    return theme ? theme.info : "#06B6D4"
                                }
                            }

                            AppBadge {
                                theme: control.theme
                                variant: "subtle"
                                text: modelData.severity.toUpperCase()
                            }

                            Text {
                                text: modelData.node
                                font.pixelSize: theme ? theme.fontSizeXS : 10
                                font.family: theme ? theme.fontFamilyMono : "JetBrains Mono"
                                color: theme ? theme.textPrimary : "#ffffff"
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Item { width: 1; height: 1 }

                            Text {
                                text: modelData.time
                                font.pixelSize: theme ? theme.fontSizeXS : 10
                                color: theme ? theme.textDisabled : "#606060"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }
                }
            }
        }
    }
}