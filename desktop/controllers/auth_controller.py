from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot, QThread
from desktop.services.api_client import get_api_client, ApiError, ApiClient
class _LoginWorker(QThread):
    finished_ok=pyqtSignal(dict); finished_err=pyqtSignal(str)
    def __init__(self, client, username, password, parent=None):
        super().__init__(parent); self._client,self._username,self._password=client,username,password
    def run(self):
        try: self.finished_ok.emit(self._client.login(self._username, self._password))
        except ApiError as e: self.finished_err.emit(str(e.detail or e))
        except Exception as e: self.finished_err.emit(str(e))
class AuthController(QObject):
    DEMO_USER, DEMO_PASSWORD = "admin", "azerty"
    loginSuccess=pyqtSignal(); loginFailed=pyqtSignal(str)
    twoFactorRequired=pyqtSignal(); twoFactorSuccess=pyqtSignal(); twoFactorFailed=pyqtSignal(str)
    passwordResetSent=pyqtSignal(); passwordResetFailed=pyqtSignal(str)
    backendStatusChanged=pyqtSignal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._client=get_api_client(); self._is_authenticated=False
        self._user_email=self._user_role=""; self._use_demo=False; self._worker=None
        self._client.connectionChanged.connect(self.backendStatusChanged)
    @pyqtProperty(bool, notify=loginSuccess)
    def isAuthenticated(self): return self._is_authenticated
    @pyqtProperty(str, notify=loginSuccess)
    def userEmail(self): return self._user_email
    @pyqtProperty(str, notify=loginSuccess)
    def userRole(self): return self._user_role
    @pyqtProperty(bool, notify=backendStatusChanged)
    def backendOnline(self): return self._client.is_online
    @pyqtSlot(str, str)
    def login(self, email, password):
        email, password = (email or "").strip(), password or ""
        if not email or not password: self.loginFailed.emit("Email and password are required"); return
        if self._worker and self._worker.isRunning(): self._worker.terminate(); self._worker.wait(500)
        self._worker=_LoginWorker(self._client, email, password, self)
        self._worker.finished_ok.connect(self._on_ok)
        self._worker.finished_err.connect(lambda m: self._on_err(m, email, password))
        self._worker.start()
    def _on_ok(self, result):
        user=result.get("user") or {}
        self._user_email=user.get("email") or user.get("username") or ""
        self._user_role=user.get("role") or ""; self._use_demo=False
        self._is_authenticated=True; self.loginSuccess.emit()
    def _on_err(self, message, email, password):
        if "unreachable" in message.lower() or "connection" in message.lower():
            if email==self.DEMO_USER and password==self.DEMO_PASSWORD:
                self._user_email,self._user_role,self._use_demo=email,"admin",True
                self.twoFactorRequired.emit(); return
            self.loginFailed.emit("Backend unreachable. Demo: admin / azerty"); return
        self.loginFailed.emit(message or "Invalid credentials")
    @pyqtSlot(str)
    def verify_two_factor(self, code):
        if len((code or "").strip())==6 and code.strip().isdigit():
            self._is_authenticated=True; self.loginSuccess.emit(); self.twoFactorSuccess.emit()
        else: self.twoFactorFailed.emit("Invalid verification code (6 digits)")
    @pyqtSlot(str)
    def verifyTwoFactor(self, code): self.verify_two_factor(code)
    @pyqtSlot(str)
    def requestPasswordReset(self, email): self.request_password_reset(email)
    @pyqtSlot(str)
    def request_password_reset(self, email):
        if (email or "").strip(): self.passwordResetSent.emit()
        else: self.passwordResetFailed.emit("Email required")
    @pyqtSlot()
    def logout(self):
        self._client.logout(); self._is_authenticated=False
        self._user_email=self._user_role=""; self._use_demo=False
