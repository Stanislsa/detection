"""
Bot Telegram pour les notifications d'alerte.

Notifications push instantanées via Telegram Bot API.
"""

import asyncio
import time
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path

from telegram import Bot, InputFile
from telegram.error import TelegramError

from app.config import settings
from app.core import GravityLevel


class TelegramBot:
    """
    Bot Telegram asynchrone pour l'envoi d'alertes.
    
    Fonctionnalités:
    - Envoi de messages textuels
    - Envoi d'images (squelette)
    - Rate limiting (1 alerte/minute)
    - Templates de messages personnalisés
    """
    
    def __init__(self):
        """Initialise le bot Telegram."""
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN non configuré")
        
        self.bot = Bot(token=self.bot_token)
        
        # Rate limiting
        self.last_alert_time = 0
        self.min_alert_interval = settings.ALERT_COOLDOWN_SECONDS
    
    async def send_fall_alert(
        self,
        person_name: str,
        gravity_level: GravityLevel,
        gravity_score: float,
        location: str = None,
        gps_coords: tuple = None,
        image_path: Path = None
    ) -> Dict[str, any]:
        """
        Envoie une alerte de chute.
        
        Args:
            person_name: Nom de la personne
            gravity_level: Niveau de gravité
            gravity_score: Score de gravité [0, 100]
            location: Lieu de la chute (pièce, adresse)
            gps_coords: Coordonnées GPS (latitude, longitude)
            image_path: Chemin de l'image à envoyer (squelette)
        
        Returns:
            Dictionnaire avec le résultat de l'envoi
        """
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_alert_time < self.min_alert_interval:
            return {
                "success": False,
                "error": "rate_limited",
                "message": "Trop d'alertes, veuillez attendre"
            }
        
        self.last_alert_time = current_time
        
        # Générer le message
        message = self._template_fall_alert(
            person_name=person_name,
            gravity_level=gravity_level,
            gravity_score=gravity_score,
            location=location,
            gps_coords=gps_coords
        )
        
        try:
            start_time = time.time()
            
            # Envoyer le message texte
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="HTML"
            )
            
            # Envoyer l'image si fournie
            if image_path and image_path.exists():
                with open(image_path, 'rb') as photo:
                    await self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=InputFile(photo),
                        caption="Squelette détecté"
                    )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return {
                "success": True,
                "channel": "telegram",
                "recipient": self.chat_id,
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except TelegramError as e:
            return {
                "success": False,
                "error": str(e),
                "channel": "telegram",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def send_fall_confirmed(
        self,
        person_name: str,
        confirmed_by: str,
        notes: str = None
    ) -> Dict[str, any]:
        """
        Envoie une notification de confirmation de chute.
        
        Args:
            person_name: Nom de la personne
            confirmed_by: Qui a confirmé
            notes: Notes additionnelles
        
        Returns:
            Résultat de l'envoi
        """
        message = self._template_fall_confirmed(
            person_name=person_name,
            confirmed_by=confirmed_by,
            notes=notes
        )
        
        try:
            start_time = time.time()
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="HTML"
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return {
                "success": True,
                "channel": "telegram",
                "latency_ms": latency_ms
            }
            
        except TelegramError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_test_message(self) -> Dict[str, any]:
        """
        Envoie un message de test.
        
        Returns:
            Résultat de l'envoi
        """
        message = self._template_test()
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="HTML"
            )
            
            return {
                "success": True,
                "message": "Test message sent"
            }
            
        except TelegramError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _template_fall_alert(
        self,
        person_name: str,
        gravity_level: GravityLevel,
        gravity_score: float,
        location: str = None,
        gps_coords: tuple = None
    ) -> str:
        """
        Génère le template d'alerte de chute.
        
        Args:
            person_name: Nom de la personne
            gravity_level: Niveau de gravité
            gravity_score: Score de gravité
            location: Lieu
            gps_coords: Coordonnées GPS
        
        Returns:
            Message HTML
        """
        # Emoji selon le niveau de gravité
        gravity_emojis = {
            GravityLevel.FAIBLE: "⚠️",
            GravityLevel.MOYENNE: "🟡",
            GravityLevel.ELEVEE: "🟠",
            GravityLevel.CRITIQUE: "🔴"
        }
        
        emoji = gravity_emojis.get(gravity_level, "⚠️")
        
        message = f"""
{emoji} <b>ALERTE CHUTE DÉTECTÉE</b> {emoji}

<b>Personne :</b> {person_name}
<b>Niveau de gravité :</b> {gravity_level.value.upper()} ({gravity_score:.1f}/100)
<b>Heure :</b> {datetime.utcnow().strftime('%H:%M:%S')}
"""
        
        if location:
            message += f"<b>Lieu :</b> {location}\n"
        
        if gps_coords:
            lat, lon = gps_coords
            message += f"<b>GPS :</b> <a href='https://maps.google.com/?q={lat},{lon}'>{lat:.4f}, {lon:.4f}</a>\n"
        
        message += "\n<b>Veuillez vérifier la situation immédiatement !</b>"
        
        return message.strip()
    
    def _template_fall_confirmed(
        self,
        person_name: str,
        confirmed_by: str,
        notes: str = None
    ) -> str:
        """
        Génère le template de confirmation de chute.
        
        Args:
            person_name: Nom de la personne
            confirmed_by: Qui a confirmé
            notes: Notes
        
        Returns:
            Message HTML
        """
        message = f"""
✅ <b>CHUTE CONFIRMÉE</b>

<b>Personne :</b> {person_name}
<b>Confirmé par :</b> {confirmed_by}
<b>Heure :</b> {datetime.utcnow().strftime('%H:%M:%S')}
"""
        
        if notes:
            message += f"<b>Notes :</b> {notes}\n"
        
        return message.strip()
    
    def _template_test(self) -> str:
        """
        Génère un message de test.
        
        Returns:
            Message HTML
        """
        return f"""
🧪 <b>MESSAGE DE TEST</b>

Le système de détection de chutes fonctionne correctement.
<b>Heure :</b> {datetime.utcnow().strftime('%H:%M:%S')}
"""
    
    async def close(self):
        """Ferme la connexion du bot."""
        if self.bot:
            await self.bot.close()
    
    def __aenter__(self):
        """Context manager entry."""
        return self
    
    def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        return self.close()
