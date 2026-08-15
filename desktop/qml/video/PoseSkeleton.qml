import QtQuick 2.15
import "../theme"

Canvas {
    id: control
    
    property var theme
    property var keypoints: [] // Array of {x, y} for body joints
    property color color: theme ? theme.primary : "#0078d4"
    
    implicitWidth: parent.width
    implicitHeight: parent.height
    
    onPaint: {
        var ctx = getContext("2d")
        ctx.clearRect(0, 0, width, height)
        
        if (control.keypoints.length < 2) return
        
        ctx.strokeStyle = control.color
        ctx.lineWidth = 2
        ctx.lineCap = "round"
        
        // Define skeleton connections (COCO format)
        var connections = [
            [0, 1], [0, 2], [1, 3], [2, 4], // Head
            [5, 6], [5, 7], [7, 9], [6, 8], [8, 10], // Arms
            [5, 11], [6, 12], [11, 12], // Torso
            [11, 13], [13, 15], [12, 14], [14, 16] // Legs
        ]
        
        // Draw connections
        connections.forEach(function(conn) {
            var kp1 = control.keypoints[conn[0]]
            var kp2 = control.keypoints[conn[1]]
            
            if (kp1 && kp2 && kp1.confidence > 0.5 && kp2.confidence > 0.5) {
                var x1 = kp1.x * width
                var y1 = kp1.y * height
                var x2 = kp2.x * width
                var y2 = kp2.y * height
                
                ctx.beginPath()
                ctx.moveTo(x1, y1)
                ctx.lineTo(x2, y2)
                ctx.stroke()
            }
        })
        
        // Draw keypoints
        control.keypoints.forEach(function(kp) {
            if (kp && kp.confidence > 0.5) {
                var x = kp.x * width
                var y = kp.y * height
                
                ctx.fillStyle = control.color
                ctx.beginPath()
                ctx.arc(x, y, 4, 0, 2 * Math.PI)
                ctx.fill()
            }
        })
    }
}
