"""
Composant Card réutilisable.
Carte avec coins arrondis et style cohérent.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class Card(QFrame):
    """
    Carte générique avec style Dark Mode.
    """
    
    def __init__(self, title: str = None, parent=None):
        super().__init__(parent)
        
        self.title = title
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setStyleSheet("""
            QFrame {
                background-color: #2D2D44;
                border-radius: 12px;
                border: 1px solid #4A4A6A;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-size: 12pt;
                    font-weight: 600;
                    margin-bottom: 12px;
                }
            """)
            layout.addWidget(title_label)
        
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
    
    def add_widget(self, widget):
        """
        Ajoute un widget au contenu de la carte.
        
        Args:
            widget: Widget à ajouter
        """
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """
        Ajoute un layout au contenu de la carte.
        
        Args:
            layout: Layout à ajouter
        """
        self.content_layout.addLayout(layout)


class StatCard(Card):
    """
    Carte de statistique avec titre et valeur.
    """
    
    def __init__(self, title: str, value: str, color: str = "#2563EB", parent=None):
        super().__init__(title, parent)
        
        self.value = value
        self.color = color
        self._init_stat_ui()
    
    def _init_stat_ui(self):
        """Initialise l'interface de statistique."""
        value_label = QLabel(self.value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 24pt;
                font-weight: 700;
            }}
        """)
        self.content_layout.addWidget(value_label)
    
    def update_value(self, new_value: str):
        """
        Met à jour la valeur affichée.
        
        Args:
            new_value: Nouvelle valeur
        """
        self.value = new_value
        if self.content_layout.count() > 0:
            widget = self.content_layout.itemAt(0).widget()
            if widget:
                widget.setText(new_value)
