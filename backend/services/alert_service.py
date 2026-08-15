"""
Alert service - Business logic for alert management.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.core.logger import get_logger
from backend.core.constants import AlertStatus, AlertChannel
from backend.database.crud import (
    get_alert, get_alerts, get_alerts_by_fall_event, create_alert, update_alert_status
)
from backend.notifications.manager import notification_manager

logger = get_logger(__name__)


class AlertService:
    """
    Service for alert management and notification coordination.
    """
    
    def __init__(self):
        """Initialize alert service."""
        self.notification_manager = notification_manager
    
    async def create_and_send_alert(
        self,
        fall_event_id: int,
        channels: List[AlertChannel],
        db: Session
    ) -> Dict[str, Any]:
        """
        Create and send alert for fall event.
        
        Args:
            fall_event_id: Fall event ID
            channels: Channels to use
            db: Database session
        
        Returns:
            Alert creation result
        """
        try:
            from backend.database.crud import get_fall_event, get_person
            
            # Get fall event
            fall_event = get_fall_event(db, fall_event_id)
            if not fall_event:
                return {"error": "Fall event not found"}
            
            # Get person details
            person = get_person(db, fall_event.person_id)
            if not person:
                return {"error": "Person not found"}
            
            # Get sensitive data
            sensitive_data = person.decrypt_sensitive_data()
            
            # Create alerts for each channel
            created_alerts = []
            for channel in channels:
                recipient = self._get_recipient_for_channel(channel, sensitive_data)
                
                alert_data = {
                    "fall_event_id": fall_event_id,
                    "channel": channel,
                    "recipient": recipient,
                    "subject": f"Fall Alert - {person.first_name} {person.last_name}",
                    "status": AlertStatus.PENDING
                }
                
                alert = create_alert(db, alert_data)
                created_alerts.append(alert)
                
                # Send notification
                await self._send_notification(alert, person, fall_event, sensitive_data)
            
            return {
                "success": True,
                "alerts_created": len(created_alerts),
                "alert_ids": [alert.id for alert in created_alerts]
            }
            
        except Exception as e:
            logger.error(f"Failed to create and send alerts: {e}")
            return {"error": str(e)}
    
    def _get_recipient_for_channel(
        self,
        channel: AlertChannel,
        sensitive_data: Dict[str, Any]
    ) -> str:
        """Get recipient for channel."""
        from backend.core.config import settings
        
        if channel == AlertChannel.TELEGRAM:
            return settings.TELEGRAM_CHAT_ID
        elif channel == AlertChannel.EMAIL:
            return sensitive_data.get("email", settings.SMTP_USER)
        elif channel == AlertChannel.SMS:
            return sensitive_data.get("phone", "")
        else:
            return "default"
    
    async def _send_notification(
        self,
        alert,
        person,
        fall_event,
        sensitive_data: Dict[str, Any]
    ):
        """Send notification for alert."""
        try:
            from backend.core.constants import GravityLevel
            
            result = await self.notification_manager.send_fall_alert(
                person_name=f"{person.first_name} {person.last_name}",
                gravity_level=fall_event.gravity_level or GravityLevel.MOYENNE,
                gravity_score=fall_event.gravity_score or 0.0,
                location=person.address,
                gps_coords=(
                    sensitive_data.get("latitude"),
                    sensitive_data.get("longitude")
                ) if sensitive_data.get("latitude") else None,
                channels=[alert.channel]
            )
            
            # Update alert status based on result
            if result and result[0].get("result", {}).get("success"):
                update_alert_status(
                    alert.fall_event_id,
                    alert.id,
                    AlertStatus.SENT,
                    delivery_time_ms=result[0].get("result", {}).get("latency_ms")
                )
            else:
                update_alert_status(
                    alert.fall_event_id,
                    alert.id,
                    AlertStatus.FAILED,
                    error_message="Notification failed"
                )
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def get_alert_statistics(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get alert statistics.
        
        Args:
            db: Database session
            days: Number of days to analyze
        
        Returns:
            Statistics dictionary
        """
        from datetime import timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        alerts = get_alerts(
            db, skip=0, limit=10000,
            start_date=start_date, end_date=end_date
        )
        
        total = len(alerts)
        sent = sum(1 for a in alerts if a.status == AlertStatus.SENT)
        delivered = sum(1 for a in alerts if a.status == AlertStatus.DELIVERED)
        failed = sum(1 for a in alerts if a.status == AlertStatus.FAILED)
        
        # Average delivery time
        delivery_times = [a.delivery_time_ms for a in alerts if a.delivery_time_ms]
        avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0.0
        
        # Channel distribution
        channel_dist = {}
        for alert in alerts:
            channel = alert.channel.value
            channel_dist[channel] = channel_dist.get(channel, 0) + 1
        
        return {
            "period_days": days,
            "total_alerts": total,
            "sent": sent,
            "delivered": delivered,
            "failed": failed,
            "success_rate": (sent / total * 100) if total > 0 else 0.0,
            "avg_delivery_time_ms": avg_delivery_time,
            "channel_distribution": channel_dist
        }


# Global alert service instance
alert_service = AlertService()
