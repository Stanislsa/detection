import QtQuick 2.15

/*
 * ClusterMap — boxes-and-lines topology diagram.
 * `topology: { regions: [{label, color, azs: [{label, status, nodes:[{...}]}]}] }`
 * Kept simple: regions as columns, AZs as rows, nodes as labeled dots.
 */
Item {
    id: control
    property var theme
    property var topology: ({ "regions": [] })

    implicitHeight: 360

    Rectangle {
        anchors.fill: parent
        color: theme ? theme.background : "#0B0E14"
        border.color: theme ? theme.border : "#1E293B"
        border.width: 1
        radius: theme ? theme.radiusM : 4
    }

    Row {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingM : 16
        spacing: theme ? theme.spacingL : 24

        Repeater {
            model: control.topology.regions || []
            delegate: Column {
                spacing: theme ? theme.spacingS : 8
                width: (parent.width - (theme ? theme.spacingL * 2 : 48)) / 3

                Text {
                    text: modelData.label
                    font.family: theme ? theme.fontFamilyMono : "Consolas"
                    font.pixelSize: theme ? theme.fontSizeS : 12
                    font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                    color: modelData.color || (theme ? theme.primary : "#2563EB")
                    font.letterSpacing: theme ? theme.letterSpacingM : 0.04
                }

                Repeater {
                    model: modelData.azs || []
                    delegate: Rectangle {
                        width: parent.width
                        height: 56
                        color: theme ? theme.surface : "#151C28"
                        border.color: theme ? theme.border : "#1E293B"
                        border.width: 1
                        radius: theme ? theme.radiusM : 4

                        Row {
                            anchors.fill: parent
                            anchors.margins: theme ? theme.spacingS : 8
                            spacing: theme ? theme.spacingS : 8

                            Text {
                                text: modelData.label
                                font.pixelSize: theme ? theme.fontSizeS : 12
                                color: theme ? theme.textPrimary : "#E5E7EB"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            Item { Layout.fillWidth: true }
                            Chip {
                                theme: control.theme
                                label: modelData.status
                                status: modelData.status
                                variant: "outline"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }
                }
            }
        }
    }
}