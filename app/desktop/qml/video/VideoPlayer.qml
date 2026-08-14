import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"

Item {
    id: control
    
    property var theme
    property string cameraId: ""
    property bool playing: false
    property bool muted: false
    property real volume: 1.0
    property bool showOverlay: true
    
    signal play()
    signal pause()
    signal seek(real position)
    signal volumeChanged(real volume)
    
    implicitWidth: theme ? theme.videoWidth : 640
    implicitHeight: theme ? theme.videoHeight : 480
    
    // Connexion au VideoPipeline
    Connections {
        target: VideoPipeline
        function onFrameReady(camId, frame) {
            if (camId === control.cameraId) {
                // Le provider d'images gère automatiquement l'affichage
                videoImage.source = "image://video/" + camId
            }
        }
    }
    
    Rectangle {
        id: videoContainer
        anchors.fill: parent
        color: theme ? theme.surfaceElevated : "#3d3d3d"
        radius: theme ? theme.radiusM : 8
        
        // Image pour afficher les frames du pipeline via le provider
        Image {
            id: videoImage
            anchors.fill: parent
            fillMode: Image.PreserveAspectFit
            source: control.cameraId !== "" ? "image://video/" + control.cameraId : ""
            visible: control.cameraId !== ""
            cache: false
            
            Behavior on opacity {
                NumberAnimation { duration: 200 }
            }
        }
        
        // Placeholder quand pas de caméra
        Rectangle {
            anchors.fill: parent
            color: theme ? theme.surfaceElevated : "#3d3d3d"
            visible: control.cameraId === ""
            
            Text {
                anchors.centerIn: parent
                text: "📷 No Camera Selected"
                font.pixelSize: theme ? theme.fontSizeXXL : 32
                color: theme ? theme.textDisabled : "#606060"
            }
        }
        
        // Detection overlay
        DetectionOverlay {
            id: detectionOverlay
            anchors.fill: parent
            theme: control.theme
            visible: control.showOverlay
            cameraId: control.cameraId
        }
        
        // Video controls
        VideoControls {
            id: videoControls
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            theme: control.theme
            playing: control.playing
            muted: control.muted
            volume: control.volume
            
            onPlayClicked: {
                control.playing = true
                if (control.cameraId !== "") {
                    VideoPipeline.start_camera(control.cameraId)
                }
            }
            
            onPauseClicked: {
                control.playing = false
                if (control.cameraId !== "") {
                    VideoPipeline.stop_camera(control.cameraId)
                }
            }
            
            onMuteClicked: {
                control.muted = !control.muted
            }
            
            onVolumeChanged: {
                control.volume = volume
            }
            
            onSeekRequested: {
                // Seek not implemented for live stream
            }
        }
    }
    
    function play() {
        control.playing = true
        if (control.cameraId !== "") {
            VideoPipeline.start_camera(control.cameraId)
        }
    }
    
    function pause() {
        control.playing = false
        if (control.cameraId !== "") {
            VideoPipeline.stop_camera(control.cameraId)
        }
    }
    
    function stop() {
        control.playing = false
        if (control.cameraId !== "") {
            VideoPipeline.stop_camera(control.cameraId)
        }
    }
    
    Component.onDestruction: {
        if (control.cameraId !== "") {
            VideoPipeline.stop_camera(control.cameraId)
        }
    }
}
