import QtQuick 2.15

/*
 * KpiDeltaBadge — small pill showing "+5%" / "-12%" with up/down
 * arrow. Color follows the magnitude: positive by default, but you
 * can pass `deltaColor: "critical"` to invert semantics for threats.
 */
Rectangle {
    id: control

    property var theme
    property string delta: "0%"
    property bool positive: true
    // Renamed from `color` to avoid shadowing Rectangle.color and
    // the multi-set error; callers should now use `deltaColor`.
    property string deltaColor: "success"   // success | warning | critical | info

    property color resolvedColor: {
        if (!theme) return "#10B981"
        switch (deltaColor) {
            case "success":  return theme.success
            case "warning":  return theme.warning
            case "critical": return theme.critical
            case "info":     return theme.info
        }
        return theme.success
    }

    implicitWidth: layout.implicitWidth + theme.spacingXS * 2
    implicitHeight: layout.implicitHeight + theme.spacingXS
    radius: theme ? theme.radiusS : 2
    color: "transparent"
    border.color: resolvedColor
    border.width: 1

    Row {
        id: layout
        anchors.centerIn: parent
        spacing: 4

        Text {
            text: positive ? "▲" : "▼"
            font.pixelSize: theme ? theme.fontSizeXS : 10
            color: control.resolvedColor
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
            text: control.delta
            font.family: theme ? theme.fontFamilyMono : "Consolas"
            font.pixelSize: theme ? theme.fontSizeXS : 10
            font.weight: theme ? theme.weightSemiBold : Font.DemiBold
            color: control.resolvedColor
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}