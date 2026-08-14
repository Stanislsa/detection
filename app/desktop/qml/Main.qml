import QtQuick 2.15
import QtQuick.Controls 2.15
import "theme"
import "layouts"
import "pages/auth"

ApplicationWindow {
    id: root
    visible: true
    width: 1280
    height: 800
    minimumWidth: 1024
    minimumHeight: 768
    title: "SentinelAI"
    color: theme.background
    
    ThemeManager {
        id: theme
    }
    
    // Authentication state
    property string authState: "login" // login, two_factor, app
    
    // Login Page
    LoginPage {
        id: loginPage
        anchors.fill: parent
        theme: theme
        authController: AuthController
        visible: authState === "login"
        
        onForgotPasswordRequested: {
            authState = "forgot_password"
        }
    }
    
    // Two Factor Page
    TwoFactorPage {
        id: twoFactorPage
        anchors.fill: parent
        theme: theme
        authController: AuthController
        visible: authState === "two_factor"
    }
    
    // Forgot Password Page
    ForgotPasswordPage {
        id: forgotPasswordPage
        anchors.fill: parent
        theme: theme
        authController: AuthController
        visible: authState === "forgot_password"
        
        onBackToLogin: {
            authState = "login"
        }
    }
    
    // Main Application Layout
    AppLayout {
        id: appLayout
        anchors.fill: parent
        theme: theme
        currentPage: "dashboard"
        visible: authState === "app"
        onPageChanged: function(page) {
            console.log("Page changed to:", page)
        }
    }
    
    Connections {
        target: AuthController
        function onTwoFactorRequired() {
            authState = "two_factor"
        }
        function onLoginSuccess() {
            authState = "app"
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
}
