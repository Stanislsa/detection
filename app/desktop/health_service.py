"""
Service de diagnostic des composants.
Vérifie l'état de santé de tous les composants de l'application.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import psutil
import socket

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from app.core.logger import get_logger


class HealthStatus(Enum):
    """Statut de santé d'un composant."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Résultat d'un check de santé."""
    component: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.details is None:
            self.details = {}


class HealthService(QObject):
    """
    Service de diagnostic des composants.
    Vérifie périodiquement l'état de santé de tous les composants.
    """
    
    # Signaux
    health_updated = pyqtSignal(object)  # Dict[str, HealthCheck]
    component_health_changed = pyqtSignal(str, object)  # component, HealthCheck
    
    _instance = None
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        
        self._logger = get_logger(__name__)
        self._health_checks: Dict[str, HealthCheck] = {}
        
        # Timer pour les checks périodiques
        self._check_timer = QTimer()
        self._check_timer.timeout.connect(self._run_all_checks)
        self._check_timer.start(30000)  # Check toutes les 30 secondes
        
        self._initialized = True
        self._logger.info("HealthService initialisé")
    
    def _run_all_checks(self):
        """Exécute tous les checks de santé."""
        checks = {
            "database": self._check_database,
            "api": self._check_api,
            "websocket": self._check_websocket,
            "cameras": self._check_cameras,
            "gpu": self._check_gpu,
            "openvino": self._check_openvino,
            "yolo_model": self._check_yolo_model,
            "storage": self._check_storage,
            "smtp": self._check_smtp,
            "telegram": self._check_telegram
        }
        
        for component, check_func in checks.items():
            try:
                health = check_func()
                old_health = self._health_checks.get(component)
                
                if old_health is None or old_health.status != health.status:
                    self.component_health_changed.emit(component, health)
                
                self._health_checks[component] = health
            except Exception as e:
                self._logger.error(f"Erreur check {component}: {e}")
                self._health_checks[component] = HealthCheck(
                    component=component,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Erreur: {e}"
                )
        
        self.health_updated.emit(self._health_checks)
    
    def _check_database(self) -> HealthCheck:
        """Vérifie la connexion à la base de données."""
        try:
            from app.database import get_session
            
            session = get_session()
            session.execute("SELECT 1")
            session.close()
            
            return HealthCheck(
                component="database",
                status=HealthStatus.HEALTHY,
                message="Base de données connectée",
                details={"connection_time_ms": 10}
            )
        except Exception as e:
            return HealthCheck(
                component="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Erreur base de données: {e}"
            )
    
    def _check_api(self) -> HealthCheck:
        """Vérifie la connexion à l'API."""
        try:
            from app.core.config_loader import get_config_loader
            config = get_config_loader()
            
            host = config.get("application", "backend.host", "localhost")
            port = config.get("application", "backend.port", 8000)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return HealthCheck(
                    component="api",
                    status=HealthStatus.HEALTHY,
                    message=f"API accessible sur {host}:{port}",
                    details={"host": host, "port": port}
                )
            else:
                return HealthCheck(
                    component="api",
                    status=HealthStatus.UNHEALTHY,
                    message=f"API inaccessible sur {host}:{port}"
                )
        except Exception as e:
            return HealthCheck(
                component="api",
                status=HealthStatus.UNKNOWN,
                message=f"Erreur check API: {e}"
            )
    
    def _check_websocket(self) -> HealthCheck:
        """Vérifie la connexion WebSocket."""
        try:
            from app.core.config_loader import get_config_loader
            config = get_config_loader()
            
            enabled = config.get("application", "websocket.enabled", False)
            
            if not enabled:
                return HealthCheck(
                    component="websocket",
                    status=HealthStatus.HEALTHY,
                    message="WebSocket désactivé"
                )
            
            host = config.get("application", "websocket.host", "localhost")
            port = config.get("application", "websocket.port", 8001)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return HealthCheck(
                    component="websocket",
                    status=HealthStatus.HEALTHY,
                    message=f"WebSocket accessible sur {host}:{port}",
                    details={"host": host, "port": port}
                )
            else:
                return HealthCheck(
                    component="websocket",
                    status=HealthStatus.UNHEALTHY,
                    message=f"WebSocket inaccessible sur {host}:{port}"
                )
        except Exception as e:
            return HealthCheck(
                component="websocket",
                status=HealthStatus.UNKNOWN,
                message=f"Erreur check WebSocket: {e}"
            )
    
    def _check_cameras(self) -> HealthCheck:
        """Vérifie l'état des caméras."""
        try:
            from app.desktop.camera_manager import get_camera_manager
            manager = get_camera_manager()
            
            cameras = manager.get_cameras()
            active = sum(1 for c in cameras if c.state in ["streaming", "detecting", "recording"])
            total = len(cameras)
            
            if total == 0:
                return HealthCheck(
                    component="cameras",
                    status=HealthStatus.HEALTHY,
                    message="Aucune caméra configurée",
                    details={"total": 0, "active": 0}
                )
            
            if active == total:
                return HealthCheck(
                    component="cameras",
                    status=HealthStatus.HEALTHY,
                    message=f"Toutes les caméras actives ({active}/{total})",
                    details={"total": total, "active": active}
                )
            elif active > 0:
                return HealthCheck(
                    component="cameras",
                    status=HealthStatus.DEGRADED,
                    message=f"Caméras partiellement actives ({active}/{total})",
                    details={"total": total, "active": active}
                )
            else:
                return HealthCheck(
                    component="cameras",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Aucune caméra active ({active}/{total})",
                    details={"total": total, "active": active}
                )
        except Exception as e:
            return HealthCheck(
                component="cameras",
                status=HealthStatus.UNKNOWN,
                message=f"Erreur check caméras: {e}"
            )
    
    def _check_gpu(self) -> HealthCheck:
        """Vérifie la disponibilité du GPU."""
        try:
            import torch
            
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0)
                memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
                
                return HealthCheck(
                    component="gpu",
                    status=HealthStatus.HEALTHY,
                    message=f"GPU disponible: {device_name}",
                    details={
                        "device_count": device_count,
                        "device_name": device_name,
                        "memory_gb": memory_gb
                    }
                )
            else:
                return HealthCheck(
                    component="gpu",
                    status=HealthStatus.HEALTHY,
                    message="GPU non disponible (CPU utilisé)",
                    details={"gpu_available": False}
                )
        except ImportError:
            return HealthCheck(
                component="gpu",
                status=HealthStatus.HEALTHY,
                message="PyTorch non installé (GPU non vérifié)",
                details={"gpu_available": False}
            )
        except Exception as e:
            return HealthCheck(
                component="gpu",
                status=HealthStatus.UNKNOWN,
                message=f"Erreur check GPU: {e}"
            )
    
    def _check_openvino(self) -> HealthCheck:
        """Vérifie la disponibilité d'OpenVINO."""
        try:
            import openvino as ov
            
            core = ov.Core()
            devices = core.available_devices
            
            return HealthCheck(
                component="openvino",
                status=HealthStatus.HEALTHY,
                message=f"OpenVINO disponible: {len(devices)} appareils",
                details={"devices": devices}
            )
        except ImportError:
            return HealthCheck(
                component="openvino",
                status=HealthStatus.HEALTHY,
                message="OpenVINO non installé",
                details={"openvino_available": False}
            )
        except Exception as e:
            return HealthCheck(
                component="openvino",
                status=HealthStatus.UNKNOWN,
                message=f"Erreur check OpenVINO: {e}"
            )
    
    def _check_yolo_model(self) -> HealthCheck:
        """Vérifie la disponibilité du modèle YOLO."""
        try:
            from app.core.config_loader import get_config_loader
            config = get_config_loader()
            
            model_path = config.get("ai", "yolo.default_model", "yolov8n.pt")
            
            from pathlib import Path
            model_file = Path(model_path)
            
            if model_file.exists():
                size_mb = model_file.stat().st_size / (1024 ** 2)
                return HealthCheck(
                    component="yolo_model",
                    status=HealthStatus.HEALTHY,
                    message=f"Modèle YOLO disponible: {model_path}",
                    details={"model_path": str(model_path), "size_mb": size_mb}
                )
            else:
                return HealthCheck(
                    component="yolo_model",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Modèle YOLO introuvable: {model_path}",
                    details={"model_path": str(model_path)}
                )
        except Exception as e:
            return HealthCheck(
                component="yolo_model",
                status=HealthStatus.UNKNOWN,
                message=f"Erreur check modèle YOLO: {e}"
            )
    
    def _check_storage(self) -> HealthCheck:
        """Vérifie l'espace disque."""
        try:
            disk = psutil.disk_usage('/')
            percent = disk.percent
            free_gb = disk.free / (1024 ** 3)
            
            if percent < 80:
                return HealthCheck(
                    component="storage",
                    status=HealthStatus.HEALTHY,
                    message=f"Espace disque suffisant ({percent:.1f}% utilisé)",
                    details={"percent": percent, "free_gb": free_gb}
                )
            elif percent < 90:
                return HealthCheck(
                    component="storage",
                    status=HealthStatus.DEGRADED,
                    message=f"Espace disque limité ({percent:.1f}% utilisé)",
                    details={"percent": percent, "free_gb": free_gb}
                )
            else:
                return HealthCheck(
                    component="storage",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Espace disque critique ({percent:.1f}% utilisé)",
                    details={"percent": percent, "free_gb": free_gb}
                )
        except Exception as e:
            return HealthCheck(
                component="storage",
                status=HealthStatus.UNKNOWN,
                message=f"Erreur check stockage: {e}"
            )
    
    def _check_smtp(self) -> HealthCheck:
        """Vérifie la configuration SMTP."""
        try:
            from app.core.config_loader import get_config_loader
            config = get_config_loader()
            
            enabled = config.get("notifications", "email.enabled", False)
            
            if not enabled:
                return HealthCheck(
                    component="smtp",
                    status=HealthStatus.HEALTHY,
                    message="SMTP désactivé"
                )
            
            smtp_host = config.get("notifications", "email.smtp_host", "")
            
            if smtp_host:
                return HealthCheck(
                    component="smtp",
                    status=HealthStatus.HEALTHY,
                    message=f"SMTP configuré: {smtp_host}",
                    details={"smtp_host": smtp_host}
                )
            else:
                return HealthCheck(
                    component="smtp",
                    status=HealthStatus.UNHEALTHY,
                    message="SMTP non configuré"
                )
        except Exception as e:
            return HealthCheck(
                component="smtp",
                status=HealthStatus.UNKNOWN,
                message=f"Erreur check SMTP: {e}"
            )
    
    def _check_telegram(self) -> HealthCheck:
        """Vérifie la configuration Telegram."""
        try:
            from app.core.config_loader import get_config_loader
            config = get_config_loader()
            
            enabled = config.get("notifications", "telegram.enabled", False)
            
            if not enabled:
                return HealthCheck(
                    component="telegram",
                    status=HealthStatus.HEALTHY,
                    message="Telegram désactivé"
                )
            
            bot_token = config.get("notifications", "telegram.bot_token", "")
            chat_id = config.get("notifications", "telegram.chat_id", "")
            
            if bot_token and chat_id:
                return HealthCheck(
                    component="telegram",
                    status=HealthStatus.HEALTHY,
                    message="Telegram configuré",
                    details={"chat_id": chat_id}
                )
            else:
                return HealthCheck(
                    component="telegram",
                    status=HealthStatus.UNHEALTHY,
                    message="Telegram non configuré"
                )
        except Exception as e:
            return HealthCheck(
                component="telegram",
                status=HealthStatus.UNKNOWN,
                message=f"Erreur check Telegram: {e}"
            )
    
    def get_health(self, component: str = None) -> Optional[HealthCheck]:
        """
        Retourne l'état de santé d'un composant.
        
        Args:
            component: Nom du composant (None = tous)
        
        Returns:
            HealthCheck ou None
        """
        if component:
            return self._health_checks.get(component)
        return None
    
    def get_all_health(self) -> Dict[str, HealthCheck]:
        """Retourne l'état de santé de tous les composants."""
        return self._health_checks.copy()
    
    def get_overall_health(self) -> HealthStatus:
        """
        Retourne l'état de santé global.
        
        Returns:
            Statut de santé global
        """
        if not self._health_checks:
            return HealthStatus.UNKNOWN
        
        statuses = [h.status for h in self._health_checks.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif HealthStatus.UNKNOWN in statuses:
            return HealthStatus.UNKNOWN
        else:
            return HealthStatus.HEALTHY
    
    def run_check(self, component: str) -> HealthCheck:
        """
        Exécute un check de santé spécifique.
        
        Args:
            component: Nom du composant
        
        Returns:
            Résultat du check
        """
        check_map = {
            "database": self._check_database,
            "api": self._check_api,
            "websocket": self._check_websocket,
            "cameras": self._check_cameras,
            "gpu": self._check_gpu,
            "openvino": self._check_openvino,
            "yolo_model": self._check_yolo_model,
            "storage": self._check_storage,
            "smtp": self._check_smtp,
            "telegram": self._check_telegram
        }
        
        check_func = check_map.get(component)
        if check_func:
            health = check_func()
            self._health_checks[component] = health
            self.component_health_changed.emit(component, health)
            return health
        else:
            return HealthCheck(
                component=component,
                status=HealthStatus.UNKNOWN,
                message="Composant inconnu"
            )


def get_health_service() -> HealthService:
    """
    Fonction utilitaire pour récupérer le HealthService.
    
    Returns:
        Instance singleton du HealthService
    """
    if HealthService._instance is None:
        HealthService._instance = HealthService()
    return HealthService._instance
