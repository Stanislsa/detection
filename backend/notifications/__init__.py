"""
Notifications module - Unified alert system for Telegram, Email, SMS, Webhooks.
"""

from .manager import NotificationManager, notification_manager
from .providers import TelegramProvider, EmailProvider, SMSProvider, WebhookProvider
from .templates import AlertTemplate, TemplateManager

__all__ = [
    "NotificationManager",
    "notification_manager",
    "TelegramProvider",
    "EmailProvider", 
    "SMSProvider",
    "WebhookProvider",
    "AlertTemplate",
    "TemplateManager"
]
