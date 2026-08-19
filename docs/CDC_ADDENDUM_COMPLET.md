# Addendum au Cahier des Charges — SI20220029

**Projet :** Système intelligent d'estimation en temps réel pour la détection de chutes à domicile  
**Auteur :** BOANA Adriano Stanislas  
**Objet :** Compléter les 6 axes manquants + formaliser l’IA (YOLO + MediaPipe Pose)

---

## 1. Analyse métier renforcée

### 1.1 Acteurs métier (RACI simplifié)

| Acteur | Rôle | Responsabilités |
|--------|------|-----------------|
| Personne âgée / seule | Bénéficiaire | Surveillée ; aucune action requise |
| Proche / famille | Destinataire alerte | Reçoit Telegram/e-mail ; valide ou contacte secours |
| Services de secours | Intervention | Reçoivent bilan si escalade |
| Administrateur | Exploitation | Caméras, profils, MFA, preuves vidéo chiffrées |
| Personnel autorisé | Consultation | Historique / bilans (droits limités) |
| Moteur Edge AI | Système | Détection, décompte temporel, décision d’alerte |

### 1.2 Parcours utilisateurs principaux

1. **Surveillance nominale** : flux RTSP → YOLO personne → MediaPipe squelette → critères → pas d’alerte  
2. **Chute suspecte** : critères dynamiques OK → **délai d’observation** (profil) → si toujours au sol → alerte  
3. **Crise** : alerte → Telegram + e-mail → acknowledge opérateur → intervention → qualification FP/FN  
4. **Admin** : login MFA → config caméras / profils / seuils → simulation vidéo  
5. **Calibration** : mode banc d’essai (vidéos) avant production  

### 1.3 Scénarios détaillés (recette)

| ID | Scénario | Attendu |
|----|----------|---------|
| S1 | Chute critique chambre, ne se relève pas | Alerte après délai profil ; gravité critique |
| S2 | S’assoit brutalement (faux positif potentiel) | Pas d’alerte ou FP qualifiable |
| S3 | Se relève avant fin du décompte | Pas d’alerte |
| S4 | Caméra offline | Disponibilité KPI ↓ ; pas de fausse chute |
| S5 | Admin sans MFA | Refus connexion |
| S6 | Simulation fichier vidéo | Même pipeline que RTSP |

### 1.4 Processus décisionnel (macro)

```
Frame → YOLO (bbox personne) → MediaPipe Pose (landmarks)
     → Signaux (angle, v_y, impact, horizontalité, immobilité, t_sol)
     → decide_fall (critères versionnés + profil)
     → Si chute : décompte temporel profil
     → Si timeout au sol : assess_severity → Alerte multi-canal
     → Preuve locale chiffrée + squelette anonymisé sortant
```

Voir aussi `docs/metier/` (ACTEURS, PARCOURS, SCENARIOS, PROCESSUS).

---

## 2. IA formalisée — critères de décision de chute

### 2.1 Architecture IA (contrainte technique CDC corrigée)

| Étape | Technologie | Rôle |
|-------|-------------|------|
| Localisation personne | **YOLO** (classe `person`) | Précision de présence + **ROI** |
| Squelette / pose 3D | **MediaPipe Pose** | Landmarks, angle tronc, trajectoire |
| Décision chute | `fall_criteria.decide_fall` | Règles + score composite |
| Gravité | `severity_engine.assess_severity` | faible → critique |

> **CDC d’origine :** MediaPipe Pose choisi à la place de YOLO-Pose.  
> **Complément projet :** YOLO (détection objet *person*) **en amont** de MediaPipe pour fiabiliser la pose, **sans** remplacer l’analyse squelettique.

### 2.2 Signaux mesurés

| Signal | Description | Unité / échelle |
|--------|-------------|-----------------|
| `trunk_angle_deg` | Inclinaison tronc (0 vertical → 90 horizontal) | degrés |
| `vertical_velocity_ms` | Vitesse verticale (vers le sol) | m/s (approx. image) |
| `impact_accel_ms2` | Variation brutale de vitesse | m/s² |
| `is_horizontal` | Corps au sol | bool |
| `stillness_ratio` | Immobilité post-impact | 0–1 |
| `time_on_ground_s` | Temps horizontal continu | s |

### 2.3 Seuils par défaut (v1.0.0)

| Critère | Défaut | Critique |
|---------|--------|----------|
| Angle tronc | ≥ 55° | ≥ 70° |
| Vitesse verticale | ≥ 1,8 m/s | ≥ 2,8 m/s |
| Accélération impact | ≥ 6 m/s² | — |
| Temps au sol (alerte) | ≥ 8 s | ≥ 15 s |
| Immobilité | ≥ 0,65 | — |
| Confiance composite | ≥ 0,72 | — |

**Règles :**
- **Dynamique :** angle + vitesse (ou angle critique + horizontal)
- **Impact :** accélération + posture
- **Confirmation sol :** temps au sol + immobilité (réduit les fausses alertes)
- **Profil** (`senior_fragile`, etc.) : abaisse les seuils et le délai

### 2.4 Pipeline d’inférence

`AIManager.detect_fall(..., method="hybrid")`  
→ `yolo_person` → crop ROI → `mediapipe_fall` → `decide_fall` + `assess_severity`

---

## 3. KPI qualité et performance

| KPI | Définition |
|-----|------------|
| Taux de faux positifs (FPR) | FP / (FP + TN) ou FP/alertes |
| Taux de faux négatifs (FNR) | FN / (FN + TP) |
| Précision | TP / (TP + FP) |
| Rappel (recall) | TP / (TP + FN) |
| F1-score | 2·P·R / (P+R) |
| Temps moyen de détection | latence décision (ms) |
| Délai moyen d’envoi d’alerte | détection → notification (ms/s) |
| Temps moyen d’intervention | acknowledge → intervene |

**API :** `GET /dashboard/kpis`, `GET /dashboard/history`  
**Qualification :** `POST /falls/{id}/qualify` (ground truth / FP / FN)

---

## 4. Module décisionnel — score de gravité

| Niveau | Score indicatif | Signification |
|--------|-----------------|---------------|
| Faible | 0–25 | Chute légère / déjà relevée |
| Moyenne | 26–50 | Surveillance accrue |
| Élevée | 51–75 | Alerte proches |
| Critique | 76–100 | Escalade secours |

**Sorties :**
- `gravity_score` (0–100)
- `gravity_level`
- `injury_probability` (0–1, modulée par âge/profil)
- `impact_intensity` (0–1)
- `time_on_ground_s`
- `severity_label` : normal | urgent | critique

Implémentation : `backend/services/severity_engine.py`

---

## 5. Tableau de bord (exploitation)

Widgets obligatoires :

- Nombre de chutes (période)
- Répartition par **pièce** (`Camera.room`)
- Temps moyen d’intervention
- Fréquence / taux de fausses alertes
- Disponibilité des caméras (%)
- Courbes historiques (chutes/jour, FP%, précision cumulée)

**Frontend :** `DashboardController` + auto-refresh  
**API :** `/dashboard/overview`, `/dashboard/exploitation`, `/dashboard/history`

---

## 6. Sécurité renforcée

| Mesure | Implémentation |
|--------|----------------|
| Chiffrement AES-256-GCM vidéos locales | `video_crypto` / preuves admin |
| Rotation des clés | `scripts/rotate_keys.py` |
| Audit des accès (hash-chain) | `audit_logger` — login, MFA, encrypt |
| MFA obligatoire admin | TOTP — `MFA_REQUIRED` / `MFA_SETUP_REQUIRED` |
| RBAC | admin / operator / family / viewer |
| Vie privée | Image brute en RAM ; sortie = squelette / texte ; Edge-first |

---

## 7. Alignement livrables CDC §13

| Livrable | Couverture addendum |
|----------|---------------------|
| Algorithmes décompte + géométrie | §2 critères + délai profil |
| Moteur IA | YOLO + MediaPipe + `fall_criteria` |
| API REST | KPI, history, qualifies, cameras RTSP |
| Desktop | Dashboard, simulation, admin MFA |
| Passerelle alerte | Telegram + SMTP |
| Modèle entraîné | `ml/` sévérité + critères live |

---

## 8. Synthèse des corrections par rapport au CDC initial

1. Analyse métier : acteurs, parcours, scénarios, processus formalisés  
2. IA : critères explicites + **YOLO (personne) + MediaPipe (squelette)**  
3. KPI qualité/latence définis et branchés dashboard  
4. Gravité multi-niveaux + probabilité de blessure  
5. Dashboard exploitation (pièce, intervention, FP, caméras)  
6. AES, rotation clés, audit, MFA admin  

**Cœur applicatif :** la décision de chute repose sur le **squelette MediaPipe**, guidé par **YOLO** pour la précision de détection de personne, puis sur les **critères versionnés** et le **score de gravité**.
