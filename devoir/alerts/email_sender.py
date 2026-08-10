"""
Client SMTP asynchrone pour l'envoi d'emails d'alerte.

Emails détaillés avec bilan HTML via SMTP.
"""

import asyncio
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path

import aiosmtplib
from aiosmtplib import SMTP

from config import settings
from detection.gravity_scorer import GravityLevel


class EmailSender:
    """
    Client SMTP asynchrone pour l'envoi d'emails.
    
    Fonctionnalités:
    - Envoi d'emails HTML
    - Pièces jointes (images)
    - Templates HTML personnalisés
    - Connexion sécurisée STARTTLS
    """
    
    def __init__(self):
        """Initialise le client SMTP."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        
        if not self.smtp_username or not self.smtp_password:
            raise ValueError("SMTP_USERNAME et SMTP_PASSWORD non configurés")
        
        # Rate limiting
        self.last_email_time = 0
        self.min_email_interval = 60.0  # 1 minute entre les emails
    
    async def send_fall_alert(
        self,
        recipient_email: str,
        person_name: str,
        gravity_level: GravityLevel,
        gravity_score: float,
        location: str = None,
        gps_coords: tuple = None,
        image_path: Path = None
    ) -> Dict[str, any]:
        """
        Envoie un email d'alerte de chute.
        
        Args:
            recipient_email: Email du destinataire
            person_name: Nom de la personne
            gravity_level: Niveau de gravité
            gravity_score: Score de gravité [0, 100]
            location: Lieu de la chute
            gps_coords: Coordonnées GPS (latitude, longitude)
            image_path: Chemin de l'image à joindre
        
        Returns:
            Dictionnaire avec le résultat de l'envoi
        """
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_email_time < self.min_email_interval:
            return {
                "success": False,
                "error": "rate_limited",
                "message": "Trop d'emails, veuillez attendre"
            }
        
        self.last_email_time = current_time
        
        # Générer le contenu HTML
        html_content = self._template_fall_alert_html(
            person_name=person_name,
            gravity_level=gravity_level,
            gravity_score=gravity_score,
            location=location,
            gps_coords=gps_coords
        )
        
        # Créer le message
        message = MIMEMultipart("related")
        message["Subject"] = f"⚠️ ALERTE CHUTE - {person_name}"
        message["From"] = self.email_from
        message["To"] = recipient_email
        
        # Ajouter le contenu HTML
        message.attach(MIMEText(html_content, "html"))
        
        # Ajouter l'image si fournie
        if image_path and image_path.exists():
            with open(image_path, 'rb') as f:
                img_data = f.read()
            
            image = MIMEImage(img_data)
            image.add_header("Content-ID", "<skeleton>")
            image.add_header("Content-Disposition", "inline", filename="skeleton.png")
            message.attach(image)
        
        try:
            start_time = time.time()
            
            # Envoyer l'email
            await self._send_email(message, recipient_email)
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return {
                "success": True,
                "channel": "email",
                "recipient": recipient_email,
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "channel": "email",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def send_fall_confirmed(
        self,
        recipient_email: str,
        person_name: str,
        confirmed_by: str,
        notes: str = None
    ) -> Dict[str, any]:
        """
        Envoie un email de confirmation de chute.
        
        Args:
            recipient_email: Email du destinataire
            person_name: Nom de la personne
            confirmed_by: Qui a confirmé
            notes: Notes additionnelles
        
        Returns:
            Résultat de l'envoi
        """
        html_content = self._template_fall_confirmed_html(
            person_name=person_name,
            confirmed_by=confirmed_by,
            notes=notes
        )
        
        message = MIMEMultipart("alternative")
        message["Subject"] = f"✅ Chute confirmée - {person_name}"
        message["From"] = self.email_from
        message["To"] = recipient_email
        
        message.attach(MIMEText(html_content, "html"))
        
        try:
            start_time = time.time()
            
            await self._send_email(message, recipient_email)
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return {
                "success": True,
                "channel": "email",
                "latency_ms": latency_ms
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_test_email(self, recipient_email: str) -> Dict[str, any]:
        """
        Envoie un email de test.
        
        Args:
            recipient_email: Email du destinataire
        
        Returns:
            Résultat de l'envoi
        """
        html_content = self._template_test_html()
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "🧪 Test - Système de détection de chutes"
        message["From"] = self.email_from
        message["To"] = recipient_email
        
        message.attach(MIMEText(html_content, "html"))
        
        try:
            await self._send_email(message, recipient_email)
            
            return {
                "success": True,
                "message": "Test email sent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_email(self, message: MIMEMultipart, recipient: str):
        """
        Envoie l'email via SMTP.
        
        Args:
            message: Message MIME
            recipient: Destinataire
        """
        async with SMTP(
            hostname=self.smtp_host,
            port=self.smtp_port,
            use_tls=True
        ) as smtp:
            await smtp.login(self.smtp_username, self.smtp_password)
            await smtp.send_message(message, self.email_from, recipient)
    
    def _template_fall_alert_html(
        self,
        person_name: str,
        gravity_level: GravityLevel,
        gravity_score: float,
        location: str = None,
        gps_coords: tuple = None
    ) -> str:
        """
        Génère le template HTML d'alerte de chute.
        
        Args:
            person_name: Nom de la personne
            gravity_level: Niveau de gravité
            gravity_score: Score de gravité
            location: Lieu
            gps_coords: Coordonnées GPS
        
        Returns:
            Contenu HTML
        """
        # Couleur selon le niveau de gravité
        gravity_colors = {
            GravityLevel.FAIBLE: "#FFA500",  # Orange
            GravityLevel.MOYENNE: "#FFD700",  # Jaune
            GravityLevel.ELEVEE: "#FF4500",  # Orange rouge
            GravityLevel.CRITIQUE: "#FF0000"  # Rouge
        }
        
        color = gravity_colors.get(gravity_level, "#FFA500")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .alert-box {{ background-color: {color}; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .info-box {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 10px; }}
        .label {{ font-weight: bold; }}
        .gps-link {{ color: #0066cc; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="alert-box">
            <h1>⚠️ ALERTE CHUTE DÉTECTÉE ⚠️</h1>
        </div>
        
        <div class="info-box">
            <p><span class="label">Personne :</span> {person_name}</p>
            <p><span class="label">Niveau de gravité :</span> {gravity_level.value.upper()} ({gravity_score:.1f}/100)</p>
            <p><span class="label">Heure :</span> {datetime.utcnow().strftime('%H:%M:%S')}</p>
"""
        
        if location:
            html += f'            <p><span class="label">Lieu :</span> {location}</p>\n'
        
        if gps_coords:
            lat, lon = gps_coords
            html += f'            <p><span class="label">GPS :</span> <a href="https://maps.google.com/?q={lat},{lon}" class="gps-link">{lat:.4f}, {lon:.4f}</a></p>\n'
        
        html += f"""
        </div>
        
        <p style="color: red; font-weight: bold; font-size: 18px;">
            Veuillez vérifier la situation immédiatement !
        </p>
    </div>
</body>
</html>
"""
        
        return html.strip()
    
    def _template_fall_confirmed_html(
        self,
        person_name: str,
        confirmed_by: str,
        notes: str = None
    ) -> str:
        """
        Génère le template HTML de confirmation de chute.
        
        Args:
            person_name: Nom de la personne
            confirmed_by: Qui a confirmé
            notes: Notes
        
        Returns:
            Contenu HTML
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .success-box {{ background-color: #28a745; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .info-box {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .label {{ font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-box">
            <h1>✅ CHUTE CONFIRMÉE</h1>
        </div>
        
        <div class="info-box">
            <p><span class="label">Personne :</span> {person_name}</p>
            <p><span class="label">Confirmé par :</span> {confirmed_by}</p>
            <p><span class="label">Heure :</span> {datetime.utcnow().strftime('%H:%M:%S')}</p>
"""
        
        if notes:
            html += f'            <p><span class="label">Notes :</span> {notes}</p>\n'
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        
        return html.strip()
    
    def _template_test_html(self) -> str:
        """
        Génère un email de test.
        
        Returns:
            Contenu HTML
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .test-box {{ background-color: #17a2b8; color: white; padding: 20px; border-radius: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="test-box">
            <h1>🧪 MESSAGE DE TEST</h1>
        </div>
        
        <p>Le système de détection de chutes fonctionne correctement.</p>
        <p><strong>Heure :</strong> {datetime.utcnow().strftime('%H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        return html.strip()


# Fonction utilitaire pour l'envoi d'email
async def send_email_alert(
    recipient_email: str,
    person_name: str,
    gravity_level: GravityLevel,
    gravity_score: float,
    location: str = None,
    gps_coords: tuple = None,
    image_path: Path = None
) -> Dict[str, any]:
    """
    Fonction utilitaire pour envoyer un email d'alerte.
    
    Args:
        recipient_email: Email du destinataire
        person_name: Nom de la personne
        gravity_level: Niveau de gravité
        gravity_score: Score de gravité
        location: Lieu
        gps_coords: Coordonnées GPS
        image_path: Chemin de l'image
    
    Returns:
        Résultat de l'envoi
    """
    sender = EmailSender()
    return await sender.send_fall_alert(
        recipient_email=recipient_email,
        person_name=person_name,
        gravity_level=gravity_level,
        gravity_score=gravity_score,
        location=location,
        gps_coords=gps_coords,
        image_path=image_path
    )
