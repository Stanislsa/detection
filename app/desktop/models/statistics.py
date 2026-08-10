"""
Modèles de données pour les statistiques.
"""

from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime


@dataclass
class AlertStats:
    """Statistiques d'alertes."""
    total: int
    by_day: Dict[str, int]  # {"2026-07-30": 15, ...}
    by_type: Dict[str, int]  # {"fall": 10, "intrusion": 5, ...}
    by_severity: Dict[str, int]  # {"critical": 2, "high": 5, ...}
    resolved: int
    false_positives: int


@dataclass
class DetectionStats:
    """Statistiques de détection."""
    total: int
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    f1_score: float
    avg_confidence: float


@dataclass
class CameraStats:
    """Statistiques de caméras."""
    total: int
    online: int
    offline: int
    avg_fps: float
    total_detections: int


@dataclass
class SystemStats:
    """Statistiques système."""
    uptime_seconds: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int


@dataclass
class Statistics:
    """Statistiques globales."""
    alerts: AlertStats
    detections: DetectionStats
    cameras: CameraStats
    system: SystemStats
    generated_at: datetime
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Statistics':
        """Crée une instance depuis un dictionnaire API."""
        return cls(
            alerts=AlertStats(**data.get("alerts", {})),
            detections=DetectionStats(**data.get("detections", {})),
            cameras=CameraStats(**data.get("cameras", {})),
            system=SystemStats(**data.get("system", {})),
            generated_at=datetime.fromisoformat(data.get("generated_at", datetime.now().isoformat()))
        )
