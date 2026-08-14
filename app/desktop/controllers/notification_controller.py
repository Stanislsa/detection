"""
Contrôleur pour la gestion des notifications (pont avec QML).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot

from app.desktop.models.notification_model import Notification, NotificationType, NotificationCategory
from app.desktop.services.notification_service import NotificationService


class NotificationController(QObject):
    """Contrôleur pour les notifications exposé à QML."""
    
    notificationsChanged = pyqtSignal()
    notificationAdded = pyqtSignal(str)
    notificationUpdated = pyqtSignal(str)
    notificationDeleted = pyqtSignal(str)
    
    def __init__(self, service: NotificationService):
        super().__init__()
        self._service = service
    
    @pyqtProperty(list, notify=notificationsChanged)
    def notifications(self) -> List[Dict[str, Any]]:
        """Liste des notifications."""
        return [notification.to_dict() for notification in self._service.get_all_notifications()]
    
    @pyqtProperty(int, notify=notificationsChanged)
    def notificationCount(self) -> int:
        """Nombre total de notifications."""
        return len(self._service.get_all_notifications())
    
    @pyqtProperty(int, notify=notificationsChanged)
    def unreadCount(self) -> int:
        """Nombre de notifications non lues."""
        return len(self._service.get_unread_notifications())
    
    @pyqtProperty(int, notify=notificationsChanged)
    def criticalCount(self) -> int:
        """Nombre de notifications critiques."""
        return len(self._service.get_notifications_by_type(NotificationType.CRITICAL))
    
    @pyqtProperty(int, notify=notificationsChanged)
    def actionRequiredCount(self) -> int:
        """Nombre de notifications nécessitant une action."""
        return len(self._service.get_action_required_notifications())
    
    @pyqtSlot(str, result='QVariantMap')
    def getNotification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une notification par ID."""
        notification = self._service.get_notification(notification_id)
        return notification.to_dict() if notification else None
    
    @pyqtSlot(str, str, str, str, str, bool, result=str)
    def createNotification(
        self,
        type: str,
        category: str,
        title: str,
        message: str,
        action_required: bool = False
    ) -> str:
        """Crée une nouvelle notification."""
        notification = self._service.create_notification(
            type=NotificationType(type),
            category=NotificationCategory(category),
            title=title,
            message=message,
            action_required=action_required
        )
        self.notificationsChanged.emit()
        self.notificationAdded.emit(notification.id)
        return notification.id
    
    @pyqtSlot(str, result=bool)
    def markAsRead(self, notification_id: str) -> bool:
        """Marque une notification comme lue."""
        notification = self._service.mark_as_read(notification_id)
        if notification:
            self.notificationsChanged.emit()
            self.notificationUpdated.emit(notification_id)
            return True
        return False
    
    @pyqtSlot()
    def markAllAsRead(self):
        """Marque toutes les notifications comme lues."""
        self._service.mark_all_as_read()
        self.notificationsChanged.emit()
    
    @pyqtSlot(str, result=bool)
    def deleteNotification(self, notification_id: str) -> bool:
        """Supprime une notification."""
        success = self._service.delete_notification(notification_id)
        if success:
            self.notificationsChanged.emit()
            self.notificationDeleted.emit(notification_id)
        return success
    
    @pyqtSlot(str, result=list)
    def getNotificationsByType(self, notification_type: str) -> List[Dict[str, Any]]:
        """Récupère les notifications par type."""
        return [n.to_dict() for n in self._service.get_notifications_by_type(NotificationType(notification_type))]
    
    @pyqtSlot(str, result=list)
    def getNotificationsByCategory(self, category: str) -> List[Dict[str, Any]]:
        """Récupère les notifications par catégorie."""
        return [n.to_dict() for n in self._service.get_notifications_by_category(NotificationCategory(category))]
    
    @pyqtSlot(result=list)
    def getUnreadNotifications(self) -> List[Dict[str, Any]]:
        """Récupère les notifications non lues."""
        return [n.to_dict() for n in self._service.get_unread_notifications()]
    
    @pyqtSlot(result=list)
    def getActionRequiredNotifications(self) -> List[Dict[str, Any]]:
        """Récupère les notifications nécessitant une action."""
        return [n.to_dict() for n in self._service.get_action_required_notifications()]
    
    @pyqtSlot(int, result=list)
    def getRecentNotifications(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Récupère les notifications récentes."""
        return [n.to_dict() for n in self._service.get_recent_notifications(hours)]
    
    @pyqtSlot(result='QVariantMap')
    def getNotificationStatistics(self) -> Dict[str, int]:
        """Récupère les statistiques des notifications."""
        return self._service.get_notification_statistics()
    
    def refresh(self) -> None:
        """Rafraîchit les données des notifications."""
        self.notificationsChanged.emit()
