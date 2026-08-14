import QtQuick 2.15
import "../theme"

Item {
    id: control

    property var theme
    property real value: 0     // current value, in the same unit as maxValue
    property real maxValue: 100
    property string unit: "%"  // suffix shown after the rounded value
    property color gaugeColor: theme ? theme.primary : "#2563EB"

    implicitWidth: 200
    implicitHeight: 120

    readonly property real _ratio: maxValue > 0 ? Math.max(0, Math.min(1, control.value / control.maxValue)) : 0

    onValueChanged: canvas.requestPaint()
    onMaxValueChanged: canvas.requestPaint()
    onGaugeColorChanged: canvas.requestPaint()

    Canvas {
        id: canvas
        anchors.fill: parent
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()

        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)

            var centerX = width / 2
            var centerY = height - 20
            var radius = Math.min(width, height) - 30

            // Draw background arc
            ctx.strokeStyle = control.theme ? control.theme.border : "#1E293B"
            ctx.lineWidth = 10
            ctx.beginPath()
            ctx.arc(centerX, centerY, radius, Math.PI, 0)
            ctx.stroke()

            // Draw value arc
            var startAngle = Math.PI
            var endAngle = Math.PI + control._ratio * Math.PI

            ctx.strokeStyle = control.gaugeColor
            ctx.lineWidth = 10
            ctx.beginPath()
            ctx.arc(centerX, centerY, radius, startAngle, endAngle)
            ctx.stroke()

            // Draw value text
            ctx.fillStyle = control.theme ? control.theme.textPrimary : "#E5E7EB"
            ctx.font = "bold 24px " + (control.theme ? control.theme.fontFamily : "Segoe UI")
            ctx.textAlign = "center"
            ctx.fillText(Math.round(control.value) + control.unit, centerX, centerY - 20)
        }
    }
}
