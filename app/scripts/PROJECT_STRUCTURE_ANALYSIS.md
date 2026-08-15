# Analyse de la Structure des Projets de Détection de Chutes

## Vue d'ensemble des Deux Projets

### 1. Projet Fall-Detection (Approche MoveNet + LSTM)
**Emplacement:** `F:\Axyris\proj_indiv\detection\donne\Fall-Detection`

**Architecture:**
- **Pose Estimation:** MoveNet (TensorFlow Hub) pour détecter les points clés du corps
- **Optical Flow:** Analyse du mouvement dynamique
- **LSTM Models:** Deux modèles LSTM pour l'analyse séquentielle
  - Keypoint LSTM: 67% accuracy
  - Optical Flow LSTM: 61% accuracy

**Structure du projet:**
```
Fall-Detection/
├── Keypoint Detection- MoveNet.py    # Détection des points clés avec MoveNet
├── Optical Flow Algorithm.py         # Calcul du flux optique
├── LSTM.py                           # Modèle LSTM pour keypoints
├── LSTM OF.py                        # Modèle LSTM pour optical flow
├── Data Prep.py                      # Préparation des données
├── Combined features.py              # Combinaison des features
├── Major Project Fall detection Notebook.ipynb  # Notebook principal
├── Keypoints Image Results/          # Résultats visuels des keypoints
├── Keypoints Numpy Results/          # Données keypoints en format numpy
├── Dense OF Image Results/           # Résultats visuels optical flow
├── Dense OF Numpy Results/           # Données optical flow en format numpy
└── UP Fall Dataset/                  # Dataset de chutes
```

**Comment il crée les cadres de détection:**
1. **Détection des keypoints:** MoveNet détecte 17 points clés du corps humain
2. **Dessin des keypoints:** Dessine des cercles verts sur les points clés
3. **Dessin des connexions:** Dessine des lignes rouges entre les points clés connectés
4. **Sauvegarde:** Sauvegarde les images annotées et les données numpy

**Code clé pour les cadres:**
```python
def draw_keypoints(frame, keypoints, confidence_threshold):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))
    
    for kp in shaped:
        ky, kx, kp_conf = kp
        if kp_conf > confidence_threshold:
            cv2.circle(frame, (int(kx), int(ky)), 4, (0, 255, 0), -1)

def draw_connections(frame, keypoints, edges, confidence_threshold):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))
    
    for edge, color in edges.items():
        p1, p2 = edge
        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]
        
        if (c1 > confidence_threshold) & (c2 > confidence_threshold):
            cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
```

### 2. Projet Real-Time-Fall-Detection-using-YOLO (Approche YOLOv11)
**Emplacement:** `F:\Axyris\proj_indiv\detection\donne\Real-Time-Fall-Detection-using-YOLO`

**Architecture:**
- **YOLOv11:** Détection d'objets en temps réel
- **Classification:** Classification des activités (A, B, D, F)
  - A: Activités normales
  - B: Activités normales  
  - D: Activités normales
  - F: Chutes (Falls)
- **Post-processing:** Filtrage des fausses positives

**Structure du projet:**
```
Real-Time-Fall-Detection-using-YOLO/
├── fall-detection-yolov11.ipynb       # Notebook principal
├── Model/                             # Modèles entraînés
├── LE2I-subset-yolov11/              # Dataset LE2I pour YOLO
├── Annotated Frames/                  # Frames annotées avec bounding boxes
├── Result videos/                     # Vidéos annotées
├── Results/                           # Résultats d'entraînement
└── README.md                          # Documentation
```

**Comment il crée les cadres de détection:**
1. **Détection YOLO:** YOLOv11 détecte les personnes et classe les activités
2. **Bounding boxes:** Dessine des rectangles autour des objets détectés
3. **Labels:** Affiche les classes (A, B, D, F) et la confiance
4. **Couleurs:** Différentes couleurs selon les classes
5. **Sauvegarde:** Génère des vidéos annotées

**Format des images annotées:**
- Les images dans `Annotated Frames/` ont des bounding boxes rectangulaires
- Labels de classe (A, B, D, F) avec scores de confiance
- Couleurs différentes selon le type d'activité

## Comparaison des Deux Approches

### Approche MoveNet + LSTM:
- **Avantages:** Analyse détaillée de la pose, meilleure compréhension du mouvement
- **Inconvénients:** Plus complexe, moins rapide (67% accuracy)
- **Type de cadres:** Points clés (cercles) + connexions (lignes)

### Approche YOLOv11:
- **Avantages:** Plus rapide (25 FPS), plus simple, meilleure accuracy (95%)
- **Inconvénients:** Moins détaillé sur la pose
- **Type de cadres:** Bounding boxes rectangulaires + labels

## Comment Créer des Vidéos avec Cadres de Détection

### Méthode 1: Utiliser YOLO (Recommandée)
**Script déjà créé:** `app/scripts/generate_annotated_video.py`

**Fonctionnement:**
1. Charger le modèle YOLOv11
2. Pour chaque frame de la vidéo:
   - Faire l'inférence YOLO
   - Dessiner les bounding boxes
   - Ajouter les labels et la confiance
3. Sauvegarder la vidéo annotée

**Exemple d'utilisation:**
```python
from generate_annotated_video import generate_annotated_video

generate_annotated_video(
    input_path="video_input.avi",
    output_path="video_output_annotated.avi",
    model_path="yolo11n.pt",
    conf_threshold=0.5
)
```

### Méthode 2: Utiliser MoveNet (Approche détaillée)
**Script à créer:** Basé sur `Keypoint Detection- MoveNet.py`

**Fonctionnement:**
1. Charger le modèle MoveNet
2. Pour chaque frame de la vidéo:
   - Détecter les keypoints
   - Dessiner les cercles sur les points clés
   - Dessiner les lignes entre les points connectés
3. Sauvegarder la vidéo annotée

## Structure des Données

### Classes de Détection:
- **A:** Activités normales (marche, assis, etc.)
- **B:** Activités normales (mouvements quotidiens)
- **D:** Activités normales (autres mouvements)
- **F:** Chutes (detection de chute)

### Format des Bounding Boxes YOLO:
- Format: [x1, y1, x2, y2] (coordonnées des coins)
- Confiance: Score entre 0 et 1
- Classe: ID de la classe (0, 1, 2, etc.)

## Recommandations

Pour créer des vidéos avec cadres de détection:

1. **Utiliser YOLOv11** pour la rapidité et la simplicité
2. **Utiliser MoveNet** pour l'analyse détaillée de la pose
3. **Combiner les deux approches** pour une analyse complète
4. **Adapter les couleurs** selon les classes de détection
5. **Ajuster le seuil de confiance** pour filtrer les fausses positives

## Scripts Disponibles

1. **generate_annotated_video.py** - Génère des vidéos avec bounding boxes YOLO
2. **yolo_crop_video.py** - Recadre les vidéos autour des détections YOLO
3. **remove_video_cropping.py** - Supprime les bordures noires des vidéos

Ces scripts permettent de créer des vidéos annotées similaires à celles du projet Real-Time-Fall-Detection-using-YOLO.
