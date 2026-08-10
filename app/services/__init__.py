"""
Services module.
"""
from .camera_service import CameraService
from .detection_service import DetectionService
from .alert_service import AlertService
from .dashboard_service import DashboardService
from .telegram_bot import TelegramBot
from .email_sender import EmailSender

__all__ = ['CameraService', 'DetectionService', 'AlertService', 'DashboardService', 'TelegramBot', 'EmailSender']
