import QtQuick 2.15
import "../theme"

Item {
    id: control
    
    property var theme
    property real value: 0 // 0 to 100
    property color gaugeColor: theme.primary
    
    implicitWidth: 200
    implicitHeight: 120
    
    Canvas {
        id: canvas
        anchors.fill: parent
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            
            var centerX = width / 2
            var centerY = height - 20
            var radius = Math.min(width, height) - 30
            
            // Draw background arc
            ctx.strokeStyle = theme.border
            ctx.lineWidth = 10
            ctx.beginPath()
            ctx.arc(centerX, centerY, radius, Math.PI, 0)
            ctx.stroke()
            
            // Draw value arc
            var startAngle = Math.PI
            var endAngle = Math.PI + (control.value / 100) * Math.PI
            
            ctx.strokeStyle = control.gaugeColor
            ctx.lineWidth = 10
            ctx.beginPath()
            ctx.arc(centerX, centerY, radius, startAngle, endAngle)
            ctx.stroke()
            
            // Draw value text
            ctx.fillStyle = theme.textPrimary
            ctx.font = "bold 24px Segoe UI"
            ctx.textAlign = "center"
            ctx.fillText(Math.round(control.value) + "%", centerX, centerY - 20)
        }
    }
}
