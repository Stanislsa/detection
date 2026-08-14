import QtQuick 2.15

/*
 * AppBadge — solid/outline/subtle variants. 4px radius. Optional
 * leading icon slot.
 */
Rectangle {
    id: control

    property var theme
    property string text: ""
    property string icon: ""
    property color fillColor: theme ? theme.primary : "#2563EB"
    property string variant: "solid"      // solid | outline | subtle

    property color _resolvedFill: variant === "solid" ? fillColor
                           : variant === "subtle" ? Qt.rgba(fillColor.r, fillColor.g, fillColor.b, 0.15)
                           : "transparent"
    property color _resolvedText: variant === "solid" ? "#FFFFFF" : fillColor

    implicitWidth: layout.implicitWidth + (theme ? theme.spacingS : 8) * 2
    implicitHeight: layout.implicitHeight + (theme ? theme.spacingXS : 4) * 2

    radius: theme ? theme.radiusM : 4
    color: _resolvedFill
    border.color: variant === "outline" ? fillColor : "transparent"
    border.width: variant === "outline" ? (theme ? theme.borderWidth : 1) : 0

    Row {
        id: layout
        anchors.centerIn: parent
        spacing: 4
        Text {
            visible: control.icon !== ""
            text: control.icon
            font.pixelSize: control.theme ? control.theme.fontSizeXS : 10
            color: control._resolvedText
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
            text: control.text
            font.family: control.theme ? control.theme.fontFamilyMono : "Consolas"
            font.pixelSize: control.theme ? control.theme.fontSizeXS : 10
            font.weight: control.theme ? control.theme.weightSemiBold : Font.DemiBold
            font.letterSpacing: control.theme ? control.theme.letterSpacingM : 0.04
            color: control._resolvedText
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}