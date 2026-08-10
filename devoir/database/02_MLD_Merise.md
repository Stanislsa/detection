# MLD - Modèle Logique de Données (Merise)
## Système de Détection de Chutes par Edge AI

---

### Transformation du MCD en MLD

Le MLD est obtenu en transformant les entités du MCD en tables relationnelles, en appliquant les règles suivantes :
- Chaque entité devient une table
- Les identifiants deviennent des clés primaires
- Les relations 1:N deviennent des clés étrangères
- Les relations 1:1 sont fusionnées ou maintenues selon le contexte
- Les propriétés deviennent des colonnes
- Les types de données sont définis

---

### Tables du MLD

#### 1. TABLE UTILISATEUR (Users)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| firstname | VARCHAR(100) | NOT NULL | Prénom |
| lastname | VARCHAR(100) | NOT NULL | Nom |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Email unique |
| password_hash | VARCHAR(255) | | Mot de passe haché (optionnel) |
| phone | VARCHAR(20) | | Téléphone |
| role | VARCHAR(20) | NOT NULL, CHECK | Rôle |
| status | VARCHAR(20) | NOT NULL, CHECK, DEFAULT 'ACTIF' | Statut |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date création |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date modification |

**Contraintes CHECK :**
- role IN ('ADMIN', 'MEDECIN', 'FAMILLE', 'TECHNICIEN')
- status IN ('ACTIF', 'INACTIF', 'SUSPENDU')

---

#### 2. TABLE PATIENT (Patients)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| user_id | INTEGER | NOT NULL, FK | Référence Users.id |
| age | INTEGER | CHECK | Âge |
| gender | VARCHAR(10) | CHECK | Genre |
| weight | DECIMAL(5,2) | CHECK | Poids en kg |
| height | DECIMAL(5,2) | CHECK | Taille en cm |
| mobility_level | VARCHAR(20) | CHECK | Niveau mobilité |
| medical_notes | TEXT | | Notes médicales |
| address | VARCHAR(255) | | Adresse |
| latitude | DECIMAL(10,8) | | Latitude GPS |
| longitude | DECIMAL(11,8) | | Longitude GPS |

**Contraintes CHECK :**
- age >= 0 AND age <= 150
- gender IN ('H', 'F', 'AUTRE')
- weight >= 0 AND weight <= 300
- height >= 0 AND height <= 250
- mobility_level IN ('AUTONOME', 'CANNE', 'DEAMBULATEUR', 'FAUTEUIL')

**Clé étrangère :**
- user_id → Users(id) ON DELETE CASCADE

---

#### 3. TABLE CONTACT_URGENCE (EmergencyContacts)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| patient_id | INTEGER | NOT NULL, FK | Référence Patients.id |
| fullname | VARCHAR(100) | NOT NULL | Nom complet |
| relationship | VARCHAR(50) | NOT NULL | Relation |
| phone | VARCHAR(20) | NOT NULL | Téléphone |
| email | VARCHAR(255) | | Email |
| priority | INTEGER | NOT NULL, CHECK, DEFAULT 2 | Priorité |

**Contraintes CHECK :**
- priority IN (1, 2, 3)

**Clé étrangère :**
- patient_id → Patients(id) ON DELETE CASCADE

---

#### 4. TABLE PIECE (Rooms)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| patient_id | INTEGER | NOT NULL, FK | Référence Patients.id |
| room_name | VARCHAR(50) | NOT NULL | Nom de la pièce |
| floor | INTEGER | NOT NULL, DEFAULT 0 | Étage |
| description | TEXT | | Description |

**Clé étrangère :**
- patient_id → Patients(id) ON DELETE CASCADE

---

#### 5. TABLE CAMERA (Cameras)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| room_id | INTEGER | NOT NULL, FK | Référence Rooms.id |
| camera_name | VARCHAR(100) | NOT NULL | Nom de la caméra |
| ip_address | VARCHAR(45) | NOT NULL, UNIQUE | Adresse IP |
| rtsp_url | VARCHAR(255) | NOT NULL | URL RTSP |
| resolution | VARCHAR(20) | NOT NULL | Résolution |
| fps | INTEGER | NOT NULL, CHECK | Images/seconde |
| status | VARCHAR(20) | NOT NULL, CHECK, DEFAULT 'ACTIVE' | Statut |
| installation_date | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date installation |

**Contraintes CHECK :**
- fps > 0
- status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE')

**Clé étrangère :**
- room_id → Rooms(id) ON DELETE CASCADE

---

#### 6. TABLE SESSION_SURVEILLANCE (MonitoringSessions)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| camera_id | INTEGER | NOT NULL, FK | Référence Cameras.id |
| patient_id | INTEGER | NOT NULL, FK | Référence Patients.id |
| start_time | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Heure début |
| end_time | DATETIME | | Heure fin |
| duration | INTEGER | CHECK | Durée en secondes |
| status | VARCHAR(20) | NOT NULL, CHECK, DEFAULT 'EN_COURS' | Statut |

**Contraintes CHECK :**
- duration >= 0
- status IN ('EN_COURS', 'TERMINEE', 'INTERROMPUE')
- end_time > start_time

**Clés étrangères :**
- camera_id → Cameras(id) ON DELETE CASCADE
- patient_id → Patients(id) ON DELETE CASCADE

---

#### 7. TABLE TRAME_SQUELETTE (SkeletonFrames)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| session_id | INTEGER | NOT NULL, FK | Référence MonitoringSessions.id |
| timestamp | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Horodatage |
| frame_number | INTEGER | NOT NULL | Numéro de trame |
| nose_x | DECIMAL(10,6) | | Position X nez |
| nose_y | DECIMAL(10,6) | | Position Y nez |
| nose_z | DECIMAL(10,6) | | Position Z nez |
| left_eye_inner_x | DECIMAL(10,6) | | Position X œil gauche interne |
| left_eye_inner_y | DECIMAL(10,6) | | Position Y œil gauche interne |
| left_eye_inner_z | DECIMAL(10,6) | | Position Z œil gauche interne |
| left_eye_x | DECIMAL(10,6) | | Position X œil gauche |
| left_eye_y | DECIMAL(10,6) | | Position Y œil gauche |
| left_eye_z | DECIMAL(10,6) | | Position Z œil gauche |
| left_eye_outer_x | DECIMAL(10,6) | | Position X œil gauche externe |
| left_eye_outer_y | DECIMAL(10,6) | | Position Y œil gauche externe |
| left_eye_outer_z | DECIMAL(10,6) | | Position Z œil gauche externe |
| right_eye_inner_x | DECIMAL(10,6) | | Position X œil droit interne |
| right_eye_inner_y | DECIMAL(10,6) | | Position Y œil droit interne |
| right_eye_inner_z | DECIMAL(10,6) | | Position Z œil droit interne |
| right_eye_x | DECIMAL(10,6) | | Position X œil droit |
| right_eye_y | DECIMAL(10,6) | | Position Y œil droit |
| right_eye_z | DECIMAL(10,6) | | Position Z œil droit |
| right_eye_outer_x | DECIMAL(10,6) | | Position X œil droit externe |
| right_eye_outer_y | DECIMAL(10,6) | | Position Y œil droit externe |
| right_eye_outer_z | DECIMAL(10,6) | | Position Z œil droit externe |
| left_ear_x | DECIMAL(10,6) | | Position X oreille gauche |
| left_ear_y | DECIMAL(10,6) | | Position Y oreille gauche |
| left_ear_z | DECIMAL(10,6) | | Position Z oreille gauche |
| right_ear_x | DECIMAL(10,6) | | Position X oreille droit |
| right_ear_y | DECIMAL(10,6) | | Position Y oreille droit |
| right_ear_z | DECIMAL(10,6) | | Position Z oreille droit |
| mouth_left_x | DECIMAL(10,6) | | Position X bouche gauche |
| mouth_left_y | DECIMAL(10,6) | | Position Y bouche gauche |
| mouth_left_z | DECIMAL(10,6) | | Position Z bouche gauche |
| mouth_right_x | DECIMAL(10,6) | | Position X bouche droite |
| mouth_right_y | DECIMAL(10,6) | | Position Y bouche droite |
| mouth_right_z | DECIMAL(10,6) | | Position Z bouche droite |
| left_shoulder_x | DECIMAL(10,6) | | Position X épaule gauche |
| left_shoulder_y | DECIMAL(10,6) | | Position Y épaule gauche |
| left_shoulder_z | DECIMAL(10,6) | | Position Z épaule gauche |
| right_shoulder_x | DECIMAL(10,6) | | Position X épaule droite |
| right_shoulder_y | DECIMAL(10,6) | | Position Y épaule droite |
| right_shoulder_z | DECIMAL(10,6) | | Position Z épaule droite |
| left_elbow_x | DECIMAL(10,6) | | Position X coude gauche |
| left_elbow_y | DECIMAL(10,6) | | Position Y coude gauche |
| left_elbow_z | DECIMAL(10,6) | | Position Z coude gauche |
| right_elbow_x | DECIMAL(10,6) | | Position X coude droit |
| right_elbow_y | DECIMAL(10,6) | | Position Y coude droit |
| right_elbow_z | DECIMAL(10,6) | | Position Z coude droit |
| left_wrist_x | DECIMAL(10,6) | | Position X poignet gauche |
| left_wrist_y | DECIMAL(10,6) | | Position Y poignet gauche |
| left_wrist_z | DECIMAL(10,6) | | Position Z poignet gauche |
| right_wrist_x | DECIMAL(10,6) | | Position X poignet droit |
| right_wrist_y | DECIMAL(10,6) | | Position Y poignet droit |
| right_wrist_z | DECIMAL(10,6) | | Position Z poignet droit |
| left_pinky_x | DECIMAL(10,6) | | Position X auriculaire gauche |
| left_pinky_y | DECIMAL(10,6) | | Position Y auriculaire gauche |
| left_pinky_z | DECIMAL(10,6) | | Position Z auriculaire gauche |
| right_pinky_x | DECIMAL(10,6) | | Position X auriculaire droit |
| right_pinky_y | DECIMAL(10,6) | | Position Y auriculaire droit |
| right_pinky_z | DECIMAL(10,6) | | Position Z auriculaire droit |
| left_index_x | DECIMAL(10,6) | | Position X index gauche |
| left_index_y | DECIMAL(10,6) | | Position Y index gauche |
| left_index_z | DECIMAL(10,6) | | Position Z index gauche |
| right_index_x | DECIMAL(10,6) | | Position X index droit |
| right_index_y | DECIMAL(10,6) | | Position Y index droit |
| right_index_z | DECIMAL(10,6) | | Position Z index droit |
| left_thumb_x | DECIMAL(10,6) | | Position X pouce gauche |
| left_thumb_y | DECIMAL(10,6) | | Position Y pouce gauche |
| left_thumb_z | DECIMAL(10,6) | | Position Z pouce gauche |
| right_thumb_x | DECIMAL(10,6) | | Position X pouce droit |
| right_thumb_y | DECIMAL(10,6) | | Position Y pouce droit |
| right_thumb_z | DECIMAL(10,6) | | Position Z pouce droit |
| left_hip_x | DECIMAL(10,6) | | Position X hanche gauche |
| left_hip_y | DECIMAL(10,6) | | Position Y hanche gauche |
| left_hip_z | DECIMAL(10,6) | | Position Z hanche gauche |
| right_hip_x | DECIMAL(10,6) | | Position X hanche droite |
| right_hip_y | DECIMAL(10,6) | | Position Y hanche droite |
| right_hip_z | DECIMAL(10,6) | | Position Z hanche droite |
| left_knee_x | DECIMAL(10,6) | | Position X genou gauche |
| left_knee_y | DECIMAL(10,6) | | Position Y genou gauche |
| left_knee_z | DECIMAL(10,6) | | Position Z genou gauche |
| right_knee_x | DECIMAL(10,6) | | Position X genou droit |
| right_knee_y | DECIMAL(10,6) | | Position Y genou droit |
| right_knee_z | DECIMAL(10,6) | | Position Z genou droit |
| left_ankle_x | DECIMAL(10,6) | | Position X cheville gauche |
| left_ankle_y | DECIMAL(10,6) | | Position Y cheville gauche |
| left_ankle_z | DECIMAL(10,6) | | Position Z cheville gauche |
| right_ankle_x | DECIMAL(10,6) | | Position X cheville droite |
| right_ankle_y | DECIMAL(10,6) | | Position Y cheville droite |
| right_ankle_z | DECIMAL(10,6) | | Position Z cheville droite |
| left_heel_x | DECIMAL(10,6) | | Position X talon gauche |
| left_heel_y | DECIMAL(10,6) | | Position Y talon gauche |
| left_heel_z | DECIMAL(10,6) | | Position Z talon gauche |
| right_heel_x | DECIMAL(10,6) | | Position X talon droit |
| right_heel_y | DECIMAL(10,6) | | Position Y talon droit |
| right_heel_z | DECIMAL(10,6) | | Position Z talon droit |
| left_foot_index_x | DECIMAL(10,6) | | Position X pied gauche |
| left_foot_index_y | DECIMAL(10,6) | | Position Y pied gauche |
| left_foot_index_z | DECIMAL(10,6) | | Position Z pied gauche |
| right_foot_index_x | DECIMAL(10,6) | | Position X pied droit |
| right_foot_index_y | DECIMAL(10,6) | | Position Y pied droit |
| right_foot_index_z | DECIMAL(10,6) | | Position Z pied droit |

**Clé étrangère :**
- session_id → MonitoringSessions(id) ON DELETE CASCADE

---

#### 8. TABLE CHUTE (Falls)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| session_id | INTEGER | NOT NULL, FK | Référence MonitoringSessions.id |
| detection_time | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Heure détection |
| trunk_angle | DECIMAL(8,4) | | Angle tronc (degrés) |
| body_height | DECIMAL(10,2) | | Hauteur corps (pixels) |
| vertical_speed | DECIMAL(10,4) | | Vitesse verticale (m/s) |
| acceleration | DECIMAL(10,4) | | Accélération (m/s²) |
| center_gravity_x | DECIMAL(10,6) | | Centre gravité X |
| center_gravity_y | DECIMAL(10,6) | | Centre gravité Y |
| center_gravity_speed | DECIMAL(10,4) | | Vitesse centre gravité |
| immobility_duration | DECIMAL(10,2) | | Durée immobilité (secondes) |
| floor_time | DECIMAL(10,2) | | Temps au sol (secondes) |
| kinetic_energy | DECIMAL(10,4) | | Énergie cinétique |
| confidence_score | DECIMAL(5,4) | CHECK | Score confiance [0,1] |
| fall_score | DECIMAL(5,4) | CHECK | Score chute [0,1] |
| severity_score | DECIMAL(5,4) | CHECK | Score gravité [0,1] |
| injury_probability | DECIMAL(5,2) | CHECK | Probabilité blessure [0,100] |
| result | VARCHAR(20) | CHECK | Résultat |

**Contraintes CHECK :**
- confidence_score >= 0 AND confidence_score <= 1
- fall_score >= 0 AND fall_score <= 1
- severity_score >= 0 AND severity_score <= 1
- injury_probability >= 0 AND injury_probability <= 100
- result IN ('CHUTE_CONFIRMEE', 'FAUX_POSITIF', 'INDETERMINE')

**Clé étrangère :**
- session_id → MonitoringSessions(id) ON DELETE CASCADE

---

#### 9. TABLE ALERTE (Alerts)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| fall_id | INTEGER | NOT NULL, FK | Référence Falls.id |
| alert_level | VARCHAR(20) | NOT NULL, CHECK | Niveau alerte |
| sent_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Heure envoi |
| acknowledged | BOOLEAN | NOT NULL, DEFAULT 0 | Accusé réception |
| response_time | INTEGER | CHECK | Temps réponse (secondes) |

**Contraintes CHECK :**
- alert_level IN ('CRITIQUE', 'HAUTE', 'MOYENNE', 'BASSE')
- response_time >= 0

**Clé étrangère :**
- fall_id → Falls(id) ON DELETE CASCADE

---

#### 10. TABLE NOTIFICATION (Notifications)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| alert_id | INTEGER | NOT NULL, FK | Référence Alerts.id |
| channel | VARCHAR(20) | NOT NULL, CHECK | Canal |
| recipient | VARCHAR(255) | NOT NULL | Destinataire |
| status | VARCHAR(20) | NOT NULL, CHECK, DEFAULT 'EN_ATTENTE' | Statut |
| sent_time | DATETIME | | Heure envoi |

**Contraintes CHECK :**
- channel IN ('TELEGRAM', 'EMAIL', 'SMS', 'PUSH')
- status IN ('ENVOYE', 'EN_ECHEC', 'EN_ATTENTE')

**Clé étrangère :**
- alert_id → Alerts(id) ON DELETE CASCADE

---

#### 11. TABLE HISTORIQUE_INCIDENT (IncidentHistory)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| fall_id | INTEGER | NOT NULL, FK | Référence Falls.id |
| event_type | VARCHAR(50) | NOT NULL | Type événement |
| description | TEXT | | Description |
| timestamp | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Horodatage |

**Clé étrangère :**
- fall_id → Falls(id) ON DELETE CASCADE

---

#### 12. TABLE VIDEO_SIMULATION (SimulationVideos)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| filename | VARCHAR(255) | NOT NULL, UNIQUE | Nom fichier |
| description | TEXT | | Description |
| expected_result | VARCHAR(20) | NOT NULL, CHECK | Résultat attendu |
| upload_date | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date upload |

**Contraintes CHECK :**
- expected_result IN ('CHUTE', 'PAS_CHUTE')

---

#### 13. TABLE RESULTAT_SIMULATION (SimulationResults)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| simulation_id | INTEGER | NOT NULL, FK | Référence SimulationVideos.id |
| precision | DECIMAL(5,4) | CHECK | Précision [0,1] |
| recall | DECIMAL(5,4) | CHECK | Rappel [0,1] |
| f1_score | DECIMAL(5,4) | CHECK | Score F1 [0,1] |
| false_positive | INTEGER | CHECK | Faux positifs |
| false_negative | INTEGER | CHECK | Faux négatifs |
| detection_time | INTEGER | CHECK | Temps détection (ms) |

**Contraintes CHECK :**
- precision >= 0 AND precision <= 1
- recall >= 0 AND recall <= 1
- f1_score >= 0 AND f1_score <= 1
- false_positive >= 0
- false_negative >= 0
- detection_time >= 0

**Clé étrangère :**
- simulation_id → SimulationVideos(id) ON DELETE CASCADE

---

#### 14. TABLE PARAMETRES_IA (AISettings)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| threshold_angle | DECIMAL(8,4) | NOT NULL, DEFAULT 45.0 | Seuil angle (degrés) |
| threshold_speed | DECIMAL(8,4) | NOT NULL, DEFAULT 2.0 | Seuil vitesse (m/s) |
| threshold_acceleration | DECIMAL(8,4) | NOT NULL, DEFAULT 5.0 | Seuil accélération (m/s²) |
| threshold_immobility | DECIMAL(8,2) | NOT NULL, DEFAULT 30.0 | Seuil immobilité (secondes) |
| threshold_floor_time | DECIMAL(8,2) | NOT NULL, DEFAULT 60.0 | Seuil temps sol (secondes) |
| threshold_severity | DECIMAL(5,4) | NOT NULL, DEFAULT 0.7 | Seuil gravité |
| weight_angle | DECIMAL(5,4) | NOT NULL, DEFAULT 0.2 | Pondération angle |
| weight_speed | DECIMAL(5,4) | NOT NULL, DEFAULT 0.25 | Pondération vitesse |
| weight_acceleration | DECIMAL(5,4) | NOT NULL, DEFAULT 0.2 | Pondération accélération |
| weight_immobility | DECIMAL(5,4) | NOT NULL, DEFAULT 0.15 | Pondération immobilité |
| weight_floor_time | DECIMAL(5,4) | NOT NULL, DEFAULT 0.2 | Pondération temps sol |
| modified_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date modification |

**Contraintes CHECK :**
- threshold_angle > 0
- threshold_speed > 0
- threshold_acceleration > 0
- threshold_immobility >= 0
- threshold_floor_time >= 0
- threshold_severity >= 0 AND threshold_severity <= 1
- weight_angle >= 0 AND weight_angle <= 1
- weight_speed >= 0 AND weight_speed <= 1
- weight_acceleration >= 0 AND weight_acceleration <= 1
- weight_immobility >= 0 AND weight_immobility <= 1
- weight_floor_time >= 0 AND weight_floor_time <= 1
- (weight_angle + weight_speed + weight_acceleration + weight_immobility + weight_floor_time) = 1.0

---

#### 15. TABLE KPI (KPIs)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| accuracy | DECIMAL(5,4) | CHECK | Exactitude [0,1] |
| precision | DECIMAL(5,4) | CHECK | Précision [0,1] |
| recall | DECIMAL(5,4) | CHECK | Rappel [0,1] |
| specificity | DECIMAL(5,4) | CHECK | Spécificité [0,1] |
| sensitivity | DECIMAL(5,4) | CHECK | Sensibilité [0,1] |
| f1_score | DECIMAL(5,4) | CHECK | Score F1 [0,1] |
| false_positive_rate | DECIMAL(5,4) | CHECK | Taux faux positifs [0,1] |
| false_negative_rate | DECIMAL(5,4) | CHECK | Taux faux négatifs [0,1] |
| mean_detection_time | DECIMAL(10,2) | CHECK | Temps détection moyen (ms) |
| mean_alert_time | DECIMAL(10,2) | CHECK | Temps alerte moyen (ms) |
| uptime | DECIMAL(5,2) | CHECK | Disponibilité [0,100] |
| calculated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date calcul |

**Contraintes CHECK :**
- accuracy >= 0 AND accuracy <= 1
- precision >= 0 AND precision <= 1
- recall >= 0 AND recall <= 1
- specificity >= 0 AND specificity <= 1
- sensitivity >= 0 AND sensitivity <= 1
- f1_score >= 0 AND f1_score <= 1
- false_positive_rate >= 0 AND false_positive_rate <= 1
- false_negative_rate >= 0 AND false_negative_rate <= 1
- mean_detection_time >= 0
- mean_alert_time >= 0
- uptime >= 0 AND uptime <= 100

---

#### 16. TABLE JOURNAL_AUDIT (AuditLogs)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| user_id | INTEGER | FK | Référence Users.id |
| action | VARCHAR(50) | NOT NULL, CHECK | Action |
| table_name | VARCHAR(50) | NOT NULL | Table concernée |
| record_id | INTEGER | | ID enregistrement |
| old_values | TEXT | | Anciennes valeurs JSON |
| new_values | TEXT | | Nouvelles valeurs JSON |
| timestamp | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Horodatage |
| ip_address | VARCHAR(45) | | Adresse IP |

**Contraintes CHECK :**
- action IN ('CONNEXION', 'MODIFICATION', 'SUPPRESSION', 'EXPORT', 'PARAMETRES')

**Clé étrangère :**
- user_id → Users(id) ON DELETE SET NULL

---

#### 17. TABLE JOURNAL_SECURITE (SecurityLogs)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| user_id | INTEGER | FK | Référence Users.id |
| event_type | VARCHAR(50) | NOT NULL, CHECK | Type événement |
| description | TEXT | | Description |
| success | BOOLEAN | NOT NULL, DEFAULT 1 | Succès |
| timestamp | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Horodatage |
| ip_address | VARCHAR(45) | | Adresse IP |

**Contraintes CHECK :**
- event_type IN ('TENTATIVE_CONNEXION', 'MFA', 'CHANGEMENT_MDP', 'ROTATION_CLES', 'ACCES_VIDEO')

**Clé étrangère :**
- user_id → Users(id) ON DELETE SET NULL

---

#### 18. TABLE PARAMETRES_SYSTEME (SystemSettings)

| Nom colonne | Type de données | Contraintes | Description |
|-------------|-----------------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Identifiant unique |
| key | VARCHAR(100) | NOT NULL, UNIQUE | Clé |
| value | TEXT | NOT NULL | Valeur |
| description | TEXT | | Description |
| modified_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Date modification |

---

### Normalisation 3NF

Toutes les tables respectent la 3ème Forme Normale :

1. **1NF** : Tous les attributs sont atomiques (pas de valeurs multiples)
2. **2NF** : Tous les attributs non-clé dépendent de la clé primaire entière
3. **3NF** : Aucun attribut non-clé ne dépend transitivement d'un autre attribut non-clé

**Exemples de dépendances fonctionnelles :**

- Users : id → firstname, lastname, email, password_hash, phone, role, status, created_at, updated_at
- Patients : id → user_id, age, gender, weight, height, mobility_level, medical_notes, address, latitude, longitude
- Cameras : id → room_id, camera_name, ip_address, rtsp_url, resolution, fps, status, installation_date
- Falls : id → session_id, detection_time, trunk_angle, body_height, vertical_speed, acceleration, ..., result

---

### Index recommandés

| Table | Index | Colonnes | Type |
|-------|-------|----------|------|
| Users | idx_users_email | email | UNIQUE |
| Users | idx_users_role_status | role, status | Composite |
| Patients | idx_patients_user_id | user_id | FK |
| EmergencyContacts | idx_contacts_patient_id | patient_id | FK |
| EmergencyContacts | idx_contacts_priority | patient_id, priority | Composite |
| Rooms | idx_rooms_patient_id | patient_id | FK |
| Cameras | idx_cameras_room_id | room_id | FK |
| Cameras | idx_cameras_ip | ip_address | UNIQUE |
| Cameras | idx_cameras_status | status | Simple |
| MonitoringSessions | idx_sessions_camera_id | camera_id | FK |
| MonitoringSessions | idx_sessions_patient_id | patient_id | FK |
| MonitoringSessions | idx_sessions_dates | start_time, end_time | Composite |
| MonitoringSessions | idx_sessions_status | status | Simple |
| SkeletonFrames | idx_frames_session_id | session_id | FK |
| SkeletonFrames | idx_frames_timestamp | session_id, timestamp | Composite |
| Falls | idx_falls_session_id | session_id | FK |
| Falls | idx_falls_detection_time | detection_time | Simple |
| Falls | idx_falls_result | result | Simple |
| Alerts | idx_alerts_fall_id | fall_id | FK |
| Alerts | idx_alerts_level | alert_level | Simple |
| Alerts | idx_alerts_sent_at | sent_at | Simple |
| Notifications | idx_notifications_alert_id | alert_id | FK |
| Notifications | idx_notifications_status | status | Simple |
| IncidentHistory | idx_history_fall_id | fall_id | FK |
| SimulationResults | idx_results_simulation_id | simulation_id | FK |
| AuditLogs | idx_audit_user_id | user_id | FK |
| AuditLogs | idx_audit_timestamp | timestamp | Simple |
| AuditLogs | idx_audit_action | action | Simple |
| SecurityLogs | idx_security_user_id | user_id | FK |
| SecurityLogs | idx_security_timestamp | timestamp | Simple |
| SecurityLogs | idx_security_event_type | event_type | Simple |
| SystemSettings | idx_settings_key | key | UNIQUE |
