import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"
import "../components"

Rectangle {
    id: control

    property var theme
    property string title: "Active Threats"
    property string kpiValue: "0"
    property string icon: ""
    property color cardColor: theme ? theme.primary : "#2563EB"

    // Spec extras
    property string delta: ""            // "+5%" / "-12%"
    property bool deltaPositive: true
    property string deltaColor: "success"
    property string unit: ""             // "Mb/s", "GB", "%"
    property bool monoValue: true        // render big value in mono
    property string accent: ""           // left-rail color; defaults to cardColor

    implicitWidth: 220
    implicitHeight: 120

    color: theme ? theme.surface : "#151C28"
    radius: theme ? theme.radiusM : 4
    border.color: theme ? theme.border : "#1E293B"
    border.width: 1

    Rectangle {
        width: 3
        height: parent.height
        color: control.accent !== "" ? control.accent : control.cardColor
        radius: 1
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: theme ? theme.spacingM : 16
        anchors.topMargin: theme ? theme.spacingM : 16
        anchors.bottomMargin: theme ? theme.spacingM : 16
        anchors.rightMargin: theme ? theme.spacingM : 16
        spacing: theme ? theme.spacingM : 16

        Column {
            width: parent.width - 56
            anchors.verticalCenter: parent.verticalCenter
            spacing: theme ? theme.spacingXS : 4

            Row {
                spacing: theme ? theme.spacingXS : 4
                AppIcon {
                    width: theme ? theme.iconSizeM : 18
                    height: theme ? theme.iconSizeM : 18
                    iconName: control.icon
                    iconColor: control.cardColor
                    visible: control.icon !== ""
                    anchors.verticalCenter: parent.verticalCenter
                }
                Text {
                    text: control.title.toUpperCase()
                    font.family: theme ? theme.fontFamilyMono : "JetBrains Mono"
                    font.pixelSize: theme ? theme.fontSizeXS : 11
                    font.letterSpacing: theme ? theme.letterSpacingM : 0.04
                    font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                    color: theme ? theme.textSecondary : "#94A3B8"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            Row {
                spacing: 4
                Text {
                    text: control.kpiValue
                    font.family: (control.monoValue && theme) ? theme.fontFamilyMono : (theme ? theme.fontFamily : "Inter")
                    font.pixelSize: theme ? theme.fontSizeXXXL : 28
                    font.weight: theme ? theme.weightBold : Font.Bold
                    color: theme ? theme.textPrimary : "#E5E7EB"
                }
                Text {
                    visible: control.unit !== ""
                    text: control.unit
                    font.family: theme ? theme.fontFamilyMono : "JetBrains Mono"
                    font.pixelSize: theme ? theme.fontSizeL : 14
                    font.weight: theme ? theme.weightRegular : Font.Normal
                    color: theme ? theme.textSecondary : "#94A3B8"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            KpiDeltaBadge {
                visible: control.delta !== ""
                theme: control.theme
                delta: control.delta
                positive: control.deltaPositive
                deltaColor: control.deltaColor
            }
        }

        Item {
            width: 56
            height: 32
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
