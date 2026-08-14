import QtQuick 2.15
import "../theme"

Item {
    id: control
    
    property var theme
    property var data: [] // Array of {x, y} values
    property color lineColor: theme.primary
    property real lineWidth: 2
    
    implicitWidth: 300
    implicitHeight: 200
    
    Canvas {
        id: canvas
        anchors.fill: parent
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            
            if (control.data.length < 2) return
            
            // Draw axes
            ctx.strokeStyle = theme.border
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(30, 10)
            ctx.lineTo(30, height - 20)
            ctx.lineTo(width - 10, height - 20)
            ctx.stroke()
            
            // Draw line
            ctx.strokeStyle = control.lineColor
            ctx.lineWidth = control.lineWidth
            ctx.beginPath()
            
            var minX = Math.min(...control.data.map(d => d.x))
            var maxX = Math.max(...control.data.map(d => d.x))
            var minY = Math.min(...control.data.map(d => d.y))
            var maxY = Math.max(...control.data.map(d => d.y))
            
            var xScale = (width - 40) / (maxX - minX || 1)
            var yScale = (height - 30) / (maxY - minY || 1)
            
            control.data.forEach((point, index) => {
                var x = 30 + (point.x - minX) * xScale
                var y = (height - 20) - (point.y - minY) * yScale
                
                if (index === 0) {
                    ctx.moveTo(x, y)
                } else {
                    ctx.lineTo(x, y)
                }
            })
            
            ctx.stroke()
        }
    }
}
