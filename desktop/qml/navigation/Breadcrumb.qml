import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"
import "../components"

Row {
    id: control

    property var theme
    property var items: []   // list of strings

    spacing: theme.spacingXS

    Repeater {
        model: control.items

        Row {
            spacing: theme.spacingXS

            BreadcrumbItem {
                theme: control.theme
                label: modelData
                isLast: index === control.items.length - 1
                onClicked: control.itemClicked(index)
            }

            Text {
                visible: index < control.items.length - 1
                anchors.verticalCenter: parent.verticalCenter
                text: "›"
                font.pixelSize: theme.fontSizeM
                color: theme.textDisabled
            }
        }
    }

    signal itemClicked(int index)
}