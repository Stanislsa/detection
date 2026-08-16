"""
Tests pour l'API Client.
Tests unitaires des communications avec le backend FastAPI.
"""

import pytest
from unittest.mock import Mock, patch
from desktop.services.api_client import APIClient, APIResponse


class TestAPIClient:
    """Tests pour la classe APIClient."""
    
    def setup_method(self):
        """Initialise le client API pour chaque test."""
        self.api_client = APIClient(base_url="http://test.local/api/v1")
    
    def test_initialization(self):
        """Test l'initialisation du client API."""
        assert self.api_client.base_url == "http://test.local/api/v1"
        assert self.api_client.access_token is None
        assert self.api_client.refresh_token is None
    
    def test_set_auth_tokens(self):
        """Test la définition des tokens d'authentification."""
        access_token = "test_access_token"
        refresh_token = "test_refresh_token"
        
        self.api_client.set_auth_tokens(access_token, refresh_token)
        
        assert self.api_client.access_token == access_token
        assert self.api_client.refresh_token == refresh_token
        assert "Authorization" in self.api_client.session.headers
        assert self.api_client.session.headers["Authorization"] == f"Bearer {access_token}"
    
    def test_clear_auth(self):
        """Test l'effacement des tokens d'authentification."""
        self.api_client.set_auth_tokens("access", "refresh")
        self.api_client.clear_auth()
        
        assert self.api_client.access_token is None
        assert self.api_client.refresh_token is None
        assert "Authorization" not in self.api_client.session.headers
    
    @patch('app.desktop.services.api_client.requests.Session.request')
    def test_successful_request(self, mock_request):
        """Test une requête réussie."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_request.return_value = mock_response
        
        response = self.api_client._request("GET", "/test")
        
        assert response.success is True
        assert response.data == {"data": "test"}
        assert response.status_code == 200
    
    @patch('app.desktop.services.api_client.requests.Session.request')
    def test_failed_request(self, mock_request):
        """Test une requête échouée."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_request.return_value = mock_response
        
        response = self.api_client._request("GET", "/test")
        
        assert response.success is False
        assert response.error == "Not Found"
        assert response.status_code == 404
    
    @patch('app.desktop.services.api_client.requests.Session.request')
    def test_login_success(self, mock_request):
        """Test une connexion réussie."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access",
            "refresh_token": "test_refresh"
        }
        mock_request.return_value = mock_response
        
        response = self.api_client.login("user", "pass")
        
        assert response.success is True
        assert self.api_client.access_token == "test_access"
        assert self.api_client.refresh_token == "test_refresh"
    
    @patch('app.desktop.services.api_client.requests.Session.request')
    def test_logout(self, mock_request):
        """Test la déconnexion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        self.api_client.set_auth_tokens("access", "refresh")
        response = self.api_client.logout()
        
        assert response.success is True
        assert self.api_client.access_token is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
