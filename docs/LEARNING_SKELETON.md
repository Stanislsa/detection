# Apprentissage sur features squelette

## Objectif

Aligner l’**entraînement** (`start_train.py`) sur la **détection live** (YOLO + MediaPipe) :
les arbres apprennent aussi la **biomécanique de chute**, pas seulement le flou image.

## Pipeline

```
données/vidéo/
  → fragmentation (clips)
  → pour chaque clip :
       frames → (YOLO crop optionnel) → MediaPipe Pose
       → séries angle / v_y / horizontalité / immobilité
       → 15 features sk_*  + 21 features image
  → triage normal | urgent | critique
  → RandomForest / arbres + hyperparam + F1
  → data/models/severity_trees.joblib
```

## Features `sk_*`

| ID | Sens |
|----|------|
| sk_trunk_angle_mean/max/std/final | Posture tronc |
| sk_vertical_speed_max/mean | Dynamique chute |
| sk_impact_proxy | Choc (Δv) |
| sk_horizontal_ratio | Fraction au sol |
| sk_time_on_ground_proxy | Durée horizontalité |
| sk_stillness_landmarks | Immobilité articulations |
| sk_hip_drop | Descente du bassin |
| sk_head_hip_delta_y | Tête vs hanche |
| sk_pose_visibility | Qualité pose |
| sk_frames_with_pose | Couverture |
| sk_person_detected_ratio | Ratio frames posées |

## Lancement

```bash
# dépendances
pip install mediapipe ultralytics opencv-python scikit-learn

python start_train.py
# ou
python -m ml.pipeline --video-dir données/vidéo
```

Sans MediaPipe, les `sk_*` valent 0 (fallback image seul).

## Lien détection live

Mêmes notions que `backend/ai/fall_criteria.py` :
angle tronc, vitesse verticale, temps au sol, immobilité → cohérent entre **train** et **infer**.
