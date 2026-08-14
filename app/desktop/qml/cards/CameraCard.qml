import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

Rectangle {
    id: control
    property var theme
    property string cameraName: "Camera"
    property string cameraId: "CAM-0000"
    property string location: "Zone"
    property bool isOnline: true
    property bool hasAlert: false
    property string resolution: "1080p"     // 4K | 1080p | 720p
    property bool isRecording: false
    property string lastActivity: "—"
    property string ipAddress: "10.0.0.0"

    signal clicked()
    signal settingsClicked()

    implicitWidth: 300
    implicitHeight: 200

    color: theme ? theme.surface : "#151C28"
    radius: theme ? theme.radiusM : 4
    border.color: hasAlert ? (theme ? theme.critical : "#EF4444") : (theme ? theme.border : "#1E293B")
    border.width: 1

    Column {
        anchors.fill: parent
        anchors.margins: theme ? theme.spacingM : 16
        spacing: theme ? theme.spacingS : 8

        RowLayout {
            width: parent.width
            spacing: theme ? theme.spacingS : 8

            Text {
                text: "▣"
                font.pixelSize: theme.fontSizeXL
                color: theme.textPrimary
                Layout.alignment: Qt.AlignVCenter
            }

            Column {
                spacing: theme.spacingXS
                Layout.alignment: Qt.AlignVCenter

                Text {
                    text: control.cameraName
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeM
                    font.weight: theme.weightSemiBold
                    font.letterSpacing: theme.letterSpacingS
                    color: theme.textPrimary
                }
                Text {
                    text: control.cameraId + " · " + control.location
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeXS
                    color: theme.textMuted
                }
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                Layout.alignment: Qt.AlignVCenter
                visible: control.isRecording
                color: theme.critical
                radius: theme.radiusS
                width: recLabel.implicitWidth + theme.spacingS * 2
                height: recLabel.implicitHeight + theme.spacingXS * 2
                Text {
                    id: recLabel
                    anchors.centerIn: parent
                    text: "● REC"
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeXS
                    font.weight: theme.weightSemiBold
                    color: "#FFFFFF"
                    font.letterSpacing: theme.letterSpacingM
                }
            }

            AppBadge {
                Layout.alignment: Qt.AlignVCenter
                theme: control.theme
                text: control.resolution
                fillColor: theme.primary
                variant: "outline"
            }

            Rectangle {
                Layout.alignment: Qt.AlignVCenter
                width: 8
                height: 8
                radius: 4
                color: control.isOnline ? theme.success : theme.textMuted
            }
        }

        // Stub video region (gray placeholder)
        Rectangle {
            width: parent.width
            height: 90
            radius: theme.radiusM
            color: theme.backgroundAlt
            border.color: theme.border
            border.width: 1
            Text {
                anchors.centerIn: parent
                text: control.isOnline ? "LIVE PREVIEW" : "◌ SIGNAL LOST"
                font.family: theme.fontFamilyMono
                font.pixelSize: theme.fontSizeS
                font.letterSpacing: theme.letterSpacingL
                color: control.isOnline ? theme.textMuted : theme.critical
            }
            Rectangle {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: 4
                color: control.hasAlert ? theme.critical : "transparent"
            }
        }

        Row {
            width: parent.width
            spacing: theme.spacingS

            Column {
                spacing: theme.spacingXS
                Text {
                    text: "IP"
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeXS
                    font.letterSpacing: theme.letterSpacingM
                    color: theme.textSecondary
                }
                Text {
                    text: control.ipAddress
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeS
                    color: theme.textPrimary
                }
            }
            Item { width: theme.spacingM; height: 1 }
            Column {
                spacing: theme.spacingXS
                Text {
                    text: "LAST"
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeXS
                    font.letterSpacing: theme.letterSpacingM
                    color: theme.textSecondary
                }
                Text {
                    text: control.lastActivity
                    font.family: theme.fontFamilyMono
                    font.pixelSize: theme.fontSizeS
                    color: theme.textPrimary
                }
            }
            Item { Layout.fillWidth: true }
            AppButton {
                theme: control.theme
                text: "View"
                variant: "primary"
                onClicked: control.clicked()
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: control.clicked()
        hoverEnabled: true
    }
}