"""
Composant Toast pour les notifications.
Notifications flottantes avec animation.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QEasingCurve
from PyQt6.QtGui import QFont
from typing import Optional

from app.desktop.services.notification_service import Notification, NotificationType


class ToastWidget(QWidget):
    """
    Widget de notification toast avec animation.
    """
    
    def __init__(self, notification: Notification, parent=None):
        super().__init__(parent)
        
        self.notification = notification
        self._opacity = 0.0
        self._init_ui()
        self._animate_in()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(350)
        
        # Couleur selon le type
        colors = {
            NotificationType.SUCCESS: "#10B981",
            NotificationType.WARNING: "#F59E0B",
            NotificationType.ERROR: "#EF4444",
            NotificationType.INFO: "#3B82F6"
        }
        bg_color = colors.get(self.notification.type, "#3B82F6")
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #2D2D44;
                border-radius: 12px;
                border-left: 4px solid {bg_color};
            }}
            QLabel {{
                color: #FFFFFF;
                background-color: transparent;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                color: #A0A0B0;
                font-size: 16pt;
                padding: 4px;
            }}
            QPushButton:hover {{
                color: #FFFFFF;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Header avec titre et bouton fermer
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.notification.title)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 11pt;
                font-weight: 600;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Message
        message_label = QLabel(self.notification.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: #A0A0B0;
                font-size: 10pt;
            }
        """)
        layout.addWidget(message_label)
    
    def _animate_in(self):
        """Anime l'apparition du toast."""
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
        
        # Auto-fermeture après 5 secondes
        QTimer.singleShot(5000, self.close)
    
    def _animate_out(self):
        """Anime la disparition du toast."""
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.animation.finished.connect(self.close)
        self.animation.start()
    
    @pyqtProperty(float)
    def opacity(self) -> float:
        """Retourne l'opacité."""
        return self._opacity
    
    @opacity.setter
    def opacity(self, value: float):
        """Définit l'opacité."""
        self._opacity = value
        self.setWindowOpacity(value)
    
    def closeEvent(self, event):
        """Gère la fermeture."""
        if hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.State.Running:
            event.ignore()
        else:
            super().closeEvent(event)


class ToastManager:
    """
    Gestionnaire de notifications toast.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialise le gestionnaire de toasts.
        
        Args:
            parent: Widget parent pour positionner les toasts
        """
        self.parent = parent
        self.toasts: list[ToastWidget] = []
        self.margin = 20
        self.spacing = 10
    
    def show_toast(self, notification: Notification):
        """
        Affiche une notification toast.
        
        Args:
            notification: Notification à afficher
        """
        toast = ToastWidget(notification, self.parent)
        
        # Positionner le toast
        if self.parent:
            x = self.parent.width() - toast.width() - self.margin
            y = self.margin + len(self.toasts) * (toast.height() + self.spacing)
            toast.move(x, y)
        
        toast.show()
        self.toasts.append(toast)
        
        # Nettoyer les toasts fermés
        toast.destroyed.connect(lambda: self._remove_toast(toast))
    
    def _remove_toast(self, toast: ToastWidget):
        """
        Supprime un toast de la liste.
        
        Args:
            toast: Toast à supprimer
        """
        if toast in self.toasts:
            self.toasts.remove(toast)
            self._reposition_toasts()
    
    def _reposition_toasts(self):
        """Repositionne tous les toasts."""
        for i, toast in enumerate(self.toasts):
            if self.parent:
                x = self.parent.width() - toast.width() - self.margin
                y = self.margin + i * (toast.height() + self.spacing)
                toast.move(x, y)
    
    def clear_all(self):
        """Ferme tous les toasts."""
        for toast in self.toasts[:]:
            toast.close()
        self.toasts.clear()
