import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"
import "../navigation"

Rectangle {
    id: control

    property var theme
    property string currentPage: "dashboard"
    property var pageParams: {}

    // Optional status values for the footer row
    property string coreEngineVersion: "v4.2.1-stable"
    property string coreEngineStatus: "ONLINE"
    property bool coreEngineOk: true
    property string uplinkLatencyMs: "880ms"
    property bool uplinkWarn: true
    property int activeAnalysts: 4
    property int unreadNotifications: 0

    color: control.theme.background

    Row {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            id: sidebar
            height: parent.height
            theme: control.theme
            currentPage: control.currentPage
            onPageChanged: function(page) {
                control.currentPage = page
                control.pageChanged(page)
            }
        }

        Column {
            width: parent.width - sidebar.width
            height: parent.height
            spacing: 0

            Header {
                id: header
                width: parent.width
                theme: control.theme
                title: control.formatPageTitle(control.currentPage)
                crumbs: control.crumbsForPage(control.currentPage)
                unreadCount: control.unreadNotifications
                onBreadcrumbClicked: function(idx) {
                    // First item ("SentinelAI") goes home; otherwise jump to that breadcrumb's page
                    if (idx === 0) control.currentPage = "dashboard"
                }
                onSearchSubmitted: function(q) { console.log("search:", q) }
                onNotificationClicked: control.currentPage = "notifications"
            }

            Rectangle {
                width: parent.width
                height: parent.height - header.height - footerRow.height
                color: control.theme.background

                Loader {
                    id: pageLoader
                    anchors.fill: parent
                    source: control.getPageSource(control.currentPage)

                    onLoaded: {
                        if (item) {
                            item.theme = control.theme
                            if (item.pageParams !== undefined) item.pageParams = control.pageParams
                        }
                    }
                }
            }

            // ---- Footer status row ----
            Rectangle {
                id: footerRow
                width: parent.width
                height: control.theme.footerStatusHeight
                color: control.theme.backgroundAlt

                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    height: 1
                    color: control.theme.border
                }

                Row {
                    anchors.fill: parent
                    anchors.leftMargin: control.theme.spacingM
                    anchors.rightMargin: control.theme.spacingM
                    spacing: 0

                    FooterCell {
                        width: parent.width / 3
                        height: parent.height
                        theme: control.theme
                        dotColor: control.coreEngineOk ? control.theme.success : control.theme.critical
                        label: "SENTINEL CORE ENGINE " + control.coreEngineVersion
                        status: control.coreEngineStatus
                    }

                    FooterCell {
                        width: parent.width / 3
                        height: parent.height
                        theme: control.theme
                        dotColor: control.uplinkWarn ? control.theme.warning : control.theme.success
                        label: "SATELLITE UPLINK " + control.uplinkLatencyMs
                        status: control.uplinkWarn ? "LATENCY_WARN" : "NOMINAL"
                    }

                    FooterCell {
                        width: parent.width / 3
                        height: parent.height
                        theme: control.theme
                        dotColor: control.theme.info
                        label: "ACTIVE SESSIONS " + (control.activeAnalysts < 10 ? "0" : "") + control.activeAnalysts + " ANALYSTS"
                        status: "MONITORING"
                    }
                }
            }
        }
    }

    signal pageChanged(string page)

    function formatPageTitle(page) {
        switch(page) {
            case "dashboard":      return "Dashboard"
            case "cameras":        return "Cameras"
            case "alerts":         return "Alerts"
            case "incidents":      return "Alerts"
            case "events":         return "Events"
            case "notifications":  return "Notifications"
            case "observability":  return "Observability"
            case "system_health":  return "System Health"
            case "health":         return "System Health"
            case "ai_training":    return "AI Training"
            case "settings":       return "Settings"
            case "users":          return "Users"
            default: return page.charAt(0).toUpperCase() + page.slice(1)
        }
    }

    function crumbsForPage(page) {
        var title = formatPageTitle(page)
        return ["SentinelAI", title]
    }

    function getPageSource(page) {
        switch(page) {
            case "dashboard":      return "../pages/dashboard/DashboardPage.qml"
            case "incidents":      return "../pages/alerts/AlertsPage.qml"
            case "alerts":         return "../pages/alerts/AlertsPage.qml"
            case "cameras":        return "../pages/cameras/CamerasPage.qml"
            case "events":         return "../pages/events/EventsPage.qml"
            case "notifications":  return "../pages/notifications/NotificationCenter.qml"
            case "observability":  return "../pages/observability/ObservabilityPage.qml"
            case "system_health":  return "../pages/health/SystemHealthPage.qml"
            case "health":         return "../pages/health/SystemHealthPage.qml"
            case "ai_training":    return "../pages/ai_training/AITrainingPage.qml"
            case "settings":       return "../pages/settings/SettingsPage.qml"
            case "users":          return "../pages/users/UsersPage.qml"
            default: return ""
        }
    }

    // Inline footer cell component
    component FooterCell : Item {
        property var theme
        property color dotColor
        property string label: ""
        property string status: ""

        Row {
            anchors.fill: parent
            anchors.leftMargin: theme.spacingS
            spacing: theme.spacingS
            Rectangle {
                width: 6
                height: 6
                radius: 3
                color: dotColor
                anchors.verticalCenter: parent.verticalCenter
            }
            Text {
                text: label
                font.family: theme.fontFamilyMono
                font.pixelSize: theme.fontSizeXS
                font.letterSpacing: theme.letterSpacingM
                color: theme.textSecondary
                anchors.verticalCenter: parent.verticalCenter
            }
            Text {
                text: "// " + status
                font.family: theme.fontFamilyMono
                font.pixelSize: theme.fontSizeXS
                font.letterSpacing: theme.letterSpacingM
                color: dotColor
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}