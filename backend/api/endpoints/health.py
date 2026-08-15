"""
Health check endpoints.
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SentinelAI API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/readiness")
async def readiness_check():
    """Readiness check for Kubernetes."""
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/liveness")
async def liveness_check():
    """Liveness check for Kubernetes."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
