import QtQuick 2.15
import "../theme"

Item {
    id: control
    
    property var theme
    property var data: [] // Array of {x, y} values
    property color lineColor: theme ? theme.primary : "#2563EB"
    property real lineWidth: 2
    
    implicitWidth: 300
    implicitHeight: 200
    
    onDataChanged: canvas.requestPaint()
    onLineColorChanged: canvas.requestPaint()
    
    Canvas {
        id: canvas
        anchors.fill: parent
        
        // Explicit repaint-on-resize hooks on the Canvas itself (not just
        // on the outer Item): with two or more nested `anchors.margins`
        // levels above this Canvas, its final width/height settle one
        // layout pass after Canvas's own automatic first paint, and
        // Canvas does not reliably repaint itself afterwards without
        // this. Without it, charts nested a couple of margin'd
        // containers deep (as on the Observability and AI Training
        // pages) rendered permanently blank.
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            
            if (control.data.length < 2) return
            
            // Draw axes
            ctx.strokeStyle = theme ? theme.border : "#1E293B"
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
