# Pipeline IA — YOLO + MediaPipe Pose

## Pourquoi les deux ?

| Besoin CDC | Solution |
|------------|----------|
| Détecter qu’une **personne** est bien dans le cadre | **YOLO** classe COCO `person` |
| Extraire le **squelette** (anonymisation, angle, dynamique) | **MediaPipe Pose** |
| Décider chute / gravité | `fall_criteria` + `severity_engine` |

MediaPipe reste le moteur de **pose** (comme dans le CDC).  
YOLO n’est **pas** YOLO-Pose : il fournit uniquement la **bbox personne** pour rogner la ROI.

## Flux

```
Frame BGR
   │
   ▼
YOLOPersonDetector.detect()  →  liste de bbox + confidence
   │
   ▼
Crop ROI (+15 % padding) sur la meilleure détection
   │
   ▼
MediaPipeFallDetector.detect_fall(ROI)
   │  landmarks → trunk_angle, horizontal, v_y, impact, t_sol, stillness
   ▼
decide_fall(signals, criteria_for_profile(profil))
   │
   ▼
assess_severity(...) → gravity_level, injury_probability
   │
   ▼
Si fall + délai observation écoulé → Alerte
```

## API code

```python
from backend.ai.manager import AIManager
ai = AIManager()
result = ai.detect_fall(frame, person_profile={"age": 82, "profile_type": "senior_fragile"})
# result["fall_detected"], result["severity"], result["person_present"], result["roi_crop"]
```

## Réduction des fausses alertes

1. Pas de personne YOLO + confiance pose faible → pas de chute  
2. Délai **temps au sol** avant alerte (profil)  
3. Qualification humaine FP/FN pour les KPI  

## Fichiers

- `backend/ai/yolo.py` — YOLO / YOLOPersonDetector  
- `backend/ai/mediapipe.py` — Pose + FallDetector  
- `backend/ai/fall_criteria.py` — seuils versionnés  
- `backend/ai/manager.py` — orchestration hybrid  
- `backend/services/severity_engine.py` — gravité  
