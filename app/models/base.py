"""
Base déclarative SQLAlchemy et énumérations communes.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from contextlib import contextmanager
import enum

Base = declarative_base()

# Engine et Session globale (à initialiser dans init_db)
_engine = None
_SessionLocal = None


def init_db_engine(database_url: str = None):
    """Initialise le moteur de base de données."""
    global _engine, _SessionLocal
    from app.config import settings
    url = database_url or settings.DATABASE_URL
    _engine = create_engine(url, echo=False)
    _SessionLocal = sessionmaker(bind=_engine)
    return _engine


def get_db_session() -> Session:
    """Retourne une session de base de données."""
    global _SessionLocal
    if _SessionLocal is None:
        init_db_engine()
    return _SessionLocal()


@contextmanager
def get_db():
    """Context manager pour les sessions de base de données (FastAPI dependency)."""
    db = get_db_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"


class GravityLevel(enum.Enum):
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"


class ProfileType(enum.Enum):
    SENIOR_FRAGILE = "senior_fragile"
    SENIOR_AUTONOME = "senior_autonome"
    ADULTE = "adulte"
    HANDICAPE = "handicape"
