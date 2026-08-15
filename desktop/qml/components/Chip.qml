import QtQuick 2.15

/*
 * Chip — small status pill (`ACTIVE` / `DEGRADED` / `STABLE` /
 * `FAILED` / `CONVERGED`). Color follows `status`, variant `solid`
 * or `outline`.
 */
Rectangle {
    id: control
    property var theme
    property string label: "ACTIVE"
    property string status: "active"   // active | degraded | stable | failed | converged | warning | offline
    property string variant: "solid"   // solid | outline

    property color resolvedColor: {
        if (!theme) return "#10B981"
        switch (status) {
            case "active":    return theme.success
            case "degraded":  return theme.warning
            case "warning":   return theme.warning
            case "stable":    return theme.success
            case "converged": return theme.success
            case "failed":    return theme.critical
            case "offline":   return theme.textMuted
        }
        return theme.success
    }

    implicitWidth: layout.implicitWidth + (theme ? theme.spacingS : 8) * 2
    implicitHeight: theme ? theme.inputHeight / 1.6 : 22
    radius: height / 2
    color: variant === "solid" ? resolvedColor : "transparent"
    border.color: resolvedColor
    border.width: 1

    Row {
        id: layout
        anchors.centerIn: parent
        spacing: 4

        Rectangle {
            width: 6
            height: 6
            radius: 3
            color: control.variant === "solid" ? "#0B0E14" : control.resolvedColor
            anchors.verticalCenter: parent.verticalCenter
        }
        Text {
            text: control.label
            font.family: theme ? theme.fontFamilyMono : "Consolas"
            font.pixelSize: theme ? theme.fontSizeXS : 10
            font.letterSpacing: theme ? theme.letterSpacingM : 0.04
            font.weight: theme ? theme.weightSemiBold : Font.DemiBold
            color: control.variant === "solid" ? "#0B0E14" : control.resolvedColor
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}