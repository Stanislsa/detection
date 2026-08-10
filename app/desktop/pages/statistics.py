"""
Page Statistiques avec graphiques modernes.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from typing import List


class ChartCard(QFrame):
    """
    Carte de graphique générique.
    """
    
    def __init__(self, title: str, parent=None):
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
        
        # Titre
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12pt;
                font-weight: 600;
            }
        """)
        layout.addWidget(title_label)
        
        # Placeholder pour le graphique
        chart_placeholder = QLabel("📊 Graphique")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("""
            QLabel {
                background-color: #1E1E2F;
                border-radius: 8px;
                color: #A0A0B0;
                font-size: 14pt;
                padding: 40px;
            }
        """)
        chart_placeholder.setMinimumHeight(200)
        layout.addWidget(chart_placeholder)


class BarChart(QFrame):
    """
    Graphique à barres simple.
    """
    
    def __init__(self, data: List[tuple], parent=None):
        super().__init__(parent)
        
        self.data = data  # [(label, value), ...]
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
            painter.setBrush(QBrush(QColor("#2563EB")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))
            
            # Dessiner le label
            painter.setPen(QColor("#A0A0B0"))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(int(x), int(height - margin + 15), label)


class PieChart(QFrame):
    """
    Graphique circulaire simple.
    """
    
    def __init__(self, data: List[tuple], parent=None):
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


class StatisticsPage(QWidget):
    """
    Page Statistiques avec graphiques.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._init_ui()
        self._load_sample_data()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Titre de la page
        title_label = QLabel("Statistiques")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20pt;
                font-weight: 700;
            }
        """)
        layout.addWidget(title_label)
        
        # Grille de graphiques
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        # Alertes par jour (bar chart)
        self.alerts_chart = BarChart([
            ("Lun", 12), ("Mar", 8), ("Mer", 15), ("Jeu", 6),
            ("Ven", 10), ("Sam", 4), ("Dim", 7)
        ])
        alerts_card = self._create_chart_card("Alertes par jour", self.alerts_chart)
        grid_layout.addWidget(alerts_card, 0, 0, 1, 2)
        
        # Activités détectées (pie chart)
        self.activities_chart = PieChart([
            ("Chutes", 15, "#EF4444"),
            ("Mouvements", 25, "#F59E0B"),
            ("Intrusions", 8, "#3B82F6"),
            ("Normales", 52, "#10B981")
        ])
        activities_card = self._create_chart_card("Activités détectées", self.activities_chart)
        grid_layout.addWidget(activities_card, 0, 2)
        
        # Performance du modèle (bar chart)
        self.performance_chart = BarChart([
            ("Précision", 92), ("Rappel", 88), ("F1-score", 90)
        ])
        performance_card = self._create_chart_card("Performance du modèle IA (%)", self.performance_chart)
        grid_layout.addWidget(performance_card, 1, 0)
        
        # Taux de détection (bar chart)
        self.detection_chart = BarChart([
            ("Vrais positifs", 45), ("Faux positifs", 5),
            ("Faux négatifs", 3), ("Vrais négatifs", 47)
        ])
        detection_card = self._create_chart_card("Taux de détection", self.detection_chart)
        grid_layout.addWidget(detection_card, 1, 1)
        
        # Temps de réponse (bar chart)
        self.response_chart = BarChart([
            ("< 100ms", 60), ("100-200ms", 25), ("200-500ms", 10), ("> 500ms", 5)
        ])
        response_card = self._create_chart_card("Temps de réponse", self.response_chart)
        grid_layout.addWidget(response_card, 1, 2)
        
        layout.addLayout(grid_layout)
    
    def _create_chart_card(self, title: str, chart_widget: QWidget) -> QFrame:
        """
        Crée une carte de graphique.
        
        Args:
            title: Titre du graphique
            chart_widget: Widget du graphique
        
        Returns:
            QFrame contenant le graphique
        """
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2D2D44;
                border-radius: 12px;
                border: 1px solid #4A4A6A;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12pt;
                font-weight: 600;
            }
        """)
        layout.addWidget(title_label)
        
        # Graphique
        layout.addWidget(chart_widget)
        
        return card
    
    def _load_sample_data(self):
        """Charge des données d'exemple."""
        # Les données sont déjà chargées dans _init_ui
        pass
