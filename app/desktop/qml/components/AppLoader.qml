import QtQuick 2.15
import "../theme"

Item {
    id: control

    property var theme
    property bool loading: false
    property string label: ""

    implicitWidth: 48
    implicitHeight: 48

    // Outer ring
    Rectangle {
        id: ring
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.85
        height: width
        color: "transparent"
        border.color: theme ? theme.primary : "#2563EB"
        border.width: 3
        radius: width / 2
        opacity: control.loading ? 1 : 0

        // Gradient arc simulation via rotation
        Rectangle {
            width: parent.width
            height: parent.height
            radius: width / 2
            color: "transparent"
            border.color: theme ? theme.primaryHover : "#3B82F6"
            border.width: 3
            // Clip to arc by rotating a mask-like effect is limited in pure QML;
            // we use a simple continuous spin.
        }

        RotationAnimation on rotation {
            from: 0
            to: 360
            duration: 900
            loops: Animation.Infinite
            running: control.loading
        }

        Behavior on opacity {
            NumberAnimation { duration: 180 }
        }
    }

    // Inner pulse
    Rectangle {
        anchors.centerIn: parent
        width: ring.width * 0.35
        height: width
        radius: width / 2
        color: theme ? theme.primary : "#2563EB"
        opacity: control.loading ? 0.35 : 0

        SequentialAnimation on scale {
            running: control.loading
            loops: Animation.Infinite
            NumberAnimation { to: 1.25; duration: 500; easing.type: Easing.InOutQuad }
            NumberAnimation { to: 0.85; duration: 500; easing.type: Easing.InOutQuad }
        }

        Behavior on opacity {
            NumberAnimation { duration: 180 }
        }
    }

    // Optional label
    Text {
        anchors.top: ring.bottom
        anchors.topMargin: 8
        anchors.horizontalCenter: parent.horizontalCenter
        text: control.label
        visible: control.label !== "" && control.loading
        font.family: theme ? theme.fontFamily : "sans-serif"
        font.pixelSize: theme ? theme.fontSizeS : 12
        color: theme ? theme.textSecondary : "#94A3B8"
    }
}
