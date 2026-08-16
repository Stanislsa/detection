"""
Service de gestion des alertes et incidents — avec flux temps réel simulé.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import List, Optional, Callable

from desktop.models.alert_model import Alert, AlertPriority, AlertStatus, AlertType
from desktop.models.alert_config import AlertRealtimeConfig


CRITICAL_SCENARIOS = []  # filled after

_SCENARIOS = [
    {
        "title": "Unauthorized Access Detected",
        "description": "AI engine detected unauthorized access at Server Room A - Zone 4.",
        "priority": AlertPriority.CRITICAL,
        "alert_type": AlertType.INTRUSION,
        "camera_id": "CAM-SR-04",
        "camera_name": "Server Room Corridor",
        "location": "Server Room A - Zone 4",
        "confidence": 0.984,
    },
    {
        "title": "Unrecognized Person",
        "description": "Unidentified individual lingering near Main Office entrance.",
        "priority": AlertPriority.HIGH,
        "alert_type": AlertType.PERSON,
        "camera_id": "CAM-MO-01",
        "camera_name": "Main Office",
        "location": "Main Office",
        "confidence": 0.912,
    },
    {
        "title": "Tailgating Event",
        "description": "Possible tailgating detected at Loading Dock 2.",
        "priority": AlertPriority.MEDIUM,
        "alert_type": AlertType.INTRUSION,
        "camera_id": "CAM-LD-02",
        "camera_name": "Loading Dock 2",
        "location": "Loading Dock 2",
        "confidence": 0.84,
    },
    {
        "title": "Vehicle Detected - Parking",
        "description": "Unknown vehicle lingering at north parking perimeter.",
        "priority": AlertPriority.MEDIUM,
        "alert_type": AlertType.VEHICLE,
        "camera_id": "CAM-PK-12",
        "camera_name": "Parking West",
        "location": "Parking Lot / North",
        "confidence": 0.821,
    },
    {
        "title": "Motion - Restricted Zone",
        "description": "Unexpected motion in restricted Zone B-4 (Vault Perimeter).",
        "priority": AlertPriority.HIGH,
        "alert_type": AlertType.MOTION,
        "camera_id": "CAM-VLT-02",
        "camera_name": "Vault Perimeter",
        "location": "Zone B-4",
        "confidence": 0.91,
    },
    {
        "title": "Camera Signal Interrupted",
        "description": "Stream lost on perimeter fence camera PERIM_FNC_09.",
        "priority": AlertPriority.CRITICAL,
        "alert_type": AlertType.SYSTEM,
        "camera_id": "CAM-PF-09",
        "camera_name": "Perimeter Fence",
        "location": "Exterior / South Fence",
        "confidence": 1.0,
    },
    {
        "title": "Crowd Density Warning",
        "description": "Lobby occupancy exceeds configured threshold (current: 42).",
        "priority": AlertPriority.LOW,
        "alert_type": AlertType.PERSON,
        "camera_id": "CAM-LOB-04",
        "camera_name": "Main Lobby",
        "location": "Lobby",
        "confidence": 0.765,
    },
]


class AlertService:
    """Service de gestion des alertes avec génération temps réel."""

    def __init__(self):
        self._alerts: List[Alert] = []
        self._config = AlertRealtimeConfig()
        self._counter = 89200
        self._on_new_alert: Optional[Callable[[dict], None]] = None
        self._generate_mock_data()

    def get_config(self) -> dict:
        return self._config.to_dict()

    def update_config(self, data: dict) -> dict:
        self._config = AlertRealtimeConfig.from_dict({**self._config.to_dict(), **data})
        return self._config.to_dict()

    def set_new_alert_callback(self, cb: Callable[[dict], None]) -> None:
        self._on_new_alert = cb

    def get_all_alerts(self) -> List[dict]:
        return [a.to_dict() for a in sorted(self._alerts, key=lambda x: x.timestamp, reverse=True)]

    def get_alert_by_id(self, alert_id: str) -> Optional[dict]:
        for a in self._alerts:
            if a.id == alert_id:
                return a.to_dict()
        return None

    def get_open_count(self) -> int:
        return sum(
            1
            for a in self._alerts
            if a.status in (AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED, AlertStatus.INVESTIGATING)
        )

    def get_critical_open_count(self) -> int:
        return sum(
            1
            for a in self._alerts
            if a.priority == AlertPriority.CRITICAL
            and a.status in (AlertStatus.OPEN, AlertStatus.ACKNOWLEDGED, AlertStatus.INVESTIGATING)
        )

    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        for alert in self._alerts:
            if alert.id == alert_id and alert.status == AlertStatus.OPEN:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = user
                alert.acknowledged_at = datetime.now()
                return True
        return False

    def update_alert_status(self, alert_id: str, status: AlertStatus, user: str) -> bool:
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.status = status
                if status == AlertStatus.RESOLVED:
                    alert.resolved_by = user
                    alert.resolved_at = datetime.now()
                return True
        return False

    def get_alert_statistics(self) -> dict:
        return {
            "total": len(self._alerts),
            "open": sum(1 for a in self._alerts if a.status == AlertStatus.OPEN),
            "critical": sum(1 for a in self._alerts if a.priority == AlertPriority.CRITICAL),
            "high": sum(1 for a in self._alerts if a.priority == AlertPriority.HIGH),
            "medium": sum(1 for a in self._alerts if a.priority == AlertPriority.MEDIUM),
            "low": sum(1 for a in self._alerts if a.priority == AlertPriority.LOW),
        }


    def simulate_critical_burst(self, count: int = 3) -> list:
        """Force-create N critical alerts immediately (for demo / tests)."""
        import random as _rnd
        created = []
        pool = [s for s in _SCENARIOS if s["priority"] == AlertPriority.CRITICAL]
        if not pool:
            pool = _SCENARIOS
        for _ in range(max(1, min(count, 10))):
            scenario = _rnd.choice(pool)
            confidence = scenario.get("confidence", 0.95)
            self._counter += 1
            alert = Alert(
                id=f"ALRT-{self._counter}",
                title=scenario["title"],
                description=f"{scenario['description']} (AI conf: {confidence * 100:.1f}%)",
                priority=AlertPriority.CRITICAL,
                status=AlertStatus.OPEN,
                alert_type=scenario["alert_type"],
                camera_id=scenario["camera_id"],
                camera_name=scenario["camera_name"],
                location=scenario["location"],
                timestamp=datetime.now(),
            )
            self._alerts.insert(0, alert)
            payload = alert.to_dict()
            payload["confidence"] = round(confidence * 100, 1)
            if self._on_new_alert:
                self._on_new_alert(payload)
            created.append(payload)
        return created

    def tick_realtime(self) -> Optional[dict]:
        if not self._config.enabled:
            return None
        # Higher chance overall; bias toward critical (~50% of generated alerts)
        if random.random() > 0.55:
            return None

        prefer_critical = random.random() < 0.50
        pool = [s for s in _SCENARIOS if s["priority"] == AlertPriority.CRITICAL] if prefer_critical else _SCENARIOS
        if not pool:
            pool = _SCENARIOS
        scenario = random.choice(pool)

        type_map = {
            AlertType.PERSON: self._config.enable_person,
            AlertType.VEHICLE: self._config.enable_vehicle,
            AlertType.INTRUSION: self._config.enable_intrusion,
            AlertType.MOTION: self._config.enable_motion,
            AlertType.SYSTEM: self._config.enable_system,
            AlertType.OTHER: True,
        }
        if not type_map.get(scenario["alert_type"], True):
            return None

        confidence = scenario.get("confidence", random.uniform(0.6, 0.99))
        if confidence < self._config.min_confidence:
            return None
        if self.get_open_count() >= self._config.max_open_alerts:
            return None

        self._counter += 1
        alert = Alert(
            id=f"ALRT-{self._counter}",
            title=scenario["title"],
            description=f"{scenario['description']} (AI conf: {confidence * 100:.1f}%)",
            priority=scenario["priority"],
            status=AlertStatus.OPEN,
            alert_type=scenario["alert_type"],
            camera_id=scenario["camera_id"],
            camera_name=scenario["camera_name"],
            location=scenario["location"],
            timestamp=datetime.now(),
        )
        self._alerts.insert(0, alert)
        payload = alert.to_dict()
        payload["confidence"] = round(confidence * 100, 1)
        if self._on_new_alert:
            self._on_new_alert(payload)
        return payload


    def inject_alert(
        self,
        title: str,
        description: str,
        priority: str = "HIGH",
        alert_type: str = "INTRUSION",
        camera_id: str = "CAM-00",
        camera_name: str = "Manual",
        location: str = "Unknown",
    ) -> dict:
        self._counter += 1
        try:
            prio = AlertPriority(priority)
        except ValueError:
            prio = AlertPriority.HIGH
        try:
            atype = AlertType(alert_type)
        except ValueError:
            atype = AlertType.OTHER
        alert = Alert(
            id=f"ALRT-{self._counter}",
            title=title,
            description=description,
            priority=prio,
            status=AlertStatus.OPEN,
            alert_type=atype,
            camera_id=camera_id,
            camera_name=camera_name,
            location=location,
            timestamp=datetime.now(),
        )
        self._alerts.insert(0, alert)
        payload = alert.to_dict()
        if self._on_new_alert:
            self._on_new_alert(payload)
        return payload

    def _generate_mock_data(self):
        now = datetime.now()
        self._alerts = [
            Alert(
                id="ALRT-89214",
                title="Unauthorized Access Detected",
                description="Unauthorized access at Server Room A - Zone 4.",
                priority=AlertPriority.CRITICAL,
                status=AlertStatus.OPEN,
                alert_type=AlertType.INTRUSION,
                camera_id="CAM-SR-04",
                camera_name="Server Room Corridor",
                location="Server Room A - Zone 4",
                timestamp=now - timedelta(minutes=2),
            ),
            Alert(
                id="ALRT-89210",
                title="Unidentified Person",
                description="Unidentified individual near Main Office.",
                priority=AlertPriority.HIGH,
                status=AlertStatus.ACKNOWLEDGED,
                alert_type=AlertType.PERSON,
                camera_id="CAM-MO-01",
                camera_name="Main Office",
                location="Main Office",
                timestamp=now - timedelta(minutes=8),
                acknowledged_by="admin",
                acknowledged_at=now - timedelta(minutes=6),
            ),
            Alert(
                id="ALRT-89205",
                title="Tailgating - Loading Dock 2",
                description="Possible tailgating event.",
                priority=AlertPriority.MEDIUM,
                status=AlertStatus.OPEN,
                alert_type=AlertType.INTRUSION,
                camera_id="CAM-LD-02",
                camera_name="Loading Dock 2",
                location="Loading Dock 2",
                timestamp=now - timedelta(minutes=20),
            ),
            Alert(
                id="ALRT-89199",
                title="Crowd Density",
                description="Lobby occupancy elevated.",
                priority=AlertPriority.LOW,
                status=AlertStatus.RESOLVED,
                alert_type=AlertType.PERSON,
                camera_id="CAM-LOB-04",
                camera_name="Main Lobby",
                location="Lobby",
                timestamp=now - timedelta(minutes=40),
                resolved_by="system",
                resolved_at=now - timedelta(minutes=30),
            ),
            Alert(
                id="ALRT-89192",
                title="Perimeter Breach - North Gate",
                description="Perimeter intrusion pattern matched.",
                priority=AlertPriority.CRITICAL,
                status=AlertStatus.ACKNOWLEDGED,
                alert_type=AlertType.INTRUSION,
                camera_id="CAM-NG-01",
                camera_name="North Gate",
                location="North Gate",
                timestamp=now - timedelta(hours=1),
                acknowledged_by="soc",
                acknowledged_at=now - timedelta(minutes=50),
            ),
            Alert(
                id="ALRT-89185",
                title="Facial Match - Executive Wing",
                description="Facial recognition event on executive corridor.",
                priority=AlertPriority.HIGH,
                status=AlertStatus.RESOLVED,
                alert_type=AlertType.PERSON,
                camera_id="CAM-EX-03",
                camera_name="Executive Wing",
                location="Executive Wing",
                timestamp=now - timedelta(hours=2),
                resolved_by="admin",
                resolved_at=now - timedelta(hours=1, minutes=45),
            ),
        ]
        self._counter = 89214
