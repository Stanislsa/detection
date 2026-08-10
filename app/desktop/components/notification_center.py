"""
Centre de notifications.
Panneau latéral affichant l'historique des notifications.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional

from app.desktop.services.notification_service import Notification, NotificationType
from app.desktop.components.badge import Badge


class NotificationItem(QWidget):
    """
    Élément de notification dans la liste.
    """
    
    def __init__(self, notification: Notification, parent=None):
        super().__init__(parent)
        
        self.notification = notification
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                padding: 12px;
                border-bottom: 1px solid #3D3D5C;
            }
            QWidget:hover {
                background-color: rgba(45, 45, 68, 0.5);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header avec titre et badge
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.notification.title)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 10pt;
                font-weight: 600;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Badge de type
        badge_types = {
            NotificationType.SUCCESS: "success",
            NotificationType.WARNING: "warning",
            NotificationType.ERROR: "danger",
            NotificationType.INFO: "info"
        }
        badge = Badge(self.notification.type.value.capitalize(), badge_types.get(self.notification.type, "info"))
        header_layout.addWidget(badge)
        
        layout.addLayout(header_layout)
        
        # Message
        message_label = QLabel(self.notification.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: #A0A0B0;
                font-size: 9pt;
            }
        """)
        layout.addWidget(message_label)
        
        # Timestamp
        from app.desktop.utils.formatters import format_datetime
        timestamp_label = QLabel(format_datetime(self.notification.timestamp, "%d/%m/%Y %H:%M"))
        timestamp_label.setStyleSheet("""
            QLabel {
                color: #6B7280;
                font-size: 8pt;
            }
        """)
        layout.addWidget(timestamp_label)


class NotificationCenter(QWidget):
    """
    Centre de notifications avec liste et actions.
    """
    
    notification_clicked = pyqtSignal(Notification)
    
    def __init__(self, notification_service, parent=None):
        super().__init__(parent)
        
        self.notification_service = notification_service
        self._init_ui()
        self._load_notifications()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setFixedWidth(400)
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D44;
                border-left: 1px solid #4A4A6A;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1E1E2F;
                border-bottom: 1px solid #4A4A6A;
                padding: 16px;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        title_label = QLabel("Notifications")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12pt;
                font-weight: 600;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Badge de compteur
        self.count_badge = Badge(str(self.notification_service.get_unread_count()), "danger")
        header_layout.addWidget(self.count_badge)
        
        # Bouton fermer
        close_btn = QPushButton("×")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #A0A0B0;
                font-size: 18pt;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(16, 12, 16, 12)
        
        mark_all_btn = QPushButton("Tout marquer comme lu")
        mark_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #3D3D5C;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #4A4A6A;
            }
        """)
        mark_all_btn.clicked.connect(self._mark_all_as_read)
        actions_layout.addWidget(mark_all_btn)
        
        clear_btn = QPushButton("Effacer tout")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        clear_btn.clicked.connect(self._clear_all)
        actions_layout.addWidget(clear_btn)
        
        layout.addLayout(actions_layout)
        
        # Liste des notifications
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1E1E2F;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #4A4A6A;
                border-radius: 4px;
                min-height: 30px;
            }
        """)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 0;
            }
            QListWidget::item:selected {
                background-color: rgba(37, 99, 235, 0.2);
            }
        """)
        
        self.scroll_area.setWidget(self.list_widget)
        layout.addWidget(self.scroll_area)
    
    def _load_notifications(self):
        """Charge les notifications dans la liste."""
        self.list_widget.clear()
        
        notifications = self.notification_service.get_notifications()
        
        for notification in reversed(notifications):  # Plus récent en premier
            item = QListWidgetItem()
            item_widget = NotificationItem(notification)
            item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)
    
    def _mark_all_as_read(self):
        """Marque toutes les notifications comme lues."""
        self.notification_service.mark_all_as_read()
        self._update_count()
    
    def _clear_all(self):
        """Efface toutes les notifications."""
        self.notification_service.clear_notifications()
        self._load_notifications()
        self._update_count()
    
    def _update_count(self):
        """Met à jour le compteur de notifications."""
        count = self.notification_service.get_unread_count()
        self.count_badge.set_text(str(count))
    
    def refresh(self):
        """Rafraîchit la liste des notifications."""
        self._load_notifications()
        self._update_count()
