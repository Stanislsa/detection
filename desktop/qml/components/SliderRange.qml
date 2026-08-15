import QtQuick 2.15
import QtQuick.Controls 2.15

/*
 * SliderRange — single-axis slider with a labeled value pill.
 * Used by Events filter sidebar for the AI-confidence threshold.
 */
Item {
    id: control
    property var theme
    property real value: 75
    property real from: 0
    property real to: 100
    property string label: "AI Confidence"
    property color activeColor: theme ? theme.primary : "#2563EB"

    implicitHeight: 56

    Row {
        anchors.fill: parent
        spacing: theme ? theme.spacingM : 16

        Column {
            width: parent.width - 80
            spacing: theme ? theme.spacingXS : 4

            Text {
                text: control.label
                font.family: theme ? theme.fontFamilyMono : "Consolas"
                font.pixelSize: theme ? theme.fontSizeXS : 11
                font.letterSpacing: theme ? theme.letterSpacingM : 0.04
                color: theme ? theme.textSecondary : "#94A3B8"
            }

            Slider {
                width: parent.width
                from: control.from
                to: control.to
                value: control.value
                onValueChanged: control.value = value
            }
        }

        Rectangle {
            width: 64
            height: theme ? theme.buttonHeight : 36
            radius: theme ? theme.radiusM : 4
            color: theme ? theme.surfaceAlt : "#1B2433"
            border.color: control.activeColor
            border.width: 1
            anchors.verticalCenter: parent.verticalCenter

            Text {
                anchors.centerIn: parent
                text: "> " + Math.round(control.value) + "%"
                font.family: theme ? theme.fontFamilyMono : "Consolas"
                font.pixelSize: theme ? theme.fontSizeS : 12
                font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                color: control.activeColor
            }
        }
    }
}