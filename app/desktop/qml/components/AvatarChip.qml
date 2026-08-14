import QtQuick 2.15

/*
 * AvatarChip — header right-side chip. Shows initials avatar + name + role.
 */
Item {
    id: control
    property var theme
    property string name: "Alex Rivers"
    property string role: "SOC Analyst"
    property string initials: "AR"

    implicitWidth: layout.implicitWidth + theme.spacingM * 2
    implicitHeight: theme ? theme.buttonHeight : 36

    Rectangle {
        id: bg
        anchors.fill: parent
        color: control.containsMouse ? (theme ? theme.surfaceAlt : "#1B2433") : "transparent"
        radius: theme ? theme.radiusM : 4
        border.color: theme ? theme.border : "#1E293B"
        border.width: 1

        Behavior on color { ColorAnimation { duration: 120 } }
    }

    Row {
        id: layout
        anchors.centerIn: parent
        spacing: theme ? theme.spacingS : 8

        Rectangle {
            width: control.theme ? control.theme.avatarSizeS : 32
            height: width
            radius: width / 2
            color: control.theme ? control.theme.primary : "#2563EB"

            Text {
                anchors.centerIn: parent
                text: control.initials
                font.family: control.theme ? control.theme.fontFamily : "Inter"
                font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                font.weight: control.theme ? control.theme.weightSemiBold : Font.DemiBold
                color: "#0B0E14"
            }
        }

        Column {
            spacing: 0
            anchors.verticalCenter: parent.verticalCenter

            Text {
                text: control.name
                font.family: control.theme ? control.theme.fontFamily : "Inter"
                font.pixelSize: control.theme ? control.theme.fontSizeS : 12
                font.weight: control.theme ? control.theme.weightSemiBold : Font.DemiBold
                color: control.theme ? control.theme.textPrimary : "#E5E7EB"
            }
            Text {
                text: control.role
                font.family: control.theme ? control.theme.fontFamilyMono : "Consolas"
                font.pixelSize: control.theme ? control.theme.fontSizeXS : 10
                font.letterSpacing: control.theme ? control.theme.letterSpacingM : 0.04
                color: control.theme ? control.theme.textSecondary : "#94A3B8"
            }
        }
    }

    property bool containsMouse: hoverArea.containsMouse
    MouseArea {
        id: hoverArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
    }
}