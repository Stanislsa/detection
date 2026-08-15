"""
Notification templates for different alert types.
"""

from typing import Optional
from datetime import datetime

from backend.core.constants import GravityLevel
from backend.core.logger import get_logger

logger = get_logger(__name__)


class AlertTemplate:
    """Base class for alert templates."""
    
    def __init__(self):
        """Initialize template."""
        self._logger = get_logger(self.__class__.__name__)
    
    def generate(self, **kwargs) -> str:
        """
        Generate alert message.
        
        Args:
            **kwargs: Template variables
        
        Returns:
            Formatted message
        """
        pass


class FallAlertTemplate(AlertTemplate):
    """Template for fall detection alerts."""
    
    def generate(
        self,
        person_name: str,
        gravity_level: GravityLevel,
        gravity_score: float,
        location: Optional[str] = None,
        gps_coords: Optional[tuple] = None
    ) -> str:
        """
        Generate fall alert message.
        
        Args:
            person_name: Person's name
            gravity_level: Gravity level
            gravity_score: Gravity score (0-100)
            location: Location description
            gps_coords: GPS coordinates (lat, lon)
        
        Returns:
            Formatted HTML message
        """
        # Emoji based on gravity level
        gravity_emojis = {
            GravityLevel.FAIBLE: "⚠️",
            GravityLevel.MOYENNE: "🟡",
            GravityLevel.ELEVEE: "🟠",
            GravityLevel.CRITIQUE: "🔴"
        }
        
        emoji = gravity_emojis.get(gravity_level, "⚠️")
        
        message = f"""
{emoji} <b>FALL DETECTED</b> {emoji}

<b>Person:</b> {person_name}
<b>Severity:</b> {gravity_level.value.upper()} ({gravity_score:.1f}/100)
<b>Time:</b> {datetime.utcnow().strftime('%H:%M:%S')}
"""
        
        if location:
            message += f"<b>Location:</b> {location}\n"
        
        if gps_coords:
            lat, lon = gps_coords
            message += f"<b>GPS:</b> <a href='https://maps.google.com/?q={lat},{lon}'>{lat:.4f}, {lon:.4f}</a>\n"
        
        message += "\n<b>Please check the situation immediately!</b>"
        
        return message.strip()


class FallConfirmedTemplate(AlertTemplate):
    """Template for fall confirmation alerts."""
    
    def generate(
        self,
        person_name: str,
        confirmed_by: str,
        notes: Optional[str] = None
    ) -> str:
        """
        Generate fall confirmation message.
        
        Args:
            person_name: Person's name
            confirmed_by: Who confirmed
            notes: Additional notes
        
        Returns:
            Formatted HTML message
        """
        message = f"""
✅ <b>FALL CONFIRMED</b>

<b>Person:</b> {person_name}
<b>Confirmed by:</b> {confirmed_by}
<b>Time:</b> {datetime.utcnow().strftime('%H:%M:%S')}
"""
        
        if notes:
            message += f"<b>Notes:</b> {notes}\n"
        
        return message.strip()


class TestAlertTemplate(AlertTemplate):
    """Template for test alerts."""
    
    def generate(self) -> str:
        """
        Generate test alert message.
        
        Returns:
            Formatted HTML message
        """
        return f"""
🧪 <b>TEST ALERT</b>

The SentinelAI notification system is working correctly.
<b>Time:</b> {datetime.utcnow().strftime('%H:%M:%S')}
<b>System:</b> SentinelAI v2.0.0
""".strip()


class TemplateManager:
    """Manager for notification templates."""
    
    def __init__(self):
        """Initialize template manager."""
        self.templates = {
            "fall_alert": FallAlertTemplate(),
            "fall_confirmed": FallConfirmedTemplate(),
            "test": TestAlertTemplate()
        }
    
    def generate_fall_alert(
        self,
        person_name: str,
        gravity_level: GravityLevel,
        gravity_score: float,
        location: Optional[str] = None,
        gps_coords: Optional[tuple] = None
    ) -> str:
        """
        Generate fall alert message.
        
        Args:
            person_name: Person's name
            gravity_level: Gravity level
            gravity_score: Gravity score
            location: Location
            gps_coords: GPS coordinates
        
        Returns:
            Formatted message
        """
        template = self.templates["fall_alert"]
        return template.generate(
            person_name=person_name,
            gravity_level=gravity_level,
            gravity_score=gravity_score,
            location=location,
            gps_coords=gps_coords
        )
    
    def generate_fall_confirmed(
        self,
        person_name: str,
        confirmed_by: str,
        notes: Optional[str] = None
    ) -> str:
        """
        Generate fall confirmation message.
        
        Args:
            person_name: Person's name
            confirmed_by: Who confirmed
            notes: Additional notes
        
        Returns:
            Formatted message
        """
        template = self.templates["fall_confirmed"]
        return template.generate(
            person_name=person_name,
            confirmed_by=confirmed_by,
            notes=notes
        )
    
    def generate_test_message(self) -> str:
        """
        Generate test message.
        
        Returns:
            Formatted message
        """
        template = self.templates["test"]
        return template.generate()
