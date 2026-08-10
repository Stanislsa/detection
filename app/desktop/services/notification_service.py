"""
Service de notifications.
Gère les notifications toast et les alertes système.
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class NotificationType(Enum):
    """Types de notifications."""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


@dataclass
class Notification:
    """Modèle de notification."""
    id: str
    title: str
    message: str
    type: NotificationType
    timestamp: datetime
    is_read: bool = False


class NotificationService:
    """
    Service pour la gestion des notifications.
    """
    
    def __init__(self):
        """Initialise le service de notifications."""
        self._notifications: List[Notification] = []
        self._notification_counter = 0
        
        # Callback pour afficher les notifications toast
        self.on_show_notification: Optional[Callable[[Notification], None]] = None
    
    def add_notification(self, title: str, message: str, 
                       notification_type: NotificationType = NotificationType.INFO) -> Notification:
        """
        Ajoute une notification.
        
        Args:
            title: Titre de la notification
            message: Message de la notification
            notification_type: Type de notification
        
        Returns:
            Notification créée
        """
        self._notification_counter += 1
        notification = Notification(
            id=str(self._notification_counter),
            title=title,
            message=message,
            type=notification_type,
            timestamp=datetime.now(),
            is_read=False
        )
        
        self._notifications.append(notification)
        
        # Garder seulement les 100 dernières notifications
        if len(self._notifications) > 100:
            self._notifications = self._notifications[-100:]
        
        # Afficher la notification si callback défini
        if self.on_show_notification:
            self.on_show_notification(notification)
        
        return notification
    
    def get_notifications(self, unread_only: bool = False) -> List[Notification]:
        """
        Récupère les notifications.
        
        Args:
            unread_only: Uniquement les non lues
        
        Returns:
            Liste des notifications
        """
        if unread_only:
            return [n for n in self._notifications if not n.is_read]
        return self._notifications
    
    def mark_as_read(self, notification_id: str):
        """
        Marque une notification comme lue.
        
        Args:
            notification_id: ID de la notification
        """
        for notification in self._notifications:
            if notification.id == notification_id:
                notification.is_read = True
                break
    
    def mark_all_as_read(self):
        """Marque toutes les notifications comme lues."""
        for notification in self._notifications:
            notification.is_read = True
    
    def clear_notifications(self):
        """Efface toutes les notifications."""
        self._notifications.clear()
    
    def get_unread_count(self) -> int:
        """
        Retourne le nombre de notifications non lues.
        
        Returns:
            Nombre de notifications non lues
        """
        return len([n for n in self._notifications if not n.is_read])
