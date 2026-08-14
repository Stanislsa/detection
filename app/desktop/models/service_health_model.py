"""
Modèle de données pour la santé des services.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any


class ServiceStatus(Enum):
    """Statut de santé d'un service."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


class ServiceType(Enum):
    """Types de services."""
    CAMERA_MANAGER = "camera_manager"
    AI_ENGINE = "ai_engine"
    EVENT_BUS = "event_bus"
    DATABASE = "database"
    API = "api"
    STORAGE = "storage"
    NOTIFICATION_SERVICE = "notification_service"


@dataclass
class ServiceHealth:
    """Santé d'un service."""
    service_type: ServiceType
    name: str
    status: ServiceStatus
    uptime: timedelta
    latency: float  # ms
    last_check: datetime
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire."""
        return {
            "service_type": self.service_type.value,
            "name": self.name,
            "status": self.status.value,
            "uptime_seconds": self.uptime.total_seconds(),
            "uptime_formatted": self._format_uptime(),
            "latency": self.latency,
            "last_check": self.last_check.isoformat(),
            "last_check_formatted": self._format_last_check(),
            "version": self.version,
            "metadata": self.metadata
        }
    
    def _format_uptime(self) -> str:
        """Formate le temps de fonctionnement."""
        total_seconds = int(self.uptime.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    def _format_last_check(self) -> str:
        """Formate la date du dernier check."""
        now = datetime.now()
        diff = now - self.last_check
        
        if diff.total_seconds() < 60:
            return "Just now"
        if diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() // 60)} min ago"
        if diff.total_seconds() < 86400:
            return f"{int(diff.total_seconds() // 3600)} hours ago"
        return self.last_check.strftime("%Y-%m-%d %H:%M")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServiceHealth":
        """Crée une santé de service depuis un dictionnaire."""
        return cls(
            service_type=ServiceType(data["service_type"]),
            name=data["name"],
            status=ServiceStatus(data["status"]),
            uptime=timedelta(seconds=data.get("uptime_seconds", 0)),
            latency=data.get("latency", 0.0),
            last_check=datetime.fromisoformat(data["last_check"]),
            version=data.get("version", "1.0.0"),
            metadata=data.get("metadata", {})
        )


@dataclass
class SystemHealthOverview:
    """Vue d'ensemble de la santé du système."""
    services: list[ServiceHealth] = field(default_factory=list)
    overall_status: ServiceStatus = ServiceStatus.HEALTHY
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire."""
        return {
            "services": [s.to_dict() for s in self.services],
            "overall_status": self.overall_status.value,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemHealthOverview":
        """Crée une vue d'ensemble depuis un dictionnaire."""
        return cls(
            services=[ServiceHealth.from_dict(s) for s in data.get("services", [])],
            overall_status=ServiceStatus(data.get("overall_status", "healthy")),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        )
    
    def calculate_overall_status(self) -> ServiceStatus:
        """Calcule le statut global du système."""
        if not self.services:
            return ServiceStatus.OFFLINE
        
        if any(s.status == ServiceStatus.OFFLINE for s in self.services):
            return ServiceStatus.CRITICAL
        if any(s.status == ServiceStatus.CRITICAL for s in self.services):
            return ServiceStatus.CRITICAL
        if any(s.status == ServiceStatus.WARNING for s in self.services):
            return ServiceStatus.WARNING
        return ServiceStatus.HEALTHY
