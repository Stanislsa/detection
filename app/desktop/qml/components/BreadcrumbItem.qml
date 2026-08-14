import QtQuick 2.15

/*
 * BreadcrumbItem — single clickable crumb. Last item is non-clickable
 * (rendered in textPrimary); siblings render in textSecondary.
 */
Item {
    id: control
    property var theme
    property string label: ""
    property bool isLast: false

    signal clicked()

    implicitWidth: labelText.implicitWidth
    implicitHeight: labelText.implicitHeight

    Text {
        id: labelText
        text: control.label
        font.family: theme ? theme.fontFamilyMono : "Consolas"
        font.pixelSize: theme ? theme.fontSizeS : 12
        font.letterSpacing: theme ? theme.letterSpacingM : 0.04
        color: control.isLast ? (theme ? theme.textPrimary : "#E5E7EB")
                              : (theme ? theme.textSecondary : "#94A3B8")
    }

    MouseArea {
        anchors.fill: parent
        enabled: !control.isLast
        cursorShape: control.isLast ? Qt.ArrowCursor : Qt.PointingHandCursor
        onClicked: control.clicked()
    }
}