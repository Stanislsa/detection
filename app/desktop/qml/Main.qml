import QtQuick 2.15
import QtQuick.Controls 2.15
import "theme"
import "layouts"
import "pages/auth"
import "components"

ApplicationWindow {
    id: root
    visible: true
    width: 1440
    height: 900
    minimumWidth: 640
    minimumHeight: 480
    title: (typeof I18n !== "undefined" && I18n)
           ? (I18n.t("app.name") + " — " + I18n.t("app.subtitle"))
           : "SentinelAI"
    color: theme.background

    Behavior on color {
        ColorAnimation { duration: 280; easing.type: Easing.InOutQuad }
    }

    ThemeManager {
        id: theme
        isDark: (typeof ThemePrefs !== "undefined" && ThemePrefs)
                ? ThemePrefs.isDark : true

        Component.onCompleted: {
            if (typeof ThemePrefs !== "undefined" && ThemePrefs)
                setDark(ThemePrefs.isDark)
        }
    }

    Connections {
        target: typeof ThemePrefs !== "undefined" ? ThemePrefs : null
        enabled: typeof ThemePrefs !== "undefined" && ThemePrefs !== null
        function onIsDarkChanged() {
            if (ThemePrefs)
                theme.setDark(ThemePrefs.isDark)
        }
    }

    // Authentication state
    property string authState: "login" // login, two_factor, forgot_password, app

    // ---- Auth pages with fade transitions ----
    Item {
        anchors.fill: parent
        visible: authState !== "app"

        LoginPage {
            id: loginPage
            anchors.fill: parent
            theme: theme
            authController: AuthController
            opacity: authState === "login" ? 1 : 0
            visible: opacity > 0
            enabled: authState === "login"

            Behavior on opacity {
                NumberAnimation { duration: 280; easing.type: Easing.InOutQuad }
            }

            onForgotPasswordRequested: {
                authState = "forgot_password"
            }
        }

        TwoFactorPage {
            id: twoFactorPage
            anchors.fill: parent
            theme: theme
            authController: AuthController
            opacity: authState === "two_factor" ? 1 : 0
            visible: opacity > 0
            enabled: authState === "two_factor"

            Behavior on opacity {
                NumberAnimation { duration: 280; easing.type: Easing.InOutQuad }
            }
        }

        ForgotPasswordPage {
            id: forgotPasswordPage
            anchors.fill: parent
            theme: theme
            authController: AuthController
            opacity: authState === "forgot_password" ? 1 : 0
            visible: opacity > 0
            enabled: authState === "forgot_password"

            Behavior on opacity {
                NumberAnimation { duration: 280; easing.type: Easing.InOutQuad }
            }

            onBackToLogin: {
                authState = "login"
            }
        }
    }

    // Main Application Layout
    AppLayout {
        id: appLayout
        anchors.fill: parent
        theme: theme
        currentPage: "dashboard"
        opacity: authState === "app" ? 1 : 0
        visible: opacity > 0
        enabled: authState === "app"

        Behavior on opacity {
            NumberAnimation { duration: 320; easing.type: Easing.OutCubic }
        }

        onPageChanged: function(page) {
            console.log("Page changed to:", page)
        }
    }

    Connections {
        target: typeof AuthController !== "undefined" ? AuthController : null
        enabled: typeof AuthController !== "undefined" && AuthController !== null
        function onTwoFactorRequired() {
            authState = "two_factor"
        }
        function onLoginSuccess() {
            authState = "app"
            // Welcome toast after login
            Qt.callLater(function() {
                if (appLayout) appLayout.showToast("Welcome back, Alex Rivers — Session secured", "success", 3500)
            })
        }
        function onLoginFailed(message) {
            console.log("Login failed:", message)
        }
        function onTwoFactorFailed(message) {
            console.log("2FA failed:", message)
        }
        function onPasswordResetSent() {
            console.log("Password reset sent")
            authState = "login"
        }
        function onPasswordResetFailed(message) {
            console.log("Password reset failed:", message)
        }
    }

    // Global keyboard shortcut for theme toggle (Ctrl+Shift+T)
    Shortcut {
        sequence: "Ctrl+Shift+T"
        onActivated: {
            theme.toggleTheme()
            if (typeof ThemePrefs !== "undefined" && ThemePrefs)
                ThemePrefs.setDark(theme.isDark)
        }
    }
}
