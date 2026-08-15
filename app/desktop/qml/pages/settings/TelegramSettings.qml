import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../theme"
import "../../components"

/*
 * Connexion Telegram Bot — token, chat_id, filtres, test.
 */
Flickable {
    id: control
    property var theme
    readonly property bool isNarrow: width < 700
    property var telegramController: typeof TelegramController !== "undefined" ? TelegramController : null

    contentWidth: width
    contentHeight: col.implicitHeight + 40
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    property string statusMsg: ""
    property bool statusOk: false

    function cfg(key, fallback) {
        if (!telegramController) return fallback
        var c = telegramController.config
        return c && c[key] !== undefined ? c[key] : fallback
    }

    function setCfg(key, value) {
        if (telegramController)
            telegramController.setConfigValue(key, value)
    }

    Connections {
        target: typeof TelegramController !== "undefined" ? TelegramController : control.telegramController
        enabled: (typeof TelegramController !== "undefined" && TelegramController)
                 || (control.telegramController !== undefined && control.telegramController !== null)
        function onTestFinished(ok, message) {
            control.statusOk = ok
            control.statusMsg = message
        }
        function onMessageSent(ok, message) {
            control.statusOk = ok
            control.statusMsg = ok ? "Message sent" : ("Send failed: " + message)
        }
        function onPermissionsCheckFinished(ok, message) {
            control.statusOk = ok
            control.statusMsg = message
        }
        function onConfigChanged() {
            // force UI refresh of bound fields if needed
            control.statusMsg = control.statusMsg
        }
    }

    Component.onCompleted: {
        if (typeof TelegramController !== "undefined" && TelegramController)
            control.telegramController = TelegramController
    }

    Column {
        id: col
        width: parent.width
        spacing: 16
        leftPadding: 4
        rightPadding: 4

        // Header card
        Rectangle {
            width: parent.width - 8
            height: headCol.implicitHeight + 28
            radius: 4
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"
            border.width: 1

            Column {
                id: headCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 16
                spacing: 12

                RowLayout {
                    width: parent.width
                    Row {
                        spacing: 10
                        Rectangle {
                            width: 36; height: 36; radius: 18
                            color: "#229ED9"
                            Text {
                                anchors.centerIn: parent
                                text: "✈"
                                font.pixelSize: 16
                                color: "#FFF"
                            }
                        }
                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 2
                            Text {
                                text: "Telegram Bot"
                                font.pixelSize: 15
                                font.weight: Font.DemiBold
                                color: theme ? theme.textPrimary : "#E5E7EB"
                            }
                            Text {
                                text: "Forward critical alerts to a Telegram chat or channel"
                                font.pixelSize: 12
                                color: theme ? theme.textSecondary : "#94A3B8"
                            }
                        }
                    }
                    Item { Layout.fillWidth: true }
                    Rectangle {
                        width: st.implicitWidth + 14
                        height: 22
                        radius: 11
                        color: {
                            if (!telegramController) return "#64748B22"
                            if (telegramController.enabled && telegramController.isConfigured) return "#10B98122"
                            if (telegramController.isConfigured) return "#F59E0B22"
                            return "#64748B22"
                        }
                        border.color: {
                            if (!telegramController) return "#64748B"
                            if (telegramController.enabled && telegramController.isConfigured) return "#10B981"
                            if (telegramController.isConfigured) return "#F59E0B"
                            return "#64748B"
                        }
                        border.width: 1
                        Text {
                            id: st
                            anchors.centerIn: parent
                            text: {
                                if (!telegramController) return "N/A"
                                if (telegramController.enabled && telegramController.isConfigured) return "CONNECTED"
                                if (telegramController.isConfigured) return "CONFIGURED"
                                return "NOT SET"
                            }
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: {
                                if (!telegramController) return "#64748B"
                                if (telegramController.enabled && telegramController.isConfigured) return "#10B981"
                                if (telegramController.isConfigured) return "#F59E0B"
                                return "#64748B"
                            }
                        }
                    }
                }

                RowLayout {
                    width: parent.width
                    Text {
                        text: "Enable Telegram alerts"
                        font.pixelSize: 13
                        color: theme ? theme.textPrimary : "#E5E7EB"
                        Layout.fillWidth: true
                    }
                    AppSwitch {
                        theme: control.theme
                        checked: control.cfg("enabled", false)
                        onToggled: control.setCfg("enabled", checked)
                    }
                }
            }
        }

        // Credentials
        Rectangle {
            width: parent.width - 8
            height: credCol.implicitHeight + 28
            radius: 4
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"
            border.width: 1

            Column {
                id: credCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 16
                spacing: 12

                Text {
                    text: "Connection"
                    font.pixelSize: 14
                    font.weight: Font.DemiBold
                    color: theme ? theme.textPrimary : "#E5E7EB"
                }

                Text {
                    width: parent.width
                    text: "Create a bot via @BotFather, copy the token, then start a chat with the bot and get your chat_id (@userinfobot or getUpdates)."
                    font.pixelSize: 12
                    color: theme ? theme.textSecondary : "#94A3B8"
                    wrapMode: Text.WordWrap
                }

                Text {
                    text: "BOT TOKEN"
                    font.pixelSize: 10
                    font.family: theme ? theme.fontFamilyMono : "monospace"
                    color: theme ? theme.textMuted : "#64748B"
                }
                AppInput {
                    id: tokenInput
                    width: parent.width
                    theme: control.theme
                    placeholderText: "123456:ABC-DEF..."
                    text: control.cfg("bot_token", "")
                    echoMode: TextInput.Password
                    onEditingFinished: control.setCfg("bot_token", text)
                }

                Text {
                    text: "CHAT ID"
                    font.pixelSize: 10
                    font.family: theme ? theme.fontFamilyMono : "monospace"
                    color: theme ? theme.textMuted : "#64748B"
                }
                AppInput {
                    id: chatInput
                    width: parent.width
                    theme: control.theme
                    placeholderText: "-1001234567890 or 123456789"
                    text: control.cfg("chat_id", "")
                    mono: true
                    onEditingFinished: control.setCfg("chat_id", text)
                }

                Row {
                    spacing: 10
                    AppButton {
                        text: telegramController && telegramController.busy ? "Testing…" : "Test connection"
                        variant: "primary"
                        theme: control.theme
                        enabled: !(telegramController && telegramController.busy)
                        onClicked: {
                            // Persist current fields first
                            control.setCfg("bot_token", tokenInput.text)
                            control.setCfg("chat_id", chatInput.text)
                            if (telegramController)
                                telegramController.testConnection()
                        }
                    }
                    AppButton {
                        text: "Send test message"
                        variant: "secondary"
                        theme: control.theme
                        enabled: !(telegramController && telegramController.busy)
                        onClicked: {
                            control.setCfg("bot_token", tokenInput.text)
                            control.setCfg("chat_id", chatInput.text)
                            if (telegramController)
                                telegramController.sendTestMessage("🛡️ <b>SentinelAI</b> — manual test from Settings")
                        }
                    }
                    AppButton {
                        text: "Save"
                        variant: "ghost"
                        theme: control.theme
                        onClicked: {
                            control.setCfg("bot_token", tokenInput.text)
                            control.setCfg("chat_id", chatInput.text)
                            control.statusMsg = "Configuration saved"
                            control.statusOk = true
                        }
                    }
                }

                Rectangle {
                    visible: control.statusMsg !== ""
                    width: parent.width
                    height: statusLab.implicitHeight + 16
                    radius: 4
                    color: control.statusOk ? "#10B98122" : "#EF444422"
                    border.color: control.statusOk ? "#10B981" : "#EF4444"
                    border.width: 1
                    Text {
                        id: statusLab
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.margins: 10
                        text: control.statusMsg
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                        color: control.statusOk ? "#10B981" : "#EF4444"
                    }
                }
            }
        }

        
        // Bot permissions
        Rectangle {
            width: parent.width - 8
            height: permCol.implicitHeight + 28
            radius: 4
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"
            border.width: 1

            Column {
                id: permCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 16
                spacing: 12

                RowLayout {
                    width: parent.width
                    Text {
                        text: "Bot permissions"
                        font.pixelSize: 14
                        font.weight: Font.DemiBold
                        color: theme ? theme.textPrimary : "#E5E7EB"
                        Layout.fillWidth: true
                    }
                    Rectangle {
                        width: pLab.implicitWidth + 14
                        height: 22
                        radius: 11
                        color: {
                            if (!telegramController || !telegramController.permissions || !telegramController.permissions.status)
                                return "#64748B22"
                            if (telegramController.canSendMessages) return "#10B98122"
                            return "#EF444422"
                        }
                        border.color: {
                            if (!telegramController || !telegramController.permissions || !telegramController.permissions.status)
                                return "#64748B"
                            if (telegramController.canSendMessages) return "#10B981"
                            return "#EF4444"
                        }
                        border.width: 1
                        Text {
                            id: pLab
                            anchors.centerIn: parent
                            text: {
                                if (!telegramController || !telegramController.permissions || !telegramController.permissions.status)
                                    return "NOT CHECKED"
                                if (telegramController.canSendMessages) return "CAN SEND"
                                return "BLOCKED"
                            }
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: {
                                if (!telegramController || !telegramController.permissions || !telegramController.permissions.status)
                                    return "#64748B"
                                if (telegramController.canSendMessages) return "#10B981"
                                return "#EF4444"
                            }
                        }
                    }
                }

                Text {
                    width: parent.width
                    text: "Verify that the bot can post in the configured chat (required for channels: admin + Post Messages)."
                    font.pixelSize: 12
                    color: theme ? theme.textSecondary : "#94A3B8"
                    wrapMode: Text.WordWrap
                }

                // Detail grid
                GridLayout {
                    width: parent.width
                    columns: 2
                    columnSpacing: 12
                    rowSpacing: 6
                    visible: telegramController && telegramController.permissions && telegramController.permissions.bot_username !== undefined && telegramController.permissions.bot_username !== ""

                    Text { text: "Bot"; font.pixelSize: 11; color: theme ? theme.textMuted : "#64748B" }
                    Text {
                        text: telegramController && telegramController.permissions
                              ? ("@" + (telegramController.permissions.bot_username || "") + "  (" + (telegramController.permissions.bot_name || "") + ")")
                              : "—"
                        font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB"
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                    }
                    Text { text: "Chat"; font.pixelSize: 11; color: theme ? theme.textMuted : "#64748B" }
                    Text {
                        text: telegramController && telegramController.permissions
                              ? ((telegramController.permissions.chat_title || "") + " · " + (telegramController.permissions.chat_type || ""))
                              : "—"
                        font.pixelSize: 12; color: theme ? theme.textPrimary : "#E5E7EB"
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                    Text { text: "Status"; font.pixelSize: 11; color: theme ? theme.textMuted : "#64748B" }
                    Text {
                        text: telegramController ? (telegramController.botStatus || "—") : "—"
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                        color: theme ? theme.textPrimary : "#E5E7EB"
                    }
                }

                // Permission chips
                Flow {
                    width: parent.width
                    spacing: 8
                    visible: telegramController && telegramController.permissions && telegramController.permissions.status

                    Repeater {
                        model: [
                            { key: "can_send_messages", label: "Send messages" },
                            { key: "can_send_media", label: "Send media" },
                            { key: "is_admin", label: "Admin" },
                            { key: "can_delete_messages", label: "Delete" },
                            { key: "can_pin_messages", label: "Pin" }
                        ]
                        Rectangle {
                            width: chipLab.implicitWidth + 16
                            height: 24
                            radius: 12
                            property bool on: telegramController && telegramController.permissions
                                              ? !!telegramController.permissions[modelData.key]
                                              : false
                            color: on ? "#10B98122" : "#EF444422"
                            border.color: on ? "#10B981" : "#EF4444"
                            border.width: 1
                            Text {
                                id: chipLab
                                anchors.centerIn: parent
                                text: (parent.on ? "✓ " : "✗ ") + modelData.label
                                font.pixelSize: 11
                                color: parent.on ? "#10B981" : "#EF4444"
                            }
                        }
                    }
                }

                // Issues
                Column {
                    width: parent.width
                    spacing: 4
                    visible: telegramController && telegramController.permissions
                             && telegramController.permissions.issues
                             && telegramController.permissions.issues.length > 0
                    Text {
                        text: "Issues"
                        font.pixelSize: 11
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        color: theme ? theme.critical : "#EF4444"
                    }
                    Repeater {
                        model: telegramController && telegramController.permissions
                               ? (telegramController.permissions.issues || [])
                               : []
                        Text {
                            width: parent.width
                            text: "• " + modelData
                            font.pixelSize: 12
                            color: theme ? theme.critical : "#EF4444"
                            wrapMode: Text.WordWrap
                        }
                    }
                }

                // Hints
                Column {
                    width: parent.width
                    spacing: 4
                    visible: telegramController && telegramController.permissions
                             && telegramController.permissions.hints
                             && telegramController.permissions.hints.length > 0
                    Text {
                        text: "Hints"
                        font.pixelSize: 11
                        font.family: theme ? theme.fontFamilyMono : "monospace"
                        color: theme ? theme.textMuted : "#64748B"
                    }
                    Repeater {
                        model: telegramController && telegramController.permissions
                               ? (telegramController.permissions.hints || [])
                               : []
                        Text {
                            width: parent.width
                            text: "• " + modelData
                            font.pixelSize: 12
                            color: theme ? theme.textSecondary : "#94A3B8"
                            wrapMode: Text.WordWrap
                        }
                    }
                }

                Row {
                    spacing: 10
                    AppButton {
                        text: telegramController && telegramController.busy ? "Checking…" : "Check permissions"
                        variant: "primary"
                        theme: control.theme
                        enabled: !(telegramController && telegramController.busy)
                        onClicked: {
                            control.setCfg("bot_token", tokenInput.text)
                            control.setCfg("chat_id", chatInput.text)
                            if (telegramController)
                                telegramController.checkPermissions()
                        }
                    }
                    AppButton {
                        text: "Register bot commands"
                        variant: "secondary"
                        theme: control.theme
                        enabled: !(telegramController && telegramController.busy)
                        onClicked: {
                            if (telegramController)
                                telegramController.setupCommands()
                        }
                    }
                }
            }
        }


        // Filters
        Rectangle {
            width: parent.width - 8
            height: filtCol.implicitHeight + 28
            radius: 4
            color: theme ? theme.surface : "#151C28"
            border.color: theme ? theme.border : "#1E293B"
            border.width: 1

            Column {
                id: filtCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 16
                spacing: 10

                Text {
                    text: "Alert priorities to forward"
                    font.pixelSize: 14
                    font.weight: Font.DemiBold
                    color: theme ? theme.textPrimary : "#E5E7EB"
                }

                Repeater {
                    model: [
                        { key: "send_critical", label: "CRITICAL", color: "#EF4444" },
                        { key: "send_high", label: "HIGH", color: "#F59E0B" },
                        { key: "send_medium", label: "MEDIUM", color: "#06B6D4" },
                        { key: "send_low", label: "LOW", color: "#64748B" }
                    ]
                    RowLayout {
                        width: parent.width
                        Rectangle {
                            width: 8; height: 8; radius: 4
                            color: modelData.color
                        }
                        Text {
                            text: modelData.label
                            font.pixelSize: 13
                            color: theme ? theme.textPrimary : "#E5E7EB"
                            Layout.fillWidth: true
                        }
                        AppSwitch {
                            theme: control.theme
                            checked: control.cfg(modelData.key, modelData.key === "send_critical" || modelData.key === "send_high")
                            onToggled: control.setCfg(modelData.key, checked)
                        }
                    }
                }

                Rectangle { width: parent.width; height: 1; color: theme ? theme.border : "#1E293B" }

                RowLayout {
                    width: parent.width
                    Text {
                        text: "Include location"
                        font.pixelSize: 13
                        color: theme ? theme.textPrimary : "#E5E7EB"
                        Layout.fillWidth: true
                    }
                    AppSwitch {
                        theme: control.theme
                        checked: control.cfg("include_location", true)
                        onToggled: control.setCfg("include_location", checked)
                    }
                }
                RowLayout {
                    width: parent.width
                    Text {
                        text: "Include camera name"
                        font.pixelSize: 13
                        color: theme ? theme.textPrimary : "#E5E7EB"
                        Layout.fillWidth: true
                    }
                    AppSwitch {
                        theme: control.theme
                        checked: control.cfg("include_camera", true)
                        onToggled: control.setCfg("include_camera", checked)
                    }
                }
                RowLayout {
                    width: parent.width
                    Text {
                        text: "Silent notifications (no sound on phone)"
                        font.pixelSize: 13
                        color: theme ? theme.textPrimary : "#E5E7EB"
                        Layout.fillWidth: true
                    }
                    AppSwitch {
                        theme: control.theme
                        checked: control.cfg("silent", false)
                        onToggled: control.setCfg("silent", checked)
                    }
                }
            }
        }
    }
}
