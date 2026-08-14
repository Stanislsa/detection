import QtQuick 2.15

/*
 * SplitPane — horizontal split with a draggable divider.
 * Use it as a parent container with two `default property` children.
 */
Item {
    id: control
    property var theme
    property real leftRatio: 0.5
    property real minLeftWidth: 240
    property real minRightWidth: 240
    property color dividerColor: theme ? theme.borderStrong : "#334155"

    default property alias leftPane: leftContainer.data
    default property alias rightPane: rightContainer.data

    Item {
        id: leftContainer
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        width: Math.max(control.minLeftWidth, parent.width * control.leftRatio)
    }

    Item {
        id: rightContainer
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        width: Math.max(control.minRightWidth, parent.width - leftContainer.width)
    }

    Rectangle {
        id: handle
        width: 4
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        x: leftContainer.width - width / 2
        color: control.dividerColor
        opacity: dragArea.containsMouse ? 0.8 : 0.4

        Behavior on opacity { NumberAnimation { duration: 120 } }

        MouseArea {
            id: dragArea
            anchors.fill: parent
            anchors.leftMargin: -4
            anchors.rightMargin: -4
            hoverEnabled: true
            cursorShape: Qt.SplitHCursor
            property real startX
            property real startRatio

            onPressed: {
                startX = mouse.x
                startRatio = control.leftRatio
            }
            onPositionChanged: {
                if (pressed) {
                    var delta = (mouse.x - startX) / parent.parent.width
                    var newRatio = startRatio + delta
                    control.leftRatio = Math.max(0.15, Math.min(0.85, newRatio))
                }
            }
        }
    }
}