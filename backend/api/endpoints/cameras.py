"""
Camera management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.api.dependencies import get_db, get_current_user, require_permission
from backend.database.crud import (
    get_camera, get_cameras, get_active_cameras, 
    create_camera, update_camera, delete_camera, update_camera_last_seen
)
from backend.database.models import Camera, User
from backend.core.constants import CameraStatus

router = APIRouter()


# Pydantic schemas
class CameraBase(BaseModel):
    name: str
    rtsp_url: str
    room: Optional[str] = None
    fps: int = 30
    resolution_width: int = 1920
    resolution_height: int = 1080
    detection_zones: Optional[dict] = None


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    room: Optional[str] = None
    fps: Optional[int] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    detection_zones: Optional[dict] = None
    status: Optional[CameraStatus] = None


class CameraResponse(BaseModel):
    id: int
    name: str
    rtsp_url: str
    room: Optional[str] = None
    fps: int
    resolution_width: int
    resolution_height: int
    detection_zones: Optional[dict] = None
    status: CameraStatus
    is_active: bool
    created_at: datetime
    last_seen: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CameraResponse])
async def list_cameras(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CameraStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all cameras."""
    cameras = get_cameras(db, skip=skip, limit=limit, status=status)
    return cameras


@router.get("/active", response_model=List[CameraResponse])
async def list_active_cameras(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all active cameras."""
    cameras = get_active_cameras(db)
    return cameras


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera_endpoint(
    camera_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get camera by ID."""
    camera = get_camera(db, camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    return camera


@router.post("/", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera_endpoint(
    camera_data: CameraCreate,
    current_user: User = Depends(require_permission("write_camera")),
    db: Session = Depends(get_db)
):
    """Create new camera."""
    camera_dict = camera_data.model_dump()
    camera = create_camera(db, camera_dict)
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera_endpoint(
    camera_id: int,
    camera_data: CameraUpdate,
    current_user: User = Depends(require_permission("write_camera")),
    db: Session = Depends(get_db)
):
    """Update camera."""
    update_dict = camera_data.model_dump(exclude_unset=True)
    camera = update_camera(db, camera_id, update_dict)
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    return camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera_endpoint(
    camera_id: int,
    current_user: User = Depends(require_permission("delete_camera")),
    db: Session = Depends(get_db)
):
    """Delete camera (soft delete)."""
    success = delete_camera(db, camera_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    return None


@router.post("/{camera_id}/heartbeat")
async def camera_heartbeat(
    camera_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update camera last_seen timestamp (heartbeat)."""
    success = update_camera_last_seen(db, camera_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    return {"message": "Heartbeat recorded"}


class RtspTestRequest(BaseModel):
    rtsp_url: Optional[str] = None
    grab_frame: bool = True

@router.post("/test-rtsp")
async def test_rtsp_url(body: RtspTestRequest, current_user: User = Depends(get_current_user)):
    if not body.rtsp_url:
        raise HTTPException(status_code=400, detail="rtsp_url requis")
    from backend.services.camera_network import probe_rtsp
    return probe_rtsp(body.rtsp_url, grab_frame=body.grab_frame)

@router.post("/{camera_id}/test-rtsp")
async def test_camera_rtsp(camera_id: int, grab_frame: bool = True,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    camera = get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    from backend.services.camera_network import probe_rtsp
    result = probe_rtsp(camera.rtsp_url, grab_frame=grab_frame)
    return {"camera_id": camera_id, "name": camera.name, **result}

@router.get("/network/settings")
async def camera_network_settings(current_user: User = Depends(get_current_user)):
    from backend.core.config import settings
    return {"rtsp_transport": getattr(settings, "RTSP_TRANSPORT", "tcp"),
            "lan_subnet": getattr(settings, "CAMERA_LAN_SUBNET", ""),
            "detection_fps": getattr(settings, "DETECTION_FPS", 5.0)}
