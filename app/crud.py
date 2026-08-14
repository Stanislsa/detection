"""
Opérations CRUD pour les modèles SQLAlchemy de l'application (`app.models`).

Ce module est utilisé par les routes FastAPI de `app/api/endpoints/`.
Il agit sur la même base de données que `app.dependencies.get_db` (qui crée
les tables via `app.models.base.Base.metadata.create_all`).

Les modèles de `app/models/` sont la source de vérité côté application ;
les modèles équivalents dans `database/models.py` sont un héritage d'un
ancien layout et ne sont PAS utilisés ici.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import Alert, FallEvent, Person
from app.schemas import AlertCreate, AlertUpdate, FallEventUpdate


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
    """Récupère une alerte par son ID."""
    return db.query(Alert).filter(Alert.id == alert_id).first()


def get_alerts(db: Session, skip: int = 0, limit: int = 100) -> List[Alert]:
    """Récupère la liste paginée des alertes, triée par date d'envoi décroissante."""
    return (
        db.query(Alert)
        .order_by(Alert.sent_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_alerts_by_fall_event(db: Session, fall_event_id: int) -> List[Alert]:
    """Récupère toutes les alertes associées à un événement de chute."""
    return (
        db.query(Alert)
        .filter(Alert.fall_event_id == fall_event_id)
        .all()
    )


def create_alert(db: Session, alert: AlertCreate) -> Alert:
    """Crée une nouvelle alerte et la persiste."""
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def update_alert(db: Session, alert_id: int, alert: AlertUpdate) -> Optional[Alert]:
    """Met à jour une alerte existante (partiel)."""
    db_alert = get_alert(db, alert_id)
    if db_alert is None:
        return None
    for key, value in alert.model_dump(exclude_unset=True).items():
        setattr(db_alert, key, value)
    db.commit()
    db.refresh(db_alert)
    return db_alert


# ---------------------------------------------------------------------------
# FallEvents
# ---------------------------------------------------------------------------

def get_fall_event(db: Session, fall_event_id: int) -> Optional[FallEvent]:
    """Récupère un événement de chute par son ID."""
    return db.query(FallEvent).filter(FallEvent.id == fall_event_id).first()


def update_fall_event(
    db: Session,
    fall_event_id: int,
    fall_event_update: FallEventUpdate,
) -> Optional[FallEvent]:
    """Met à jour un événement de chute (partiel)."""
    db_fall_event = get_fall_event(db, fall_event_id)
    if db_fall_event is None:
        return None
    for key, value in fall_event_update.model_dump(exclude_unset=True).items():
        setattr(db_fall_event, key, value)
    db.commit()
    db.refresh(db_fall_event)
    return db_fall_event


# ---------------------------------------------------------------------------
# Persons (lookup utilitaire pour l'auth via get_current_user)
# ---------------------------------------------------------------------------

def get_person(db: Session, person_id: int) -> Optional[Person]:
    """Récupère une personne par son ID."""
    return db.query(Person).filter(Person.id == person_id).first()