import QtQuick 2.15

/*
 * MonospaceValue — Text element pinned to theme.fontFamilyMono.
 * Use for IDs, IPs, file paths, metric values, hex strings.
 */
Text {
    id: control
    property var theme
    property string prefix: ""
    property string suffix: ""

    font.family: theme ? theme.fontFamilyMono : "Consolas"
    font.pixelSize: theme ? theme.fontSizeS : 12
    font.weight: theme ? theme.weightRegular : Font.Normal
    color: theme ? theme.textPrimary : "#E5E7EB"
    elide: Text.ElideRight
    text: prefix + "·" + suffix  // overridable by callers
}