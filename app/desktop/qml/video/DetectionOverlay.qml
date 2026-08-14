import QtQuick 2.15
import "../theme"

Item {
    id: control
    
    property var theme
    property string cameraId: ""
    property var detections: [] // Array of detection objects
    
    implicitWidth: parent.width
    implicitHeight: parent.height
    
    // Connexion au VideoPipeline pour recevoir les détections
    Connections {
        target: VideoPipeline
        function onDetectionsReady(camId, detections) {
            if (camId === control.cameraId) {
                control.detections = detections
            }
        }
    }
    
    Repeater {
        model: control.detections
        
        BoundingBox {
            x: modelData.bbox ? modelData.bbox[0] : (modelData.x * parent.width)
            y: modelData.bbox ? modelData.bbox[1] : (modelData.y * parent.height)
            width: modelData.bbox ? modelData.bbox[2] : (modelData.width * parent.width)
            height: modelData.bbox ? modelData.bbox[3] : (modelData.height * parent.height)
            label: modelData.label || ""
            confidence: modelData.confidence || 0
            color: {
                if (modelData.type === "person") return (theme ? theme.success : "#107c10")
                if (modelData.type === "vehicle") return (theme ? theme.warning : "#ff8c00")
                return (theme ? theme.primary : "#0078d4")
            }
            theme: control.theme
        }
    }
}
