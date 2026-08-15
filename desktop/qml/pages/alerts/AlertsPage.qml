import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

Item {
    id: control
    property var theme
    property var alertController

    property string severityFilter: "ALL"
    property string searchText: ""
    property int selectedIndex: 0
    readonly property bool narrow: width < 960

    property var liveAlerts: []
    readonly property var fallbackAlerts: [
        {
            "id": "ALRT-89214", "title": "Unauthorized Access", "priority": "CRITICAL",
            "status": "OPEN", "location": "Server Room A", "camera_name": "CAM-SR-04",
            "timestamp": "2024-05-20T14:22:01", "description": "Unauthorized access detected",
            "confidence": 98.4
        },
        {
            "id": "ALRT-89210", "title": "Unidentified Person", "priority": "HIGH",
            "status": "ACKNOWLEDGED", "location": "Main Office", "camera_name": "CAM-MO-01",
            "timestamp": "2024-05-20T14:15:44", "description": "Unidentified individual",
            "confidence": 91.2
        }
    ]

    function buildAlerts() {
        var src = (liveAlerts && liveAlerts.length) ? liveAlerts : fallbackAlerts
        var out = []
        for (var i = 0; i < src.length; i++) {
            var a = src[i]
            var st = a.status || "OPEN"
            var statusLabel = "Pending"
            if (st === "ACKNOWLEDGED") statusLabel = "Acknowledged"
            else if (st === "RESOLVED") statusLabel = "Resolved"
            else if (st === "INVESTIGATING") statusLabel = "Investigating"
            out.push({
                "id": a.id || ("A-" + i),
                "ts": a.timestamp || "",
                "sev": a.priority || "MEDIUM",
                "detail": a.title || "",
                "status": statusLabel,
                "conf": a.confidence || 90,
                "threat": (a.priority === "CRITICAL") ? "SEVERE" : (a.priority || "MEDIUM"),
                "loc": a.location || "",
                "cam": a.camera_name || a.camera_id || ""
            })
        }
        return out
    }

    property var alerts: buildAlerts()

    function reloadFromController() {
        if (alertController && alertController.alerts) {
            liveAlerts = alertController.alerts
            alerts = buildAlerts()
        }
    }

    function sevColor(s) {
        if (s === "CRITICAL") return theme ? theme.critical : "#EF4444"
        if (s === "HIGH") return theme ? theme.warning : "#F59E0B"
        if (s === "MEDIUM") return theme ? theme.info : "#06B6D4"
        return theme ? theme.textMuted : "#64748B"
    }

    // Prefer global context property (set before Loader completes wiring)
    Connections {
        target: typeof AlertController !== "undefined" ? AlertController : null
        enabled: typeof AlertController !== "undefined" && AlertController !== null
        function onAlertsChanged() {
            control.reloadFromController()
        }
        function onAlertReceived(payload) {
            control.reloadFromController()
        }
        function onRealtimeStateChanged() {
            control.reloadFromController()
        }
        function onStatsChanged() {
            control.reloadFromController()
        }
    }

    Connections {
        // Fallback if page property is set later via wirePage
        target: control.alertController
        enabled: control.alertController !== undefined
                 && control.alertController !== null
                 && (typeof AlertController === "undefined" || control.alertController !== AlertController)
        ignoreUnknownSignals: true
        function onAlertsChanged() { control.reloadFromController() }
        function onAlertReceived(payload) { control.reloadFromController() }
    }

    Component.onCompleted: {
        if (typeof AlertController !== "undefined" && AlertController)
            control.alertController = AlertController
        control.reloadFromController()
    }

    Flickable {
        id: rootFlick
        anchors.fill: parent
        anchors.margins: control.narrow ? 12 : 24
        contentWidth: width
        contentHeight: Math.max(height, colRoot.implicitHeight)
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar {
            policy: rootFlick.contentHeight > rootFlick.height ? ScrollBar.AsNeeded : ScrollBar.AlwaysOff
        }

        ColumnLayout {
            id: colRoot
            width: rootFlick.width
            spacing: 16

            // Title
            RowLayout {
                Layout.fillWidth: true
                Column {
                    spacing: 4
                    Text {
                        text: (typeof I18n !== "undefined" && I18n) ? I18n.t("alerts.title") : "Incidents & Alerts"
                        font.pixelSize: theme ? theme.fontSizeXXL : 20
                        font.weight: Font.Bold
                        color: theme ? theme.textPrimary : "#E5E7EB"
                    }
                    Text {
                        text: (typeof I18n !== "undefined" && I18n) ? I18n.t("alerts.subtitle") : "SOC monitoring"
                        font.pixelSize: 12
                        color: theme ? theme.textSecondary : "#94A3B8"
                    }
                }
                Item { Layout.fillWidth: true }
                AppButton { text: (typeof I18n !== "undefined" && I18n) ? I18n.t("alerts.export") : "Export CSV"; variant: "secondary"; theme: control.theme }
                AppButton { text: (typeof I18n !== "undefined" && I18n) ? I18n.t("alerts.bulk_resolve") : "Bulk Resolve"; variant: "primary"; theme: control.theme }
            }

            // Filters
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                Text {
                    text: "SEVERITY:"
                    font.family: theme ? theme.fontFamilyMono : "monospace"
                    font.pixelSize: 11
                    color: theme ? theme.textMuted : "#64748B"
                }
                Repeater {
                    model: ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
                    Rectangle {
                        width: lab.implicitWidth + 20
                        height: 28
                        radius: 4
                        color: control.severityFilter === modelData
                               ? (theme ? theme.primary : "#2563EB")
                               : (theme ? theme.surface : "#151C28")
                        border.color: theme ? theme.border : "#1E293B"
                        border.width: 1
                        Text {
                            id: lab
                            anchors.centerIn: parent
                            text: modelData
                            font.pixelSize: 11
                            font.weight: Font.DemiBold
                            color: control.severityFilter === modelData
                                   ? "#FFFFFF"
                                   : (theme ? theme.textSecondary : "#94A3B8")
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                control.severityFilter = modelData
                                if (control.alertController)
                                    control.alertController.setFilterPriority(modelData)
                            }
                        }
                    }
                }
                Item { Layout.fillWidth: true }
                AppInput {
                    Layout.preferredWidth: control.narrow ? 160 : 240
                    Layout.preferredHeight: 32
                    theme: control.theme
                    placeholderText: (typeof I18n !== "undefined" && I18n) ? I18n.t("alerts.search") : "Search…"
                    leadingIcon: "search"
                    onTextChanged: {
                        control.searchText = text
                        if (control.alertController)
                            control.alertController.setSearch(text)
                    }
                }
            }

            // Split table + detail
            GridLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: control.narrow ? 880 : 440
                Layout.minimumHeight: 300
                columns: control.narrow ? 1 : 2
                rowSpacing: 12
                columnSpacing: 12

                // Table
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredWidth: 1
                    Layout.minimumHeight: 280
                    radius: 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"
                    border.width: 1
                    clip: true

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 0
                        spacing: 0

                        Rectangle {
                            Layout.fillWidth: true
                            height: 36
                            color: theme ? theme.backgroundAlt : "#0F172A"
                            Row {
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                spacing: 0
                                Text {
                                    width: 90; anchors.verticalCenter: parent.verticalCenter
                                    text: "ID"; font.pixelSize: 10
                                    font.family: theme ? theme.fontFamilyMono : "monospace"
                                    color: theme ? theme.textMuted : "#64748B"
                                }
                                Text {
                                    width: 70; anchors.verticalCenter: parent.verticalCenter
                                    text: "SEV"; font.pixelSize: 10
                                    font.family: theme ? theme.fontFamilyMono : "monospace"
                                    color: theme ? theme.textMuted : "#64748B"
                                }
                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: "DETAILS"; font.pixelSize: 10
                                    font.family: theme ? theme.fontFamilyMono : "monospace"
                                    color: theme ? theme.textMuted : "#64748B"
                                }
                            }
                        }

                        ListView {
                            id: alertList
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            model: control.alerts
                            currentIndex: control.selectedIndex
                            delegate: Rectangle {
                                width: alertList.width
                                height: 48
                                color: index === control.selectedIndex
                                       ? (theme ? theme.surfaceElevated : "#1E293B")
                                       : (index % 2 === 0 ? "transparent" : (theme ? theme.backgroundAlt : "#0F172A"))

                                Rectangle {
                                    anchors.left: parent.left
                                    anchors.top: parent.top
                                    anchors.bottom: parent.bottom
                                    width: 3
                                    color: control.sevColor(modelData.sev)
                                }

                                Row {
                                    anchors.fill: parent
                                    anchors.leftMargin: 12
                                    spacing: 8
                                    Text {
                                        width: 90
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: modelData.id
                                        font.pixelSize: 11
                                        font.family: theme ? theme.fontFamilyMono : "monospace"
                                        color: theme ? theme.textPrimary : "#E5E7EB"
                                        elide: Text.ElideRight
                                    }
                                    Rectangle {
                                        width: 64; height: 20; radius: 4
                                        anchors.verticalCenter: parent.verticalCenter
                                        color: "transparent"
                                        border.color: control.sevColor(modelData.sev)
                                        border.width: 1
                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData.sev
                                            font.pixelSize: 9
                                            font.weight: Font.Bold
                                            color: control.sevColor(modelData.sev)
                                        }
                                    }
                                    Text {
                                        width: parent.width - 180
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: modelData.detail
                                        font.pixelSize: 12
                                        color: theme ? theme.textPrimary : "#E5E7EB"
                                        elide: Text.ElideRight
                                    }
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: control.selectedIndex = index
                                }
                            }
                        }
                    }
                }

                // Detail panel
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredWidth: 1
                    Layout.minimumHeight: 280
                    radius: 4
                    color: theme ? theme.surface : "#151C28"
                    border.color: theme ? theme.border : "#1E293B"
                    border.width: 1

                    readonly property var sel: (control.alerts && control.alerts.length > control.selectedIndex)
                                              ? control.alerts[control.selectedIndex] : null

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 12

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 120
                            radius: 4
                            color: "#0A0C10"
                            clip: true

                            Rectangle {
                                width: 8; height: 8; radius: 4
                                anchors.left: parent.left
                                anchors.top: parent.top
                                anchors.margins: 10
                                color: "#EF4444"
                                SequentialAnimation on opacity {
                                    loops: Animation.Infinite
                                    NumberAnimation { to: 0.3; duration: 600 }
                                    NumberAnimation { to: 1.0; duration: 600 }
                                }
                            }
                            Text {
                                anchors.left: parent.left
                                anchors.top: parent.top
                                anchors.leftMargin: 26
                                anchors.topMargin: 8
                                text: "LIVE EVIDENCE  ·  " + (parent.parent.sel ? parent.parent.sel.cam : "")
                                font.family: theme ? theme.fontFamilyMono : "monospace"
                                font.pixelSize: 10
                                color: "#E5E7EB"
                            }
                            AppButton {
                                anchors.bottom: parent.bottom
                                anchors.left: parent.left
                                anchors.margins: 8
                                text: "Playback Sequence"
                                variant: "primary"
                                theme: control.theme
                            }
                        }

                        Text {
                            text: parent.parent.sel ? parent.parent.sel.detail : "Select an alert"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: theme ? theme.textPrimary : "#E5E7EB"
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }
                        Text {
                            text: parent.parent.sel
                                  ? (parent.parent.sel.id + "  ·  " + parent.parent.sel.ts)
                                  : ""
                            font.pixelSize: 11
                            font.family: theme ? theme.fontFamilyMono : "monospace"
                            color: theme ? theme.textMuted : "#64748B"
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12
                            Rectangle {
                                Layout.fillWidth: true
                                height: 64
                                radius: 4
                                color: theme ? theme.backgroundAlt : "#0F172A"
                                Column {
                                    anchors.centerIn: parent
                                    spacing: 2
                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: "AI CONFIDENCE"
                                        font.pixelSize: 10
                                        color: theme ? theme.textMuted : "#64748B"
                                    }
                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: (parent.parent.parent.parent.sel
                                               ? parent.parent.parent.parent.sel.conf : 0) + "%"
                                        font.pixelSize: 18
                                        font.weight: Font.Bold
                                        color: theme ? theme.info : "#06B6D4"
                                    }
                                }
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                height: 64
                                radius: 4
                                color: theme ? theme.backgroundAlt : "#0F172A"
                                Column {
                                    anchors.centerIn: parent
                                    spacing: 2
                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: "THREAT"
                                        font.pixelSize: 10
                                        color: theme ? theme.textMuted : "#64748B"
                                    }
                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: parent.parent.parent.parent.sel
                                              ? parent.parent.parent.parent.sel.threat : ""
                                        font.pixelSize: 16
                                        font.weight: Font.Bold
                                        color: theme ? theme.critical : "#EF4444"
                                    }
                                }
                            }
                        }

                        Text {
                            text: "Location: " + (parent.parent.sel ? parent.parent.sel.loc : "—")
                            font.pixelSize: 12
                            color: theme ? theme.textSecondary : "#94A3B8"
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        Item { Layout.fillHeight: true }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            AppButton {
                                Layout.fillWidth: true
                                text: (typeof I18n !== "undefined" && I18n) ? I18n.t("alerts.false_positive") : "False Positive"
                                variant: "secondary"
                                theme: control.theme
                            }
                            AppButton {
                                Layout.fillWidth: true
                                text: (typeof I18n !== "undefined" && I18n) ? I18n.t("alerts.acknowledge") : "Acknowledge"
                                variant: "primary"
                                theme: control.theme
                                onClicked: {
                                    var a = control.alerts[control.selectedIndex]
                                    if (a && control.alertController)
                                        control.alertController.acknowledgeAlert(a.id, "admin")
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
