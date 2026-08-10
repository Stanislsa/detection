"""
Constantes globales de l'application.
"""

# Application
APP_NAME = "Surveillance IA"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Axyris"

# Couleurs Windows 11 Dark Mode
COLORS = {
    "primary": "#2563EB",      # Bleu
    "primary_dark": "#1D4ED8",
    "success": "#10B981",      # Vert
    "success_dark": "#059669",
    "warning": "#F59E0B",      # Orange
    "warning_dark": "#D97706",
    "danger": "#EF4444",       # Rouge
    "danger_dark": "#DC2626",
    "info": "#3B82F6",         # Bleu clair
    "dark_bg": "#1E1E2F",      # Fond sombre
    "card_bg": "#2D2D44",      # Fond carte
    "border": "#4A4A6A",       # Bordure
    "text_primary": "#FFFFFF",
    "text_secondary": "#A0A0B0",
}

# API
DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1"
DEFAULT_WS_URL = "ws://localhost:8000/ws"

# Configuration
CONFIG_DIR_NAME = ".surveillance_ia"
CONFIG_FILE_NAME = "config.json"

# Tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Détection
DETECTION_CONFIDENCE_THRESHOLD = 0.5
FALL_CONFIDENCE_THRESHOLD = 0.7

# Vidéo
DEFAULT_FPS = 30
DEFAULT_RESOLUTION = "1920x1080"
SUPPORTED_RESOLUTIONS = [
    "640x480",
    "1280x720",
    "1920x1080",
    "2560x1440",
    "3840x2160",
]

# Stockage
STORAGE_DIR_NAME = "surveillance_data"
SNAPSHOTS_DIR = "snapshots"
RECORDINGS_DIR = "recordings"
REPORTS_DIR = "reports"
EXPORTS_DIR = "exports"
CACHE_DIR = "cache"

# WebSocket
WS_RECONNECT_DELAY = 5
WS_MAX_RECONNECT_ATTEMPTS = 10

# Workers
MAX_WORKER_THREADS = 4
VIDEO_THREAD_TIMEOUT = 30
DETECTION_THREAD_TIMEOUT = 60
