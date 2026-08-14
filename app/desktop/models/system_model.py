"""
Modèle de données pour les métriques système.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


class HealthStatus(Enum):
    """Statut de santé d'un composant."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """Types de composants système."""
    CPU = "cpu"
    RAM = "ram"
    GPU = "gpu"
    AI_INFERENCE = "ai_inference"
    API_LATENCY = "api_latency"
    CAMERA_STREAMS = "camera_streams"
    DATABASE = "database"
    EVENT_BUS = "event_bus"


@dataclass
class SystemMetric:
    """Métrique système."""
    component_type: ComponentType
    name: str
    value: float
    unit: str
    timestamp: datetime
    status: HealthStatus = HealthStatus.HEALTHY
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire."""
        return {
            "component_type": self.component_type.value,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemMetric":
        """Crée une métrique depuis un dictionnaire."""
        return cls(
            component_type=ComponentType(data["component_type"]),
            name=data["name"],
            value=data["value"],
            unit=data["unit"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            status=HealthStatus(data.get("status", "healthy")),
            metadata=data.get("metadata", {})
        )


@dataclass
class ComponentHealth:
    """Santé d'un composant."""
    component_type: ComponentType
    name: str
    status: HealthStatus
    message: str
    last_updated: datetime
    metrics: List[SystemMetric] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire."""
        return {
            "component_type": self.component_type.value,
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "last_updated": self.last_updated.isoformat(),
            "metrics": [m.to_dict() for m in self.metrics]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComponentHealth":
        """Crée une santé de composant depuis un dictionnaire."""
        return cls(
            component_type=ComponentType(data["component_type"]),
            name=data["name"],
            status=HealthStatus(data["status"]),
            message=data["message"],
            last_updated=datetime.fromisoformat(data["last_updated"]),
            metrics=[SystemMetric.from_dict(m) for m in data.get("metrics", [])]
        )


@dataclass
class SystemOverview:
    """Vue d'ensemble du système."""
    overall_status: HealthStatus
    components: List[ComponentHealth] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire."""
        return {
            "overall_status": self.overall_status.value,
            "components": [c.to_dict() for c in self.components],
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemOverview":
        """Crée une vue d'ensemble depuis un dictionnaire."""
        return cls(
            overall_status=HealthStatus(data["overall_status"]),
            components=[ComponentHealth.from_dict(c) for c in data.get("components", [])],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        )
