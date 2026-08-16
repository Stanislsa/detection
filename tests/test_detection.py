"""
Tests pour le service de détection.
Tests unitaires de la gestion des détections IA.
"""

import pytest
from unittest.mock import Mock, patch
from desktop.services.detection_service import DetectionService
from desktop.services.api_client import APIClient, APIResponse
from desktop.models.alert import Alert, AlertSeverity, AlertStatus, AlertType
from datetime import datetime


class TestDetectionService:
    """Tests pour la classe DetectionService."""
    
    def setup_method(self):
        """Initialise le service de détection pour chaque test."""
        self.mock_api_client = Mock(spec=APIClient)
        self.detection_service = DetectionService(self.mock_api_client)
    
    def test_initialization(self):
        """Test l'initialisation du service de détection."""
        assert self.detection_service.api_client == self.mock_api_client
        assert self.detection_service._detections_cache == []
    
    def test_get_detections_with_cache(self):
        """Test la récupération des détections depuis le cache."""
        # Préparer le cache
        alert = Alert(
            id=1,
            camera_id=1,
            camera_name="Camera 1",
            alert_type=AlertType.FALL,
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.NEW,
            detected_at=datetime.now(),
            confidence=0.95,
            bbox=(100, 100, 200, 300)
        )
        self.detection_service._detections_cache = [alert]
        
        # Récupérer depuis le cache
        detections = self.detection_service.get_detections(use_cache=True)
        
        assert len(detections) == 1
        assert detections[0].id == 1
        assert detections[0].alert_type == AlertType.FALL
    
    def test_get_detections_from_api(self):
        """Test la récupération des détections depuis l'API."""
        # Mock la réponse API
        mock_response = APIResponse(
            success=True,
            data=[
                {
                    "id": 1,
                    "camera_id": 1,
                    "camera_name": "Camera 1",
                    "alert_type": "fall",
                    "severity": "critical",
                    "status": "new",
                    "detected_at": datetime.now().isoformat(),
                    "confidence": 0.95,
                    "bbox": [100, 100, 200, 300]
                }
            ]
        )
        self.mock_api_client.get_detections.return_value = mock_response
        
        # Récupérer depuis l'API
        detections = self.detection_service.get_detections(use_cache=False)
        
        assert len(detections) == 1
        assert detections[0].alert_type == AlertType.FALL
        assert self.mock_api_client.get_detections.called
    
    def test_get_detection_by_id(self):
        """Test la récupération d'une détection par son ID."""
        alert = Alert(
            id=1,
            camera_id=1,
            camera_name="Camera 1",
            alert_type=AlertType.FALL,
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.NEW,
            detected_at=datetime.now(),
            confidence=0.95,
            bbox=(100, 100, 200, 300)
        )
        self.detection_service._detections_cache = [alert]
        
        retrieved = self.detection_service.get_detection(1)
        
        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.alert_type == AlertType.FALL
    
    def test_get_detection_not_found(self):
        """Test la récupération d'une détection inexistante."""
        retrieved = self.detection_service.get_detection(999)
        
        assert retrieved is None
    
    def test_get_statistics(self):
        """Test la récupération des statistiques."""
        mock_response = APIResponse(
            success=True,
            data={
                "total_alerts": 100,
                "critical_alerts": 10,
                "high_alerts": 20,
                "medium_alerts": 30,
                "low_alerts": 40,
                "total_detections": 500,
                "fall_detections": 50,
                "intrusion_detections": 100,
                "movement_detections": 350,
                "active_cameras": 5,
                "online_cameras": 4,
                "offline_cameras": 1
            }
        )
        self.mock_api_client.get_statistics.return_value = mock_response
        
        stats = self.detection_service.get_statistics()
        
        assert stats is not None
        assert stats.total_alerts == 100
        assert stats.critical_alerts == 10
        assert stats.fall_detections == 50
    
    def test_update_detection_status(self):
        """Test la mise à jour du statut d'une détection."""
        detection_id = 1
        new_status = AlertStatus.RESOLVED
        
        mock_response = APIResponse(success=True, data=None)
        self.mock_api_client.update_detection_status.return_value = mock_response
        
        result = self.detection_service.update_detection_status(detection_id, new_status)
        
        assert result is True
        assert self.mock_api_client.update_detection_status.called
        self.mock_api_client.update_detection_status.assert_called_with(detection_id, new_status.value)
    
    def test_filter_by_severity(self):
        """Test le filtrage des détections par gravité."""
        alerts = [
            Alert(
                id=1,
                camera_id=1,
                camera_name="Camera 1",
                alert_type=AlertType.FALL,
                severity=AlertSeverity.CRITICAL,
                status=AlertStatus.NEW,
                detected_at=datetime.now(),
                confidence=0.95,
                bbox=(100, 100, 200, 300)
            ),
            Alert(
                id=2,
                camera_id=1,
                camera_name="Camera 1",
                alert_type=AlertType.MOVEMENT,
                severity=AlertSeverity.LOW,
                status=AlertStatus.NEW,
                detected_at=datetime.now(),
                confidence=0.80,
                bbox=(50, 50, 150, 250)
            )
        ]
        
        critical = self.detection_service.filter_by_severity(alerts, AlertSeverity.CRITICAL)
        
        assert len(critical) == 1
        assert critical[0].severity == AlertSeverity.CRITICAL
    
    def test_filter_by_camera(self):
        """Test le filtrage des détections par caméra."""
        alerts = [
            Alert(
                id=1,
                camera_id=1,
                camera_name="Camera 1",
                alert_type=AlertType.FALL,
                severity=AlertSeverity.CRITICAL,
                status=AlertStatus.NEW,
                detected_at=datetime.now(),
                confidence=0.95,
                bbox=(100, 100, 200, 300)
            ),
            Alert(
                id=2,
                camera_id=2,
                camera_name="Camera 2",
                alert_type=AlertType.MOVEMENT,
                severity=AlertSeverity.LOW,
                status=AlertStatus.NEW,
                detected_at=datetime.now(),
                confidence=0.80,
                bbox=(50, 50, 150, 250)
            )
        ]
        
        camera1_alerts = self.detection_service.filter_by_camera(alerts, 1)
        
        assert len(camera1_alerts) == 1
        assert camera1_alerts[0].camera_id == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
