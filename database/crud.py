"""
Opérations CRUD pour la base de données.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas

# Person CRUD
def get_person(db: Session, person_id: int) -> Optional[models.Person]:
    """Récupérer une personne par son ID."""
    return db.query(models.Person).filter(models.Person.id == person_id).first()

def get_persons(db: Session, skip: int = 0, limit: int = 100) -> List[models.Person]:
    """Récupérer la liste des personnes."""
    return db.query(models.Person).offset(skip).limit(limit).all()

def create_person(db: Session, person: schemas.PersonCreate) -> models.Person:
    """Créer une nouvelle personne."""
    db_person = models.Person(**person.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def update_person(db: Session, person_id: int, person: schemas.PersonUpdate) -> Optional[models.Person]:
    """Mettre à jour une personne."""
    db_person = get_person(db, person_id)
    if db_person:
        for key, value in person.model_dump(exclude_unset=True).items():
            setattr(db_person, key, value)
        db.commit()
        db.refresh(db_person)
    return db_person

def delete_person(db: Session, person_id: int) -> bool:
    """Supprimer une personne."""
    db_person = get_person(db, person_id)
    if db_person:
        db.delete(db_person)
        db.commit()
        return True
    return False

# Camera CRUD
def get_camera(db: Session, camera_id: int) -> Optional[models.Camera]:
    """Récupérer une caméra par son ID."""
    return db.query(models.Camera).filter(models.Camera.id == camera_id).first()

def get_cameras(db: Session, skip: int = 0, limit: int = 100) -> List[models.Camera]:
    """Récupérer la liste des caméras."""
    return db.query(models.Camera).offset(skip).limit(limit).all()

def get_active_cameras(db: Session) -> List[models.Camera]:
    """Récupérer les caméras actives."""
    return db.query(models.Camera).filter(models.Camera.is_active == True).all()

def create_camera(db: Session, camera: schemas.CameraCreate) -> models.Camera:
    """Créer une nouvelle caméra."""
    db_camera = models.Camera(**camera.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

def update_camera(db: Session, camera_id: int, camera: schemas.CameraUpdate) -> Optional[models.Camera]:
    """Mettre à jour une caméra."""
    db_camera = get_camera(db, camera_id)
    if db_camera:
        for key, value in camera.model_dump(exclude_unset=True).items():
            setattr(db_camera, key, value)
        db.commit()
        db.refresh(db_camera)
    return db_camera

def delete_camera(db: Session, camera_id: int) -> bool:
    """Supprimer une caméra."""
    db_camera = get_camera(db, camera_id)
    if db_camera:
        db.delete(db_camera)
        db.commit()
        return True
    return False

# FallEvent CRUD
def get_fall_event(db: Session, fall_event_id: int) -> Optional[models.FallEvent]:
    """Récupérer un événement de chute par son ID."""
    return db.query(models.FallEvent).filter(models.FallEvent.id == fall_event_id).first()

def get_fall_events(db: Session, skip: int = 0, limit: int = 100) -> List[models.FallEvent]:
    """Récupérer la liste des événements de chute."""
    return db.query(models.FallEvent).order_by(models.FallEvent.detected_at.desc()).offset(skip).limit(limit).all()

def get_fall_events_by_person(db: Session, person_id: int, skip: int = 0, limit: int = 100) -> List[models.FallEvent]:
    """Récupérer les événements de chute d'une personne."""
    return db.query(models.FallEvent).filter(models.FallEvent.person_id == person_id).order_by(models.FallEvent.detected_at.desc()).offset(skip).limit(limit).all()

def get_fall_events_by_camera(db: Session, camera_id: int, skip: int = 0, limit: int = 100) -> List[models.FallEvent]:
    """Récupérer les événements de chute d'une caméra."""
    return db.query(models.FallEvent).filter(models.FallEvent.camera_id == camera_id).order_by(models.FallEvent.detected_at.desc()).offset(skip).limit(limit).all()

def create_fall_event(db: Session, fall_event: schemas.FallEventCreate) -> models.FallEvent:
    """Créer un nouvel événement de chute."""
    db_fall_event = models.FallEvent(**fall_event.model_dump())
    db.add(db_fall_event)
    db.commit()
    db.refresh(db_fall_event)
    return db_fall_event

def update_fall_event(db: Session, fall_event_id: int, fall_event: schemas.FallEventUpdate) -> Optional[models.FallEvent]:
    """Mettre à jour un événement de chute."""
    db_fall_event = get_fall_event(db, fall_event_id)
    if db_fall_event:
        for key, value in fall_event.model_dump(exclude_unset=True).items():
            setattr(db_fall_event, key, value)
        db.commit()
        db.refresh(db_fall_event)
    return db_fall_event

def delete_fall_event(db: Session, fall_event_id: int) -> bool:
    """Supprimer un événement de chute."""
    db_fall_event = get_fall_event(db, fall_event_id)
    if db_fall_event:
        db.delete(db_fall_event)
        db.commit()
        return True
    return False

# Alert CRUD
def get_alert(db: Session, alert_id: int) -> Optional[models.Alert]:
    """Récupérer une alerte par son ID."""
    return db.query(models.Alert).filter(models.Alert.id == alert_id).first()

def get_alerts(db: Session, skip: int = 0, limit: int = 100) -> List[models.Alert]:
    """Récupérer la liste des alertes."""
    return db.query(models.Alert).order_by(models.Alert.sent_at.desc()).offset(skip).limit(limit).all()

def get_alerts_by_fall_event(db: Session, fall_event_id: int) -> List[models.Alert]:
    """Récupérer les alertes d'un événement de chute."""
    return db.query(models.Alert).filter(models.Alert.fall_event_id == fall_event_id).all()

def create_alert(db: Session, alert: schemas.AlertCreate) -> models.Alert:
    """Créer une nouvelle alerte."""
    db_alert = models.Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def update_alert(db: Session, alert_id: int, alert: schemas.AlertUpdate) -> Optional[models.Alert]:
    """Mettre à jour une alerte."""
    db_alert = get_alert(db, alert_id)
    if db_alert:
        for key, value in alert.model_dump(exclude_unset=True).items():
            setattr(db_alert, key, value)
        db.commit()
        db.refresh(db_alert)
    return db_alert

# AuditLog CRUD
def create_audit_log(db: Session, audit_log: schemas.AuditLogCreate) -> models.AuditLog:
    """Créer un nouveau log d'audit."""
    db_audit_log = models.AuditLog(**audit_log.model_dump())
    db.add(db_audit_log)
    db.commit()
    db.refresh(db_audit_log)
    return db_audit_log

def get_audit_logs(db: Session, skip: int = 0, limit: int = 100) -> List[models.AuditLog]:
    """Récupérer la liste des logs d'audit."""
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

# SystemMetric CRUD
def create_system_metric(db: Session, metric: schemas.SystemMetricCreate) -> models.SystemMetric:
    """Créer une nouvelle métrique système."""
    db_metric = models.SystemMetric(**metric.model_dump())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

def get_system_metrics(db: Session, metric_name: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[models.SystemMetric]:
    """Récupérer les métriques système."""
    query = db.query(models.SystemMetric)
    if metric_name:
        query = query.filter(models.SystemMetric.metric_name == metric_name)
    return query.order_by(models.SystemMetric.timestamp.desc()).offset(skip).limit(limit).all()
