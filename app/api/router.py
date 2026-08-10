"""
Agrégateur de routes API.
"""

from fastapi import APIRouter

from app.api.endpoints import persons, cameras, falls, alerts, dashboard, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentification"])
api_router.include_router(persons.router, prefix="/persons", tags=["personnes"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["caméras"])
api_router.include_router(falls.router, prefix="/falls", tags=["chutes"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alertes"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["tableau de bord"])
