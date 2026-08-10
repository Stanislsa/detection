"""
Barre latérale de navigation.
Style Windows 11 avec icônes et animations.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon


class Sidebar(QWidget):
    """
    Barre latérale avec navigation.
    """
    
    # Signal émis lors de la sélection d'une page
    page_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_page = "dashboard"
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)
        
        # Logo / Titre
        title_label = QLabel("Surveillance IA")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 16pt;
                font-weight: 700;
                padding: 20px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #4A4A6A;")
        layout.addWidget(separator)
        
        # Boutons de navigation
        self.buttons = {}
        
        nav_items = [
            ("dashboard", "Tableau de bord"),
            ("cameras", "Caméras"),
            ("alerts", "Alertes"),
        ]
        
        # Ajouter le bouton Entraînement seulement si disponible
        try:
            from app.desktop.main_window import TRAINING_AVAILABLE
            if TRAINING_AVAILABLE:
                nav_items.append(("training", "Entraînement"))
        except ImportError:
            pass
        
        nav_items.extend([
            ("statistics", "Statistiques"),
            ("users", "Utilisateurs"),
            ("settings", "Paramètres"),
        ])
        
        for page_id, label in nav_items:
            btn = self._create_nav_button(page_id, label)
            self.buttons[page_id] = btn
            layout.addWidget(btn)
        
        # Espaceur
        layout.addStretch()
        
        # Bouton déconnexion
        logout_btn = QPushButton("Déconnexion")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                text-align: left;
                font-size: 10pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        logout_btn.clicked.connect(self._logout)
        layout.addWidget(logout_btn)
    
    def _create_nav_button(self, page_id: str, label: str) -> QPushButton:
        """
        Crée un bouton de navigation.
        
        Args:
            page_id: ID de la page
            label: Texte du bouton
        
        Returns:
            QPushButton configuré
        """
        btn = QPushButton(label)
        btn.setObjectName(page_id)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 12px 20px;
                text-align: left;
                color: #A0A0B0;
                border-radius: 8px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #3D3D5C;
                color: #FFFFFF;
            }
            QPushButton:active {
                background-color: #2563EB;
                color: #FFFFFF;
            }
        """)
        
        btn.clicked.connect(lambda: self._on_button_clicked(page_id))
        
        return btn
    
    def _on_button_clicked(self, page_id: str):
        """
        Gère le clic sur un bouton de navigation.
        
        Args:
            page_id: ID de la page sélectionnée
        """
        self.page_selected.emit(page_id)
    
    def set_active_page(self, page_id: str):
        """
        Définit la page active.
        
        Args:
            page_id: ID de la page à activer
        """
        self.current_page = page_id
        
        # Réinitialiser tous les boutons
        for btn_id, btn in self.buttons.items():
            if btn_id == page_id:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2563EB;
                        color: #FFFFFF;
                        border: none;
                        padding: 12px 20px;
                        text-align: left;
                        border-radius: 8px;
                        font-size: 10pt;
                        font-weight: 600;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        padding: 12px 20px;
                        text-align: left;
                        color: #A0A0B0;
                        border-radius: 8px;
                        font-size: 10pt;
                    }
                    QPushButton:hover {
                        background-color: #3D3D5C;
                        color: #FFFFFF;
                    }
                """)
    
    def _logout(self):
        """Gère la déconnexion."""
        # TODO: Implémenter la logique de déconnexion
        self.page_selected.emit("logout")
