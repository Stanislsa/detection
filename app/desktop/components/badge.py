"""
Composant Badge réutilisable.
Badge coloré pour statuts et gravité.
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class Badge(QLabel):
    """
    Badge coloré pour le statut/gravité.
    """
    
    def __init__(self, text: str, badge_type: str = "info", parent=None):
        super().__init__(text, parent)
        
        self.badge_type = badge_type
        self._set_style()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def _set_style(self):
        """Définit le style selon le type."""
        colors = {
            "success": "#10B981",
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "info": "#3B82F6",
            "primary": "#2563EB",
            "default": "#6B7280"
        }
        
        bg_color = colors.get(self.badge_type, colors["default"])
        
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: #FFFFFF;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 8pt;
                font-weight: 600;
            }}
        """)
    
    def set_type(self, badge_type: str):
        """
        Change le type du badge.
        
        Args:
            badge_type: Nouveau type (success, warning, danger, info, primary, default)
        """
        self.badge_type = badge_type
        self._set_style()
    
    def set_text(self, text: str):
        """
        Change le texte du badge.
        
        Args:
            text: Nouveau texte
        """
        self.setText(text)
