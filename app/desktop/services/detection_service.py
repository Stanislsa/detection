"""
Service de détection IA.
Gère les détections en temps réel, le filtrage et l'historique.
"""

from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

from app.desktop.services.api_client import APIClient, APIResponse
from app.desktop.models.alert import Alert, AlertSeverity, AlertStatus, AlertType


@dataclass
class Detection:
    """Modèle de détection."""
    id: int
    camera_id: int
    camera_name: str
    detection_type: str  # 'fall', 'intrusion', 'movement', etc.
    confidence: float
    timestamp: datetime
    bbox: tuple  # (x1, y1, x2, y2)
    severity: str  # 'low', 'medium', 'high', 'critical'
    is_confirmed: bool
    
    @property
    def alert_type(self) -> AlertType:
        try:
            return AlertType(self.detection_type)
        except ValueError:
            return AlertType.FALL


class DictWrapper:
    """Wrapper permettant l'accès par attributs ou clés aux statistiques."""
    def __init__(self, data: dict):
        self._data = data
        for k, v in data.items():
            setattr(self, k, v)
            
    def get(self, key, default=None):
        return self._data.get(key, default)


class DetectionService:
    """
    Service pour la gestion des détections / alertes.
    """
    
    def __init__(self, api_client: APIClient):
        """
        Initialise le service de détection.
        
        Args:
            api_client: Client API
        """
        self.api_client = api_client
        self._detections_cache: List[Any] = []
        
        # Callbacks pour les événements temps réel
        self.on_new_detection: Optional[Callable[[Any], None]] = None
        self.on_detection_confirmed: Optional[Callable[[Any], None]] = None
    
    def get_detections(self, use_cache: bool = True, camera_id: Optional[int] = None, 
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       limit: int = 100) -> List[Any]:
        """
        Récupère la liste des détections/alertes.
        """
        if use_cache and self._detections_cache:
            return self._detections_cache
        
        if hasattr(self.api_client, 'get_detections'):
            response = self.api_client.get_detections()
        else:
            params = {"limit": limit}
            if camera_id:
                params["camera_id"] = camera_id
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
            url = f"/detections?{'&'.join(f'{k}={v}' for k, v in params.items())}"
            response = self.api_client._request("GET", url)
            
        if response and response.success and response.data:
            results = []
            for det_data in response.data:
                alert_type_val = det_data.get("alert_type") or det_data.get("detection_type", "fall")
                try:
                    alert_type = AlertType(alert_type_val)
                except ValueError:
                    alert_type = AlertType.FALL
                
                severity_val = det_data.get("severity", "medium")
                try:
                    severity = AlertSeverity(severity_val)
                except ValueError:
                    severity = AlertSeverity.MEDIUM
                    
                status_val = det_data.get("status", "new")
                try:
                    status = AlertStatus(status_val)
                except ValueError:
                    status = AlertStatus.NEW

                detected_at_raw = det_data.get("detected_at") or det_data.get("timestamp")
                if isinstance(detected_at_raw, str):
                    detected_at = datetime.fromisoformat(detected_at_raw)
                elif isinstance(detected_at_raw, datetime):
                    detected_at = detected_at_raw
                else:
                    detected_at = datetime.now()

                alert = Alert(
                    id=det_data.get("id"),
                    camera_id=det_data.get("camera_id"),
                    camera_name=det_data.get("camera_name", ""),
                    alert_type=alert_type,
                    severity=severity,
                    status=status,
                    detected_at=detected_at,
                    confidence=det_data.get("confidence", 0.0),
                    bbox=tuple(det_data.get("bbox", (0, 0, 0, 0))) if det_data.get("bbox") else (0, 0, 0, 0)
                )
                results.append(alert)
            self._detections_cache = results
            return results
        
        return []
        
    def get_detection(self, detection_id: int) -> Optional[Any]:
        """Récupère une détection par son ID dans le cache."""
        for item in self._detections_cache:
            if getattr(item, "id", None) == detection_id:
                return item
        return None

    def update_detection_status(self, detection_id: int, new_status: Any) -> bool:
        """Met à jour le statut d'une détection."""
        status_value = new_status.value if hasattr(new_status, "value") else str(new_status)
        if hasattr(self.api_client, 'update_detection_status'):
            response = self.api_client.update_detection_status(detection_id, status_value)
        else:
            response = self.api_client._request("PUT", f"/detections/{detection_id}/status", json={"status": status_value})
        
        if response and response.success:
            for item in self._detections_cache:
                if getattr(item, "id", None) == detection_id:
                    if hasattr(item, "status"):
                        item.status = new_status
                    break
            return True
        return False

    def confirm_detection(self, detection_id: int, confirmed: bool) -> bool:
        """Confirme ou infirme une détection."""
        response = self.api_client._request(
            "PUT",
            f"/detections/{detection_id}",
            json={"is_confirmed": confirmed}
        )
        if response and response.success:
            for detection in self._detections_cache:
                if getattr(detection, "id", None) == detection_id:
                    if hasattr(detection, "is_confirmed"):
                        detection.is_confirmed = confirmed
                    if self.on_detection_confirmed:
                        self.on_detection_confirmed(detection)
                    break
            return True
        return False

    def handle_websocket_detection(self, data: Dict):
        """Gère une détection reçue via WebSocket."""
        detection = Detection(
            id=data.get("id"),
            camera_id=data.get("camera_id"),
            camera_name=data.get("camera_name", ""),
            detection_type=data.get("detection_type", "fall"),
            confidence=data.get("confidence", 0.0),
            timestamp=datetime.fromisoformat(data.get("timestamp")),
            bbox=tuple(data.get("bbox", (0, 0, 0, 0))),
            severity=data.get("severity", "medium"),
            is_confirmed=data.get("is_confirmed", False)
        )
        self._detections_cache.append(detection)
        if len(self._detections_cache) > 1000:
            self._detections_cache = self._detections_cache[-1000:]
        if self.on_new_detection:
            self.on_new_detection(detection)

    def get_statistics(self, days: int = 7) -> Optional[DictWrapper]:
        """Récupère les statistiques de détection."""
        if hasattr(self.api_client, 'get_statistics'):
            response = self.api_client.get_statistics()
        else:
            response = self.api_client._request("GET", f"/statistics/detections?days={days}")
        
        if response and response.success and response.data:
            return DictWrapper(response.data)
        return None

    @staticmethod
    def filter_by_severity(alerts: List[Any], severity: Any) -> List[Any]:
        """Filtre les alertes par gravité."""
        sev_val = severity.value if hasattr(severity, "value") else severity
        return [
            a for a in alerts 
            if (hasattr(a.severity, "value") and a.severity.value == sev_val) or a.severity == severity
        ]

    @staticmethod
    def filter_by_camera(alerts: List[Any], camera_id: int) -> List[Any]:
        """Filtre les alertes par caméra."""
        return [a for a in alerts if getattr(a, "camera_id", None) == camera_id]
