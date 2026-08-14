import QtQuick 2.15

/*
 * PageTransition — fade + directional slide for page swaps.
 *
 * Usage:
 *   enterAnim.target = loader
 *   enterAnim.direction = "forward"   // forward | back | fade
 *   enterAnim.playEnter()
 *
 *   exitAnim.target = loader
 *   exitAnim.direction = "forward"
 *   exitAnim.playExit(function() { ... })
 */
Item {
    id: control

    property Item target: null
    property string direction: "forward"   // forward | back | fade
    property int durationMs: 280
    property real slideDistance: 36

    signal finished()

    // Internal animation
    ParallelAnimation {
        id: anim
        NumberAnimation {
            id: opacityAnim
            target: control.target
            property: "opacity"
            duration: control.durationMs
            easing.type: Easing.OutCubic
        }
        NumberAnimation {
            id: xAnim
            target: control.target
            property: "x"
            duration: control.durationMs
            easing.type: Easing.OutCubic
        }
        NumberAnimation {
            id: scaleAnim
            target: control.target
            property: "scale"
            duration: control.durationMs
            easing.type: Easing.OutCubic
        }
        onFinished: control.finished()
    }

    function playEnter() {
        if (!target) {
            finished()
            return
        }

        // Starting pose
        var startX = 0
        if (direction === "forward") startX = slideDistance
        else if (direction === "back") startX = -slideDistance

        target.x = startX
        target.y = 0
        target.opacity = 0
        target.scale = 0.985

        // End pose
        opacityAnim.to = 1
        xAnim.to = 0
        scaleAnim.to = 1

        anim.start()
    }

    function playExit(callback) {
        if (!target) {
            if (callback) callback()
            finished()
            return
        }

        var endX = 0
        if (direction === "forward") endX = -slideDistance * 0.55
        else if (direction === "back") endX = slideDistance * 0.55

        opacityAnim.to = 0
        xAnim.to = endX
        scaleAnim.to = 0.985

        if (callback) {
            var handler = function() {
                anim.finished.disconnect(handler)
                callback()
            }
            anim.finished.connect(handler)
        }

        anim.start()
    }

    function stop() {
        anim.stop()
    }
}
