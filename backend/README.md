# SentinelAI Backend - Unified Architecture

Version 2.0.0 - Professional unified backend architecture combining app/ and devoir/ backends.

## 🏗️ Architecture Overview

The unified backend follows a clean, layered architecture:

```
backend/
├── core/              # Core configuration, exceptions, logging, constants
├── database/          # SQLAlchemy models, CRUD operations, session management
├── api/               # FastAPI routers, endpoints, dependencies
├── security/          # Authentication, encryption, RBAC, audit logging
├── ai/                # AI/ML detection engines (YOLO, MediaPipe, OpenVINO, Scientific)
├── notifications/     # Unified notification system (Telegram, Email, SMS, Webhooks)
├── services/          # Business logic layer
├── main.py            # Application entry point
└── requirements.txt   # Python dependencies
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Copy environment configuration
cp backend/.env.example backend/.env

# Edit .env with your configuration
nano backend/.env
```

### Configuration

Key environment variables:

```bash
# Security (REQUIRED)
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///data/db/sentinel_ai.db

# Notifications (Optional)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Running the Server

```bash
# Development mode with auto-reload
python -m backend.main

# Production mode with uvicorn directly
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## 📊 Key Features

### 🔐 Security
- **JWT Authentication** with access/refresh tokens
- **MFA TOTP** support (RFC 6238)
- **AES-256-GCM** encryption for sensitive data
- **RBAC** with granular permissions
- **Audit logging** with integrity chain
- **Account lockout** anti-brute force

### 🤖 AI/ML Detection
- **YOLO** (Ultralytics) for object detection
- **MediaPipe** for pose estimation
- **OpenVINO** for Intel hardware optimization
- **Scientific engine** with biomechanics and physics analysis
- **Hybrid detection** combining multiple methods
- **Adaptive profiles** for different user types

### 📢 Notifications
- **Telegram** bot with image support
- **Email** with HTML templates
- **SMS** (placeholder for future)
- **Webhooks** for custom integrations
- **Rate limiting** and retry logic
- **Template system** for alerts

### 🗄️ Database
- **SQLAlchemy ORM** with unified models
- **Soft delete** support
- **Encrypted fields** for sensitive data
- **Audit trail** with hash chain
- **System metrics** for monitoring

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/mfa/setup` - Setup MFA
- `POST /api/v1/auth/mfa/verify` - Verify MFA
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Users
- `GET /api/v1/users/` - List users (admin)
- `GET /api/v1/users/{id}` - Get user
- `POST /api/v1/users/` - Create user (admin)
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user (admin)

### Persons
- `GET /api/v1/persons/` - List monitored persons
- `GET /api/v1/persons/{id}` - Get person
- `POST /api/v1/persons/` - Create person
- `PUT /api/v1/persons/{id}` - Update person
- `DELETE /api/v1/persons/{id}` - Delete person
- `GET /api/v1/persons/{id}/sensitive-data` - Get decrypted data

### Cameras
- `GET /api/v1/cameras/` - List cameras
- `GET /api/v1/cameras/active` - List active cameras
- `GET /api/v1/cameras/{id}` - Get camera
- `POST /api/v1/cameras/` - Create camera
- `PUT /api/v1/cameras/{id}` - Update camera
- `DELETE /api/v1/cameras/{id}` - Delete camera
- `POST /api/v1/cameras/{id}/heartbeat` - Camera heartbeat

### Falls
- `GET /api/v1/falls/` - List fall events
- `GET /api/v1/falls/person/{person_id}` - Get person falls
- `GET /api/v1/falls/camera/{camera_id}` - Get camera falls
- `GET /api/v1/falls/{id}` - Get fall event
- `POST /api/v1/falls/` - Create fall event
- `PUT /api/v1/falls/{id}` - Update fall event
- `POST /api/v1/falls/{id}/confirm` - Confirm/reject fall

### Alerts
- `GET /api/v1/alerts/` - List alerts
- `GET /api/v1/alerts/fall/{fall_event_id}` - Get fall alerts
- `GET /api/v1/alerts/{id}` - Get alert
- `POST /api/v1/alerts/` - Create alert
- `PUT /api/v1/alerts/{id}/status` - Update alert status
- `POST /api/v1/alerts/send-test` - Send test alert

### Dashboard
- `GET /api/v1/dashboard/kpis` - System KPIs
- `GET /api/v1/dashboard/statistics/falls` - Fall statistics
- `GET /api/v1/dashboard/statistics/cameras` - Camera statistics
- `GET /api/v1/dashboard/statistics/persons` - Person statistics
- `GET /api/v1/dashboard/metrics` - System metrics

## 🔧 Development

### Code Structure

- **core/** - Foundation layer (config, exceptions, logging)
- **database/** - Data access layer (models, CRUD)
- **api/** - Presentation layer (FastAPI endpoints)
- **security/** - Security layer (auth, encryption, RBAC)
- **ai/** - AI/ML layer (detectors, classifiers, scientific)
- **notifications/** - Notification layer (providers, templates)
- **services/** - Business logic layer

### Adding New Features

1. **New Model**: Add to `database/models.py`
2. **CRUD Operations**: Add to `database/crud.py`
3. **API Endpoint**: Add to `api/endpoints/`
4. **Business Logic**: Add to `services/`
5. **Update Router**: Add to `api/router.py`

### Testing

```bash
# Run tests
pytest backend/tests/

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html
```

## 🔄 Migration from Old Architecture

See [MIGRATION.md](MIGRATION.md) for detailed migration guide.

## 📝 Configuration

### AI Backend Selection

```bash
# Auto-detect best available
AI_BACKEND=auto

# Force specific backend
AI_BACKEND=cpu
AI_BACKEND=cuda
AI_BACKEND=openvino
AI_BACKEND=directml
```

### Database Options

```bash
# SQLite (default)
DATABASE_URL=sqlite:///data/db/sentinel_ai.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/sentinel_ai

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/sentinel_ai
```

### Profile Types

- `senior_fragile` - High sensitivity, low thresholds
- `senior_autonome` - Balanced thresholds
- `adulte` - Lower sensitivity, higher thresholds
- `handicape` - Very high sensitivity

## 🛡️ Security Best Practices

1. **Change default admin password** immediately
2. **Use strong SECRET_KEY** in production
3. **Enable MFA** for all admin users
4. **Use HTTPS** in production
5. **Regularly update dependencies**
6. **Monitor audit logs**
7. **Implement rate limiting** (built-in)
8. **Use environment variables** for secrets

## 📊 Monitoring

### System Metrics

The backend automatically tracks:
- CPU usage
- Memory usage
- Detection latency
- Frame rate
- Alert delivery times

Access via `GET /api/v1/dashboard/metrics`

### Logging

Logs are stored in `logs/sentinel_ai.log` with rotation.

## 🤝 Contributing

1. Follow the existing code structure
2. Add type hints for all functions
3. Write docstrings for public APIs
4. Add tests for new features
5. Update documentation

## 📄 License

Proprietary - Axyris Security

## 🆘 Support

For issues and questions, contact the development team.
