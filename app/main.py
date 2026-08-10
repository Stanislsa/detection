"""
Point d'entrée principal de l'application FastAPI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.base import init_db
from app.api.router import api_router

# Création de l'application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Système intelligent de détection de chutes à domicile",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Événements de démarrage
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage."""
    init_db()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} démarré")


@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt."""
    print("👋 Arrêt du système")


# Routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Vérification de santé."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "connected"
    }
