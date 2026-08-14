import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"
import "../components"

Rectangle {
    id: control

    property var theme
    property string title: "Event"
    property string type: "detection" // detection, alert, system, personnel, vehicle, access, hardware, ai, analytics
    property string description: ""
    property string timestamp: ""
    property string camera: ""
    property string cameraId: ""
    property real confidence: 0         // 0..1
    property string thumbnail: ""      // url to a still frame
    property string node: ""
    property var actions: []            // optional [{label, signal?}]

    signal actionTriggered(string action)

    implicitWidth: 380
    implicitHeight: 96
    color: control.theme.surface
    border.color: control.theme.border
    border.width: 1
    radius: control.theme ? control.theme.radiusM : 4

    property color typeColor: {
        switch(control.type) {
            case "detection": return control.theme.primary
            case "alert":     return control.theme.critical
            case "warning":   return control.theme.warning
            case "system":    return control.theme.warning
            case "personnel": return control.theme.info
            case "vehicle":   return control.theme.success
            case "access":    return control.theme.critical
            case "hardware":  return control.theme.warning
            case "ai":
            case "analytics": return control.theme.primary
        }
        return control.theme.info
    }

    Row {
        anchors.fill: parent
        anchors.margins: control.theme.spacingM
        spacing: control.theme.spacingM

        // Type indicator
        Rectangle {
            width: 40
            height: 40
            color: control.typeColor
            radius: control.theme.radiusM
            Text {
                anchors.centerIn: parent
                text: {
                    switch(control.type) {
                        case "detection": return "⌖"
                        case "alert":     return "⚠"
                        case "system":    return "⚙"
                        case "personnel": return "☺"
                        case "vehicle":   return "▶"
                        case "access":    return "⚿"
                        case "hardware":  return "▤"
                        case "ai":
                        case "analytics": return "⚛"
                    }
                    return "•"
                }
                font.pixelSize: control.theme.fontSizeXL
                color: "#FFFFFF"
            }
        }

        Column {
            width: parent.width - 40 - 80 - control.theme.spacingM * 2
            spacing: control.theme.spacingXS

            Text {
                text: control.title
                font.family: control.theme.fontFamily
                font.pixelSize: control.theme.fontSizeM
                font.weight: control.theme.weightSemiBold
                color: control.theme.textPrimary
            }

            Text {
                text: control.description
                font.family: control.theme.fontFamily
                font.pixelSize: control.theme.fontSizeS
                color: control.theme.textSecondary
                width: parent.width
                wrapMode: Text.WordWrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }

            Row {
                spacing: control.theme.spacingS

                Text {
                    text: control.camera
                    font.pixelSize: control.theme.fontSizeXS
                    color: control.theme.textMuted
                }
                Text {
                    text: "·"
                    font.pixelSize: control.theme.fontSizeXS
                    color: control.theme.textMuted
                }
                Text {
                    text: control.node
                    font.family: control.theme.fontFamilyMono
                    font.pixelSize: control.theme.fontSizeXS
                    color: control.theme.textMuted
                }
                Text {
                    text: "·"
                    font.pixelSize: control.theme.fontSizeXS
                    color: control.theme.textMuted
                }
                Text {
                    text: control.timestamp
                    font.family: control.theme.fontFamilyMono
                    font.pixelSize: control.theme.fontSizeXS
                    color: control.theme.textMuted
                }
            }
        }

        Item { width: control.theme.spacingM; height: 1 }

        // Right side: AI score + thumbnail
        Column {
            width: 80
            spacing: control.theme.spacingXS
            anchors.verticalCenter: parent.verticalCenter

            Text {
                width: parent.width
                text: "AI: " + (control.confidence * 100).toFixed(1) + "%"
                font.family: control.theme.fontFamilyMono
                font.pixelSize: control.theme.fontSizeXS
                font.letterSpacing: control.theme.letterSpacingS
                color: control.confidence > 0.9 ? control.theme.success
                     : control.confidence > 0.7 ? control.theme.info
                     : control.theme.warning
                horizontalAlignment: Text.AlignRight
            }

            Rectangle {
                width: 80
                height: 48
                radius: control.theme.radiusM
                color: control.theme.backgroundAlt
                border.color: control.theme.border
                border.width: 1
                clip: true
                Text {
                    anchors.centerIn: parent
                    visible: control.thumbnail === ""
                    text: "◫"
                    font.pixelSize: control.theme.fontSizeXL
                    color: control.theme.textMuted
                }
                Image {
                    anchors.fill: parent
                    visible: control.thumbnail !== ""
                    source: control.thumbnail
                    fillMode: Image.PreserveAspectCrop
                }
            }
        }
    }
}