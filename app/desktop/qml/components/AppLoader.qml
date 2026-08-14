import QtQuick 2.15
import "../theme"

Item {
    id: control
    
    property var theme
    property bool loading: false
    
    implicitWidth: 48
    implicitHeight: 48
    
    Rectangle {
        anchors.centerIn: parent
        width: 40
        height: 40
        color: "transparent"
        border.color: theme.primary
        border.width: 3
        radius: width / 2
        
        RotationAnimation on rotation {
            from: 0
            to: 360
            duration: 1000
            loops: Animation.Infinite
            running: control.loading
        }
    }
    
    opacity: control.loading ? 1 : 0
    
    Behavior on opacity {
        NumberAnimation { duration: 150 }
    }
}
