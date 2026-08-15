import QtQuick 2.15

/*
 * AppIcon — renders SVG from assets/icons (via AppPaths) or falls back
 * to a text glyph. Prefer iconName as camelCase matching Icons.qml keys
 * or the SVG filename without extension (e.g. "layout-dashboard", "bell").
 */
Item {
    id: control

    property string iconName: ""
    property color iconColor: "#ffffff"
    property var theme: null

    implicitWidth: 16
    implicitHeight: 16

    function _isGlyph(name) {
        if (!name || name.length === 0) return true
        if (name.length > 1) return false
        var code = name.charCodeAt(0)
        return !(code >= 0x30 && code <= 0x39)
            && !(code >= 0x41 && code <= 0x5A)
            && !(code >= 0x61 && code <= 0x7A)
    }

    function _toKebab(name) {
        if (!name) return ""
        // already kebab?
        if (name.indexOf("-") >= 0) return name.toLowerCase()
        // camelCase → kebab-case
        return name.replace(/([A-Z])/g, "-$1").toLowerCase().replace(/^-/, "")
    }

    function _svgPath(name) {
        if (!name) return ""
        var kebab = _toKebab(name)
        // Prefer AppPaths when available (portable absolute URI)
        if (typeof AppPaths !== "undefined" && AppPaths) {
            var url = AppPaths.iconUrl(kebab)
            if (url && url.length > 0) return url
            // try original name
            url = AppPaths.iconUrl(name)
            if (url && url.length > 0) return url
        }
        // Relative fallback
        return Qt.resolvedUrl("../../assets/icons/" + kebab + ".svg")
    }

    Image {
        id: svgImage
        anchors.fill: parent
        visible: !textFallback.visible
        fillMode: Image.PreserveAspectFit
        smooth: true
        antialiasing: true
        source: control._isGlyph(control.iconName) ? "" : control._svgPath(control.iconName)
        sourceSize.width: Math.max(width * 2, 32)
        sourceSize.height: Math.max(height * 2, 32)
        asynchronous: true
        // Subtle opacity so dark-stroke SVGs remain visible on dark bg
        opacity: 0.92

        onStatusChanged: {
            if (status === Image.Error)
                textFallback.visible = true
        }
    }

    Text {
        id: textFallback
        anchors.fill: parent
        visible: control._isGlyph(control.iconName) || svgImage.status === Image.Error
        text: control.iconName
        color: control.iconColor
        font.pixelSize: Math.min(width, height)
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        Behavior on color { ColorAnimation { duration: 150 } }
    }
}
