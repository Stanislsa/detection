# Machine à États des Caméras

## Vue d'Ensemble

La machine à états formalise le cycle de vie des caméras avec 8 états définis et des transitions explicites.

## États

### 1. DISCONNECTED

**Description** : La caméra n'est pas connectée.

**Transitions possibles** :
- → CONNECTING (événement: CONNECT)

**Actions** : Aucune

### 2. CONNECTING

**Description** : La caméra est en cours de connexion.

**Transitions possibles** :
- → CONNECTED (événement: STREAM_START)
- → ERROR (événement: ERROR_OCCURRED)

**Actions** : Log de connexion en cours

### 3. CONNECTED

**Description** : La caméra est connectée mais ne stream pas encore.

**Transitions possibles** :
- → STREAMING (événement: STREAM_START)
- → DISCONNECTED (événement: DISCONNECT)

**Actions** : Log de connexion réussie

### 4. STREAMING

**Description** : La caméra stream des frames vidéo.

**Transitions possibles** :
- → DETECTING (événement: DETECTION_START)
- → RECORDING (événement: RECORDING_START)
- → DISCONNECTED (événement: DISCONNECT)
- → ERROR (événement: ERROR_OCCURRED)

**Actions** : Log de streaming démarré

### 5. DETECTING

**Description** : La caméra stream et exécute la détection IA.

**Transitions possibles** :
- → STREAMING (événement: DETECTION_STOP)
- → RECORDING (événement: RECORDING_START)
- → ERROR (événement: ERROR_OCCURRED)

**Actions** : Log de détection IA démarrée

### 6. RECORDING

**Description** : La caméra enregistre les frames vidéo.

**Transitions possibles** :
- → STREAMING (événement: RECORDING_STOP)
- → DETECTING (événement: DETECTION_START)
- → ERROR (événement: ERROR_OCCURRED)

**Actions** : Log d'enregistrement démarré

### 7. ERROR

**Description** : Une erreur est survenue.

**Transitions possibles** :
- → RECONNECTING (événement: RECONNECT)
- → DISCONNECTED (événement: DISCONNECT)

**Actions** : Log de l'erreur

### 8. RECONNECTING

**Description** : La caméra tente de se reconnecter après une erreur.

**Transitions possibles** :
- → CONNECTING (événement: CONNECT)
- → ERROR (événement: ERROR_OCCURRED)

**Actions** : Log de reconnexion en cours

## Diagramme des États

```
    ┌─────────────┐
    │DISCONNECTED │
    └──────┬──────┘
           │ CONNECT
           ▼
    ┌─────────────┐
    │ CONNECTING │
    └──────┬──────┘
           │ STREAM_START
           ▼
    ┌─────────────┐
    │  CONNECTED  │
    └──────┬──────┘
           │ STREAM_START
           ▼
    ┌─────────────┐
    │  STREAMING  │◄─────────────┐
    └──────┬──────┘              │
           │                      │
    ┌──────┴──────┐              │
    │             │              │
    ▼             ▼              │
┌─────────┐  ┌─────────┐        │
│DETECTING│  │RECORDING│        │
└────┬────┘  └────┬────┘        │
     │            │             │
     │            │             │
     └──────┬─────┘             │
            │                   │
            │ ERROR_OCCURRED   │
            ▼                   │
      ┌─────────┐               │
      │  ERROR  │               │
      └────┬────┘               │
           │ RECONNECT          │
           ▼                     │
    ┌─────────────┐              │
    │RECONNECTING │──────────────┘
    └──────┬──────┘
           │ CONNECT
           └──────────┘
```

## Utilisation

### Création de la Machine à États

```python
from app.desktop.camera_state_machine import CameraStateMachine, CameraEvent

state_machine = CameraStateMachine(camera_id="camera_1")
```

### Déclenchement de Transitions

```python
# Connexion
state_machine.trigger(CameraEvent.CONNECT)

# Démarrage du streaming
state_machine.trigger(CameraEvent.STREAM_START)

# Démarrage de la détection
state_machine.trigger(CameraEvent.DETECTION_START)

# Arrêt de la détection
state_machine.trigger(CameraEvent.DETECTION_STOP)
```

### Vérification de l'État

```python
# État actuel
state = state_machine.get_current_state()
print(state)  # CameraState.STREAMING

# Vérifier si opérationnel
if state_machine.is_operational():
    print("La caméra peut recevoir des frames")

# Vérifier si la détection peut être activée
if state_machine.can_detect():
    print("La détection peut être activée")

# Vérifier si l'enregistrement peut être activé
if state_machine.can_record():
    print("L'enregistrement peut être activé")
```

### Callbacks

```python
def on_state_change(camera_id, state):
    print(f"Caméra {camera_id} : {state}")

state_machine.register_state_callback(CameraState.STREAMING, on_state_change)
```

### Métriques

```python
# Informations sur l'état
info = state_machine.get_state_info()
print(f"État: {info.state}")
print(f"Entré à: {info.entered_at}")
print(f"Dernière transition: {info.last_transition}")
print(f"Durée: {state_machine.get_state_duration()}s")
```

## Garde (Guard)

Les gardes permettent de conditionner les transitions :

```python
def guard_check(**kwargs):
    return kwargs.get("permission", False)

transition = StateTransition(
    from_state=CameraState.DISCONNECTED,
    event=CameraEvent.CONNECT,
    to_state=CameraState.CONNECTING,
    guard=guard_check
)
```

## Actions

Les actions sont exécutées lors des transitions :

```python
def on_connecting(**kwargs):
    print("Connexion en cours...")

transition = StateTransition(
    from_state=CameraState.DISCONNECTED,
    event=CameraEvent.CONNECT,
    to_state=CameraState.CONNECTING,
    action=on_connecting
)
```

## Intégration avec CameraManager

La machine à états est intégrée dans le CameraManager pour gérer le cycle de vie des caméras :

```python
from app.desktop.camera_manager import get_camera_manager

manager = get_camera_manager()

# Ajouter une caméra
manager.add_camera(camera_id="camera_1", source="rtsp://...")

# Démarrer la capture
manager.start_capture("camera_1")

# La machine à états gère automatiquement les transitions
# DISCONNECTED → CONNECTING → CONNECTED → STREAMING
```

## Gestion des Erreurs

En cas d'erreur, la machine à états passe automatiquement à l'état ERROR :

```python
# L'erreur est détectée par le CameraWorker
state_machine.trigger(CameraEvent.ERROR_OCCURRED, error_message="Connection timeout")

# La caméra tente de se reconnecter
state_machine.trigger(CameraEvent.RECONNECT)
```

## Réinitialisation

Pour réinitialiser la machine à états à l'état DISCONNECTED :

```python
state_machine.reset()
```
