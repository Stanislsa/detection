# Critères de décision de chute (CDC SI20220029)

## Principe

Analyse **uniquement le squelette MediaPipe Pose** (anonymisation).  
YOLO éventuel = détection de **personne** (bbox), **pas** YOLO-Pose.

## Indicateurs

| Signal | Rôle |
|--------|------|
| `trunk_angle_deg` | Inclinaison du tronc (0 vertical → 90 horizontal) |
| `vertical_velocity_ms` | Vitesse verticale estimée |
| `impact_accel_ms2` | Choc à l'impact |
| `is_horizontal` | Corps au sol |
| `stillness_ratio` | Immobilité post-chute |
| `time_on_ground_s` | Temps passé au sol |

## Décision (`decide_fall`)

Score composite pondéré + règles :
1. **Dynamique** : angle élevé + vitesse forte
2. **Impact** : accélération + horizontalité
3. **Temps au sol** : observation selon profil (réduit les faux positifs)

Version des seuils : `criteria_version` (traçabilité KPI).

## Gravité (`severity_engine`)

- `gravity_level` : faible / moyenne / elevee / critique  
- `gravity_score` 0–100  
- `injury_probability`  
- `severity_label` : normal / urgent / critique  
- `should_alert` selon gravité + temps d’observation  

## API

- `POST /api/v1/detection/process-frame` — image → décision  
- `GET  /api/v1/detection/criteria` — seuils  
- `POST /api/v1/detection/simulate-signals` — test sans caméra  

## Alignement CDC

- Edge AI local (pas de cloud pour la vidéo)  
- Délai d’observation avant alerte  
- Adaptation profil (âge / mobilité)  
- Vidéo preuve : squelette / chiffrement local (RBAC admin)  
