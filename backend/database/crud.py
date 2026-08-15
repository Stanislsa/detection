"""
Unified CRUD operations for all models.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .models import (
    User, Person, Camera, FallEvent, Alert, 
    AuditLog, SystemMetric
)
from backend.core.constants import (
    Role, ProfileType, GravityLevel, 
    AlertStatus, CameraStatus, FallStatus
)
from backend.core.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# USER CRUD
# ============================================================================

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    role: Optional[Role] = None,
    is_active: Optional[bool] = None
) -> List[User]:
    """Get users with optional filters."""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()


def create_user(db: Session, user_data: Dict[str, Any]) -> User:
    """Create new user."""
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
    """Update user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    for key, value in user_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user (soft delete)."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db_user.is_active = False
    db.commit()
    return True


# ============================================================================
# PERSON CRUD
# ============================================================================

def get_person(db: Session, person_id: int) -> Optional[Person]:
    """Get person by ID."""
    return db.query(Person).filter(Person.id == person_id).first()


def get_persons(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    profile_type: Optional[ProfileType] = None,
    is_active: Optional[bool] = None
) -> List[Person]:
    """Get persons with optional filters."""
    query = db.query(Person).filter(Person.is_active == True)
    
    if profile_type:
        query = query.filter(Person.profile_type == profile_type)
    if is_active is not None:
        query = query.filter(Person.is_active == is_active)
    
    return query.order_by(Person.created_at.desc()).offset(skip).limit(limit).all()


def create_person(db: Session, person_data: Dict[str, Any]) -> Person:
    """Create new person."""
    db_person = Person(**person_data)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


def update_person(db: Session, person_id: int, person_data: Dict[str, Any]) -> Optional[Person]:
    """Update person."""
    db_person = get_person(db, person_id)
    if not db_person:
        return None
    
    for key, value in person_data.items():
        if hasattr(db_person, key) and key != 'id':
            setattr(db_person, key, value)
    
    db_person.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_person)
    return db_person


def delete_person(db: Session, person_id: int) -> bool:
    """Delete person (soft delete)."""
    db_person = get_person(db, person_id)
    if not db_person:
        return False
    
    db_person.is_active = False
    db.commit()
    return True


# ============================================================================
# CAMERA CRUD
# ============================================================================

def get_camera(db: Session, camera_id: int) -> Optional[Camera]:
    """Get camera by ID."""
    return db.query(Camera).filter(Camera.id == camera_id).first()


def get_cameras(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[CameraStatus] = None,
    is_active: Optional[bool] = None
) -> List[Camera]:
    """Get cameras with optional filters."""
    query = db.query(Camera)
    
    if status:
        query = query.filter(Camera.status == status)
    if is_active is not None:
        query = query.filter(Camera.is_active == is_active)
    
    return query.order_by(Camera.created_at.desc()).offset(skip).limit(limit).all()


def get_active_cameras(db: Session) -> List[Camera]:
    """Get all active cameras."""
    return db.query(Camera).filter(
        and_(Camera.is_active == True, Camera.status == CameraStatus.ACTIVE)
    ).all()


def create_camera(db: Session, camera_data: Dict[str, Any]) -> Camera:
    """Create new camera."""
    db_camera = Camera(**camera_data)
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


def update_camera(db: Session, camera_id: int, camera_data: Dict[str, Any]) -> Optional[Camera]:
    """Update camera."""
    db_camera = get_camera(db, camera_id)
    if not db_camera:
        return None
    
    for key, value in camera_data.items():
        if hasattr(db_camera, key) and key != 'id':
            setattr(db_camera, key, value)
    
    db.commit()
    db.refresh(db_camera)
    return db_camera


def delete_camera(db: Session, camera_id: int) -> bool:
    """Delete camera (soft delete)."""
    db_camera = get_camera(db, camera_id)
    if not db_camera:
        return False
    
    db_camera.is_active = False
    db.commit()
    return True


def update_camera_last_seen(db: Session, camera_id: int) -> bool:
    """Update camera last_seen timestamp."""
    db_camera = get_camera(db, camera_id)
    if not db_camera:
        return False
    
    db_camera.last_seen = datetime.utcnow()
    db.commit()
    return True


# ============================================================================
# FALL EVENT CRUD
# ============================================================================

def get_fall_event(db: Session, fall_event_id: int) -> Optional[FallEvent]:
    """Get fall event by ID."""
    return db.query(FallEvent).filter(FallEvent.id == fall_event_id).first()


def get_fall_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    person_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    gravity_level: Optional[GravityLevel] = None,
    status: Optional[FallStatus] = None,
    is_false_positive: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[FallEvent]:
    """Get fall events with filters."""
    query = db.query(FallEvent)
    
    if person_id:
        query = query.filter(FallEvent.person_id == person_id)
    if camera_id:
        query = query.filter(FallEvent.camera_id == camera_id)
    if gravity_level:
        query = query.filter(FallEvent.gravity_level == gravity_level)
    if status:
        query = query.filter(FallEvent.status == status)
    if is_false_positive is not None:
        query = query.filter(FallEvent.is_false_positive == is_false_positive)
    if start_date:
        query = query.filter(FallEvent.detected_at >= start_date)
    if end_date:
        query = query.filter(FallEvent.detected_at <= end_date)
    
    return query.order_by(FallEvent.detected_at.desc()).offset(skip).limit(limit).all()


def get_fall_events_by_person(
    db: Session,
    person_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[FallEvent]:
    """Get fall events for a specific person."""
    return db.query(FallEvent).filter(
        FallEvent.person_id == person_id
    ).order_by(FallEvent.detected_at.desc()).offset(skip).limit(limit).all()


def get_fall_events_by_camera(
    db: Session,
    camera_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[FallEvent]:
    """Get fall events for a specific camera."""
    return db.query(FallEvent).filter(
        FallEvent.camera_id == camera_id
    ).order_by(FallEvent.detected_at.desc()).offset(skip).limit(limit).all()


def create_fall_event(db: Session, fall_event_data: Dict[str, Any]) -> FallEvent:
    """Create new fall event."""
    db_fall_event = FallEvent(**fall_event_data)
    db.add(db_fall_event)
    db.commit()
    db.refresh(db_fall_event)
    return db_fall_event


def update_fall_event(db: Session, fall_event_id: int, fall_event_data: Dict[str, Any]) -> Optional[FallEvent]:
    """Update fall event."""
    db_fall_event = get_fall_event(db, fall_event_id)
    if not db_fall_event:
        return None
    
    for key, value in fall_event_data.items():
        if hasattr(db_fall_event, key) and key not in ['id', 'detected_at', 'created_at']:
            setattr(db_fall_event, key, value)
    
    db_fall_event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_fall_event)
    return db_fall_event


def delete_fall_event(db: Session, fall_event_id: int) -> bool:
    """Delete fall event."""
    db_fall_event = get_fall_event(db, fall_event_id)
    if not db_fall_event:
        return False
    
    db.delete(db_fall_event)
    db.commit()
    return True


def confirm_fall_event(
    db: Session,
    fall_event_id: int,
    confirmed_by: str,
    is_false_positive: bool = False,
    notes: Optional[str] = None
) -> Optional[FallEvent]:
    """Confirm or reject a fall event."""
    db_fall_event = get_fall_event(db, fall_event_id)
    if not db_fall_event:
        return None
    
    db_fall_event.status = FallStatus.FALSE_POSITIVE if is_false_positive else FallStatus.CONFIRMED
    db_fall_event.is_false_positive = is_false_positive
    db_fall_event.confirmed_by = confirmed_by
    db_fall_event.confirmed_at = datetime.utcnow()
    if notes:
        db_fall_event.notes = notes
    
    db_fall_event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_fall_event)
    return db_fall_event


# ============================================================================
# ALERT CRUD
# ============================================================================

def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
    """Get alert by ID."""
    return db.query(Alert).filter(Alert.id == alert_id).first()


def get_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    fall_event_id: Optional[int] = None,
    channel: Optional[str] = None,
    status: Optional[AlertStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Alert]:
    """Get alerts with filters."""
    query = db.query(Alert)
    
    if fall_event_id:
        query = query.filter(Alert.fall_event_id == fall_event_id)
    if channel:
        query = query.filter(Alert.channel == channel)
    if status:
        query = query.filter(Alert.status == status)
    if start_date:
        query = query.filter(Alert.sent_at >= start_date)
    if end_date:
        query = query.filter(Alert.sent_at <= end_date)
    
    return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


def get_alerts_by_fall_event(db: Session, fall_event_id: int) -> List[Alert]:
    """Get all alerts for a specific fall event."""
    return db.query(Alert).filter(Alert.fall_event_id == fall_event_id).all()


def create_alert(db: Session, alert_data: Dict[str, Any]) -> Alert:
    """Create new alert."""
    db_alert = Alert(**alert_data)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def update_alert(db: Session, alert_id: int, alert_data: Dict[str, Any]) -> Optional[Alert]:
    """Update alert."""
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return None
    
    for key, value in alert_data.items():
        if hasattr(db_alert, key) and key not in ['id', 'created_at']:
            setattr(db_alert, key, value)
    
    db_alert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_alert)
    return db_alert


def update_alert_status(
    db: Session,
    alert_id: int,
    status: AlertStatus,
    delivery_time_ms: Optional[int] = None,
    error_message: Optional[str] = None
) -> Optional[Alert]:
    """Update alert status."""
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return None
    
    db_alert.status = status
    
    if status == AlertStatus.SENT:
        db_alert.sent_at = datetime.utcnow()
    elif status == AlertStatus.DELIVERED:
        db_alert.delivered_at = datetime.utcnow()
    elif status == AlertStatus.READ:
        db_alert.read_at = datetime.utcnow()
    
    if delivery_time_ms is not None:
        db_alert.delivery_time_ms = delivery_time_ms
    if error_message:
        db_alert.error_message = error_message
    
    db_alert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_alert)
    return db_alert


# ============================================================================
# AUDIT LOG CRUD
# ============================================================================

def create_audit_log(db: Session, audit_data: Dict[str, Any]) -> AuditLog:
    """Create new audit log entry."""
    # Calculate hash for integrity
    import hashlib
    audit_data['current_hash'] = hashlib.sha256(
        str(audit_data).encode() + str(datetime.utcnow()).encode()
    ).hexdigest()
    
    db_audit_log = AuditLog(**audit_data)
    db.add(db_audit_log)
    db.commit()
    db.refresh(db_audit_log)
    return db_audit_log


def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[AuditLog]:
    """Get audit logs with filters."""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource:
        query = query.filter(AuditLog.resource == resource)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()


# ============================================================================
# SYSTEM METRIC CRUD
# ============================================================================

def create_system_metric(db: Session, metric_data: Dict[str, Any]) -> SystemMetric:
    """Create new system metric."""
    db_metric = SystemMetric(**metric_data)
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


def get_system_metrics(
    db: Session,
    metric_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[SystemMetric]:
    """Get system metrics with filters."""
    query = db.query(SystemMetric)
    
    if metric_name:
        query = query.filter(SystemMetric.metric_name == metric_name)
    if start_date:
        query = query.filter(SystemMetric.timestamp >= start_date)
    if end_date:
        query = query.filter(SystemMetric.timestamp <= end_date)
    
    return query.order_by(SystemMetric.timestamp.desc()).offset(skip).limit(limit).all()


def get_aggregated_metrics(
    db: Session,
    metric_name: str,
    aggregation: str = 'avg',
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Optional[float]:
    """Get aggregated metric value."""
    query = db.query(SystemMetric).filter(SystemMetric.metric_name == metric_name)
    
    if start_date is None:
        start_date = datetime.utcnow() - timedelta(hours=24)
    if end_date is None:
        end_date = datetime.utcnow()
    
    query = query.filter(SystemMetric.timestamp.between(start_date, end_date))
    
    if aggregation == 'avg':
        result = query.with_entities(func.avg(SystemMetric.metric_value)).scalar()
    elif aggregation == 'sum':
        result = query.with_entities(func.sum(SystemMetric.metric_value)).scalar()
    elif aggregation == 'min':
        result = query.with_entities(func.min(SystemMetric.metric_value)).scalar()
    elif aggregation == 'max':
        result = query.with_entities(func.max(SystemMetric.metric_value)).scalar()
    else:
        result = None
    
    return float(result) if result is not None else None
