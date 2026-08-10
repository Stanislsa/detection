"""
Client API pour communiquer avec le backend FastAPI.
Gère les requêtes HTTP, authentification JWT et erreurs.
"""

import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class APIResponse:
    """Réponse standardisée de l'API."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    status_code: int = 200


class APIClient:
    """
    Client HTTP pour communiquer avec l'API FastAPI.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        """
        Initialise le client API.
        
        Args:
            base_url: URL de base de l'API
        """
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def set_auth_tokens(self, access_token: str, refresh_token: str):
        """
        Définit les tokens d'authentification.
        
        Args:
            access_token: Token d'accès JWT
            refresh_token: Token de rafraîchissement JWT
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
    
    def clear_auth(self):
        """Efface les tokens d'authentification."""
        self.access_token = None
        self.refresh_token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
    
    def _request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """
        Effectue une requête HTTP.
        
        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint de l'API
            **kwargs: Arguments supplémentaires pour requests
        
        Returns:
            APIResponse
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 200:
                return APIResponse(
                    success=True,
                    data=response.json(),
                    status_code=response.status_code
                )
            elif response.status_code == 401:
                # Token expiré, tentative de rafraîchissement
                if self._refresh_token():
                    # Réessayer la requête
                    response = self.session.request(method, url, **kwargs)
                    if response.status_code == 200:
                        return APIResponse(
                            success=True,
                            data=response.json(),
                            status_code=response.status_code
                        )
                
                return APIResponse(
                    success=False,
                    error=response.text or "Authentification échouée",
                    status_code=401
                )
            else:
                return APIResponse(
                    success=False,
                    error=response.text,
                    status_code=response.status_code
                )
        
        except requests.exceptions.RequestException as e:
            return APIResponse(
                success=False,
                error=str(e),
                status_code=0
            )
    
    def _refresh_token(self) -> bool:
        """
        Tente de rafraîchir le token d'accès.
        
        Returns:
            True si succès, False sinon
        """
        if not self.refresh_token:
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.set_auth_tokens(
                    data.get("access_token"),
                    data.get("refresh_token", self.refresh_token)
                )
                return True
        
        except Exception:
            pass
        
        return False
    
    # ===== AUTHENTIFICATION =====
    
    def login(self, username: str, password: str, totp_code: Optional[str] = None) -> APIResponse:
        """
        Connexion utilisateur.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            totp_code: Code TOTP (optionnel si MFA activé)
        
        Returns:
            APIResponse avec tokens
        """
        payload = {"username": username, "password": password}
        if totp_code:
            payload["totp_code"] = totp_code
        
        response = self._request("POST", "/auth/login", json=payload)
        
        if response.success and response.data:
            self.set_auth_tokens(
                response.data.get("access_token"),
                response.data.get("refresh_token")
            )
        
        return response
    
    def logout(self) -> APIResponse:
        """
        Déconnexion utilisateur.
        
        Returns:
            APIResponse
        """
        response = self._request("POST", "/auth/logout")
        self.clear_auth()
        return response
    
    def verify_mfa(self, totp_code: str) -> APIResponse:
        """
        Vérifie le code MFA.
        
        Args:
            totp_code: Code TOTP
        
        Returns:
            APIResponse
        """
        return self._request("POST", "/auth/verify-mfa", json={"totp_code": totp_code})
    
    # ===== CAMÉRAS =====
    
    def get_cameras(self) -> APIResponse:
        """
        Récupère la liste des caméras.
        
        Returns:
            APIResponse avec la liste des caméras
        """
        return self._request("GET", "/cameras")
    
    def get_camera(self, camera_id: int) -> APIResponse:
        """
        Récupère les détails d'une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            APIResponse avec les détails de la caméra
        """
        return self._request("GET", f"/cameras/{camera_id}")
    
    def create_camera(self, camera_data: Dict) -> APIResponse:
        """
        Crée une nouvelle caméra.
        
        Args:
            camera_data: Données de la caméra
        
        Returns:
            APIResponse
        """
        return self._request("POST", "/cameras", json=camera_data)
    
    def update_camera(self, camera_id: int, camera_data: Dict) -> APIResponse:
        """
        Met à jour une caméra.
        
        Args:
            camera_id: ID de la caméra
            camera_data: Données de la caméra
        
        Returns:
            APIResponse
        """
        return self._request("PUT", f"/cameras/{camera_id}", json=camera_data)
    
    def delete_camera(self, camera_id: int) -> APIResponse:
        """
        Supprime une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            APIResponse
        """
        return self._request("DELETE", f"/cameras/{camera_id}")
    
    # ===== ALERTES =====
    
    def get_alerts(self, skip: int = 0, limit: int = 100) -> APIResponse:
        """
        Récupère la liste des alertes.
        
        Args:
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments
        
        Returns:
            APIResponse avec la liste des alertes
        """
        return self._request("GET", f"/alerts?skip={skip}&limit={limit}")
    
    def get_alert(self, alert_id: int) -> APIResponse:
        """
        Récupère les détails d'une alerte.
        
        Args:
            alert_id: ID de l'alerte
        
        Returns:
            APIResponse avec les détails de l'alerte
        """
        return self._request("GET", f"/alerts/{alert_id}")
    
    def update_alert(self, alert_id: int, alert_data: Dict) -> APIResponse:
        """
        Met à jour une alerte.
        
        Args:
            alert_id: ID de l'alerte
            alert_data: Données de l'alerte
        
        Returns:
            APIResponse
        """
        return self._request("PUT", f"/alerts/{alert_id}", json=alert_data)
    
    # ===== DÉTECTIONS =====
    
    def get_detections(self) -> APIResponse:
        """
        Récupère la liste des détections.
        
        Returns:
            APIResponse avec la liste des détections
        """
        return self._request("GET", "/detections")
    
    def update_detection_status(self, detection_id: int, status: str) -> APIResponse:
        """
        Met à jour le statut d'une détection.
        
        Args:
            detection_id: ID de la détection
            status: Nouveau statut
        
        Returns:
            APIResponse
        """
        return self._request("PUT", f"/detections/{detection_id}/status", json={"status": status})
    
    # ===== UTILISATEURS =====
    
    def get_users(self) -> APIResponse:
        """
        Récupère la liste des utilisateurs.
        
        Returns:
            APIResponse avec la liste des utilisateurs
        """
        return self._request("GET", "/users")
    
    def get_user(self, user_id: int) -> APIResponse:
        """
        Récupère les détails d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            APIResponse avec les détails de l'utilisateur
        """
        return self._request("GET", f"/users/{user_id}")
    
    def create_user(self, user_data: Dict) -> APIResponse:
        """
        Crée un nouvel utilisateur.
        
        Args:
            user_data: Données de l'utilisateur
        
        Returns:
            APIResponse
        """
        return self._request("POST", "/users", json=user_data)
    
    def update_user(self, user_id: int, user_data: Dict) -> APIResponse:
        """
        Met à jour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            user_data: Données de l'utilisateur
        
        Returns:
            APIResponse
        """
        return self._request("PUT", f"/users/{user_id}", json=user_data)
    
    def delete_user(self, user_id: int) -> APIResponse:
        """
        Supprime un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            APIResponse
        """
        return self._request("DELETE", f"/users/{user_id}")
    
    # ===== STATISTIQUES =====
    
    def get_statistics(self) -> APIResponse:
        """
        Récupère les statistiques globales.
        
        Returns:
            APIResponse avec les statistiques
        """
        return self._request("GET", "/statistics")
    
    def get_alerts_stats(self, days: int = 7) -> APIResponse:
        """
        Récupère les statistiques d'alertes.
        
        Args:
            days: Nombre de jours
        
        Returns:
            APIResponse avec les statistiques d'alertes
        """
        return self._request("GET", f"/statistics/alerts?days={days}")
