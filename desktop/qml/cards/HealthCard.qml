import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"
import "../charts"

Rectangle {
    id: control
    property var theme
    property string title: "System Health"
    property string status: "healthy" // healthy, warning, critical
    property real value: 0
    property string unit: "%"

    implicitWidth: 220
    implicitHeight: 130
    color: control.theme.surface
    border.color: control.theme.border
    border.width: 1
    radius: control.theme ? control.theme.radiusM : 4

    property color statusColor: {
        switch(control.status) {
            case "healthy": return control.theme.success
            case "warning": return control.theme.warning
            case "critical": return control.theme.critical
        }
        return control.theme.border
    }

    Column {
        anchors.fill: parent
        anchors.margins: control.theme.spacingM
        spacing: control.theme.spacingS

        Row {
            width: parent.width
            spacing: control.theme.spacingS
            Text {
                text: control.title.toUpperCase()
                font.family: control.theme.fontFamilyMono
                font.pixelSize: control.theme.fontSizeXS
                font.letterSpacing: control.theme.letterSpacingM
                font.weight: control.theme.weightSemiBold
                color: control.theme.textSecondary
            }
            Item { width: 1; height: parent.height }
            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: control.statusColor
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        Item {
            width: parent.width
            height: 50
            Gauge {
                anchors.fill: parent
                theme: control.theme
                value: control.value
                color: control.statusColor
            }
        }

        Row {
            width: parent.width
            spacing: control.theme.spacingS
            Text {
                text: control.value.toFixed(1)
                font.family: control.theme.fontFamilyMono
                font.pixelSize: control.theme.fontSizeXXL
                font.weight: control.theme.weightBold
                color: control.theme.textPrimary
            }
            Text {
                text: control.unit
                font.family: control.theme.fontFamilyMono
                font.pixelSize: control.theme.fontSizeM
                color: control.theme.textSecondary
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}