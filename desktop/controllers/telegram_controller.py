"""
Contrôleur Telegram exposé à QML.
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtProperty, pyqtSlot

from app.desktop.services.telegram_service import TelegramService


class _Worker(QThread):
    finished_ok = pyqtSignal(bool, str)

    def __init__(self, fn):
        super().__init__()
        self._fn = fn

    def run(self):
        try:
            ok, msg = self._fn()
            self.finished_ok.emit(bool(ok), str(msg))
        except Exception as exc:
            self.finished_ok.emit(False, str(exc))


class TelegramController(QObject):
    configChanged = pyqtSignal()
    testFinished = pyqtSignal(bool, str)  # success, message
    messageSent = pyqtSignal(bool, str)
    permissionsChanged = pyqtSignal()
    permissionsCheckFinished = pyqtSignal(bool, str)  # ok, summary

    def __init__(self, service: TelegramService | None = None):
        super().__init__()
        self._service = service or TelegramService()
        self._busy = False
        self._worker: _Worker | None = None
        self._permissions: dict = {}

    @pyqtProperty("QVariantMap", notify=configChanged)
    def config(self):
        return self._service.get_config()

    @pyqtProperty(bool, notify=configChanged)
    def enabled(self):
        return bool(self._service.get_config().get("enabled"))

    @pyqtProperty(bool, notify=configChanged)
    def isConfigured(self):
        return bool(self._service.get_config().get("is_configured"))

    @pyqtProperty(bool, notify=configChanged)
    def busy(self):
        return self._busy

    @pyqtSlot("QVariantMap")
    def updateConfig(self, data: dict):
        if not isinstance(data, dict):
            return
        clean = {str(k): v for k, v in data.items()}
        self._service.update_config(clean)
        self.configChanged.emit()

    @pyqtSlot(str, "QVariant")
    def setConfigValue(self, key: str, value):
        self.updateConfig({key: value})

    @pyqtSlot()
    def testConnection(self):
        if self._busy:
            return
        self._busy = True
        self.configChanged.emit()

        def job():
            return self._service.test_connection()

        self._worker = _Worker(job)
        self._worker.finished_ok.connect(self._on_test_done)
        self._worker.start()

    def _on_test_done(self, ok: bool, msg: str):
        self._busy = False
        self.configChanged.emit()
        self.testFinished.emit(ok, msg)

    @pyqtSlot(str)
    def sendTestMessage(self, text: str = "SentinelAI test"):
        if self._busy:
            return
        self._busy = True
        self.configChanged.emit()
        body = text or "🛡️ SentinelAI test message"

        def job():
            return self._service.send_message(body)

        self._worker = _Worker(job)
        self._worker.finished_ok.connect(self._on_send_done)
        self._worker.start()

    def _on_send_done(self, ok: bool, msg: str):
        self._busy = False
        self.configChanged.emit()
        self.messageSent.emit(ok, msg)


    @pyqtProperty("QVariantMap", notify=permissionsChanged)
    def permissions(self):
        return self._permissions or {}

    @pyqtProperty(bool, notify=permissionsChanged)
    def canSendMessages(self):
        return bool((self._permissions or {}).get("can_send_messages"))

    @pyqtProperty(str, notify=permissionsChanged)
    def botStatus(self):
        return str((self._permissions or {}).get("status") or "unknown")

    @pyqtSlot()
    def checkPermissions(self):
        """Vérifie les droits du bot dans le chat (async)."""
        if self._busy:
            return
        self._busy = True
        self.configChanged.emit()

        def job():
            report = self._service.check_bot_permissions()
            ok = bool(report.get("ok"))
            if ok:
                summary = (
                    f"@{report.get('bot_username') or 'bot'} · "
                    f"{report.get('chat_title') or report.get('chat_id')} · "
                    f"status={report.get('status')} · can_send=yes"
                )
            else:
                issues = report.get("issues") or ["Permission check failed"]
                summary = "; ".join(str(i) for i in issues[:3])
            # stash report on service side via return encoding
            return ok, summary + "|||" + __import__("json").dumps(report)

        self._worker = _Worker(job)
        self._worker.finished_ok.connect(self._on_perm_done)
        self._worker.start()

    def _on_perm_done(self, ok: bool, payload: str):
        self._busy = False
        summary = payload
        report = {}
        if "|||" in payload:
            summary, raw = payload.split("|||", 1)
            try:
                report = __import__("json").loads(raw)
            except Exception:
                report = {}
        self._permissions = report if isinstance(report, dict) else {}
        self.permissionsChanged.emit()
        self.configChanged.emit()
        self.permissionsCheckFinished.emit(bool(ok), summary)

    @pyqtSlot()
    def setupCommands(self):
        if self._busy:
            return
        self._busy = True
        self.configChanged.emit()

        def job():
            return self._service.setup_default_commands()

        self._worker = _Worker(job)

        def done(ok, msg):
            self._busy = False
            self.configChanged.emit()
            self.testFinished.emit(ok, "Commands registered" if ok else str(msg))

        self._worker.finished_ok.connect(done)
        self._worker.start()

    def notify_alert(self, alert: dict):
        """Appelé depuis Application sur alertReceived."""
        try:
            if self._permissions and self._permissions.get("can_send_messages") is False:
                print("[Telegram] skip alert: bot cannot send messages")
                return
            self._service.send_alert(alert)
        except Exception as exc:
            print(f"[Telegram] alert send failed: {exc}")
