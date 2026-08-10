"""
API Backend FastAPI principale.

Application FastAPI asynchrone pour la gestion du système de détection de chutes.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import settings
from database.models import Base, init_db
from database import crud, schemas

# Import des routers
from backend.routers import cameras, profiles, alerts, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application.
    
    Startup: Initialisation de la base de données
    Shutdown: Nettoyage des ressources
    """
    # Startup
    print("Démarrage de l'application FastAPI...")
    db_path = settings.DATA_DIR / "db" / "fall_detection.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    engine = init_db(str(db_path))
    app.state.engine = engine
    app.state.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    print(f"Base de données initialisée: {db_path}")
    
    yield
    
    # Shutdown
    print("Arrêt de l'application FastAPI...")
    if hasattr(app.state, 'engine'):
        app.state.engine.dispose()


# Création de l'application FastAPI
app = FastAPI(
    title="Fall Detection API",
    description="API REST pour le système de détection de chutes",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dépendance de session de base de données
def get_db():
    """
    Dépendance pour obtenir une session de base de données.
    
    Yields:
        Session SQLAlchemy
    """
    db = app.state.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Enregistrement des routers
app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


# Route racine
@app.get("/")
async def root():
    """Route racine de l'API."""
    return {
        "message": "Fall Detection API",
        "version": "1.0.0",
        "status": "running"
    }


# Route de santé
@app.get("/health")
async def health_check():
    """Vérification de santé de l'API."""
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
