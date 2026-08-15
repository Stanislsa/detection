# Migration Guide - From app/ and devoir/ to Unified Backend

This guide helps migrate from the dual backend architecture (app/ + devoir/) to the unified backend architecture.

## Overview

The unified backend consolidates:
- `app/models/` + `database/models.py` → `backend/database/models.py`
- `app/crud.py` + `database/crud.py` → `backend/database/crud.py`
- `app/api/` + `devoir/backend/routers/` → `backend/api/endpoints/`
- `app/security/` → `backend/security/`
- `app/ai/` + `devoir/ai_engine/` → `backend/ai/`
- `devoir/alerts/` → `backend/notifications/`

## Step-by-Step Migration

### 1. Database Migration

#### Old Models Location
- `app/models/person.py`
- `app/models/fall_event.py`
- `app/models/alert.py`
- `app/models/user.py`
- `database/models.py`

#### New Models Location
- `backend/database/models.py` (unified)

#### Migration Steps

1. **Backup existing database**
```bash
cp data/db/fall_detection.db data/db/fall_detection.db.backup
```

2. **Update model imports**
```python
# Old
from app.models.person import Person
from database.models import Camera

# New
from backend.database.models import Person, Camera
```

3. **Handle schema changes**
The unified models include:
- Additional fields (e.g., `detection_method`, `vertical_velocity`)
- New enums (e.g., `AlertChannel`, `CameraStatus`)
- Encrypted fields (e.g., `emergency_contact_phone_encrypted`)

Run Alembic migrations:
```bash
alembic upgrade head
```

### 2. API Migration

#### Old API Structure
- `app/api/endpoints/auth.py`
- `app/api/endpoints/persons.py`
- `devoir/backend/routers/dashboard.py`

#### New API Structure
- `backend/api/endpoints/auth.py`
- `backend/api/endpoints/persons.py`
- `backend/api/endpoints/dashboard.py`

#### Migration Steps

1. **Update API imports**
```python
# Old
from app.api.router import api_router

# New
from backend.api.router import api_router
```

2. **Update endpoint paths**
All endpoints now use `/api/v1/` prefix:
- Old: `/auth/login`
- New: `/api/v1/auth/login`

3. **Update response schemas**
The unified API uses consistent Pydantic schemas. Check response formats in each endpoint.

### 3. Security Migration

#### Old Security
- `app/security/auth.py`
- `app/security/encryption.py`
- `app/security/rbac.py`

#### New Security
- `backend/security/auth.py`
- `backend/security/encryption.py`
- `backend/security/rbac.py`
- `backend/security/audit.py` (new)

#### Migration Steps

1. **Update security imports**
```python
# Old
from app.security.auth import AuthManager

# New
from backend.security.auth import AuthManager
```

2. **Update session management**
The new `SessionManager` is in-memory by default. For production, configure Redis:
```bash
REDIS_URL=redis://localhost:6379/0
```

3. **Update RBAC usage**
The new RBAC system uses the same interface but with additional permissions:
```python
# Old
from app.security.rbac import Permission

# New
from backend.security.rbac import Permission
```

### 4. AI/ML Migration

#### Old AI
- `app/ai/yolo_detector.py`
- `app/ai/mediapipe_detector.py`
- `devoir/ai_engine/` (scientific components)

#### New AI
- `backend/ai/yolo.py`
- `backend/ai/mediapipe.py`
- `backend/ai/scientific.py` (unified scientific engine)
- `backend/ai/manager.py` (unified AI manager)

#### Migration Steps

1. **Update AI imports**
```python
# Old
from app.ai.yolo_detector import YOLODetector

# New
from backend.ai.yolo import YOLODetector
```

2. **Use AI Manager**
The new architecture uses a unified AI manager:
```python
# Old
detector = YOLODetector()
results = detector.detect(image)

# New
from backend.ai.manager import ai_manager
results = ai_manager.detect_persons(image, method="yolo_person")
```

3. **Scientific engine integration**
The devoir scientific components are now integrated:
```python
# Old
from devoir.ai_engine.biomechanics import BiomechanicsEngine

# New
from backend.ai.scientific import BiomechanicsEngine
```

### 5. Notifications Migration

#### Old Notifications
- `devoir/alerts/telegram_bot.py`
- `devoir/alerts/email_sender.py`

#### New Notifications
- `backend/notifications/manager.py`
- `backend/notifications/providers.py`
- `backend/notifications/templates.py`

#### Migration Steps

1. **Update notification imports**
```python
# Old
from devoir.alerts.telegram_bot import TelegramBot

# New
from backend.notifications.manager import notification_manager
```

2. **Use notification manager**
```python
# Old
bot = TelegramBot()
await bot.send_alert(message)

# New
await notification_manager.send_fall_alert(
    person_name="John Doe",
    gravity_level=GravityLevel.ELEVEE,
    gravity_score=75.0
)
```

### 6. Configuration Migration

#### Old Configuration
- `app/config.py`
- `config/application.yaml`
- `config/ai.yaml`

#### New Configuration
- `backend/core/config.py` (unified Pydantic settings)
- `backend/.env` (environment variables)

#### Migration Steps

1. **Migrate YAML to environment variables**
```yaml
# Old (config/application.yaml)
backend:
  host: "0.0.0.0"
  port: 8000

# New (backend/.env)
HOST=0.0.0.0
PORT=8000
```

2. **Update config imports**
```python
# Old
from app.config import settings

# New
from backend.core.config import settings
```

3. **Migrate AI configuration**
```yaml
# Old (config/ai.yaml)
ai:
  yolo:
    default_model: "yolo11n.pt"

# New (backend/.env)
YOLO_MODEL=yolo11n.pt
YOLO_CONFIDENCE_THRESHOLD=0.5
```

### 7. Service Layer Migration

The unified backend introduces a service layer for business logic:

```python
# New pattern
from backend.services.fall_service import fall_service

result = await fall_service.detect_and_process_fall(
    image=image,
    person_id=person_id,
    camera_id=camera_id,
    person_profile=profile,
    db=db
)
```

## Testing the Migration

### 1. Database Verification
```python
from backend.database.base import init_db
from backend.database.models import Person, Camera, FallEvent

init_db()
# Verify tables created correctly
```

### 2. API Verification
```bash
# Start the server
python -m backend.main

# Test health endpoint
curl http://localhost:8000/

# Test API docs
curl http://localhost:8000/api/docs
```

### 3. AI Models Verification
```python
from backend.ai.manager import ai_manager

status = ai_manager.get_model_status()
print(status)
```

### 4. Notifications Verification
```python
from backend.notifications.manager import notification_manager

await notification_manager.send_test_notification(
    channel="telegram",
    recipient="your_chat_id"
)
```

## Rollback Plan

If issues occur:

1. **Restore database**
```bash
cp data/db/fall_detection.db.backup data/db/fall_detection.db
```

2. **Revert to old backend**
```bash
# Use old entry point
python -m app.main
```

3. **Check logs**
```bash
tail -f logs/sentinel_ai.log
```

## Breaking Changes

### 1. Import Paths
All imports now use `backend.` prefix instead of `app.` or `devoir.`

### 2. API Routes
All API routes now include `/api/v1/` prefix

### 3. Model Fields
Some model fields have been renamed or added:
- `emergency_contact_phone` → `emergency_contact_phone_encrypted`
- New fields: `detection_method`, `vertical_velocity`, etc.

### 4. Configuration
YAML configuration replaced by environment variables

### 5. Session Management
Session storage moved to in-memory (Redis recommended for production)

## Post-Migration Checklist

- [ ] Database migrated successfully
- [ ] All API endpoints tested
- [ ] AI models loaded correctly
- [ ] Notifications working
- [ ] Authentication working
- [ ] MFA setup tested
- [ ] Audit logs generated
- [ ] Performance acceptable
- [ ] Documentation updated
- [ ] Old code backed up

## Support

For migration issues:
1. Check logs in `logs/sentinel_ai.log`
2. Verify environment variables in `backend/.env`
3. Test database connectivity
4. Verify AI model paths
5. Check notification provider credentials

## Additional Resources

- [Unified Backend README](README.md)
- [API Documentation](http://localhost:8000/api/docs)
- [Configuration Guide](#configuration)
