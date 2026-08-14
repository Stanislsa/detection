"""
Contrôleur pour la gestion des utilisateurs (pont avec QML).
"""

from typing import List, Optional, Dict, Any

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot

from app.desktop.models.user_model import (
    User, UserRole, UserStatus, Permission
)
from app.desktop.services.user_service import UserService


class UserController(QObject):
    """Contrôleur pour les utilisateurs exposé à QML."""
    
    usersChanged = pyqtSignal()
    userAdded = pyqtSignal(str)
    userUpdated = pyqtSignal(str)
    userDeleted = pyqtSignal(str)
    
    def __init__(self, service: UserService):
        super().__init__()
        self._service = service
    
    @pyqtProperty(list, notify=usersChanged)
    def users(self) -> List[Dict[str, Any]]:
        """Liste des utilisateurs."""
        return [user.to_dict() for user in self._service.get_all_users()]
    
    @pyqtProperty(int, notify=usersChanged)
    def userCount(self) -> int:
        """Nombre total d'utilisateurs."""
        return len(self._service.get_all_users())
    
    @pyqtProperty('QVariantMap', notify=usersChanged)
    def userStatistics(self) -> Dict[str, int]:
        """Statistiques des utilisateurs."""
        return self._service.get_user_statistics()
    
    @pyqtSlot(str, result='QVariantMap')
    def getUser(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par ID."""
        user = self._service.get_user(user_id)
        return user.to_dict() if user else None
    
    @pyqtSlot(str, str, str, str, result=str)
    def createUser(
        self,
        username: str,
        email: str,
        role: str,
        status: str = "pending"
    ) -> str:
        """Crée un nouvel utilisateur."""
        user = self._service.create_user(
            username=username,
            email=email,
            role=UserRole(role),
            status=UserStatus(status)
        )
        self.usersChanged.emit()
        self.userAdded.emit(user.id)
        return user.id
    
    @pyqtSlot(str, str, str, str, result=bool)
    def updateUser(
        self,
        user_id: str,
        username: str,
        email: str,
        role: str,
        status: str
    ) -> bool:
        """Met à jour un utilisateur."""
        user = self._service.update_user(
            user_id,
            username=username,
            email=email,
            role=UserRole(role),
            status=UserStatus(status)
        )
        if user:
            self.usersChanged.emit()
            self.userUpdated.emit(user_id)
            return True
        return False
    
    @pyqtSlot(str, result=bool)
    def deleteUser(self, user_id: str) -> bool:
        """Supprime un utilisateur."""
        success = self._service.delete_user(user_id)
        if success:
            self.usersChanged.emit()
            self.userDeleted.emit(user_id)
        return success
    
    @pyqtSlot(str, result=list)
    def getUsersByRole(self, role: str) -> List[Dict[str, Any]]:
        """Récupère les utilisateurs par rôle."""
        return [u.to_dict() for u in self._service.get_users_by_role(UserRole(role))]
    
    @pyqtSlot(str, result=list)
    def getUsersByStatus(self, status: str) -> List[Dict[str, Any]]:
        """Récupère les utilisateurs par statut."""
        return [u.to_dict() for u in self._service.get_users_by_status(UserStatus(status))]
    
    @pyqtSlot(str, result=list)
    def searchUsers(self, query: str) -> List[Dict[str, Any]]:
        """Recherche des utilisateurs."""
        return [u.to_dict() for u in self._service.search_users(query)]
    
    def refresh(self) -> None:
        """Rafraîchit les données des utilisateurs."""
        self.usersChanged.emit()
