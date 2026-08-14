"""
Contrôleur pour la gestion des paramètres système (pont avec QML).
"""

from typing import Dict, Any

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot

from app.desktop.models.settings_model import (
    SystemSettings, GeneralSettings, CameraSettings, AISettings,
    NotificationSettings, StorageSettings, SecuritySettings
)
from app.desktop.services.settings_service import SettingsService


class SettingsController(QObject):
    """Contrôleur pour les paramètres système exposé à QML."""
    
    settingsChanged = pyqtSignal()
    
    def __init__(self, service: SettingsService):
        super().__init__()
        self._service = service
    
    @pyqtProperty(dict, notify=settingsChanged)
    def generalSettings(self) -> Dict[str, Any]:
        """Paramètres généraux."""
        return self._service.get_general_settings().to_dict()
    
    @pyqtProperty(dict, notify=settingsChanged)
    def cameraSettings(self) -> Dict[str, Any]:
        """Paramètres de caméra."""
        return self._service.get_camera_settings().to_dict()
    
    @pyqtProperty(dict, notify=settingsChanged)
    def aiSettings(self) -> Dict[str, Any]:
        """Paramètres IA."""
        return self._service.get_ai_settings().to_dict()
    
    @pyqtProperty(dict, notify=settingsChanged)
    def notificationSettings(self) -> Dict[str, Any]:
        """Paramètres de notification."""
        return self._service.get_notification_settings().to_dict()
    
    @pyqtProperty(dict, notify=settingsChanged)
    def storageSettings(self) -> Dict[str, Any]:
        """Paramètres de stockage."""
        return self._service.get_storage_settings().to_dict()
    
    @pyqtProperty(dict, notify=settingsChanged)
    def securitySettings(self) -> Dict[str, Any]:
        """Paramètres de sécurité."""
        return self._service.get_security_settings().to_dict()
    
    @pyqtSlot(str, str, str, bool, bool, str, result=bool)
    def updateGeneralSettings(
        self,
        application_name: str,
        theme: str,
        language: str,
        auto_update: bool,
        debug_mode: bool,
        log_level: str
    ) -> bool:
        """Met à jour les paramètres généraux."""
        settings = GeneralSettings(
            application_name=application_name,
            theme=theme,
            language=language,
            auto_update=auto_update,
            debug_mode=debug_mode,
            log_level=log_level
        )
        success = self._service.update_general_settings(settings)
        if success:
            self.settingsChanged.emit()
        return success
    
    @pyqtSlot(str, int, bool, int, bool, int, result=bool)
    def updateCameraSettings(
        self,
        default_resolution: str,
        default_fps: int,
        auto_reconnect: bool,
        reconnect_interval: int,
        recording_enabled: bool,
        retention_days: int
    ) -> bool:
        """Met à jour les paramètres de caméra."""
        settings = CameraSettings(
            default_resolution=default_resolution,
            default_fps=default_fps,
            auto_reconnect=auto_reconnect,
            reconnect_interval=reconnect_interval,
            recording_enabled=recording_enabled,
            retention_days=retention_days
        )
        success = self._service.update_camera_settings(settings)
        if success:
            self.settingsChanged.emit()
        return success
    
    @pyqtSlot(str, float, float, int, bool, bool, str, result=bool)
    def updateAISettings(
        self,
        model_name: str,
        confidence_threshold: float,
        nms_threshold: float,
        max_detections: int,
        enable_pose_estimation: bool,
        enable_face_recognition: bool,
        inference_device: str
    ) -> bool:
        """Met à jour les paramètres IA."""
        settings = AISettings(
            model_name=model_name,
            confidence_threshold=confidence_threshold,
            nms_threshold=nms_threshold,
            max_detections=max_detections,
            enable_pose_estimation=enable_pose_estimation,
            enable_face_recognition=enable_face_recognition,
            inference_device=inference_device
        )
        success = self._service.update_ai_settings(settings)
        if success:
            self.settingsChanged.emit()
        return success
    
    @pyqtSlot(bool, str, bool, str, bool, bool, bool, str, str, result=bool)
    def updateNotificationSettings(
        self,
        email_enabled: bool,
        email_address: str,
        sms_enabled: bool,
        sms_number: str,
        push_enabled: bool,
        critical_only: bool,
        quiet_hours_enabled: bool,
        quiet_hours_start: str,
        quiet_hours_end: str
    ) -> bool:
        """Met à jour les paramètres de notification."""
        settings = NotificationSettings(
            email_enabled=email_enabled,
            email_address=email_address,
            sms_enabled=sms_enabled,
            sms_number=sms_number,
            push_enabled=push_enabled,
            critical_only=critical_only,
            quiet_hours_enabled=quiet_hours_enabled,
            quiet_hours_start=quiet_hours_start,
            quiet_hours_end=quiet_hours_end
        )
        success = self._service.update_notification_settings(settings)
        if success:
            self.settingsChanged.emit()
        return success
    
    @pyqtSlot(str, int, bool, int, bool, str, str, result=bool)
    def updateStorageSettings(
        self,
        storage_path: str,
        max_storage_gb: int,
        auto_cleanup: bool,
        cleanup_threshold: int,
        backup_enabled: bool,
        backup_path: str,
        backup_schedule: str
    ) -> bool:
        """Met à jour les paramètres de stockage."""
        settings = StorageSettings(
            storage_path=storage_path,
            max_storage_gb=max_storage_gb,
            auto_cleanup=auto_cleanup,
            cleanup_threshold=cleanup_threshold,
            backup_enabled=backup_enabled,
            backup_path=backup_path,
            backup_schedule=backup_schedule
        )
        success = self._service.update_storage_settings(settings)
        if success:
            self.settingsChanged.emit()
        return success
    
    @pyqtSlot(int, int, int, bool, int, bool, bool, bool, result=bool)
    def updateSecuritySettings(
        self,
        session_timeout: int,
        max_login_attempts: int,
        lockout_duration: int,
        two_factor_enabled: bool,
        password_min_length: int,
        password_require_special: bool,
        password_require_number: bool,
        audit_logging: bool
    ) -> bool:
        """Met à jour les paramètres de sécurité."""
        settings = SecuritySettings(
            session_timeout=session_timeout,
            max_login_attempts=max_login_attempts,
            lockout_duration=lockout_duration,
            two_factor_enabled=two_factor_enabled,
            password_min_length=password_min_length,
            password_require_special=password_require_special,
            password_require_number=password_require_number,
            audit_logging=audit_logging
        )
        success = self._service.update_security_settings(settings)
        if success:
            self.settingsChanged.emit()
        return success
    
    @pyqtSlot(result=bool)
    def resetToDefaults(self) -> bool:
        """Réinitialise tous les paramètres aux valeurs par défaut."""
        success = self._service.reset_to_defaults()
        if success:
            self.settingsChanged.emit()
        return success
    
    def refresh(self) -> None:
        """Rafraîchit les données des paramètres."""
        self.settingsChanged.emit()
