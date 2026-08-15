"""
Unified API router aggregating all endpoints.
"""

from fastapi import APIRouter

from .endpoints import auth, users, persons, cameras, falls, alerts, dashboard, health

api_router = APIRouter()

# Health check (no auth required)
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Protected routes
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(persons.router, prefix="/persons", tags=["persons"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
api_router.include_router(falls.router, prefix="/falls", tags=["falls"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
