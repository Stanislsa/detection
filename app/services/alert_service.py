"""
Service d'envoi d'alertes.

Envoi des notifications via Telegram et Email.
"""

from typing import Dict, Optional
from pathlib import Path

from app.config import settings
from app.core import GravityLevel
from app.services.telegram_bot import TelegramBot
from app.services.email_sender import EmailSender


class AlertService:
    """Service pour l'envoi d'alertes."""
    
    def __init__(self):
        """Initialise le service d'alertes."""
        self.telegram_bot = TelegramBot()
        self.email_sender = EmailSender()
    
    async def send_fall_alert(
        self,
        person_name: str,
        gravity_level: GravityLevel,
        gravity_score: float,
        location: str = None,
        gps_coords: tuple = None,
        image_path: Path = None,
        email_recipient: str = None
    ) -> Dict[str, any]:
        """
        Envoie une alerte de chute via les canaux configurés.
        
        Args:
            person_name: Nom de la personne
            gravity_level: Niveau de gravité
            gravity_score: Score de gravité
            location: Lieu de la chute
            gps_coords: Coordonnées GPS
            image_path: Chemin de l'image
            email_recipient: Email du destinataire
        
        Returns:
            Résultats de l'envoi
        """
        results = {
            "telegram": None,
            "email": None
        }
        
        # Envoi Telegram
        try:
            results["telegram"] = await self.telegram_bot.send_fall_alert(
                person_name=person_name,
                gravity_level=gravity_level,
                gravity_score=gravity_score,
                location=location,
                gps_coords=gps_coords,
                image_path=image_path
            )
        except Exception as e:
            results["telegram"] = {"success": False, "error": str(e)}
        
        # Envoi Email si configuré
        if email_recipient:
            try:
                results["email"] = await self.email_sender.send_fall_alert(
                    recipient_email=email_recipient,
                    person_name=person_name,
                    gravity_level=gravity_level,
                    gravity_score=gravity_score,
                    location=location,
                    gps_coords=gps_coords,
                    image_path=image_path
                )
            except Exception as e:
                results["email"] = {"success": False, "error": str(e)}
        
        return results
    
    async def send_fall_confirmed(
        self,
        person_name: str,
        confirmed_by: str,
        notes: str = None,
        email_recipient: str = None
    ) -> Dict[str, any]:
        """
        Envoie une notification de confirmation de chute.
        
        Args:
            person_name: Nom de la personne
            confirmed_by: Qui a confirmé
            notes: Notes additionnelles
            email_recipient: Email du destinataire
        
        Returns:
            Résultats de l'envoi
        """
        results = {
            "telegram": None,
            "email": None
        }
        
        # Envoi Telegram
        try:
            results["telegram"] = await self.telegram_bot.send_fall_confirmed(
                person_name=person_name,
                confirmed_by=confirmed_by,
                notes=notes
            )
        except Exception as e:
            results["telegram"] = {"success": False, "error": str(e)}
        
        # Envoi Email si configuré
        if email_recipient:
            try:
                results["email"] = await self.email_sender.send_fall_confirmed(
                    recipient_email=email_recipient,
                    person_name=person_name,
                    confirmed_by=confirmed_by,
                    notes=notes
                )
            except Exception as e:
                results["email"] = {"success": False, "error": str(e)}
        
        return results
    
    async def send_test_alert(self, email_recipient: str = None) -> Dict[str, any]:
        """
        Envoie une alerte de test.
        
        Args:
            email_recipient: Email du destinataire
        
        Returns:
            Résultats de l'envoi
        """
        results = {
            "telegram": None,
            "email": None
        }
        
        # Test Telegram
        try:
            results["telegram"] = await self.telegram_bot.send_test_message()
        except Exception as e:
            results["telegram"] = {"success": False, "error": str(e)}
        
        # Test Email si configuré
        if email_recipient:
            try:
                results["email"] = await self.email_sender.send_test_email(email_recipient)
            except Exception as e:
                results["email"] = {"success": False, "error": str(e)}
        
        return results
