"""
Composants Charts réutilisables.
Graphiques à barres et secteurs personnalisés.
"""

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from typing import List, Tuple


class BarChart(QFrame):
    """
    Graphique à barres simple.
    """
    
    def __init__(self, data: List[Tuple[str, float]], parent=None):
        super().__init__(parent)
        
        self.data = data  # [(label, value), ...]
        self.bar_color = "#2563EB"
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setStyleSheet("""
            QFrame {
                background-color: #1E1E2F;
                border-radius: 8px;
            }
        """)
        self.setMinimumHeight(200)
    
    def paintEvent(self, event):
        """Dessine le graphique à barres."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dimensions
        width = self.width()
        height = self.height()
        margin = 40
        
        # Trouver la valeur maximale
        max_value = max(value for _, value in self.data) if self.data else 1
        
        # Dessiner les barres
        bar_width = (width - 2 * margin) / len(self.data) - 10
        
        for i, (label, value) in enumerate(self.data):
            x = margin + i * (bar_width + 10)
            bar_height = (value / max_value) * (height - 2 * margin)
            y = height - margin - bar_height
            
            # Dessiner la barre
            painter.setBrush(QBrush(QColor(self.bar_color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))
            
            # Dessiner le label
            painter.setPen(QColor("#A0A0B0"))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(int(x), int(height - margin + 15), label)
    
    def set_color(self, color: str):
        """
        Définit la couleur des barres.
        
        Args:
            color: Couleur hexadécimale
        """
        self.bar_color = color
        self.update()


class PieChart(QFrame):
    """
    Graphique circulaire simple.
    """
    
    def __init__(self, data: List[Tuple[str, float, str]], parent=None):
        super().__init__(parent)
        
        self.data = data  # [(label, value, color), ...]
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setStyleSheet("""
            QFrame {
                background-color: #1E1E2F;
                border-radius: 8px;
            }
        """)
        self.setMinimumHeight(200)
    
    def paintEvent(self, event):
        """Dessine le graphique circulaire."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dimensions
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 20
        
        # Calculer le total
        total = sum(value for _, value, _ in self.data)
        
        # Dessiner les segments
        start_angle = 0
        for label, value, color in self.data:
            if total == 0:
                continue
            
            span_angle = int((value / total) * 360 * 16)
            
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPie(
                center_x - radius, center_y - radius,
                radius * 2, radius * 2,
                start_angle, span_angle
            )
            
            start_angle += span_angle


class LineChart(QFrame):
    """
    Graphique linéaire simple.
    """
    
    def __init__(self, data: List[Tuple[str, float]], parent=None):
        super().__init__(parent)
        
        self.data = data  # [(label, value), ...]
        self.line_color = "#2563EB"
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setStyleSheet("""
            QFrame {
                background-color: #1E1E2F;
                border-radius: 8px;
            }
        """)
        self.setMinimumHeight(200)
    
    def paintEvent(self, event):
        """Dessine le graphique linéaire."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dimensions
        width = self.width()
        height = self.height()
        margin = 40
        
        if len(self.data) < 2:
            return
        
        # Trouver les valeurs min/max
        values = [value for _, value in self.data]
        min_value = min(values)
        max_value = max(values)
        value_range = max_value - min_value if max_value != min_value else 1
        
        # Calculer les points
        points = []
        for i, (label, value) in enumerate(self.data):
            x = margin + i * (width - 2 * margin) / (len(self.data) - 1)
            y = height - margin - ((value - min_value) / value_range) * (height - 2 * margin)
            points.append((x, y))
        
        # Dessiner la ligne
        painter.setPen(QPen(QColor(self.line_color), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        for i in range(len(points) - 1):
            painter.drawLine(
                int(points[i][0]), int(points[i][1]),
                int(points[i + 1][0]), int(points[i + 1][1])
            )
        
        # Dessiner les points
        painter.setBrush(QBrush(QColor(self.line_color)))
        for x, y in points:
            painter.drawEllipse(int(x) - 4, int(y) - 4, 8, 8)
        
        # Dessiner les labels
        painter.setPen(QColor("#A0A0B0"))
        painter.setFont(QFont("Segoe UI", 8))
        for i, (label, _) in enumerate(self.data):
            x = margin + i * (width - 2 * margin) / (len(self.data) - 1)
            painter.drawText(int(x), int(height - margin + 15), label)
    
    def set_color(self, color: str):
        """
        Définit la couleur de la ligne.
        
        Args:
            color: Couleur hexadécimale
        """
        self.line_color = color
        self.update()
