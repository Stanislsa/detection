import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"
import "../components"

Rectangle {
    id: control
    
    property var theme
    property bool playing: false
    property bool muted: false
    property real volume: 1.0
    property real position: 0
    property real duration: 100
    
    signal playClicked()
    signal pauseClicked()
    signal muteClicked()
    signal volumeChanged(real volume)
    signal seekRequested(real position)
    
    implicitHeight: theme ? theme.videoControlsHeight : 50
    color: theme ? theme.surface : "#2d2d2d"
    opacity: 0.8
    
    Row {
        anchors.fill: parent
        anchors.leftMargin: theme ? theme.spacingM : 16
        anchors.rightMargin: theme ? theme.spacingM : 16
        spacing: theme ? theme.spacingM : 16
        
        // Play/Pause button
        AppIconButton {
            anchors.verticalCenter: parent.verticalCenter
            icon: control.playing ? "⏸️" : "▶️"
            theme: control.theme
            onClicked: {
                if (control.playing) {
                    control.pauseClicked()
                } else {
                    control.playClicked()
                }
            }
        }
        
        // Progress bar
        Slider {
            id: progressBar
            anchors.verticalCenter: parent.verticalCenter
            width: parent.width - playButton.width - muteButton.width - volumeSlider.width - parent.spacing * 4
            from: 0
            to: control.duration
            value: control.position
            
            onMoved: {
                control.seekRequested(value)
            }
        }
        
        // Mute button
        AppIconButton {
            id: muteButton
            anchors.verticalCenter: parent.verticalCenter
            icon: control.muted ? "🔇" : "🔊"
            theme: control.theme
            onClicked: control.muteClicked()
        }
        
        // Volume slider
        Slider {
            id: volumeSlider
            anchors.verticalCenter: parent.verticalCenter
            width: theme ? theme.columnWidthS / 2 : 80
            from: 0
            to: 1
            value: control.volume
            
            onMoved: {
                control.volumeChanged(value)
            }
        }
    }
}
