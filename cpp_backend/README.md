# Backend C++ Minimaliste - Installation

## Architecture

Ce backend C++ minimaliste utilise:
- **ONNX Runtime** pour l'inférence YOLO
- **TCP/IP standard (Winsock2)** pour la communication avec Python
- **Aucune dépendance externe lourde** (pas d'OpenCV, Boost, OpenSSL)

Python gère la capture vidéo et envoie les images via TCP au backend C++ qui effectue l'inférence.

## Dépendances Requises (SEULEMENT 2)

### 1. CMake
**Téléchargement:** https://cmake.org/download/

Installer CMake (version 3.16+) et ajouter au PATH.

```powershell
# Vérifier installation
cmake --version
```

### 2. Visual Studio Build Tools
**Téléchargement:** https://visualstudio.microsoft.com/downloads/

Installer "Build Tools for Visual Studio 2022" avec:
- C++ build tools
- Windows 10/11 SDK

### 3. ONNX Runtime C++ API
**Téléchargement:** https://github.com/microsoft/onnxruntime/releases

Télécharger `onnxruntime-win-x64-1.28.0.zip` et extraire dans `C:\fall_detection_deps\onnxruntime`.

## Compilation

```powershell
cd cpp_backend
mkdir build
cd build
cmake .. -DONNXRUNTIME_ROOT="C:\fall_detection_deps\onnxruntime"
cmake --build . --config Release
```

## Utilisation

### 1. Démarrer le backend C++

```powershell
cd cpp_backend\build\bin
.\fall_detection_backend.exe --model ..\..\..\models\fall_detection.onnx --port 8888
```

### 2. Démarrer le client Python

```powershell
python app/scripts/cpp_client.py
```

## Structure du Projet Minimaliste

```
cpp_backend/
├── CMakeLists.txt              # Configuration CMake minimaliste
├── include/
│   ├── onnx_engine/
│   │   └── SimpleInference.hpp  # Inférence ONNX simple
│   └── network/
│       └── TcpServer.hpp         # Serveur TCP standard
├── src/
│   ├── onnx_engine/
│   │   └── SimpleInference.cpp
│   ├── network/
│   │   └── TcpServer.cpp
│   └── main.cpp                 # Point d'entrée
├── models/
│   └── fall_detection.onnx      # Modèle ONNX
└── build/
```

## Protocole TCP

### Client → Serveur (Python → C++)
1. Envoi header: `[width (4 bytes), height (4 bytes), channels (4 bytes)]`
2. Envoi image: `[RGB data (width * height * channels bytes)]`

### Serveur → Client (C++ → Python)
1. Réception nombre de détections: `[num_detections (4 bytes)]`
2. Pour chaque détection: `[x, y, w, h, confidence, class_id, padding]` (7 floats = 28 bytes)

## Modules

### ONNX Engine (SimpleInference)
- Chargement modèle ONNX
- Inférence sur images RGB brutes
- Parsing des sorties YOLO
- Aucune dépendance externe

### Network (TcpServer)
- Serveur TCP/IP standard (Winsock2)
- Réception images depuis Python
- Envoi détections vers Python
- Communication asynchrone
