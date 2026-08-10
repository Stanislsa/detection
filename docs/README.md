# SentinelAI - Documentation

## Table des matières

- [Architecture](ARCHITECTURE.md)
- [Pipeline Vidéo](PIPELINE.md)
- [Machine à États Caméras](STATE_MACHINE.md)
- [API Interne](API.md)
- [Guide d'Installation](#guide-dinstallation)
- [Guide Développeur](#guide-développeur)

---

## Guide d'Installation

### Prérequis

- Python 3.10+
- Windows 10/11
- GPU NVIDIA (optionnel, pour CUDA)
- OpenVINO (optionnel)

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/sentinelai.git
cd sentinelai

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Charger la configuration
python -c "from app.core.config_loader import get_config_loader; get_config_loader().load_all()"

# Lancer l'application
python app/desktop/main.py
```

### Configuration

Les fichiers de configuration se trouvent dans le dossier `config/` :

- `application.yaml` : Configuration générale de l'application
- `cameras.yaml` : Configuration des caméras
- `ai.yaml` : Configuration de l'IA
- `notifications.yaml` : Configuration des notifications
- `storage.yaml` : Configuration du stockage
- `logging.yaml` : Configuration de la journalisation

---

## Guide Développeur

### Structure du Projet

```
app/
├── core/                  # Fonctionnalités transversales
│   ├── constants.py       # Constantes globales
│   ├── logger.py          # Logger centralisé
│   ├── exceptions.py      # Exceptions personnalisées
│   ├── settings.py       # Configuration persistante
│   └── config_loader.py   # Chargeur de configuration YAML
│
├── desktop/               # Interface PyQt6
│   ├── main_window.py     # Fenêtre principale
│   ├── pages/             # Pages (Caméras, Alertes, Utilisateurs)
│   ├── workers/          # Workers QThread
│   ├── services/          # Services (Analytics)
│   ├── pipeline/          # Pipeline vidéo
│   ├── camera_manager.py  # Gestionnaire multi-caméras
│   ├── state_manager.py   # État partagé
│   ├── health_service.py  # Service de diagnostic
│   └── observability.py   # Service d'observabilité
│
├── ai/                    # Intelligence Artificielle
│   ├── base_detector.py   # Interface détecteurs
│   ├── yolo_detector.py   # YOLO (Ultralytics)
│   ├── mediapipe_detector.py  # MediaPipe
│   ├── classifier.py      # Classificateur PyTorch
│   ├── scheduler/         # Ordonnanceur d'inférence
│   └── rules/             # Moteur de règles
│
├── events/                # Bus d'événements
│   ├── event_types.py     # Types d'événements
│   ├── event_bus.py       # Bus publish/subscribe
│   └── handlers.py        # Handlers d'événements
│
├── storage/               # Gestion du stockage
│   └── storage_manager.py # Gestionnaire centralisé
│
├── database/              # Base de données
│   └── __init__.py        # Modèles SQLAlchemy
│
├── translations/          # Internationalisation
│   └── translator.py      # Gestionnaire de traductions
│
└── version.py             # Versionnement centralisé

config/                    # Fichiers de configuration YAML
plugins/                   # Plugins extensibles
├── detectors/            # Détecteurs personnalisés
├── rules/                # Règles personnalisées
└── notifications/        # Canaux de notification personnalisés

tests/                     # Tests unitaires
docs/                      # Documentation
```

### Ajouter un Nouveau Détecteur

1. Créer une classe héritant de `BaseDetector` :

```python
from app.ai.base_detector import BaseDetector

class MyDetector(BaseDetector):
    def __init__(self, model_path: str, device: str = "cpu"):
        super().__init__(model_path, device)
        # Initialisation
    
    def detect(self, frame):
        # Implémentation de la détection
        pass
```

2. Ajouter le détecteur dans `plugins/detectors/` pour le rendre extensible.

### Ajouter une Nouvelle Règle

1. Créer une classe héritant de `BaseRuleEngine` :

```python
from app.ai.rules.base_rule import BaseRuleEngine

class MyRuleEngine(BaseRuleEngine):
    def __init__(self, event_bus):
        super().__init__(event_bus)
        # Initialisation
    
    def process_detections(self, detections, context):
        # Implémentation de la règle
        pass
```

2. Ajouter la règle dans `plugins/rules/` pour la rendre extensible.

### Ajouter un Nouveau Canal de Notification

1. Créer une classe héritant de `NotificationPlugin` :

```python
from plugins.plugin_manager import NotificationPlugin

class MyNotification(NotificationPlugin):
    @property
    def name(self):
        return "my_notification"
    
    def send(self, message, **kwargs):
        # Implémentation de l'envoi
        pass
```

2. Ajouter le canal dans `plugins/notifications/`.

### Tests

```bash
# Exécuter tous les tests
pytest tests/

# Exécuter un test spécifique
pytest tests/test_camera.py

# Avec couverture
pytest --cov=app tests/
```

### Build pour Windows

```bash
# Installer PyInstaller
pip install pyinstaller

# Créer l'exécutable
pyinstaller --onefile --windowed --name SentinelAI app/desktop/main.py
```

---

## Support

Pour toute question ou problème, ouvrez une issue sur GitHub.
