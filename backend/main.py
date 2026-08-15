"""
Unified SentinelAI Backend - Main Entry Point

FastAPI application with unified architecture combining app/ and devoir/ backends.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from backend.core.config import settings
from backend.core.logger import get_logger, setup_logging
from backend.database.base import init_db
from backend.api.router import api_router
from backend.security.rbac import rbac_manager
from backend.security.auth import session_manager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting SentinelAI Backend v2.0.0")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Initialize AI models
    try:
        from backend.ai.manager import ai_manager
        model_status = ai_manager.get_model_status()
        logger.info(f"AI models initialized: {len(model_status['detectors'])} detectors, {len(model_status['classifiers'])} classifiers")
    except Exception as e:
        logger.warning(f"AI models initialization failed: {e}")
    
    # Initialize notification providers
    try:
        from backend.notifications.manager import notification_manager
        logger.info("Notification providers initialized")
    except Exception as e:
        logger.warning(f"Notification providers initialization failed: {e}")
    
    # Initialize default admin user if needed
    try:
        _ensure_default_admin()
    except Exception as e:
        logger.warning(f"Failed to ensure default admin: {e}")
    
    logger.info("Startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SentinelAI Backend")
    
    # Cleanup expired sessions
    try:
        session_manager.cleanup_expired_sessions()
        logger.info("Session cleanup complete")
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")


def _ensure_default_admin():
    """Ensure default admin user exists."""
    from backend.database.base import get_db
    from backend.database.crud import get_user_by_username, create_user
    from backend.api.dependencies import get_password_hash
    from backend.core.constants import Role
    
    with get_db() as db:
        admin = get_user_by_username(db, "admin")
        if not admin:
            logger.info("Creating default admin user")
            admin_data = {
                "username": "admin",
                "email": "admin@sentinelai.local",
                "password_hash": get_password_hash("admin123"),  # Change in production!
                "role": Role.ADMIN,
                "is_active": True,
                "mfa_enabled": False
            }
            create_user(db, admin_data)
            
            # Assign RBAC role
            rbac_manager.assign_role("admin", Role.ADMIN)
            
            logger.warning("Default admin created with password 'admin123' - CHANGE IN PRODUCTION!")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="SentinelAI Fall Detection System - Unified Backend",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    # Global exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "environment": settings.ENVIRONMENT
        }
    
    return app


# Create application instance
app = create_app()


def main():
    """
    Run the application with uvicorn.
    """
    setup_logging()
    
    logger.info(f"Starting服务器 on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
