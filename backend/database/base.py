"""
Base SQLAlchemy configuration and session management.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from contextlib import contextmanager
from typing import Generator

from backend.core.config import settings
from backend.core.logger import get_logger

logger = get_logger(__name__)

# Base declarative class
Base = declarative_base()

# Engine and session factory
_engine = None
_SessionLocal = None


def create_engine_with_settings() -> object:
    """Create SQLAlchemy engine with settings."""
    from sqlalchemy.pool import QueuePool
    
    return create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        poolclass=QueuePool,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )


def init_db() -> object:
    """Initialize database engine and create tables."""
    global _engine, _SessionLocal
    
    if _engine is None:
        logger.info(f"Initializing database: {settings.DATABASE_URL}")
        _engine = create_engine_with_settings()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine
        )
        
        # Create all tables
        Base.metadata.create_all(bind=_engine)
        logger.info("Database tables created successfully")
    
    return _engine


def get_engine() -> object:
    """Get or create database engine."""
    if _engine is None:
        return init_db()
    return _engine


def get_session_local() -> sessionmaker:
    """Get or create session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    return _SessionLocal


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Yields:
        Session: SQLAlchemy session
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


def get_db_dependency() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Yields:
        Session: SQLAlchemy session
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Export for backward compatibility
engine = property(get_engine)
SessionLocal = property(get_session_local)
