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
    property color cardColor: theme.primary

    // Spec extras
    property string delta: ""            // "+5%" / "-12%"
    property bool deltaPositive: true
    property string deltaColor: "success"
    property string unit: ""             // "Mb/s", "GB", "%"
    property bool monoValue: true        // render big value in mono
    property string accent: ""           // left-rail color; defaults to cardColor

    implicitWidth: 220
    implicitHeight: 120

    color: theme.surface
    radius: theme.radiusM
    border.color: theme.border
    border.width: 1

    Rectangle {
        width: 3
        height: parent.height
        color: control.accent !== "" ? control.accent : control.cardColor
        radius: 1
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: theme.spacingM
        anchors.topMargin: theme.spacingM
        anchors.bottomMargin: theme.spacingM
        anchors.rightMargin: theme.spacingM
        spacing: theme.spacingM

        Column {
            width: parent.width - 56
            anchors.verticalCenter: parent.verticalCenter
            spacing: theme.spacingXS

            Row {
                spacing: theme.spacingXS
                AppIcon {
                    width: theme.iconSizeM
                    height: theme.iconSizeM
                    iconName: control.icon
                    iconColor: control.cardColor
                    visible: control.icon !== ""
                    anchors.verticalCenter: parent.verticalCenter
                }
                Text {
                    text: control.title.toUpperCase()
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeXS
                    font.letterSpacing: theme.letterSpacingM
                    font.weight: theme.weightSemiBold
                    color: theme.textSecondary
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            Row {
                spacing: 4
                Text {
                    text: control.kpiValue
                    font.family: control.monoValue && theme ? theme.fontFamilyMono : theme.fontFamily
                    font.pixelSize: theme.fontSizeXXXL
                    font.weight: theme.weightBold
                    color: theme.textPrimary
                }
                Text {
                    visible: control.unit !== ""
                    text: control.unit
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeL
                    font.weight: theme.weightRegular
                    color: theme.textSecondary
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