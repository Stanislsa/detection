"""
Service pour la gestion des notifications."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import random

from app.desktop.models.notification_model import Notification, NotificationType, NotificationCategory


class NotificationService:
    """Service de gestion des notifications."""
    
    def __init__(self):
        self._notifications: Dict[str, Notification] = {}
        self._initialize_demo_notifications()
    
    def _initialize_demo_notifications(self) -> None:
        """Initialise des notifications de démonstration."""
        demo_notifications = [
            Notification(
                id=str(uuid.uuid4()),
                type=NotificationType.CRITICAL,
                category=NotificationCategory.ALERT,
                title="Fall Detected",
                message="Fall detected in Warehouse Zone by Camera 3",
                timestamp=datetime.now() - timedelta(minutes=2),
                action_required=True,
                metadata={"camera_id": "cam3", "location": "Warehouse"}
            ),
            Notification(
                id=str(uuid.uuid4()),
                type=NotificationType.WARNING,
                category=NotificationCategory.CAMERA,
                title="Camera Disconnected",
                message="Camera 5 has lost connection",
                timestamp=datetime.now() - timedelta(minutes=15),
                action_required=True,
                metadata={"camera_id": "cam5"}
            ),
            Notification(
                id=str(uuid.uuid4()),
                type=NotificationType.CRITICAL,
                category=NotificationCategory.ALERT,
                title="Unauthorized Access",
                message="Unauthorized access detected at Entrance Zone",
                timestamp=datetime.now() - timedelta(minutes=30),
                action_required=True,
                metadata={"camera_id": "cam1", "location": "Entrance"}
            ),
            Notification(
                id=str(uuid.uuid4()),
                type=NotificationType.WARNING,
                category=NotificationCategory.AI_MODEL,
                title="AI Model Warning",
                message="Detection confidence below threshold on Camera 2",
                timestamp=datetime.now() - timedelta(hours=1),
                action_required=False,
                metadata={"camera_id": "cam2", "confidence": 0.65}
            ),
            Notification(
                id=str(uuid.uuid4()),
                type=NotificationType.INFO,
                category=NotificationCategory.MAINTENANCE,
                title="System Maintenance",
                message="Scheduled maintenance in 2 hours",
                timestamp=datetime.now() - timedelta(hours=2),
                action_required=False,
                metadata={"scheduled_time": "12:00"}
            ),
            Notification(
                id=str(uuid.uuid4()),
                type=NotificationType.SUCCESS,
                category=NotificationCategory.SYSTEM,
                title="Backup Completed",
                message="Daily backup completed successfully",
                timestamp=datetime.now() - timedelta(hours=3),
                action_required=False,
                metadata={"backup_size": "2.5GB"}
            ),
            Notification(
                id=str(uuid.uuid4()),
                type=NotificationType.INFO,
                category=NotificationCategory.CAMERA,
                title="Camera Reconnected",
                message="Camera 4 has reconnected successfully",
                timestamp=datetime.now() - timedelta(hours=4),
                action_required=False,
                metadata={"camera_id": "cam4"}
            ),
            Notification(
                id=str(uuid.uuid4()),
                type=NotificationType.WARNING,
                category=NotificationCategory.SYSTEM,
                title="High CPU Usage",
                message="CPU usage above 80% for extended period",
                timestamp=datetime.now() - timedelta(hours=5),
                action_required=False,
                metadata={"cpu_usage": "85%"}
            )
        ]
        
        for notification in demo_notifications:
            self._notifications[notification.id] = notification
    
    def get_all_notifications(self) -> List[Notification]:
        """Récupère toutes les notifications."""
        return sorted(self._notifications.values(), key=lambda n: n.timestamp, reverse=True)
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Récupère une notification par ID."""
        return self._notifications.get(notification_id)
    
    def add_notification(self, notification: Notification) -> Notification:
        """Ajoute une nouvelle notification."""
        self._notifications[notification.id] = notification
        return notification
    
    def create_notification(
        self,
        type: NotificationType,
        category: NotificationCategory,
        title: str,
        message: str,
        action_required: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Crée une nouvelle notification."""
        notification = Notification(
            id=str(uuid.uuid4()),
            type=type,
            category=category,
            title=title,
            message=message,
            timestamp=datetime.now(),
            action_required=action_required,
            metadata=metadata or {}
        )
        self._notifications[notification.id] = notification
        return notification
    
    def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        """Marque une notification comme lue."""
        notification = self._notifications.get(notification_id)
        if notification:
            notification.mark_as_read()
            return notification
        return None
    
    def mark_all_as_read(self) -> None:
        """Marque toutes les notifications comme lues."""
        for notification in self._notifications.values():
            notification.mark_as_read()
    
    def delete_notification(self, notification_id: str) -> bool:
        """Supprime une notification."""
        if notification_id in self._notifications:
            del self._notifications[notification_id]
            return True
        return False
    
    def get_unread_notifications(self) -> List[Notification]:
        """Récupère les notifications non lues."""
        return [n for n in self._notifications.values() if not n.read]
    
    def get_notifications_by_type(self, notification_type: NotificationType) -> List[Notification]:
        """Récupère les notifications par type."""
        return [n for n in self._notifications.values() if n.type == notification_type]
    
    def get_notifications_by_category(self, category: NotificationCategory) -> List[Notification]:
        """Récupère les notifications par catégorie."""
        return [n for n in self._notifications.values() if n.category == category]
    
    def get_action_required_notifications(self) -> List[Notification]:
        """Récupère les notifications nécessitant une action."""
        return [n for n in self._notifications.values() if n.action_required]
    
    def get_recent_notifications(self, hours: int = 24) -> List[Notification]:
        """Récupère les notifications récentes."""
        threshold = datetime.now() - timedelta(hours=hours)
        return [n for n in self._notifications.values() if n.timestamp >= threshold]
    
    def get_notification_statistics(self) -> Dict[str, int]:
        """Récupère les statistiques des notifications."""
        total = len(self._notifications)
        unread = len(self.get_unread_notifications())
        critical = len(self.get_notifications_by_type(NotificationType.CRITICAL))
        warning = len(self.get_notifications_by_type(NotificationType.WARNING))
        action_required = len(self.get_action_required_notifications())
        
        return {
            "total": total,
            "unread": unread,
            "critical": critical,
            "warning": warning,
            "action_required": action_required
        }
