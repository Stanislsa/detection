import QtQuick 2.15
import QtQuick.Layouts 1.15

/*
 * TabBar — horizontal tab strip with underline indicator.
 * `tabs: ["OVERVIEW", "TELEMETRY", "AUDIT LOG"]`.
 * Emits `tabChanged(int)`.
 */
Rectangle {
    id: control
    property var theme
    property var tabs: []
    property int currentIndex: 0
    property color activeColor: theme ? theme.primary : "#2563EB"
    property color textColor: theme ? theme.textPrimary : "#E5E7EB"
    property color inactiveTextColor: theme ? theme.textSecondary : "#94A3B8"

    signal tabChanged(int index)

    implicitHeight: theme ? theme.buttonHeight : 36
    color: "transparent"

    Row {
        anchors.fill: parent
        spacing: theme ? theme.spacingL : 24

        Repeater {
            model: control.tabs
            delegate: Item {
                width: tabText.implicitWidth
                height: parent.height

                Text {
                    id: tabText
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: theme ? theme.spacingS : 8
                    text: modelData
                    color: index === control.currentIndex ? control.textColor : control.inactiveTextColor
                    font.family: theme ? theme.fontFamilyMono : "Consolas"
                    font.pixelSize: theme ? theme.fontSizeS : 12
                    font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                    font.letterSpacing: theme ? theme.letterSpacingM : 0.04
                }

                Rectangle {
                    visible: index === control.currentIndex
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottom: parent.bottom
                    width: tabText.implicitWidth + (theme ? theme.spacingS : 8)
                    height: 2
                    color: control.activeColor
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        control.currentIndex = index
                        control.tabChanged(index)
                    }
                }
            }
        }
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 1
        color: theme ? theme.border : "#1E293B"
    }
}
