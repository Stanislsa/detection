"""
Tests pour l'authentification.
Tests unitaires du login dialog et de la gestion JWT.
"""

import pytest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
import sys

from app.desktop.auth.login_dialog import LoginDialog
from app.desktop.services.api_client import APIClient, APIResponse


class TestLoginDialog:
    """Tests pour la classe LoginDialog."""
    
    @pytest.fixture
    def app(self):
        """Fixture pour l'application PyQt."""
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def mock_api_client(self):
        """Fixture pour le client API mock."""
        return Mock(spec=APIClient)
    
    def test_initialization(self, app, mock_api_client):
        """Test l'initialisation du dialog de connexion."""
        dialog = LoginDialog(mock_api_client)
        
        assert dialog.api_client == mock_api_client
        assert dialog.mfa_required is False
    
    def test_login_success(self, app, mock_api_client):
        """Test une connexion réussie."""
        # Mock la réponse API
        mock_response = APIResponse(
            success=True,
            data={
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "user": {
                    "id": 1,
                    "username": "testuser",
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "role": "admin"
                }
            }
        )
        mock_api_client.login.return_value = mock_response
        
        dialog = LoginDialog(mock_api_client)
        dialog.username_input.setText("testuser")
        dialog.password_input.setText("password")
        
        # Simuler le clic sur le bouton de connexion
        dialog._attempt_login()
        
        assert mock_api_client.login.called
        mock_api_client.login.assert_called_with("testuser", "password", None)
    
    def test_login_with_mfa(self, app, mock_api_client):
        """Test une connexion avec MFA."""
        # Mock la réponse API (MFA requis)
        mock_response = APIResponse(
            success=False,
            error="MFA required",
            status_code=401
        )
        mock_api_client.login.return_value = mock_response
        
        dialog = LoginDialog(mock_api_client)
        dialog.username_input.setText("testuser")
        dialog.password_input.setText("password")
        
        # Simuler le clic sur le bouton de connexion
        dialog._attempt_login()
        
        # Vérifier que le champ MFA est affiché
        assert dialog.mfa_required is True
    
    def test_login_failure(self, app, mock_api_client):
        """Test une connexion échouée."""
        # Mock la réponse API
        mock_response = APIResponse(
            success=False,
            error="Invalid credentials",
            status_code=401
        )
        mock_api_client.login.return_value = mock_response
        
        dialog = LoginDialog(mock_api_client)
        dialog.username_input.setText("testuser")
        dialog.password_input.setText("wrongpassword")
        
        # Simuler le clic sur le bouton de connexion
        dialog._attempt_login()
        
        assert mock_api_client.login.called
        # Vérifier qu'un message d'erreur est affiché (implémentation spécifique)


class TestJWTAuthentication:
    """Tests pour l'authentification JWT."""
    
    def setup_method(self):
        """Initialise le client API pour chaque test."""
        self.api_client = APIClient(base_url="http://test.local/api/v1")
    
    def test_token_storage(self):
        """Test le stockage des tokens."""
        access_token = "test_access_token"
        refresh_token = "test_refresh_token"
        
        self.api_client.set_auth_tokens(access_token, refresh_token)
        
        assert self.api_client.access_token == access_token
        assert self.api_client.refresh_token == refresh_token
    
    def test_token_in_header(self):
        """Test que le token est ajouté aux headers."""
        access_token = "test_access_token"
        
        self.api_client.set_auth_tokens(access_token, "refresh")
        
        assert "Authorization" in self.api_client.session.headers
        assert self.api_client.session.headers["Authorization"] == f"Bearer {access_token}"
    
    def test_token_clear(self):
        """Test l'effacement des tokens."""
        self.api_client.set_auth_tokens("access", "refresh")
        self.api_client.clear_auth()
        
        assert self.api_client.access_token is None
        assert self.api_client.refresh_token is None
        assert "Authorization" not in self.api_client.session.headers
    
    @patch('app.desktop.services.api_client.requests.Session.post')
    def test_token_refresh(self, mock_post):
        """Test le rafraîchissement du token."""
        # Mock la réponse de rafraîchissement
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token"
        }
        mock_post.return_value = mock_response
        
        self.api_client.set_auth_tokens("old_access", "old_refresh")
        
        result = self.api_client._refresh_token()
        
        assert result is True
        assert self.api_client.access_token == "new_access_token"
    
    @patch('app.desktop.services.api_client.requests.Session.post')
    def test_token_refresh_failure(self, mock_post):
        """Test l'échec du rafraîchissement du token."""
        # Mock une erreur
        mock_post.side_effect = Exception("Network error")
        
        self.api_client.set_auth_tokens("access", "refresh")
        
        result = self.api_client._refresh_token()
        
        assert result is False
        assert self.api_client.access_token == "access"  # Token inchangé


class TestMFA:
    """Tests pour l'authentification MFA (TOTP)."""
    
    def setup_method(self):
        """Initialise le client API pour chaque test."""
        self.api_client = APIClient(base_url="http://test.local/api/v1")
    
    @patch('app.desktop.services.api_client.requests.Session.request')
    def test_login_with_totp(self, mock_request):
        """Test une connexion avec code TOTP."""
        # Mock la réponse API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token"
        }
        mock_request.return_value = mock_response
        
        response = self.api_client.login("user", "password", "123456")
        
        assert response.success is True
        assert self.api_client.access_token == "test_access_token"
    
    @patch('app.desktop.services.api_client.requests.Session.request')
    def test_invalid_totp(self, mock_request):
        """Test un code TOTP invalide."""
        # Mock la réponse API
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid TOTP code"
        mock_request.return_value = mock_response
        
        response = self.api_client.login("user", "password", "000000")
        
        assert response.success is False
        assert response.error == "Invalid TOTP code"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
