import QtQuick 2.15

ParallelAnimation {
    id: control
    
    property Item target
    property string direction: "left" // left, right, up, down
    
    NumberAnimation {
        target: control.target
        property: "opacity"
        from: 0
        to: 1
        duration: 300
        easing.type: Easing.InOutQuad
    }
    
    NumberAnimation {
        target: control.target
        property: {
            switch(control.direction) {
                case "left": return "x"
                case "right": return "x"
                case "up": return "y"
                case "down": return "y"
                default: return "x"
            }
        }
        from: {
            switch(control.direction) {
                case "left": return -50
                case "right": return 50
                case "up": return -50
                case "down": return 50
                default: return -50
            }
        }
        to: 0
        duration: 300
        easing.type: Easing.InOutQuad
    }
}
