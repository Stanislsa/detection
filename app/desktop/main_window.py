"""
Fenêtre principale de l'application Desktop Surveillance IA.
Style Windows 11 Dark Mode avec PyQt6.
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
from typing import Optional

from app.desktop.styles import STYLES
from app.desktop.sidebar import Sidebar
from app.desktop.header import Header
from app.desktop.pages.dashboard import DashboardPage
from app.desktop.pages.alerts import AlertsPage
from app.desktop.pages.cameras import CamerasPage
try:
    from app.desktop.pages.training import TrainingPage
    TRAINING_AVAILABLE = True
except ImportError:
    TRAINING_AVAILABLE = False
    print("WARNING: Module d'entraînement non disponible (PyTorch/Ultralytics requis)")
from app.desktop.pages.statistics import StatisticsPage
from app.desktop.pages.users import UsersPage
from app.desktop.pages.settings import SettingsPage


class MainWindow(QMainWindow):
    """
    Fenêtre principale avec navigation latérale et pages.
    """
    
    # Signal pour les notifications
    notification_signal = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Surveillance IA - Détection de Chutes")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(STYLES)
        
        # État de l'application
        self.current_page = "dashboard"
        self.is_connected = True
        self.user_name = "Admin"
        
        # Initialiser l'UI
        self._init_ui()
        self._init_timer()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Barre latérale
        self.sidebar = Sidebar(self)
        self.sidebar.setFixedWidth(260)
        self.sidebar.page_selected.connect(self._navigate_to_page)
        main_layout.addWidget(self.sidebar)
        
        # Zone de contenu
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header
        self.header = Header(self)
        self.header.setFixedHeight(64)
        content_layout.addWidget(self.header)
        
        # Stack de pages
        self.pages_stack = QStackedWidget()
        content_layout.addWidget(self.pages_stack)
        
        main_layout.addWidget(content_widget)
        
        # Initialiser les pages
        self._init_pages()
    
    def _init_pages(self):
        """Initialise toutes les pages."""
        # Tableau de bord
        self.dashboard_page = DashboardPage(self)
        self.pages_stack.addWidget(self.dashboard_page)
        
        # Alertes
        self.alerts_page = AlertsPage(self)
        self.pages_stack.addWidget(self.alerts_page)
        
        # Caméras
        self.cameras_page = CamerasPage(self)
        self.pages_stack.addWidget(self.cameras_page)
        
        # Entraînement (optionnel)
        if TRAINING_AVAILABLE:
            self.training_page = TrainingPage(self)
            self.pages_stack.addWidget(self.training_page)
        
        # Statistiques
        self.statistics_page = StatisticsPage(self)
        self.pages_stack.addWidget(self.statistics_page)
        
        # Utilisateurs
        self.users_page = UsersPage(self)
        self.pages_stack.addWidget(self.users_page)
        
        # Paramètres
        self.settings_page = SettingsPage(self)
        self.pages_stack.addWidget(self.settings_page)
    
    def _init_timer(self):
        """Initialise le timer pour l'heure et les mises à jour."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)  # Mise à jour chaque seconde
    
    def _update_time(self):
        """Met à jour l'heure affichée dans le header."""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.header.update_time(current_time)
    
    def _navigate_to_page(self, page_name: str):
        """
        Navigue vers une page spécifique.
        
        Args:
            page_name: Nom de la page (dashboard, alerts, cameras, etc.)
        """
        if TRAINING_AVAILABLE:
            page_map = {
                "dashboard": 0,
                "alerts": 1,
                "cameras": 2,
                "training": 3,
                "statistics": 4,
                "users": 5,
                "settings": 6
            }
        else:
            page_map = {
                "dashboard": 0,
                "alerts": 1,
                "cameras": 2,
                "statistics": 3,
                "users": 4,
                "settings": 5
            }
        
        if page_name in page_map:
            self.pages_stack.setCurrentIndex(page_map[page_name])
            self.current_page = page_name
            self.sidebar.set_active_page(page_name)
    
    def show_notification(self, title: str, message: str):
        """
        Affiche une notification.
        
        Args:
            title: Titre de la notification
            message: Message de la notification
        """
        self.notification_signal.emit(title, message)
    
    def set_connection_status(self, connected: bool):
        """
        Définit le statut de connexion.
        
        Args:
            connected: True si connecté
        """
        self.is_connected = connected
        self.header.update_connection_status(connected)


def main():
    """Point d'entrée de l'application."""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Configuration de la police
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
