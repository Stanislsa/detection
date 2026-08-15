import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/*
 * ResponsivePage — shell scrollable avec marges adaptatives.
 * Usage:
 *   ResponsivePage {
 *     theme: theme
 *     content: ColumnLayout { ... }  // via default property children
 *   }
 */
Flickable {
    id: root
    property var theme
    property int contentBottomPad: 32

    readonly property bool isNarrow: width < 960
    readonly property bool isMobile: width < 720
    readonly property int pageMargin: isMobile ? 10 : (isNarrow ? 14 : (theme ? theme.spacingL : 24))
    readonly property int contentGap: isMobile ? 10 : (isNarrow ? 12 : (theme ? theme.spacingL : 16))
    readonly property int kpiColumns: width >= 1100 ? 4 : (width >= 720 ? 2 : 1)
    readonly property int gridColumns: width >= 1200 ? 3 : (width >= 800 ? 2 : 1)

    default property alias content: body.data

    anchors.fill: parent
    contentWidth: width
    contentHeight: body.implicitHeight + contentBottomPad
    clip: true
    boundsBehavior: Flickable.StopAtBounds
    flickableDirection: Flickable.VerticalFlick
    ScrollBar.vertical: ScrollBar {
        policy: root.contentHeight > root.height ? ScrollBar.AsNeeded : ScrollBar.AlwaysOff
    }

    Column {
        id: body
        width: root.width - root.pageMargin * 2
        x: root.pageMargin
        y: root.pageMargin
        spacing: root.contentGap
    }
}
