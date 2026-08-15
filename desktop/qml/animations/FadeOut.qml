import QtQuick 2.15

SequentialAnimation {
    id: control
    
    property Item target
    
    NumberAnimation {
        target: control.target
        property: "opacity"
        from: 1
        to: 0
        duration: 300
        easing.type: Easing.InOutQuad
    }
}
