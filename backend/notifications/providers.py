"""
Notification providers for different channels.
"""

import asyncio
import time
from typing import Dict, Any, Optional
from pathlib import Path
from abc import ABC, abstractmethod

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.core.exceptions import NotificationException
from .manager import BaseNotificationProvider

logger = get_logger(__name__)


class TelegramProvider(BaseNotificationProvider):
    """Telegram bot notification provider."""
    
    def __init__(self):
        """Initialize Telegram provider."""
        super().__init__()
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.default_chat_id = settings.TELEGRAM_CHAT_ID
        
        if not self.bot_token:
            raise NotificationException("TELEGRAM_BOT_TOKEN not configured")
        
        try:
            from telegram import Bot
            self.bot = Bot(token=self.bot_token)
            self._logger.info("Telegram provider initialized")
        except ImportError:
            raise NotificationException("python-telegram-bot not installed")
    
    async def send(
        self, 
        recipient: str, 
        message: str, 
        subject: Optional[str] = None,
        image_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send Telegram message.
        
        Args:
            recipient: Chat ID
            message: Message content (HTML supported)
            subject: Not used for Telegram
            image_path: Path to image to send
            **kwargs: Additional parameters
        
        Returns:
            Result dict
        """
        try:
            start_time = time.time()
            
            # Send text message
            await self.bot.send_message(
                chat_id=recipient,
                text=message,
                parse_mode="HTML"
            )
            
            # Send image if provided
            if image_path and Path(image_path).exists():
                from telegram import InputFile
                with open(image_path, 'rb') as photo:
                    await self.bot.send_photo(
                        chat_id=recipient,
                        photo=InputFile(photo),
                        caption="Detection result"
                    )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return {
                "success": True,
                "channel": "telegram",
                "recipient": recipient,
                "latency_ms": latency_ms
            }
            
        except Exception as e:
            self._logger.error(f"Telegram send failed: {e}")
            return {
                "success": False,
                "channel": "telegram",
                "error": str(e)
            }
    
    def validate_config(self) -> bool:
        """Validate Telegram configuration."""
        return bool(self.bot_token and self.default_chat_id)


class EmailProvider(BaseNotificationProvider):
    """Email notification provider using SMTP."""
    
    def __init__(self):
        """Initialize Email provider."""
        super().__init__()
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
        
        if not self.smtp_host:
            raise NotificationException("SMTP_HOST not configured")
    
    async def send(
        self,
        recipient: str,
        message: str,
        subject: Optional[str] = None,
        image_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send email message.
        
        Args:
            recipient: Email address
            message: Message content (HTML)
            subject: Email subject
            image_path: Path to image attachment
            **kwargs: Additional parameters
        
        Returns:
            Result dict
        """
        try:
            import aiosmtplib
            from email.message import EmailMessage
            from email.mime.multipart import MIMEMultipart
            from email.mime.image import MIMEImage
            
            start_time = time.time()
            
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.smtp_user
            msg["To"] = recipient
            msg["Subject"] = subject or "SentinelAI Alert"
            
            # Attach HTML body
            msg.attach(MIMEText(message, "html"))
            
            # Attach image if provided
            if image_path and Path(image_path).exists():
                with open(image_path, 'rb') as f:
                    img_data = f.read()
                image = MIMEImage(img_data, name=Path(image_path).name)
                msg.attach(image)
            
            # Send email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls
            ) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(msg)
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return {
                "success": True,
                "channel": "email",
                "recipient": recipient,
                "latency_ms": latency_ms
            }
            
        except Exception as e:
            self._logger.error(f"Email send failed: {e}")
            return {
                "success": False,
                "channel": "email",
                "error": str(e)
            }
    
    def validate_config(self) -> bool:
        """Validate email configuration."""
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)


class SMSProvider(BaseNotificationProvider):
    """SMS notification provider (placeholder for future implementation)."""
    
    def __init__(self):
        """Initialize SMS provider."""
        super().__init__()
        self._logger.warning("SMS provider not implemented")
    
    async def send(
        self,
        recipient: str,
        message: str,
        subject: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send SMS message (not implemented)."""
        return {
            "success": False,
            "channel": "sms",
            "error": "SMS provider not implemented"
        }
    
    def validate_config(self) -> bool:
        """Validate SMS configuration."""
        return False


class WebhookProvider(BaseNotificationProvider):
    """Webhook notification provider."""
    
    def __init__(self):
        """Initialize Webhook provider."""
        super().__init__()
    
    async def send(
        self,
        recipient: str,  # Webhook URL
        message: str,
        subject: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send webhook notification.
        
        Args:
            recipient: Webhook URL
            message: JSON payload
            subject: Not used for webhooks
            **kwargs: Additional parameters
        
        Returns:
            Result dict
        """
        try:
            import aiohttp
            
            start_time = time.time()
            
            payload = {
                "message": message,
                "subject": subject,
                "timestamp": time.time()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(recipient, json=payload) as response:
                    response.raise_for_status()
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return {
                "success": True,
                "channel": "webhook",
                "recipient": recipient,
                "latency_ms": latency_ms
            }
            
        except Exception as e:
            self._logger.error(f"Webhook send failed: {e}")
            return {
                "success": False,
                "channel": "webhook",
                "error": str(e)
            }
    
    def validate_config(self) -> bool:
        """Validate webhook configuration."""
        return True  # Webhooks are validated per URL
