"""
Configuration des alertes temps réel.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, Any


@dataclass
class AlertRealtimeConfig:
    """Paramètres de détection et de notification des alertes en temps réel."""

    enabled: bool = True
    poll_interval_ms: int = 5000  # simulation / polling interval

    # Types d'événements activés
    enable_person: bool = True
    enable_vehicle: bool = True
    enable_intrusion: bool = True
    enable_motion: bool = True
    enable_system: bool = True

    # Seuils
    min_confidence: float = 0.70  # 0.0 – 1.0
    critical_confidence: float = 0.90

    # Notifications locales
    toast_enabled: bool = True
    toast_critical_only: bool = False
    sound_enabled: bool = False
    badge_enabled: bool = True

    # Escalade
    auto_ack_timeout_sec: int = 0  # 0 = désactivé
    max_open_alerts: int = 200

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertRealtimeConfig":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore
        return cls(**{k: v for k, v in data.items() if k in known})
