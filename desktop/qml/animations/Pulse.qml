import QtQuick 2.15

SequentialAnimation {
    id: control
    
    property Item target
    property bool running: false
    property loops: Animation.Infinite
    
    loops: control.loops
    
    NumberAnimation {
        target: control.target
        property: "scale"
        from: 1
        to: 1.05
        duration: 150
        easing.type: Easing.InOutQuad
    }
    
    NumberAnimation {
        target: control.target
        property: "scale"
        from: 1.05
        to: 1
        duration: 150
        easing.type: Easing.InOutQuad
    }
}
