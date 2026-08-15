import QtQuick 2.15

SequentialAnimation {
    id: control
    
    property Item target
    
    ParallelAnimation {
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
            property: "scale"
            from: 0.8
            to: 1
            duration: 300
            easing.type: Easing.InOutQuad
        }
    }
}
