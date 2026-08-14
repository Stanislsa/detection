import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"
import "../dialogs"
import "../navigation"
import "../animations"

Rectangle {
    id: control

    property var theme
    property string currentPage: "dashboard"
    property var pageParams: {}

    // Status footer
    property string coreEngineVersion: "v4.2.1-stable"
    property string coreEngineStatus: "ONLINE"
    property bool coreEngineOk: true
    property string uplinkLatencyMs: "880ms"
    property bool uplinkWarn: true
    property int activeAnalysts: 4
    property int unreadNotifications: 3

    // Responsive
    property bool isNarrow: width < (theme ? theme.breakpointTablet : 1024)
    property bool sidebarCollapsed: isNarrow

    // ---- Transition state ----
    property string _previousPage: "dashboard"
    property string transitionDirection: "forward"
    property bool isTransitioning: false
    // Track which wrapper/loader pair is active ("A" or "B")
    property string activeSlot: "A"

    readonly property var pageOrder: [
        "dashboard", "cameras", "alerts", "events",
        "users", "ai_training", "observability",
        "system_health", "notifications", "settings"
    ]

    color: control.theme.background
    Behavior on color { ColorAnimation { duration: 280; easing.type: Easing.InOutQuad } }

    // Direction helpers
    function computeDirection(fromPage, toPage) {
        var fromIdx = pageOrder.indexOf(fromPage)
        var toIdx   = pageOrder.indexOf(toPage)
        if (fromIdx < 0 || toIdx < 0 || fromIdx === toIdx)
            return "fade"
        return (toIdx > fromIdx) ? "forward" : "back"
    }

    function wirePage(item) {
        if (!item) return
        item.theme = control.theme
        if (item.pageParams !== undefined) item.pageParams = control.pageParams
        if (item.alertController !== undefined) item.alertController = AlertController
        if (item.cameraController !== undefined) item.cameraController = CameraController
        if (item.videoPipeline !== undefined) item.videoPipeline = VideoPipeline
        if (item.eventController !== undefined) item.eventController = EventController
        if (item.userController !== undefined) item.userController = UserController
        if (item.notificationController !== undefined) item.notificationController = NotificationController
        if (item.healthController !== undefined) item.healthController = HealthController
        if (item.serviceHealthController !== undefined) item.serviceHealthController = ServiceHealthController
        if (item.settingsController !== undefined) item.settingsController = SettingsController
        if (item.router !== undefined) item.router = Router
    }

    function navigateTo(page) {
        if (page === currentPage || isTransitioning) return
        transitionDirection = computeDirection(currentPage, page)
        _previousPage = currentPage
        // Trigger transition before updating currentPage (so UI labels stay until mid-anim)
        startTransition(page)
        currentPage = page
        pageChanged(page)
    }

    function startTransition(page) {
        isTransitioning = true

        var enteringWrapper = (activeSlot === "A") ? wrapperB : wrapperA
        var exitingWrapper  = (activeSlot === "A") ? wrapperA : wrapperB
        var enteringLoader  = (activeSlot === "A") ? loaderB  : loaderA
        var exitingLoader   = (activeSlot === "A") ? loaderA  : loaderB
        var source          = getPageSource(page)

        // Prepare entering wrapper off-screen
        enteringWrapper.opacity = 0
        enteringWrapper.scale = 0.985
        enteringWrapper.x = (transitionDirection === "forward") ? 40
                          : (transitionDirection === "back")    ? -40 : 0
        enteringWrapper.y = 0

        function doCrossfade() {
            wirePage(enteringLoader.item)

            // Exit old page
            exitAnim.target = exitingWrapper
            exitAnim.direction = transitionDirection
            exitAnim.durationMs = 200
            exitAnim.playExit(function() {
                exitingLoader.source = ""
                exitingWrapper.opacity = 0
                exitingWrapper.x = 0
                exitingWrapper.scale = 1
            })

            // Enter new page
            enterAnim.target = enteringWrapper
            enterAnim.direction = transitionDirection
            enterAnim.durationMs = 280
            enterAnim.playEnter()

            activeSlot = (activeSlot === "A") ? "B" : "A"
            unlockTimer.restart()
        }

        // Load then animate
        var alreadyReady = enteringLoader.status === Loader.Ready
                        && enteringLoader.source.toString().length > 0
                        && enteringLoader.source.toString().indexOf(
                               source.split("/").pop()) >= 0

        if (alreadyReady) {
            doCrossfade()
        } else {
            var handler = function() {
                enteringLoader.loaded.disconnect(handler)
                doCrossfade()
            }
            enteringLoader.loaded.connect(handler)
            enteringLoader.source = source
        }
    }

    Timer {
        id: unlockTimer
        interval: 320
        onTriggered: isTransitioning = false
    }

    PageTransition { id: enterAnim; slideDistance: 36 }
    PageTransition { id: exitAnim;  slideDistance: 28 }

    // ---------------------------------------------------------------
    Row {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            id: sidebar
            height: parent.height
            theme: control.theme
            currentPage: control.currentPage
            collapsed: control.sidebarCollapsed
            width: control.sidebarCollapsed
                   ? (theme ? theme.sidebarCollapsedWidth : 64)
                   : (theme ? theme.sidebarWidth : 240)

            Behavior on width {
                NumberAnimation { duration: 220; easing.type: Easing.OutCubic }
            }

            onPageChanged: function(page) {
                control.navigateTo(page)
                if (control.isNarrow) control.sidebarCollapsed = true
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
                isDark: control.theme.isDark
                onBreadcrumbClicked: function(idx) {
                    if (idx === 0) control.navigateTo("dashboard")
                }
                onSearchSubmitted: function(q) { console.log("search:", q) }
                onNotificationClicked: control.navigateTo("notifications")
                onThemeToggleRequested: control.theme.toggleTheme()
                onMenuToggleRequested: control.sidebarCollapsed = !control.sidebarCollapsed
            }

            // Content with dual loaders
            Rectangle {
                id: contentArea
                width: parent.width
                height: parent.height - header.height - footerRow.height
                color: control.theme.background
                clip: true

                Behavior on color {
                    ColorAnimation { duration: 280; easing.type: Easing.InOutQuad }
                }

                // Wrapper items so we can animate x/opacity/scale freely
                // (anchors on Loader would fight with position animations)
                Item {
                    id: wrapperA
                    width: parent.width
                    height: parent.height
                    x: 0; y: 0
                    opacity: 1
                    scale: 1
                    transformOrigin: Item.Center
                    z: activeSlot === "A" ? 2 : 1

                    Loader {
                        id: loaderA
                        anchors.fill: parent
                        Component.onCompleted: {
                            source = control.getPageSource("dashboard")
                        }
                        onLoaded: {
                            if (item && activeSlot === "A")
                                wirePage(item)
                        }
                    }
                }

                Item {
                    id: wrapperB
                    width: parent.width
                    height: parent.height
                    x: 0; y: 0
                    opacity: 0
                    scale: 1
                    transformOrigin: Item.Center
                    z: activeSlot === "B" ? 2 : 1

                    Loader {
                        id: loaderB
                        anchors.fill: parent
                    }
                }

                // Loading overlay
                Rectangle {
                    id: loadingOverlay
                    anchors.fill: parent
                    color: control.theme.overlay
                    visible: opacity > 0
                    opacity: 0
                    z: 50
                    Behavior on opacity { NumberAnimation { duration: 200 } }

                    Column {
                        anchors.centerIn: parent
                        spacing: theme ? theme.spacingM : 16
                        AppLoader {
                            anchors.horizontalCenter: parent.horizontalCenter
                            theme: control.theme
                            loading: loadingOverlay.opacity > 0.5
                            width: 48; height: 48
                        }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "Loading…"
                            font.family: theme ? theme.fontFamily : "sans-serif"
                            font.pixelSize: theme ? theme.fontSizeM : 13
                            color: theme ? theme.textSecondary : "#94A3B8"
                        }
                    }
                }
            }

            // Footer
            Rectangle {
                id: footerRow
                width: parent.width
                height: control.theme.footerStatusHeight
                color: control.theme.backgroundAlt
                Behavior on color { ColorAnimation { duration: 280 } }

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
                        width: parent.width / 3; height: parent.height
                        theme: control.theme
                        dotColor: control.coreEngineOk ? control.theme.success : control.theme.critical
                        label: "SENTINEL CORE ENGINE " + control.coreEngineVersion
                        status: control.coreEngineStatus
                    }
                    FooterCell {
                        width: parent.width / 3; height: parent.height
                        theme: control.theme
                        dotColor: control.uplinkWarn ? control.theme.warning : control.theme.success
                        label: "SATELLITE UPLINK " + control.uplinkLatencyMs
                        status: control.uplinkWarn ? "LATENCY_WARN" : "NOMINAL"
                    }
                    FooterCell {
                        width: parent.width / 3; height: parent.height
                        theme: control.theme
                        dotColor: control.theme.info
                        label: "ACTIVE SESSIONS " + (control.activeAnalysts < 10 ? "0" : "") + control.activeAnalysts + " ANALYSTS"
                        status: "MONITORING"
                    }
                }
            }
        }
    }

    PushPermissionDialog {
        id: pushPermissionDialog
        theme: control.theme
        pushService: typeof PushService !== "undefined" ? PushService : null
        onGranted: {
            if (typeof control.showToast === "function")
                control.showToast("Push notifications enabled", "success", 3000)
        }
        onDenied: {
            if (typeof control.showToast === "function")
                control.showToast("Push notifications disabled", "info", 3000)
        }
    }

    Connections {
        target: typeof PushService !== "undefined" ? PushService : null
        function onPermissionRequestNeeded() {
            if (!pushPermissionDialog.opened)
                pushPermissionDialog.open()
        }
    }


    ToastStack {
        id: globalToast
        theme: control.theme
        z: 100
    }


    // ---- Real-time alerts → toast + badge ----
    Connections {
        target: typeof AlertController !== "undefined" ? AlertController : null
        function onAlertReceived(payload) {
            var cfg = AlertController.config || {}
            if (!cfg.toast_enabled) return
            var prio = payload.priority || "INFO"
            if (cfg.toast_critical_only && prio !== "CRITICAL") return
            var type = "info"
            if (prio === "CRITICAL") type = "danger"
            else if (prio === "HIGH") type = "warning"
            else if (prio === "MEDIUM") type = "info"
            else type = "info"
            var msg = (payload.title || "Alert") + " — " + (payload.location || payload.camera_name || "")
            control.showToast(msg, type, prio === "CRITICAL" ? 8000 : 5000)
            if (cfg.badge_enabled)
                control.unreadNotifications = AlertController.criticalOpenCount
        }
        function onStatsChanged() {
            control.unreadNotifications = AlertController.criticalOpenCount
        }
    }

    Component.onCompleted: {
        if (typeof AlertController !== "undefined")
            control.unreadNotifications = AlertController.criticalOpenCount
    }

    function showToast(message, type, durationMs) {
        globalToast.push(message, type || "info", durationMs || 4000)
    }
    function showLoading(visible) {
        loadingOverlay.opacity = visible ? 1 : 0
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
        return ["SentinelAI", "Monitoring", "Infrastructure"]
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
                width: 6; height: 6; radius: 3
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
                elide: Text.ElideRight
                width: Math.min(implicitWidth, parent.width * 0.6)
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
