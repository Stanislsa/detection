"""
Composants Loading réutilisables.
Indicateurs de chargement et splash screen.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from typing import Optional


class LoadingSpinner(QWidget):
    """
    Spinner de chargement animé.
    """
    
    def __init__(self, size: int = 40, color: str = "#2563EB", parent=None):
        super().__init__(parent)
        
        self.size = size
        self.color = color
        self.angle = 0
        self._init_ui()
        self._init_timer()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setFixedSize(self.size, self.size)
    
    def _init_timer(self):
        """Initialise le timer pour l'animation."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.start(50)  # 20 FPS
    
    def _rotate(self):
        """Fait tourner le spinner."""
        self.angle = (self.angle + 15) % 360
        self.update()
    
    def paintEvent(self, event):
        """Dessine le spinner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dimensions
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 2 - 4
        
        # Dessiner l'arc
        painter.setPen(QPen(QColor(self.color), 4))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        start_angle = self.angle * 16
        span_angle = 270 * 16  # 3/4 de cercle
        
        painter.drawArc(
            center_x - radius, center_y - radius,
            radius * 2, radius * 2,
            start_angle, span_angle
        )
    
    def stop(self):
        """Arrête l'animation."""
        self.timer.stop()
    
    def start(self):
        """Démarre l'animation."""
        self.timer.start(50)


class LoadingOverlay(QWidget):
    """
    Overlay de chargement avec spinner et message.
    """
    
    def __init__(self, message: str = "Chargement...", parent=None):
        super().__init__(parent)
        
        self.message = message
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 47, 0.9);
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Spinner
        self.spinner = LoadingSpinner(size=60)
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12pt;
                font-weight: 500;
                margin-top: 16px;
            }
        """)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
    
    def set_message(self, message: str):
        """
        Définit le message de chargement.
        
        Args:
            message: Nouveau message
        """
        self.message = message
        if self.layout().count() > 1:
            widget = self.layout().itemAt(1).widget()
            if widget:
                widget.setText(message)


class SplashScreen(QWidget):
    """
    Splash screen pour le démarrage de l'application.
    """
    
    # Signal é quand le splash screen est terminé
    finished = pyqtSignal()
    
    def __init__(self, duration: int = 3000, parent=None):
        super().__init__(parent)
        
        self.duration = duration
        self._init_ui()
        self._init_timer()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E2F;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo / Titre
        title_label = QLabel("Surveillance IA")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 32pt;
                font-weight: 700;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Sous-titre
        subtitle_label = QLabel("Détection de Chutes par Intelligence Artificielle")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #A0A0B0;
                font-size: 12pt;
                font-weight: 500;
                margin-top: 8px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Spinner
        self.spinner = LoadingSpinner(size=50)
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Version
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("""
            QLabel {
                color: #6B7280;
                font-size: 9pt;
                margin-top: 40px;
            }
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
    
    def _init_timer(self):
        """Initialise le timer pour la durée d'affichage."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._finish)
        self.timer.start(self.duration)
    
    def _finish(self):
        """Termine le splash screen."""
        self.timer.stop()
        self.spinner.stop()
        self.finished.emit()
    
    def show_splash(self):
        """Affiche le splash screen en plein écran."""
        self.showFullScreen()
