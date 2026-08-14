import QtQuick 2.15
import QtQuick.Controls 2.15

/*
 * AppButton — primary/secondary/ghost/danger variants. 4px radius.
 */
Button {
    id: control

    property var theme
    property string variant: "primary"          // primary | secondary | ghost | danger
    property string iconGlyph: ""               // optional leading glyph (avoid FINAL `icon` on Button)
    property string iconName: ""                 // SVG icon name from assets/icons

    readonly property bool _isPrimary: variant === "primary"
    readonly property bool _isSecondary: variant === "secondary"
    readonly property bool _isGhost: variant === "ghost"
    readonly property bool _isDanger: variant === "danger"

    readonly property color _fillColor: {
        if (_isDanger)   return theme ? theme.critical : "#EF4444"
        if (_isPrimary)  return theme ? theme.primary : "#2563EB"
        return "transparent"
    }
    readonly property color _hoverColor: {
        if (_isDanger)   return theme ? theme.criticalHover : "#F87171"
        if (_isPrimary)  return theme ? theme.primaryHover : "#3B82F6"
        return theme ? theme.surfaceAlt : "#1B2433"
    }
    readonly property color _pressedColor: {
        if (_isDanger)   return theme ? theme.criticalPressed : "#DC2626"
        if (_isPrimary)  return theme ? theme.primaryPressed : "#1D4ED8"
        return theme ? theme.surface : "#151C28"
    }
    readonly property color _textColor: {
        if (_isGhost)        return theme ? theme.textPrimary : "#E5E7EB"
        if (_isSecondary)    return theme ? theme.textPrimary : "#E5E7EB"
        return "#FFFFFF"
    }

    implicitHeight: theme ? theme.buttonHeight : 36

    leftPadding: theme ? theme.spacingM : 16
    rightPadding: theme ? theme.spacingM : 16

    background: Rectangle {
        implicitWidth: 120
        implicitHeight: theme ? theme.buttonHeight : 36
        color: !control.enabled ? (theme ? theme.surface : "#151C28")
             : control.pressed ? control._pressedColor
             : control.hovered ? control._hoverColor
             : control._fillColor
        radius: theme ? theme.radiusM : 4
        border.width: (control._isSecondary || control._isGhost) ? (theme ? theme.borderWidth : 1) : 0
        border.color: theme ? theme.borderStrong : "#334155"
        opacity: control.enabled ? 1.0 : 0.5

        Behavior on color { ColorAnimation { duration: 150 } }
    }

    contentItem: Row {
        spacing: theme ? theme.spacingXS : 4
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        AppIcon {
            visible: control.iconName !== ""
            width: theme ? theme.iconSizeS : 14
            height: theme ? theme.iconSizeS : 14
            iconName: control.iconName
            iconColor: control._textColor
            theme: control.theme
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
            visible: control.iconGlyph !== "" && control.iconName === ""
            text: control.iconGlyph
            color: control._textColor
            font.pixelSize: theme ? theme.fontSizeM : 13
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
            text: control.text
            color: control._textColor
            font.family: theme ? theme.fontFamily : "Inter"
            font.pixelSize: theme ? theme.fontSizeM : 13
            font.weight: theme ? theme.weightSemiBold : Font.DemiBold
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}