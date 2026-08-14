"""
Service pour la gestion des alertes et incidents.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from app.desktop.models.alert_model import Alert, AlertPriority, AlertStatus, AlertType


class AlertService:
    """Service de gestion des alertes."""
    
    def __init__(self):
        self._alerts: List[Alert] = []
        self._generate_mock_data()
    
    def _generate_mock_data(self):
        """Génère des données de test pour les alertes."""
        now = datetime.now()
        
        mock_alerts = [
            Alert(
                id="ALT-001",
                title="Motion Detected - Zone A",
                description="Unexpected motion detected in restricted area Zone A",
                priority=AlertPriority.HIGH,
                status=AlertStatus.OPEN,
                alert_type=AlertType.MOTION,
                camera_id="CAM-001",
                camera_name="Camera 1",
                location="Zone A",
                timestamp=now - timedelta(minutes=2)
            ),
            Alert(
                id="ALT-002",
                title="Person Detected - Main Entrance",
                description="Person detected at main entrance after hours",
                priority=AlertPriority.CRITICAL,
                status=AlertStatus.INVESTIGATING,
                alert_type=AlertType.PERSON,
                camera_id="CAM-002",
                camera_name="Camera 2",
                location="Main Entrance",
                timestamp=now - timedelta(minutes=5),
                acknowledged_by="admin",
                acknowledged_at=now - timedelta(minutes=4)
            ),
            Alert(
                id="ALT-003",
                title="Vehicle Detected - Parking Lot",
                description="Unknown vehicle detected in parking lot",
                priority=AlertPriority.MEDIUM,
                status=AlertStatus.OPEN,
                alert_type=AlertType.VEHICLE,
                camera_id="CAM-003",
                camera_name="Camera 3",
                location="Parking Lot",
                timestamp=now - timedelta(minutes=15)
            ),
            Alert(
                id="ALT-004",
                title="System Health Warning",
                description="High CPU usage detected on inference server",
                priority=AlertPriority.MEDIUM,
                status=AlertStatus.ACKNOWLEDGED,
                alert_type=AlertType.SYSTEM,
                camera_id="",
                camera_name="System",
                location="Server Room",
                timestamp=now - timedelta(minutes=30),
                acknowledged_by="admin",
                acknowledged_at=now - timedelta(minutes=25)
            ),
            Alert(
                id="ALT-005",
                title="Intrusion Alert - Perimeter",
                description="Potential intrusion detected at perimeter fence",
                priority=AlertPriority.CRITICAL,
                status=AlertStatus.OPEN,
                alert_type=AlertType.INTRUSION,
                camera_id="CAM-004",
                camera_name="Camera 4",
                location="Perimeter",
                timestamp=now - timedelta(minutes=1)
            ),
            Alert(
                id="ALT-006",
                title="Motion Detected - Warehouse",
                description="Motion detected in warehouse area",
                priority=AlertPriority.LOW,
                status=AlertStatus.RESOLVED,
                alert_type=AlertType.MOTION,
                camera_id="CAM-005",
                camera_name="Camera 5",
                location="Warehouse",
                timestamp=now - timedelta(hours=1),
                acknowledged_by="security",
                acknowledged_at=now - timedelta(minutes=55),
                resolved_by="security",
                resolved_at=now - timedelta(minutes=50)
            ),
        ]
        
        self._alerts = mock_alerts
    
    def get_all_alerts(self) -> List[dict]:
        """Retourne toutes les alertes."""
        return [alert.to_dict() for alert in self._alerts]
    
    def get_alert_by_id(self, alert_id: str) -> Optional[dict]:
        """Retourne une alerte par son ID."""
        for alert in self._alerts:
            if alert.id == alert_id:
                return alert.to_dict()
        return None
    
    def get_alerts_by_priority(self, priority: AlertPriority) -> List[dict]:
        """Filtre les alertes par priorité."""
        return [alert.to_dict() for alert in self._alerts if alert.priority == priority]
    
    def get_alerts_by_status(self, status: AlertStatus) -> List[dict]:
        """Filtre les alertes par statut."""
        return [alert.to_dict() for alert in self._alerts if alert.status == status]
    
    def get_alerts_by_camera(self, camera_id: str) -> List[dict]:
        """Filtre les alertes par caméra."""
        return [alert.to_dict() for alert in self._alerts if alert.camera_id == camera_id]
    
    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge une alerte."""
        for alert in self._alerts:
            if alert.id == alert_id and alert.status == AlertStatus.OPEN:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = user
                alert.acknowledged_at = datetime.now()
                return True
        return False
    
    def update_alert_status(self, alert_id: str, status: AlertStatus, user: str) -> bool:
        """Met à jour le statut d'une alerte."""
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.status = status
                if status == AlertStatus.RESOLVED:
                    alert.resolved_by = user
                    alert.resolved_at = datetime.now()
                return True
        return False
    
    def get_alert_statistics(self) -> dict:
        """Retourne des statistiques sur les alertes."""
        total = len(self._alerts)
        open_count = len([a for a in self._alerts if a.status == AlertStatus.OPEN])
        critical_count = len([a for a in self._alerts if a.priority == AlertPriority.CRITICAL])
        high_count = len([a for a in self._alerts if a.priority == AlertPriority.HIGH])
        
        return {
            "total": total,
            "open": open_count,
            "critical": critical_count,
            "high": high_count,
            "medium": len([a for a in self._alerts if a.priority == AlertPriority.MEDIUM]),
            "low": len([a for a in self._alerts if a.priority == AlertPriority.LOW])
        }
