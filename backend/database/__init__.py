"""
Database module - Models, CRUD operations, and session management.
"""

from .base import Base, engine, SessionLocal, get_db, init_db
from .models import (
    User,
    Person,
    Camera,
    FallEvent,
    Alert,
    AuditLog,
    SystemMetric
)
from .crud import (
    # User CRUD
    get_user, get_users, create_user, update_user, delete_user,
    # Person CRUD
    get_person, get_persons, create_person, update_person, delete_person,
    # Camera CRUD
    get_camera, get_cameras, get_active_cameras, create_camera, update_camera, delete_camera,
    # FallEvent CRUD
    get_fall_event, get_fall_events, get_fall_events_by_person, get_fall_events_by_camera,
    create_fall_event, update_fall_event, delete_fall_event,
    # Alert CRUD
    get_alert, get_alerts, get_alerts_by_fall_event, create_alert, update_alert,
    # AuditLog CRUD
    create_audit_log, get_audit_logs,
    # SystemMetric CRUD
    create_system_metric, get_system_metrics
)

__all__ = [
    # Base
    "Base", "engine", "SessionLocal", "get_db", "init_db",
    # Models
    "User", "Person", "Camera", "FallEvent", "Alert", "AuditLog", "SystemMetric",
    # CRUD operations
    "get_user", "get_users", "create_user", "update_user", "delete_user",
    "get_person", "get_persons", "create_person", "update_person", "delete_person",
    "get_camera", "get_cameras", "get_active_cameras", "create_camera", "update_camera", "delete_camera",
    "get_fall_event", "get_fall_events", "get_fall_events_by_person", "get_fall_events_by_camera",
    "create_fall_event", "update_fall_event", "delete_fall_event",
    "get_alert", "get_alerts", "get_alerts_by_fall_event", "create_alert", "update_alert",
    "create_audit_log", "get_audit_logs",
    "create_system_metric", "get_system_metrics"
]
