import QtQuick 2.15

/*
 * AppCard — 1px border by default, optional shadowXL elevation.
 * Surface hover already animates scale.
 */
Rectangle {
    id: control

    property var theme
    property color backgroundColor: theme ? theme.surface : "#151C28"
    property color borderColor: theme ? theme.border : "#1E293B"
    property int borderWidth: 1
    property string elevation: "none"      // none | shadowXL

    implicitWidth: 200
    implicitHeight: 100

    color: control.backgroundColor
    border.color: control.borderColor
    border.width: control.borderWidth
    radius: theme ? theme.radiusM : 4

    // Note: DropShadow requires Qt5Compat.GraphicalEffects module
    // which is not installed. Shadow effect disabled for now.

    default property alias content: contentContainer.data
    Item {
        id: contentContainer
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingM : 16
    }
}