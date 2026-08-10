"""
Barre supérieure de l'application.
Affiche le titre, notifications, heure, connexion et profil.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class Header(QWidget):
    """
    Barre supérieure avec informations système.
    """
    
    # Signal pour les actions
    notifications_clicked = pyqtSignal()
    profile_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.user_name = "Admin"
        self.is_connected = True
        self.notification_count = 3
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(16)
        
        # Titre de l'application
        app_title = QLabel("Surveillance IA")
        app_title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14pt;
                font-weight: 700;
            }
        """)
        layout.addWidget(app_title)
        
        # Espaceur
        layout.addStretch()
        
        # Statut de connexion
        self.connection_status = QLabel()
        self.connection_status.setStyleSheet("""
            QLabel {
                color: #10B981;
                font-size: 9pt;
                font-weight: 600;
                padding: 6px 12px;
                background-color: rgba(16, 185, 129, 0.1);
                border-radius: 6px;
            }
        """)
        self._update_connection_label()
        layout.addWidget(self.connection_status)
        
        # Heure
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #A0A0B0;
                font-size: 10pt;
                font-weight: 500;
            }
        """)
        layout.addWidget(self.time_label)
        
        # Notifications
        self.notification_btn = QPushButton()
        self.notification_btn.setStyleSheet("""
            QPushButton {
                background-color: #3D3D5C;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #4A4A6A;
            }
        """)
        self.notification_btn.setText(f"🔔 {self.notification_count}")
        self.notification_btn.clicked.connect(self.notifications_clicked.emit)
        layout.addWidget(self.notification_btn)
        
        # Profil utilisateur
        self.profile_btn = QPushButton()
        self.profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                color: #FFFFFF;
                font-size: 10pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        self.profile_btn.setText(f"👤 {self.user_name}")
        self.profile_btn.clicked.connect(self.profile_clicked.emit)
        layout.addWidget(self.profile_btn)
    
    def update_time(self, time_str: str):
        """
        Met à jour l'heure affichée.
        
        Args:
            time_str: Heure au format HH:MM:SS
        """
        self.time_label.setText(time_str)
    
    def update_connection_status(self, connected: bool):
        """
        Met à jour le statut de connexion.
        
        Args:
            connected: True si connecté
        """
        self.is_connected = connected
        self._update_connection_label()
    
    def _update_connection_label(self):
        """Met à jour le label de connexion."""
        if self.is_connected:
            self.connection_status.setText("● En ligne")
            self.connection_status.setStyleSheet("""
                QLabel {
                    color: #10B981;
                    font-size: 9pt;
                    font-weight: 600;
                    padding: 6px 12px;
                    background-color: rgba(16, 185, 129, 0.1);
                    border-radius: 6px;
                }
            """)
        else:
            self.connection_status.setText("● Hors ligne")
            self.connection_status.setStyleSheet("""
                QLabel {
                    color: #EF4444;
                    font-size: 9pt;
                    font-weight: 600;
                    padding: 6px 12px;
                    background-color: rgba(239, 68, 68, 0.1);
                    border-radius: 6px;
                }
            """)
    
    def set_notification_count(self, count: int):
        """
        Définit le nombre de notifications.
        
        Args:
            count: Nombre de notifications
        """
        self.notification_count = count
        self.notification_btn.setText(f"🔔 {count}")
    
    def set_user_name(self, name: str):
        """
        Définit le nom de l'utilisateur.
        
        Args:
            name: Nom de l'utilisateur
        """
        self.user_name = name
        self.profile_btn.setText(f"👤 {name}")
