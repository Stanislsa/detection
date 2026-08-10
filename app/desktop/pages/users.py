"""
Page Utilisateurs avec tableau et actions d'administration.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QFrame, QHeaderView, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import List, Dict, Optional

from app.desktop.models.user import User, UserRole
from app.desktop.components.badge import Badge
from app.desktop.components.dialogs import UserDialog, ConfirmDialog
from app.desktop.services.notification_service import NotificationType


class UsersPage(QWidget):
    """
    Page Utilisateurs avec tableau de gestion.
    """
    
    def __init__(self, api_client=None, notification_service=None, parent=None):
        super().__init__(parent)
        
        self.api_client = api_client
        self.notification_service = notification_service
        self.users: List[User] = []
        self._init_ui()
        self._load_users()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Titre de la page et boutons
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Utilisateurs")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20pt;
                font-weight: 700;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Recherche
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Rechercher un utilisateur...")
        search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
                min-width: 300px;
            }
        """)
        header_layout.addWidget(search_input)
        
        header_layout.addStretch()
        
        # Bouton ajouter
        add_btn = QPushButton("+ Ajouter un utilisateur")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        add_btn.clicked.connect(self._add_user)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Tableau des utilisateurs
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "Nom", "Email", "Rôle", "Dernière connexion", "Actions"
        ])
        
        self.users_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                gridline-color: #4A4A6A;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3D3D5C;
                color: #FFFFFF;
            }
            QTableWidget::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
            }
            QTableWidget::header {
                background-color: #2D2D44;
                border-bottom: 2px solid #4A4A6A;
                padding: 12px;
                font-weight: 600;
            }
            QTableWidget::header::section {
                background-color: #2D2D44;
                color: #FFFFFF;
                padding: 12px;
                border: none;
                border-right: 1px solid #4A4A6A;
                font-weight: 600;
            }
        """)
        
        # Configuration des colonnes
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Nom
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Email
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Rôle
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Dernière connexion
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        
        self.users_table.setAlternatingRowColors(True)
        self.users_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.users_table)
    
    def _load_users(self):
        """Charge les utilisateurs depuis l'API ou utilise des données d'exemple."""
        if self.api_client:
            response = self.api_client.get_users()
            if response.success and response.data:
                self.users = [User.from_dict(u) for u in response.data]
            else:
                self.users = []
        else:
            # Données d'exemple si pas d'API
            from datetime import datetime, timedelta
            self.users = [
                User(
                    id=1,
                    username="jdupont",
                    email="jean.dupont@example.com",
                    full_name="Jean Dupont",
                    role=UserRole.ADMIN,
                    is_active=True,
                    last_login=datetime.now() - timedelta(hours=2)
                ),
                User(
                    id=2,
                    username="mmartin",
                    email="marie.martin@example.com",
                    full_name="Marie Martin",
                    role=UserRole.OPERATOR,
                    is_active=True,
                    last_login=datetime.now() - timedelta(hours=3)
                ),
                User(
                    id=3,
                    username="pbernard",
                    email="pierre.bernard@example.com",
                    full_name="Pierre Bernard",
                    role=UserRole.OPERATOR,
                    is_active=True,
                    last_login=datetime.now() - timedelta(days=1)
                ),
            ]
        
        self._populate_table()
    
    def _populate_table(self):
        """Remplit le tableau avec les utilisateurs."""
        self.users_table.setRowCount(len(self.users))
        
        for row, user in enumerate(self.users):
            # Nom
            self.users_table.setItem(row, 0, QTableWidgetItem(user.full_name))
            
            # Email
            self.users_table.setItem(row, 1, QTableWidgetItem(user.email))
            
            # Rôle (badge)
            role_widget = QWidget()
            role_layout = QHBoxLayout(role_widget)
            role_layout.setContentsMargins(8, 4, 8, 4)
            
            role_colors = {
                UserRole.ADMIN: "danger",
                UserRole.OPERATOR: "primary",
                UserRole.VIEWER: "success"
            }
            role_names = {
                UserRole.ADMIN: "Administrateur",
                UserRole.OPERATOR: "Opérateur",
                UserRole.VIEWER: "Visualiseur"
            }
            badge = Badge(
                role_names.get(user.role, user.role.value),
                role_colors.get(user.role, "default")
            )
            role_layout.addWidget(badge)
            role_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.users_table.setCellWidget(row, 2, role_widget)
            
            # Dernière connexion
            from app.desktop.utils.formatters import format_datetime
            self.users_table.setItem(row, 3, QTableWidgetItem(format_datetime(user.last_login)))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(8, 4, 8, 4)
            
            edit_btn = QPushButton("✏")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            edit_btn.clicked.connect(lambda _, u=user: self._edit_user(u))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                }
            """)
            delete_btn.clicked.connect(lambda _, u=user: self._delete_user(u))
            actions_layout.addWidget(delete_btn)
            
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.users_table.setCellWidget(row, 4, actions_widget)
    
    def _add_user(self):
        """Ajoute un nouvel utilisateur."""
        dialog = UserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_data = dialog.get_data()
            
            if self.api_client:
                response = self.api_client.create_user(user_data)
                if response.success:
                    self._load_users()
                    if self.notification_service:
                        self.notification_service.add_notification(
                            "Utilisateur créé",
                            f"L'utilisateur {user_data['full_name']} a été créé",
                            NotificationType.SUCCESS
                        )
            else:
                # Mode hors ligne
                new_user = User(
                    id=len(self.users) + 1,
                    username=user_data["email"].split("@")[0],
                    email=user_data["email"],
                    full_name=user_data["name"],
                    role=UserRole(user_data["role"].lower()),
                    is_active=user_data["active"]
                )
                self.users.append(new_user)
                self._populate_table()
    
    def _edit_user(self, user: User):
        """
        Modifie un utilisateur.
        
        Args:
            user: Utilisateur à modifier
        """
        user_data = {
            "name": user.full_name,
            "email": user.email,
            "role": user.role.value,
            "active": user.is_active
        }
        dialog = UserDialog(user_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            
            if self.api_client:
                response = self.api_client.update_user(user.id, new_data)
                if response.success:
                    self._load_users()
                    if self.notification_service:
                        self.notification_service.add_notification(
                            "Utilisateur modifié",
                            f"L'utilisateur {new_data['name']} a été modifié",
                            NotificationType.SUCCESS
                        )
    
    def _delete_user(self, user: User):
        """
        Supprime un utilisateur.
        
        Args:
            user: Utilisateur à supprimer
        """
        dialog = ConfirmDialog(
            "Supprimer l'utilisateur",
            f"Êtes-vous sûr de vouloir supprimer l'utilisateur {user.full_name} ?",
            self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if self.api_client:
                response = self.api_client.delete_user(user.id)
                if response.success:
                    self._load_users()
                    if self.notification_service:
                        self.notification_service.add_notification(
                            "Utilisateur supprimé",
                            f"L'utilisateur {user.full_name} a été supprimé",
                            NotificationType.SUCCESS
                        )
            else:
                # Mode hors ligne
                self.users = [u for u in self.users if u.id != user.id]
                self._populate_table()
