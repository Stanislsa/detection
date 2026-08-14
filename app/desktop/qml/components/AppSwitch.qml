import QtQuick 2.15
import QtQuick.Controls 2.15

/*
 * AppSwitch — track + thumb with optional inline label.
 */
Row {
    id: control
    spacing: theme ? theme.spacingS : 8

    property var theme
    property bool checked: false
    property string label: ""

    Switch {
        id: sw
        checked: control.checked
        onCheckedChanged: control.checked = checked
        indicator: Rectangle {
            implicitWidth: 40
            implicitHeight: 22
            x: sw.leftPadding
            y: sw.topPadding + sw.availableHeight / 2 - height / 2
            width: implicitWidth
            height: implicitHeight
            radius: height / 2
            color: sw.checked ? (theme ? theme.primary : "#2563EB")
                              : (theme ? theme.surfaceAlt : "#1B2433")
            border.color: sw.checked ? (theme ? theme.primaryHover : "#3B82F6")
                                     : (theme ? theme.border : "#1E293B")
            border.width: 1

            Behavior on color { ColorAnimation { duration: 150 } }

            Rectangle {
                x: sw.checked ? parent.width - width - 2 : 2
                y: parent.height / 2 - height / 2
                width: 16
                height: 16
                radius: height / 2
                color: theme ? theme.surfaceElevated : "#1E293B"
                border.color: theme ? theme.borderStrong : "#334155"
                border.width: 1
                Behavior on x { NumberAnimation { duration: 150; easing.type: Easing.InOutQuad } }
            }
        }
    }

    Text {
        visible: control.label !== ""
        text: control.label
        font.family: theme ? theme.fontFamily : "Inter"
        font.pixelSize: theme ? theme.fontSizeM : 13
        color: theme ? theme.textPrimary : "#E5E7EB"
        anchors.verticalCenter: parent.verticalCenter
    }
}