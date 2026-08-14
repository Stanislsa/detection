import QtQuick 2.15
import "../theme"

Item {
    id: control
    
    property var theme
    property var data: [] // Array of {label, value} values
    property color barColor: theme ? theme.primary : "#2563EB"
    
    implicitWidth: 300
    implicitHeight: 200
    
    Canvas {
        id: canvas
        anchors.fill: parent
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            
            if (control.data.length === 0) return
            
            // Draw axes
            ctx.strokeStyle = theme ? theme.border : "#1E293B"
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(30, 10)
            ctx.lineTo(30, height - 20)
            ctx.lineTo(width - 10, height - 20)
            ctx.stroke()
            
            var maxValue = Math.max(...control.data.map(d => d.value))
            var barWidth = (width - 40) / control.data.length - 10
            
            control.data.forEach((item, index) => {
                var x = 35 + index * (barWidth + 10)
                var barHeight = (item.value / maxValue) * (height - 30)
                var y = (height - 20) - barHeight
                
                ctx.fillStyle = control.barColor
                ctx.fillRect(x, y, barWidth, barHeight)
            })
        }
    }
}
