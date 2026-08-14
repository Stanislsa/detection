"""
Contrôleur pour l'authentification.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot


class AuthController(QObject):
    """Contrôleur d'authentification accessible depuis QML."""

    # Credentials temporaires
    TEMP_EMAIL = "admin"
    TEMP_PASSWORD = "azerty"

    loginSuccess = pyqtSignal()
    loginFailed = pyqtSignal(str)
    twoFactorRequired = pyqtSignal()
    twoFactorSuccess = pyqtSignal()
    twoFactorFailed = pyqtSignal(str)
    passwordResetSent = pyqtSignal()
    passwordResetFailed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._is_authenticated = False
        self._user_email = ""

    @pyqtProperty(bool, notify=loginSuccess)
    def isAuthenticated(self):
        return self._is_authenticated

    @pyqtProperty(str, notify=loginSuccess)
    def userEmail(self):
        return self._user_email

    @pyqtSlot(str, str)
    def login(self, email: str, password: str):
        """Tente de connecter l'utilisateur."""
        if email == self.TEMP_EMAIL and password == self.TEMP_PASSWORD:
            self._user_email = email
            self._is_authenticated = True
            self.twoFactorRequired.emit()
        else:
            self.loginFailed.emit("Invalid email or password")

    @pyqtSlot(str)
    def verify_two_factor(self, code: str):
        """Vérifie le code 2FA."""
        # Temporairement, accepte n'importe quel code à 6 chiffres
        if len(code) == 6 and code.isdigit():
            self.loginSuccess.emit()
        else:
            self.twoFactorFailed.emit("Invalid verification code")

    @pyqtSlot(str)
    def request_password_reset(self, email: str):
        """Demande une réinitialisation de mot de passe."""
        if email == self.TEMP_EMAIL:
            self.passwordResetSent.emit()
        else:
            self.passwordResetFailed.emit("Email not found")

    @pyqtSlot()
    def logout(self):
        """Déconnecte l'utilisateur."""
        self._is_authenticated = False
        self._user_email = ""
