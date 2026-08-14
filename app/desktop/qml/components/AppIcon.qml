import QtQuick 2.15

/*
 * AppIcon — renders either an SVG from the assets/icons folder, or falls
 * back to a Text glyph (single-character unicode) when no SVG matches.
 *
 * NOTE: PyQt6 does not expose the C++ `QQuickImage::color` property to
 * QML, so colorizing an SVG via `Image.color` is not available. SVGs
 * should therefore ship with their intended color baked in, or be tinted
 * via SVG fill parameters by the caller. Glyphs are tinted via Text.color.
 */
Item {
    id: control

    property string iconName: ""
    property color iconColor: "#ffffff"

    implicitWidth: 16
    implicitHeight: 16

    // Treat empty input as glyph-rendered (renders nothing); single non-ASCII
    // characters are treated as glyphs, anything else as an SVG icon name.
    function _isGlyph(name) {
        if (!name || name.length === 0) return true;
        if (name.length > 1) return false;
        var code = name.charCodeAt(0);
        return !(code >= 0x30 && code <= 0x39)        // 0-9
            && !(code >= 0x41 && code <= 0x5A)        // A-Z
            && !(code >= 0x61 && code <= 0x7A);       // a-z
    }

    function _svgPath(name) {
        if (!name) return "";
        var converted = name.replace(/([A-Z])/g, "-$1").toLowerCase();
        // Qt.resolvedUrl already returns a file:// URL — do NOT prepend
        // another file:/// prefix or you get `file:///file:///...`.
        return Qt.resolvedUrl("../../assets/icons/" + converted + ".svg");
    }

    Image {
        id: svgImage
        anchors.fill: parent
        visible: !textFallback.visible
        fillMode: Image.PreserveAspectFit
        smooth: true
        antialiasing: true
        source: control._isGlyph(control.iconName) ? "" : control._svgPath(control.iconName)
        sourceSize.width: width
        sourceSize.height: height
        asynchronous: true

        onStatusChanged: {
            if (status === Image.Error) textFallback.visible = true;
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
        font.family: control.theme ? control.theme.fontFamily : "Inter"
        Behavior on color { ColorAnimation { duration: 150 } }
    }
}
