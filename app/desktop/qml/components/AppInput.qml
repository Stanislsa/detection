import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/*
 * AppInput — optional uppercase label above; optional leading icon.
 * Set `mono: true` to render content in monospace.
 */
Column {
    id: control

    property var theme
    property alias text: field.text
    property alias placeholderText: field.placeholderText
    property alias echoMode: field.echoMode
    property alias maximumLength: field.maximumLength
    property alias validator: field.validator
    property string label: ""
    property string leadingIcon: ""
    property bool mono: false

    // Re-emit the inner TextField's `accepted` signal so callers can use
    // `onAccepted:` directly on AppInput (Qt 6 removed signal auto-forwarding
    // from child items).
    signal accepted()

    spacing: theme ? theme.spacingXS : 4

    Text {
        visible: control.label !== ""
        text: control.label
        font.family: control.theme ? control.theme.fontFamilyMono : "Consolas"
        font.pixelSize: control.theme ? control.theme.fontSizeXS : 11
        font.letterSpacing: control.theme ? control.theme.letterSpacingM : 0.04
        font.weight: control.theme ? control.theme.weightSemiBold : Font.DemiBold
        color: control.theme ? control.theme.textSecondary : "#94A3B8"
    }

    TextField {
        id: field
        width: control.width
        implicitHeight: control.theme ? control.theme.inputHeight : 36
        leftPadding: control.leadingIcon !== ""
            ? (control.theme ? control.theme.spacingXL : 32)
            : (control.theme ? control.theme.spacingM : 16)
        rightPadding: control.theme ? control.theme.spacingM : 16
        color: control.enabled ? (control.theme ? control.theme.textPrimary : "#E5E7EB")
                               : (control.theme ? control.theme.textDisabled : "#475569")
        placeholderTextColor: control.theme ? control.theme.textMuted : "#64748B"
        font.family: control.mono && control.theme ? control.theme.fontFamilyMono : (control.theme ? control.theme.fontFamily : "Inter")
        font.pixelSize: control.theme ? control.theme.fontSizeM : 13
        selectByMouse: true
        onAccepted: control.accepted()
        background: Rectangle {
            implicitHeight: control.theme ? control.theme.inputHeight : 36
            color: control.theme ? control.theme.surfaceAlt : "#1B2433"
            border.color: field.activeFocus
                ? (control.theme ? control.theme.borderFocus : "#2563EB")
                : (control.theme ? control.theme.border : "#1E293B")
            border.width: control.theme ? control.theme.borderWidth : 1
            radius: control.theme ? control.theme.radiusM : 4

            Behavior on border.color { ColorAnimation { duration: 150 } }

            Text {
                visible: control.leadingIcon !== ""
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: control.theme ? control.theme.spacingS : 8
                text: control.leadingIcon
                color: control.theme ? control.theme.textSecondary : "#94A3B8"
                font.pixelSize: control.theme ? control.theme.fontSizeM : 13
            }
        }
    }
}