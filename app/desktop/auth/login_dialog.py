"""
Écran de connexion avec authentification JWT et OTP.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFrame, QStackedWidget, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from typing import Optional

from app.desktop.services.api_client import APIClient, APIResponse
from app.desktop.services.notification_service import NotificationService, NotificationType


class LoginDialog(QDialog):
    """
    Boîte de dialogue de connexion avec JWT et OTP.
    """
    
    # Signal émis lors de la connexion réussie
    login_success = pyqtSignal(str, str)  # access_token, refresh_token
    
    def __init__(self, api_client: APIClient, notification_service: Optional[NotificationService] = None, parent=None):
        super().__init__(parent)
        
        self.api_client = api_client
        self.notification_service = notification_service
        self.mfa_required = False
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setWindowTitle("Connexion - Surveillance IA")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E2F;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 10pt;
            }
            QLineEdit {
                background-color: #2D2D44;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
            }
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:disabled {
                background-color: #4A4A6A;
                color: #A0A0B0;
            }
            QCheckBox {
                color: #A0A0B0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #4A4A6A;
                border-radius: 4px;
                background-color: #1E1E2F;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Titre
        title_label = QLabel("Surveillance IA")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24pt;
                font-weight: 700;
                text-align: center;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Sous-titre
        subtitle_label = QLabel("Connexion à votre compte")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #A0A0B0;
                font-size: 11pt;
                text-align: center;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Stack pour les différentes étapes
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # Page 1: Identifiants
        self._create_credentials_page()
        
        # Page 2: MFA
        self._create_mfa_page()
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #4A4A6A;")
        layout.addWidget(separator)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.remember_check = QCheckBox("Se souvenir de moi")
        options_layout.addWidget(self.remember_check)
        
        options_layout.addStretch()
        
        layout.addLayout(options_layout)
    
    def _create_credentials_page(self):
        """Crée la page d'identifiants."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        
        # Nom d'utilisateur
        username_label = QLabel("Nom d'utilisateur")
        username_label.setStyleSheet("color: #A0A0B0; font-size: 9pt;")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        layout.addWidget(self.username_input)
        
        # Mot de passe
        password_label = QLabel("Mot de passe")
        password_label.setStyleSheet("color: #A0A0B0; font-size: 9pt;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        layout.addWidget(self.password_input)
        
        # Bouton de connexion
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.clicked.connect(self._attempt_login)
        layout.addWidget(self.login_btn)
        
        # Message d'erreur
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #EF4444; font-size: 9pt;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)
        
        layout.addStretch()
        self.stack.addWidget(page)
    
    def _create_mfa_page(self):
        """Crée la page MFA."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        
        # Message
        mfa_label = QLabel("Authentification à deux facteurs")
        mfa_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14pt;
                font-weight: 600;
                text-align: center;
            }
        """)
        mfa_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(mfa_label)
        
        info_label = QLabel("Entrez le code depuis votre application d'authentification")
        info_label.setStyleSheet("color: #A0A0B0; font-size: 10pt; text-align: center;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Code OTP
        otp_label = QLabel("Code OTP")
        otp_label.setStyleSheet("color: #A0A0B0; font-size: 9pt;")
        layout.addWidget(otp_label)
        
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("000000")
        self.otp_input.setMaxLength(6)
        self.otp_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.otp_input)
        
        # Bouton de vérification
        self.verify_btn = QPushButton("Vérifier")
        self.verify_btn.clicked.connect(self._verify_mfa)
        layout.addWidget(self.verify_btn)
        
        # Bouton retour
        back_btn = QPushButton("Retour")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3D3D5C;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #4A4A6A;
            }
        """)
        back_btn.clicked.connect(self._back_to_credentials)
        layout.addWidget(back_btn)
        
        # Message d'erreur
        self.mfa_error_label = QLabel()
        self.mfa_error_label.setStyleSheet("color: #EF4444; font-size: 9pt;")
        self.mfa_error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.mfa_error_label)
        
        layout.addStretch()
        self.stack.addWidget(page)
    
    def _attempt_login(self):
        """Tente la connexion avec les identifiants."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.error_label.setText("Veuillez remplir tous les champs")
            return
        
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Connexion en cours...")
        
        # Appeler l'API
        response = self.api_client.login(username, password, None)
        
        self.login_btn.setEnabled(True)
        self.login_btn.setText("Se connecter")
        
        if response.success:
            # Vérifier si MFA est requis
            if response.data and response.data.get("mfa_required"):
                self.mfa_required = True
                self.stack.setCurrentIndex(1)  # Page MFA
            else:
                # Connexion réussie sans MFA
                self._handle_login_success(response.data)
        elif response.error == "MFA required" or (response.data and isinstance(response.data, dict) and response.data.get("mfa_required")):
            self.mfa_required = True
            self.stack.setCurrentIndex(1)  # Page MFA
        else:
            self.error_label.setText(response.error or "Erreur de connexion")
    
    def _verify_mfa(self):
        """Vérifie le code MFA."""
        otp_code = self.otp_input.text().strip()
        
        if len(otp_code) != 6:
            self.mfa_error_label.setText("Le code doit contenir 6 chiffres")
            return
        
        self.verify_btn.setEnabled(False)
        self.verify_btn.setText("Vérification en cours...")
        
        # Appeler l'API avec le code OTP
        response = self.api_client.verify_mfa(otp_code)
        
        self.verify_btn.setEnabled(True)
        self.verify_btn.setText("Vérifier")
        
        if response.success:
            self._handle_login_success(response.data)
        else:
            self.mfa_error_label.setText(response.error or "Code invalide")
    
    def _handle_login_success(self, data: dict):
        """
        Gère la connexion réussie.
        
        Args:
            data: Données de réponse (tokens)
        """
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        
        if access_token and refresh_token:
            self.api_client.set_auth_tokens(access_token, refresh_token)
            if self.notification_service:
                self.notification_service.add_notification(
                    "Connexion réussie",
                    "Vous êtes maintenant connecté",
                    NotificationType.SUCCESS
                )
            self.login_success.emit(access_token, refresh_token)
            self.accept()
        else:
            self.error_label.setText("Erreur lors de la récupération des tokens")
    
    def _back_to_credentials(self):
        """Retourne à la page d'identifiants."""
        self.stack.setCurrentIndex(0)
        self.otp_input.clear()
        self.mfa_error_label.clear()
    
    def showEvent(self, event):
        """Gère l'affichage de la boîte de dialogue."""
        super().showEvent(event)
        self.username_input.setFocus()
