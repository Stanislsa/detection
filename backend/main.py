"""
Unified SentinelAI Backend - Main Entry Point

FastAPI application with unified architecture combining app/ and devoir/ backends.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import Response
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
    
    try:
        from backend.core.prometheus_metrics import PrometheusMiddleware, init_app_info, PROMETHEUS_AVAILABLE
        app.add_middleware(PrometheusMiddleware)
        init_app_info(settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)
        logger.info(f"Prometheus enabled={PROMETHEUS_AVAILABLE}")
    except Exception as e:
        logger.warning(f"Prometheus not loaded: {e}")
    @app.get("/metrics")
    async def root_metrics():
        from backend.core.prometheus_metrics import metrics_response
        resp=metrics_response()
        return Response(content=resp.body, media_type=resp.media_type, status_code=resp.status_code)
    from backend.core.exceptions import SentinelException
    from backend.core.prometheus_metrics import record_error
    @app.exception_handler(SentinelException)
    async def sentinel_exception_handler(request: Request, exc: SentinelException):
        record_error(exc.error_code, exc.status_code)
        body=exc.to_dict(); body["path"]=str(request.url.path); body["method"]=request.method
        return JSONResponse(status_code=exc.status_code, content=body)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        code=f"HTTP_{exc.status_code}"; record_error(code, exc.status_code)
        detail=exc.detail
        message=detail.get("message", str(detail)) if isinstance(detail, dict) else str(detail)
        return JSONResponse(status_code=exc.status_code, content={"error":{"code":code,"message":message},"path":str(request.url.path),"method":request.method})
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        record_error("VALIDATION_ERROR", 422)
        errors=[{"loc":list(e.get("loc",[])),"msg":e.get("msg"),"type":e.get("type")} for e in exc.errors()]
        return JSONResponse(status_code=422, content={"error":{"code":"VALIDATION_ERROR","message":"Request validation failed","details":errors},"path":str(request.url.path),"method":request.method})
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        record_error("INTERNAL_ERROR", 500)
        logger.error(f"Unhandled on {request.method} {request.url.path}: {exc}", exc_info=True)
        message=str(exc) if settings.DEBUG else "Internal server error"
        return JSONResponse(status_code=500, content={"error":{"code":"INTERNAL_ERROR","message":message},"path":str(request.url.path),"method":request.method})
    
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
