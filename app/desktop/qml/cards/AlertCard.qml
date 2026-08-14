import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"
import "../components"

Rectangle {
    id: control
    property var theme
    property string title: "Alert"
    property string severity: "high" // low, medium, high, critical
    property string message: ""
    property string timestamp: ""
    property string alertId: ""

    implicitWidth: 320
    implicitHeight: 130
    color: control.theme.surface
    border.color: control.severityColor
    border.width: 1
    radius: control.theme.radiusM

    property color severityColor: {
        switch(control.severity) {
            case "high": case "critical": return control.theme.critical
            case "medium": case "warning": return control.theme.warning
            case "low":                    return control.theme.info
        }
        return control.theme.border
    }

    Row {
        anchors.fill: parent
        anchors.margins: control.theme.spacingM
        spacing: control.theme.spacingM

        // Severity rail (2px wider than before)
        Rectangle {
            width: 2
            height: parent.height
            color: control.severityColor
        }

        Column {
            width: parent.width - 2
            spacing: control.theme.spacingXS

            Row {
                width: parent.width
                spacing: control.theme.spacingS

                Text {
                    text: control.title
                    font.family: control.theme.fontFamily
                    font.pixelSize: control.theme.fontSizeM
                    font.weight: control.theme.weightSemiBold
                    color: control.theme.textPrimary
                    width: parent.width - 90
                    elide: Text.ElideRight
                }

                Item { width: 1; height: parent.height }

                AppBadge {
                    theme: control.theme
                    text: control.severity.toUpperCase()
                    fillColor: control.severityColor
                    variant: "outline"
                }
            }

            Text {
                text: control.message
                font.family: control.theme.fontFamily
                font.pixelSize: control.theme.fontSizeS
                color: control.theme.textSecondary
                width: parent.width
                wrapMode: Text.WordWrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }

            Row {
                width: parent.width
                Text {
                    text: control.alertId
                    font.family: control.theme.fontFamilyMono
                    font.pixelSize: control.theme.fontSizeXS
                    color: control.theme.textMuted
                }
                Item { width: 1; height: parent.height }
                Text {
                    text: control.timestamp
                    font.family: control.theme.fontFamilyMono
                    font.pixelSize: control.theme.fontSizeXS
                    color: control.theme.textMuted
                }
            }
        }
    }

    // Optional inline actions slot (declared via default property)
    default property alias actionRow: containerAction.children

    Item {
        id: containerAction
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: control.theme.spacingS
        height: childrenRect.height
    }
}