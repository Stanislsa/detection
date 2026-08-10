"""
Schémas Pydantic pour validation et sérialisation.
"""
from .person import Person, PersonCreate, PersonUpdate, Gender, ProfileType
from .camera import Camera, CameraCreate, CameraUpdate
from .fall_event import FallEvent, FallEventCreate, FallEventUpdate, GravityLevel
from .alert import Alert, AlertCreate, AlertUpdate

__all__ = [
    'Person', 'PersonCreate', 'PersonUpdate', 'Gender', 'ProfileType',
    'Camera', 'CameraCreate', 'CameraUpdate',
    'FallEvent', 'FallEventCreate', 'FallEventUpdate', 'GravityLevel',
    'Alert', 'AlertCreate', 'AlertUpdate'
]
