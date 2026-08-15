"""
Alert management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.api.dependencies import get_db, get_current_user, require_permission
from backend.database.crud import get_alert, get_alerts, get_alerts_by_fall_event, create_alert, update_alert_status
from backend.database.models import Alert
from backend.core.constants import AlertStatus, AlertChannel

router = APIRouter()


# Pydantic schemas
class AlertBase(BaseModel):
    fall_event_id: int
    channel: AlertChannel
    recipient: str
    subject: Optional[str] = None
    message_content: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    error_message: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    fall_event_id: int
    channel: AlertChannel
    recipient: str
    status: AlertStatus
    subject: Optional[str] = None
    message_content: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    delivery_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    fall_event_id: Optional[int] = None,
    channel: Optional[AlertChannel] = None,
    status: Optional[AlertStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: Alert = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List alerts with filters."""
    alerts = get_alerts(
        db, skip=skip, limit=limit, fall_event_id=fall_event_id,
        channel=channel, status=status, start_date=start_date, end_date=end_date
    )
    return alerts


@router.get("/fall/{fall_event_id}", response_model=List[AlertResponse])
async def get_fall_event_alerts(
    fall_event_id: int,
    current_user: Alert = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all alerts for a specific fall event."""
    alerts = get_alerts_by_fall_event(db, fall_event_id)
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert_endpoint(
    alert_id: int,
    current_user: Alert = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert by ID."""
    alert = get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return alert


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_endpoint(
    alert_data: AlertCreate,
    current_user: Alert = Depends(require_permission("write_alert")),
    db: Session = Depends(get_db)
):
    """Create new alert (typically called by notification system)."""
    alert_dict = alert_data.model_dump()
    alert = create_alert(db, alert_dict)
    return alert


@router.put("/{alert_id}/status")
async def update_alert_status_endpoint(
    alert_id: int,
    status: AlertStatus,
    delivery_time_ms: Optional[int] = None,
    error_message: Optional[str] = None,
    current_user: Alert = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update alert status (typically called by notification system)."""
    alert = update_alert_status(
        db, alert_id, status=status,
        delivery_time_ms=delivery_time_ms,
        error_message=error_message
    )
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return {
        "message": "Alert status updated",
        "alert_id": alert.id,
        "status": status.value
    }


@router.post("/send-test")
async def send_test_alert(
    channel: AlertChannel,
    recipient: str,
    current_user: Alert = Depends(require_permission("write_alert")),
    db: Session = Depends(get_db)
):
    """Send a test alert for notification system verification."""
    from backend.notifications.manager import notification_manager
    
    try:
        result = await notification_manager.send_test_notification(channel, recipient)
        return {
            "message": "Test alert sent successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test alert: {str(e)}"
        )
