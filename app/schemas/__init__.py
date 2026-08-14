"""
Schémas Pydantic pour validation et sérialisation.
"""
from .person import PersonRead, PersonCreate, PersonUpdate
from .camera import CameraRead, CameraCreate, CameraUpdate
from .fall_event import FallEventRead, FallEventCreate, FallEventUpdate
from .alert import AlertRead, AlertCreate, AlertUpdate

# Aliases rétro-compatibles : l'ancien code parlait de `Person` / `Camera`
# / `FallEvent` / `Alert` pour désigner la vue lecture complète.
Person = PersonRead
Camera = CameraRead
FallEvent = FallEventRead
Alert = AlertRead

__all__ = [
    'Person', 'PersonRead', 'PersonCreate', 'PersonUpdate',
    'Camera', 'CameraRead', 'CameraCreate', 'CameraUpdate',
    'FallEvent', 'FallEventRead', 'FallEventCreate', 'FallEventUpdate',
    'Alert', 'AlertRead', 'AlertCreate', 'AlertUpdate',
]
