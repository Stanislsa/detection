"""
Tests pour le service de caméras.
Tests unitaires de la gestion des caméras.
"""

import pytest
from unittest.mock import Mock, patch
from desktop.services.camera_service import CameraService, Camera
from desktop.services.api_client import APIClient, APIResponse


class TestCameraService:
    """Tests pour la classe CameraService."""
    
    def setup_method(self):
        """Initialise le service de caméras pour chaque test."""
        self.mock_api_client = Mock(spec=APIClient)
        self.camera_service = CameraService(self.mock_api_client)
    
    def test_initialization(self):
        """Test l'initialisation du service de caméras."""
        assert self.camera_service.api_client == self.mock_api_client
        assert self.camera_service._cameras_cache == {}
    
    def test_get_cameras_with_cache(self):
        """Test la récupération des caméras depuis le cache."""
        # Préparer le cache
        camera = Camera(
            id=1,
            name="Test Camera",
            source="rtsp://test",
            source_type="rtsp",
            room="Test",
            is_active=True,
            fps=30,
            resolution_width=1920,
            resolution_height=1080,
            status="online"
        )
        self.camera_service._cameras_cache[1] = camera
        
        # Récupérer depuis le cache
        cameras = self.camera_service.get_cameras(use_cache=True)
        
        assert len(cameras) == 1
        assert cameras[0].id == 1
        assert cameras[0].name == "Test Camera"
    
    def test_get_cameras_from_api(self):
        """Test la récupération des caméras depuis l'API."""
        # Mock la réponse API
        mock_response = APIResponse(
            success=True,
            data=[
                {
                    "id": 1,
                    "name": "Camera 1",
                    "source": "rtsp://cam1",
                    "source_type": "rtsp",
                    "room": "Room 1",
                    "is_active": True,
                    "fps": 30,
                    "resolution_width": 1920,
                    "resolution_height": 1080,
                    "status": "online"
                }
            ]
        )
        self.mock_api_client.get_cameras.return_value = mock_response
        
        # Récupérer depuis l'API
        cameras = self.camera_service.get_cameras(use_cache=False)
        
        assert len(cameras) == 1
        assert cameras[0].name == "Camera 1"
        assert self.mock_api_client.get_cameras.called
    
    def test_get_camera_by_id(self):
        """Test la récupération d'une caméra par son ID."""
        camera = Camera(
            id=1,
            name="Test Camera",
            source="rtsp://test",
            source_type="rtsp",
            room="Test",
            is_active=True,
            fps=30,
            resolution_width=1920,
            resolution_height=1080,
            status="online"
        )
        self.camera_service._cameras_cache[1] = camera
        
        retrieved = self.camera_service.get_camera(1)
        
        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.name == "Test Camera"
    
    def test_get_camera_not_found(self):
        """Test la récupération d'une caméra inexistante."""
        retrieved = self.camera_service.get_camera(999)
        
        assert retrieved is None
    
    def test_create_camera(self):
        """Test la création d'une caméra."""
        camera_data = {
            "name": "New Camera",
            "source": "rtsp://new",
            "source_type": "rtsp",
            "room": "New Room",
            "is_active": True,
            "fps": 30,
            "resolution": "1920x1080"
        }
        
        mock_response = APIResponse(
            success=True,
            data={
                "id": 2,
                "name": "New Camera",
                "source": "rtsp://new",
                "source_type": "rtsp",
                "room": "New Room",
                "is_active": True,
                "fps": 30,
                "resolution_width": 1920,
                "resolution_height": 1080,
                "status": "offline"
            }
        )
        self.mock_api_client.create_camera.return_value = mock_response
        
        camera = self.camera_service.create_camera(camera_data)
        
        assert camera is not None
        assert camera.id == 2
        assert camera.name == "New Camera"
    
    def test_update_camera(self):
        """Test la mise à jour d'une caméra."""
        camera_id = 1
        camera_data = {
            "name": "Updated Camera",
            "source": "rtsp://updated",
            "source_type": "rtsp",
            "room": "Updated Room",
            "is_active": False,
            "fps": 25,
            "resolution": "1280x720"
        }
        
        mock_response = APIResponse(
            success=True,
            data={
                "id": 1,
                "name": "Updated Camera",
                "source": "rtsp://updated",
                "source_type": "rtsp",
                "room": "Updated Room",
                "is_active": False,
                "fps": 25,
                "resolution_width": 1280,
                "resolution_height": 720,
                "status": "offline"
            }
        )
        self.mock_api_client.update_camera.return_value = mock_response
        
        camera = self.camera_service.update_camera(camera_id, camera_data)
        
        assert camera is not None
        assert camera.name == "Updated Camera"
        assert camera.is_active is False
    
    def test_delete_camera(self):
        """Test la suppression d'une caméra."""
        mock_response = APIResponse(success=True, data=None)
        self.mock_api_client.delete_camera.return_value = mock_response
        
        result = self.camera_service.delete_camera(1)
        
        assert result is True
        assert self.mock_api_client.delete_camera.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
