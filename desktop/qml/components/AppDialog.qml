import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Effects
import "../theme"
import "."

/*
 * AppDialog — modal dialog with shadow-xl. Replaces raw `Button`
 * footers with `AppButton`.
 */
Popup {
    id: control

    property var theme
    property string title: ""
    property string state: "normal" // normal, loading, success, error, disabled
    property int dialogContentHeight: 200
    // Redirect implicit/default children (declared by callers, e.g.
    // `AddCameraDialog { Column { ... } }`) into `contentContainer`
    // instead of letting them land as direct children of the
    // `contentItem: Column` below (Column forbids anchors on direct
    // children, which broke every dialog subtype that used anchors.fill).
    default property alias content: contentContainer.data

    signal accepted()

    modal: true
    dim: true
    padding: 0

    background: Rectangle {
        color: theme ? theme.surfaceElevated : "#1E293B"
        radius: theme ? theme.radiusM : 4
        border.color: theme ? theme.border : "#1E293B"
        border.width: 1

        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: theme ? theme.shadowColor : "#000000"
            shadowBlur: Math.min(1.0, (theme ? theme.shadowBlur : 24) / 40)
            shadowVerticalOffset: theme ? theme.shadowOffsetY : 8
            shadowHorizontalOffset: 0
            shadowOpacity: theme ? theme.shadowOpacity : 0.4
        }
    }

    contentItem: Column {
        spacing: 0

        Rectangle {
            width: parent.width
            height: theme ? theme.headerHeight : 60
            color: theme ? theme.surface : "#151C28"

            Text {
                anchors.left: parent.left
                anchors.leftMargin: theme ? theme.spacingM : 16
                anchors.verticalCenter: parent.verticalCenter
                text: control.title
                font.family: theme ? theme.fontFamily : "Inter"
                font.pixelSize: theme ? theme.fontSizeL : 14
                font.weight: theme ? theme.weightSemiBold : Font.DemiBold
                color: theme ? theme.textPrimary : "#E5E7EB"
            }

            AppIconButton {
                anchors.right: parent.right
                anchors.rightMargin: theme ? theme.spacingS : 8
                anchors.verticalCenter: parent.verticalCenter
                text: "✕"
                theme: control.theme
                onClicked: control.close()
            }
        }

        Item {
            width: parent.width
            height: control.dialogContentHeight

            Item {
                id: contentContainer
                anchors.fill: parent
                anchors.margins: theme ? theme.spacingM : 16
                enabled: control.state !== "loading" && control.state !== "disabled"
                opacity: control.state === "loading" ? 0.3 : 1
                Behavior on opacity { NumberAnimation { duration: 200 } }
            }

            BusyIndicator {
                anchors.centerIn: parent
                running: control.state === "loading"
                visible: control.state === "loading"
            }
        }

        Rectangle {
            width: parent.width
            height: (theme ? theme.buttonHeight : 40) + (theme ? theme.spacingM : 16) * 2
            color: theme ? theme.surface : "#151C28"

            Row {
                anchors.right: parent.right
                anchors.rightMargin: theme ? theme.spacingM : 16
                anchors.verticalCenter: parent.verticalCenter
                spacing: theme ? theme.spacingS : 8

                AppButton {
                    text: "Cancel"
                    variant: "ghost"
                    theme: control.theme
                    enabled: control.state !== "loading" && control.state !== "disabled"
                    onClicked: control.close()
                }

                AppButton {
                    text: "OK"
                    variant: "primary"
                    theme: control.theme
                    enabled: control.state !== "loading" && control.state !== "disabled"
                    onClicked: control.accepted()
                }
            }
        }
    }
}