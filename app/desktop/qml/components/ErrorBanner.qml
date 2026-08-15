import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/*
 * Bandeau d'erreur global (haut de zone contenu).
 */
Rectangle {
    id: control

    property var theme
    property string level: "error"   // warning | error | critical
    property string message: ""
    property bool active: false

    signal dismissRequested()
    signal detailsRequested()

    visible: active && message.length > 0
    height: visible ? Math.max(40, msg.implicitHeight + 20) : 0
    clip: true

    color: {
        if (level === "critical") return "#7F1D1D"
        if (level === "warning") return "#78350F"
        if (level === "info") return "#1E3A5F"
        return "#7F1D1D"
    }
    border.color: {
        if (level === "critical") return "#EF4444"
        if (level === "warning") return "#F59E0B"
        if (level === "info") return "#3B82F6"
        return "#EF4444"
    }
    border.width: 1

    Behavior on height { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
    Behavior on opacity { NumberAnimation { duration: 160 } }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 8
        spacing: 10

        Text {
            text: level === "warning" ? "⚠" : (level === "info" ? "ℹ" : "✕")
            font.pixelSize: 14
            color: "#FFFFFF"
            Layout.alignment: Qt.AlignVCenter
        }

        Text {
            id: msg
            Layout.fillWidth: true
            text: control.message
            font.pixelSize: 12
            color: "#FEE2E2"
            wrapMode: Text.WordWrap
            maximumLineCount: 3
            elide: Text.ElideRight
        }

        Text {
            text: (typeof I18n !== "undefined" && I18n) ? I18n.t("error.dismiss") : "Dismiss"
            font.pixelSize: 11
            font.weight: Font.DemiBold
            color: "#FFFFFF"
            MouseArea {
                anchors.fill: parent
                anchors.margins: -6
                cursorShape: Qt.PointingHandCursor
                onClicked: control.dismissRequested()
            }
        }
    }
}
