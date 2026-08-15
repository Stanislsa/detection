"""
Unified notification manager with rate limiting and retry logic.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from backend.core.config import settings
from backend.core.constants import AlertChannel, GravityLevel
from backend.core.logger import get_logger
from backend.core.exceptions import NotificationException

logger = get_logger(__name__)


class BaseNotificationProvider(ABC):
    """Base class for notification providers."""
    
    def __init__(self):
        """Initialize provider."""
        self._logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    async def send(self, recipient: str, message: str, **kwargs) -> Dict[str, Any]:
        """
        Send notification.
        
        Args:
            recipient: Recipient identifier
            message: Message content
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Result dict with success status and metadata
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider configuration.
        
        Returns:
            True if configuration is valid
        """
        pass


class NotificationManager:
    """
    Unified notification manager with rate limiting and retry logic.
    
    Manages multiple notification providers with fallback and retry capabilities.
    """
    
    def __init__(self):
        """Initialize notification manager."""
        self.providers: Dict[AlertChannel, BaseNotificationProvider] = {}
        self.rate_limits: Dict[str, float] = {}  # recipient -> last_send_time
        self.min_interval = settings.TELEGRAM_ALERT_COOLDOWN  # seconds
        
        self._initialize_providers()
        logger.info("Notification manager initialized")
    
    def _initialize_providers(self):
        """Initialize all configured notification providers."""
        from .providers import TelegramProvider, EmailProvider
        
        # Telegram
        if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
            self.providers[AlertChannel.TELEGRAM] = TelegramProvider()
            logger.info("Telegram provider initialized")
        
        # Email
        if settings.SMTP_HOST and settings.SMTP_USER:
            self.providers[AlertChannel.EMAIL] = EmailProvider()
            logger.info("Email provider initialized")
    
    def register_provider(self, channel: AlertChannel, provider: BaseNotificationProvider):
        """
        Register a notification provider.
        
        Args:
            channel: Alert channel
            provider: Provider instance
        """
        self.providers[channel] = provider
        logger.info(f"Provider registered for channel: {channel.value}")
    
    def _check_rate_limit(self, recipient: str) -> bool:
        """
        Check if recipient is rate limited.
        
        Args:
            recipient: Recipient identifier
        
        Returns:
            True if rate limited (should not send)
        """
        current_time = time.time()
        last_send = self.rate_limits.get(recipient, 0)
        
        if current_time - last_send < self.min_interval:
            return True
        
        return False
    
    def _update_rate_limit(self, recipient: str):
        """
        Update rate limit for recipient.
        
        Args:
            recipient: Recipient identifier
        """
        self.rate_limits[recipient] = time.time()
    
    async def send_notification(
        self,
        channel: AlertChannel,
        recipient: str,
        message: str,
        subject: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send notification via specified channel.
        
        Args:
            channel: Notification channel
            recipient: Recipient identifier
            message: Message content
            subject: Subject (for email)
            **kwargs: Additional parameters
        
        Returns:
            Result dict
        """
        if channel not in self.providers:
            raise NotificationException(f"Provider not available for channel: {channel.value}")
        
        # Check rate limit
        if self._check_rate_limit(recipient):
            return {
                "success": False,
                "error": "rate_limited",
                "message": "Too many notifications, please wait"
            }
        
        provider = self.providers[channel]
        
        try:
            start_time = time.time()
            
            result = await provider.send(recipient, message, subject=subject, **kwargs)
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Update rate limit on success
            if result.get("success"):
                self._update_rate_limit(recipient)
                result["latency_ms"] = latency_ms
                result["timestamp"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "channel": channel.value,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def send_fall_alert(
        self,
        person_name: str,
        gravity_level: GravityLevel,
        gravity_score: float,
        location: Optional[str] = None,
        gps_coords: Optional[tuple] = None,
        image_path: Optional[str] = None,
        channels: Optional[List[AlertChannel]] = None
    ) -> List[Dict[str, Any]]:
        """
        Send fall alert via multiple channels.
        
        Args:
            person_name: Person's name
            gravity_level: Gravity level
            gravity_score: Gravity score (0-100)
            location: Location description
            gps_coords: GPS coordinates (lat, lon)
            image_path: Path to image attachment
            channels: Channels to use (default: all available)
        
        Returns:
            List of results per channel
        """
        from .templates import TemplateManager
        
        template_manager = TemplateManager()
        
        # Generate message
        message = template_manager.generate_fall_alert(
            person_name=person_name,
            gravity_level=gravity_level,
            gravity_score=gravity_score,
            location=location,
            gps_coords=gps_coords
        )
        
        # Determine channels
        if channels is None:
            channels = list(self.providers.keys())
        
        # Send to all channels
        results = []
        for channel in channels:
            try:
                result = await self.send_notification(
                    channel=channel,
                    recipient=self._get_recipient_for_channel(channel),
                    message=message,
                    subject=f"🚨 FALL ALERT - {person_name}",
                    image_path=image_path
                )
                results.append({
                    "channel": channel.value,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Failed to send via {channel.value}: {e}")
                results.append({
                    "channel": channel.value,
                    "result": {"success": False, "error": str(e)}
                })
        
        return results
    
    def _get_recipient_for_channel(self, channel: AlertChannel) -> str:
        """Get recipient for channel from settings."""
        if channel == AlertChannel.TELEGRAM:
            return settings.TELEGRAM_CHAT_ID
        elif channel == AlertChannel.EMAIL:
            return settings.SMTP_USER  # Using SMTP_USER as fallback
        else:
            return "default"
    
    async def send_test_notification(
        self,
        channel: AlertChannel,
        recipient: str
    ) -> Dict[str, Any]:
        """
        Send a test notification.
        
        Args:
            channel: Channel to use
            recipient: Recipient
        
        Returns:
            Result dict
        """
        from .templates import TemplateManager
        
        template_manager = TemplateManager()
        message = template_manager.generate_test_message()
        
        return await self.send_notification(
            channel=channel,
            recipient=recipient,
            message=message,
            subject="Test Notification"
        )
    
    async def send_with_retry(
        self,
        channel: AlertChannel,
        recipient: str,
        message: str,
        max_retries: int = 3,
        retry_delay: float = 5.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send notification with retry logic.
        
        Args:
            channel: Notification channel
            recipient: Recipient
            message: Message content
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries (seconds)
            **kwargs: Additional parameters
        
        Returns:
            Result dict
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await self.send_notification(channel, recipient, message, **kwargs)
                
                if result.get("success"):
                    result["attempts"] = attempt + 1
                    return result
                
                last_error = result.get("error")
                
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Attempt {attempt + 1} failed with exception: {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
        
        return {
            "success": False,
            "error": last_error or "Max retries exceeded",
            "attempts": max_retries,
            "channel": channel.value
        }


# Global notification manager instance
notification_manager = NotificationManager()
