"""
Composants Dialogs réutilisables.
Boîtes de dialogue pour ajouter/modifier caméras et utilisateurs.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QSpinBox, QCheckBox, QFormLayout,
    QTextEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class BaseDialog(QDialog):
    """
    Boîte de dialogue de base avec style cohérent.
    """
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E2F;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 10pt;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                background-color: #2D2D44;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #2563EB;
            }
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 10pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:cancel {
                background-color: #3D3D5C;
            }
            QPushButton:cancel:hover {
                background-color: #4A4A6A;
            }
        """)


class CameraDialog(BaseDialog):
    """
    Boîte de dialogue pour ajouter/modifier une caméra.
    """
    
    def __init__(self, camera_data: dict = None, parent=None):
        title = "Modifier la caméra" if camera_data else "Ajouter une caméra"
        super().__init__(title, parent)
        
        self.camera_data = camera_data or {}
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Nom
        self.name_input = QLineEdit()
        self.name_input.setText(self.camera_data.get("name", ""))
        self.name_input.setPlaceholderText("Ex: Caméra Salon")
        form_layout.addRow("Nom :", self.name_input)
        
        # Type de source
        self.source_type_combo = QComboBox()
        self.source_type_combo.addItems(["Webcam", "RTSP", "Fichier vidéo"])
        form_layout.addRow("Type de source :", self.source_type_combo)
        
        # Source (URL ou index)
        self.source_input = QLineEdit()
        self.source_input.setText(self.camera_data.get("source", ""))
        self.source_input.setPlaceholderText("0, rtsp://..., ou chemin fichier")
        form_layout.addRow("Source :", self.source_input)
        
        # Résolution
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["640x480", "1280x720", "1920x1080"])
        form_layout.addRow("Résolution :", self.resolution_combo)
        
        # FPS
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(self.camera_data.get("fps", 30))
        form_layout.addRow("FPS :", self.fps_spin)
        
        # Actif
        self.active_check = QCheckBox()
        self.active_check.setChecked(self.camera_data.get("active", True))
        form_layout.addRow("Actif :", self.active_check)
        
        layout.addLayout(form_layout)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setProperty("cancel", True)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def get_data(self) -> dict:
        """
        Retourne les données du formulaire.
        
        Returns:
            Dictionnaire avec les données de la caméra
        """
        return {
            "name": self.name_input.text(),
            "source_type": self.source_type_combo.currentText(),
            "source": self.source_input.text(),
            "resolution": self.resolution_combo.currentText(),
            "fps": self.fps_spin.value(),
            "active": self.active_check.isChecked()
        }


class UserDialog(BaseDialog):
    """
    Boîte de dialogue pour ajouter/modifier un utilisateur.
    """
    
    def __init__(self, user_data: dict = None, parent=None):
        title = "Modifier l'utilisateur" if user_data else "Ajouter un utilisateur"
        super().__init__(title, parent)
        
        self.user_data = user_data or {}
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Nom
        self.name_input = QLineEdit()
        self.name_input.setText(self.user_data.get("name", ""))
        self.name_input.setPlaceholderText("Jean Dupont")
        form_layout.addRow("Nom complet :", self.name_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setText(self.user_data.get("email", ""))
        self.email_input.setPlaceholderText("jean.dupont@example.com")
        form_layout.addRow("Email :", self.email_input)
        
        # Rôle
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Administrateur", "Opérateur", "Visualiseur"])
        current_role = self.user_data.get("role", "Opérateur")
        index = self.role_combo.findText(current_role)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)
        form_layout.addRow("Rôle :", self.role_combo)
        
        # Mot de passe (optionnel pour modification)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Laisser vide pour ne pas changer")
        form_layout.addRow("Mot de passe :", self.password_input)
        
        # Actif
        self.active_check = QCheckBox()
        self.active_check.setChecked(self.user_data.get("active", True))
        form_layout.addRow("Actif :", self.active_check)
        
        layout.addLayout(form_layout)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setProperty("cancel", True)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def get_data(self) -> dict:
        """
        Retourne les données du formulaire.
        
        Returns:
            Dictionnaire avec les données de l'utilisateur
        """
        return {
            "name": self.name_input.text(),
            "email": self.email_input.text(),
            "role": self.role_combo.currentText(),
            "password": self.password_input.text(),
            "active": self.active_check.isChecked()
        }


class ConfirmDialog(BaseDialog):
    """
    Boîte de dialogue de confirmation.
    """
    
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(title, parent)
        
        self.message = message
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 11pt;
                padding: 20px 0;
            }
        """)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setProperty("cancel", True)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        confirm_btn = QPushButton("Confirmer")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 10pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        confirm_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(confirm_btn)
        
        layout.addLayout(buttons_layout)


class AlertDetailDialog(BaseDialog):
    """
    Boîte de dialogue pour les détails d'une alerte.
    """
    
    def __init__(self, alert_data: dict, parent=None):
        super().__init__("Détails de l'alerte", parent)
        
        self.alert_data = alert_data
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Informations de l'alerte
        info_layout = QFormLayout()
        
        info_layout.addRow("Date :", QLabel(self.alert_data.get("date", "")))
        info_layout.addRow("Heure :", QLabel(self.alert_data.get("time", "")))
        info_layout.addRow("Caméra :", QLabel(self.alert_data.get("camera", "")))
        info_layout.addRow("Type :", QLabel(self.alert_data.get("type", "")))
        info_layout.addRow("Gravité :", QLabel(self.alert_data.get("severity", "")))
        
        layout.addLayout(info_layout)
        
        # Description
        desc_label = QLabel("Description :")
        desc_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(desc_label)
        
        desc_text = QTextEdit()
        desc_text.setText(self.alert_data.get("description", "Aucune description disponible"))
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(100)
        layout.addWidget(desc_text)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        actions_layout.addWidget(close_btn)
        
        layout.addLayout(actions_layout)
