# MPD - Modèle Physique de Données (Merise)
## Système de Détection de Chutes par Edge AI - SQLite

---

### Adaptation pour SQLite

Le MPD adapte le MLD aux spécificités du SGBD SQLite :
- Types de données SQLite spécifiques
- Contraintes SQLite (FOREIGN KEY, CHECK, UNIQUE, NOT NULL)
- AUTOINCREMENT pour les clés primaires
- Index pour l'optimisation
- Pragmas de configuration

---

### Configuration SQLite recommandée

```sql
-- Activation des clés étrangères
PRAGMA foreign_keys = ON;

-- Mode strict (erreur si type incorrect)
PRAGMA strict = ON;

-- Journaling mode WAL (Write-Ahead Logging) pour meilleure performance
PRAGMA journal_mode = WAL;

-- Synchronisation mode NORMAL (bon compromis performance/sécurité)
PRAGMA synchronous = NORMAL;

-- Cache size augmenté (10MB)
PRAGMA cache_size = -10000;

-- Temp store en mémoire
PRAGMA temp_store = MEMORY;

-- Page size 4096 bytes
PRAGMA page_size = 4096;
```

---

### Types de données SQLite

| Type générique | Type SQLite | Description |
|----------------|-------------|-------------|
| INTEGER | INTEGER | Entier signé (1, 2, 3, 4, 6, 8 bytes) |
| VARCHAR(n) | TEXT | Texte de longueur variable |
| TEXT | TEXT | Texte long |
| DECIMAL(m,d) | REAL | Nombre décimal (virgule flottante) |
| BOOLEAN | INTEGER | 0 = FALSE, 1 = TRUE |
| DATETIME | TEXT | Format ISO8601: 'YYYY-MM-DD HH:MM:SS' |
| DATE | TEXT | Format ISO8601: 'YYYY-MM-DD' |

---

### Tables SQLite avec contraintes

#### 1. TABLE Users

```sql
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT,
    phone TEXT,
    role TEXT NOT NULL CHECK(role IN ('ADMIN', 'MEDECIN', 'FAMILLE', 'TECHNICIEN')),
    status TEXT NOT NULL DEFAULT 'ACTIF' CHECK(status IN ('ACTIF', 'INACTIF', 'SUSPENDU')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_users_role_status ON Users(role, status);
```

---

#### 2. TABLE Patients

```sql
CREATE TABLE Patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    age INTEGER CHECK(age >= 0 AND age <= 150),
    gender TEXT CHECK(gender IN ('H', 'F', 'AUTRE')),
    weight REAL CHECK(weight >= 0 AND weight <= 300),
    height REAL CHECK(height >= 0 AND height <= 250),
    mobility_level TEXT CHECK(mobility_level IN ('AUTONOME', 'CANNE', 'DEAMBULATEUR', 'FAUTEUIL')),
    medical_notes TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE INDEX idx_patients_user_id ON Patients(user_id);
```

---

#### 3. TABLE EmergencyContacts

```sql
CREATE TABLE EmergencyContacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    fullname TEXT NOT NULL,
    relationship TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    priority INTEGER NOT NULL DEFAULT 2 CHECK(priority IN (1, 2, 3)),
    FOREIGN KEY (patient_id) REFERENCES Patients(id) ON DELETE CASCADE
);

CREATE INDEX idx_contacts_patient_id ON EmergencyContacts(patient_id);
CREATE INDEX idx_contacts_priority ON EmergencyContacts(patient_id, priority);
```

---

#### 4. TABLE Rooms

```sql
CREATE TABLE Rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    room_name TEXT NOT NULL,
    floor INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(id) ON DELETE CASCADE
);

CREATE INDEX idx_rooms_patient_id ON Rooms(patient_id);
```

---

#### 5. TABLE Cameras

```sql
CREATE TABLE Cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    camera_name TEXT NOT NULL,
    ip_address TEXT NOT NULL UNIQUE,
    rtsp_url TEXT NOT NULL,
    resolution TEXT NOT NULL,
    fps INTEGER NOT NULL CHECK(fps > 0),
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE')),
    installation_date TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (room_id) REFERENCES Rooms(id) ON DELETE CASCADE
);

CREATE INDEX idx_cameras_room_id ON Cameras(room_id);
CREATE INDEX idx_cameras_ip ON Cameras(ip_address);
CREATE INDEX idx_cameras_status ON Cameras(status);
```

---

#### 6. TABLE MonitoringSessions

```sql
CREATE TABLE MonitoringSessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    start_time TEXT NOT NULL DEFAULT (datetime('now')),
    end_time TEXT,
    duration INTEGER CHECK(duration >= 0),
    status TEXT NOT NULL DEFAULT 'EN_COURS' CHECK(status IN ('EN_COURS', 'TERMINEE', 'INTERROMPUE')),
    FOREIGN KEY (camera_id) REFERENCES Cameras(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES Patients(id) ON DELETE CASCADE,
    CHECK (end_time IS NULL OR end_time > start_time)
);

CREATE INDEX idx_sessions_camera_id ON MonitoringSessions(camera_id);
CREATE INDEX idx_sessions_patient_id ON MonitoringSessions(patient_id);
CREATE INDEX idx_sessions_dates ON MonitoringSessions(start_time, end_time);
CREATE INDEX idx_sessions_status ON MonitoringSessions(status);
```

---

#### 7. TABLE SkeletonFrames

```sql
CREATE TABLE SkeletonFrames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    frame_number INTEGER NOT NULL,
    nose_x REAL,
    nose_y REAL,
    nose_z REAL,
    left_eye_inner_x REAL,
    left_eye_inner_y REAL,
    left_eye_inner_z REAL,
    left_eye_x REAL,
    left_eye_y REAL,
    left_eye_z REAL,
    left_eye_outer_x REAL,
    left_eye_outer_y REAL,
    left_eye_outer_z REAL,
    right_eye_inner_x REAL,
    right_eye_inner_y REAL,
    right_eye_inner_z REAL,
    right_eye_x REAL,
    right_eye_y REAL,
    right_eye_z REAL,
    right_eye_outer_x REAL,
    right_eye_outer_y REAL,
    right_eye_outer_z REAL,
    left_ear_x REAL,
    left_ear_y REAL,
    left_ear_z REAL,
    right_ear_x REAL,
    right_ear_y REAL,
    right_ear_z REAL,
    mouth_left_x REAL,
    mouth_left_y REAL,
    mouth_left_z REAL,
    mouth_right_x REAL,
    mouth_right_y REAL,
    mouth_right_z REAL,
    left_shoulder_x REAL,
    left_shoulder_y REAL,
    left_shoulder_z REAL,
    right_shoulder_x REAL,
    right_shoulder_y REAL,
    right_shoulder_z REAL,
    left_elbow_x REAL,
    left_elbow_y REAL,
    left_elbow_z REAL,
    right_elbow_x REAL,
    right_elbow_y REAL,
    right_elbow_z REAL,
    left_wrist_x REAL,
    left_wrist_y REAL,
    left_wrist_z REAL,
    right_wrist_x REAL,
    right_wrist_y REAL,
    right_wrist_z REAL,
    left_pinky_x REAL,
    left_pinky_y REAL,
    left_pinky_z REAL,
    right_pinky_x REAL,
    right_pinky_y REAL,
    right_pinky_z REAL,
    left_index_x REAL,
    left_index_y REAL,
    left_index_z REAL,
    right_index_x REAL,
    right_index_y REAL,
    right_index_z REAL,
    left_thumb_x REAL,
    left_thumb_y REAL,
    left_thumb_z REAL,
    right_thumb_x REAL,
    right_thumb_y REAL,
    right_thumb_z REAL,
    left_hip_x REAL,
    left_hip_y REAL,
    left_hip_z REAL,
    right_hip_x REAL,
    right_hip_y REAL,
    right_hip_z REAL,
    left_knee_x REAL,
    left_knee_y REAL,
    left_knee_z REAL,
    right_knee_x REAL,
    right_knee_y REAL,
    right_knee_z REAL,
    left_ankle_x REAL,
    left_ankle_y REAL,
    left_ankle_z REAL,
    right_ankle_x REAL,
    right_ankle_y REAL,
    right_ankle_z REAL,
    left_heel_x REAL,
    left_heel_y REAL,
    left_heel_z REAL,
    right_heel_x REAL,
    right_heel_y REAL,
    right_heel_z REAL,
    left_foot_index_x REAL,
    left_foot_index_y REAL,
    left_foot_index_z REAL,
    right_foot_index_x REAL,
    right_foot_index_y REAL,
    right_foot_index_z REAL,
    FOREIGN KEY (session_id) REFERENCES MonitoringSessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_frames_session_id ON SkeletonFrames(session_id);
CREATE INDEX idx_frames_timestamp ON SkeletonFrames(session_id, timestamp);
```

---

#### 8. TABLE Falls

```sql
CREATE TABLE Falls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    detection_time TEXT NOT NULL DEFAULT (datetime('now')),
    trunk_angle REAL,
    body_height REAL,
    vertical_speed REAL,
    acceleration REAL,
    center_gravity_x REAL,
    center_gravity_y REAL,
    center_gravity_speed REAL,
    immobility_duration REAL,
    floor_time REAL,
    kinetic_energy REAL,
    confidence_score REAL CHECK(confidence_score >= 0 AND confidence_score <= 1),
    fall_score REAL CHECK(fall_score >= 0 AND fall_score <= 1),
    severity_score REAL CHECK(severity_score >= 0 AND severity_score <= 1),
    injury_probability REAL CHECK(injury_probability >= 0 AND injury_probability <= 100),
    result TEXT CHECK(result IN ('CHUTE_CONFIRMEE', 'FAUX_POSITIF', 'INDETERMINE')),
    FOREIGN KEY (session_id) REFERENCES MonitoringSessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_falls_session_id ON Falls(session_id);
CREATE INDEX idx_falls_detection_time ON Falls(detection_time);
CREATE INDEX idx_falls_result ON Falls(result);
```

---

#### 9. TABLE Alerts

```sql
CREATE TABLE Alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fall_id INTEGER NOT NULL,
    alert_level TEXT NOT NULL CHECK(alert_level IN ('CRITIQUE', 'HAUTE', 'MOYENNE', 'BASSE')),
    sent_at TEXT NOT NULL DEFAULT (datetime('now')),
    acknowledged INTEGER NOT NULL DEFAULT 0 CHECK(acknowledged IN (0, 1)),
    response_time INTEGER CHECK(response_time >= 0),
    FOREIGN KEY (fall_id) REFERENCES Falls(id) ON DELETE CASCADE
);

CREATE INDEX idx_alerts_fall_id ON Alerts(fall_id);
CREATE INDEX idx_alerts_level ON Alerts(alert_level);
CREATE INDEX idx_alerts_sent_at ON Alerts(sent_at);
```

---

#### 10. TABLE Notifications

```sql
CREATE TABLE Notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    channel TEXT NOT NULL CHECK(channel IN ('TELEGRAM', 'EMAIL', 'SMS', 'PUSH')),
    recipient TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'EN_ATTENTE' CHECK(status IN ('ENVOYE', 'EN_ECHEC', 'EN_ATTENTE')),
    sent_time TEXT,
    FOREIGN KEY (alert_id) REFERENCES Alerts(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_alert_id ON Notifications(alert_id);
CREATE INDEX idx_notifications_status ON Notifications(status);
```

---

#### 11. TABLE IncidentHistory

```sql
CREATE TABLE IncidentHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fall_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (fall_id) REFERENCES Falls(id) ON DELETE CASCADE
);

CREATE INDEX idx_history_fall_id ON IncidentHistory(fall_id);
```

---

#### 12. TABLE SimulationVideos

```sql
CREATE TABLE SimulationVideos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    description TEXT,
    expected_result TEXT NOT NULL CHECK(expected_result IN ('CHUTE', 'PAS_CHUTE')),
    upload_date TEXT NOT NULL DEFAULT (datetime('now'))
);
```

---

#### 13. TABLE SimulationResults

```sql
CREATE TABLE SimulationResults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulation_id INTEGER NOT NULL,
    precision REAL CHECK(precision >= 0 AND precision <= 1),
    recall REAL CHECK(recall >= 0 AND recall <= 1),
    f1_score REAL CHECK(f1_score >= 0 AND f1_score <= 1),
    false_positive INTEGER CHECK(false_positive >= 0),
    false_negative INTEGER CHECK(false_negative >= 0),
    detection_time INTEGER CHECK(detection_time >= 0),
    FOREIGN KEY (simulation_id) REFERENCES SimulationVideos(id) ON DELETE CASCADE
);

CREATE INDEX idx_results_simulation_id ON SimulationResults(simulation_id);
```

---

#### 14. TABLE AISettings

```sql
CREATE TABLE AISettings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    threshold_angle REAL NOT NULL DEFAULT 45.0 CHECK(threshold_angle > 0),
    threshold_speed REAL NOT NULL DEFAULT 2.0 CHECK(threshold_speed > 0),
    threshold_acceleration REAL NOT NULL DEFAULT 5.0 CHECK(threshold_acceleration > 0),
    threshold_immobility REAL NOT NULL DEFAULT 30.0 CHECK(threshold_immobility >= 0),
    threshold_floor_time REAL NOT NULL DEFAULT 60.0 CHECK(threshold_floor_time >= 0),
    threshold_severity REAL NOT NULL DEFAULT 0.7 CHECK(threshold_severity >= 0 AND threshold_severity <= 1),
    weight_angle REAL NOT NULL DEFAULT 0.2 CHECK(weight_angle >= 0 AND weight_angle <= 1),
    weight_speed REAL NOT NULL DEFAULT 0.25 CHECK(weight_speed >= 0 AND weight_speed <= 1),
    weight_acceleration REAL NOT NULL DEFAULT 0.2 CHECK(weight_acceleration >= 0 AND weight_acceleration <= 1),
    weight_immobility REAL NOT NULL DEFAULT 0.15 CHECK(weight_immobility >= 0 AND weight_immobility <= 1),
    weight_floor_time REAL NOT NULL DEFAULT 0.2 CHECK(weight_floor_time >= 0 AND weight_floor_time <= 1),
    modified_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK ((weight_angle + weight_speed + weight_acceleration + weight_immobility + weight_floor_time) = 1.0)
);
```

---

#### 15. TABLE KPIs

```sql
CREATE TABLE KPIs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accuracy REAL CHECK(accuracy >= 0 AND accuracy <= 1),
    precision REAL CHECK(precision >= 0 AND precision <= 1),
    recall REAL CHECK(recall >= 0 AND recall <= 1),
    specificity REAL CHECK(specificity >= 0 AND specificity <= 1),
    sensitivity REAL CHECK(sensitivity >= 0 AND sensitivity <= 1),
    f1_score REAL CHECK(f1_score >= 0 AND f1_score <= 1),
    false_positive_rate REAL CHECK(false_positive_rate >= 0 AND false_positive_rate <= 1),
    false_negative_rate REAL CHECK(false_negative_rate >= 0 AND false_negative_rate <= 1),
    mean_detection_time REAL CHECK(mean_detection_time >= 0),
    mean_alert_time REAL CHECK(mean_alert_time >= 0),
    uptime REAL CHECK(uptime >= 0 AND uptime <= 100),
    calculated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

---

#### 16. TABLE AuditLogs

```sql
CREATE TABLE AuditLogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL CHECK(action IN ('CONNEXION', 'MODIFICATION', 'SUPPRESSION', 'EXPORT', 'PARAMETRES')),
    table_name TEXT NOT NULL,
    record_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_user_id ON AuditLogs(user_id);
CREATE INDEX idx_audit_timestamp ON AuditLogs(timestamp);
CREATE INDEX idx_audit_action ON AuditLogs(action);
```

---

#### 17. TABLE SecurityLogs

```sql
CREATE TABLE SecurityLogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_type TEXT NOT NULL CHECK(event_type IN ('TENTATIVE_CONNEXION', 'MFA', 'CHANGEMENT_MDP', 'ROTATION_CLES', 'ACCES_VIDEO')),
    description TEXT,
    success INTEGER NOT NULL DEFAULT 1 CHECK(success IN (0, 1)),
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE SET NULL
);

CREATE INDEX idx_security_user_id ON SecurityLogs(user_id);
CREATE INDEX idx_security_timestamp ON SecurityLogs(timestamp);
CREATE INDEX idx_security_event_type ON SecurityLogs(event_type);
```

---

#### 18. TABLE SystemSettings

```sql
CREATE TABLE SystemSettings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    modified_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_settings_key ON SystemSettings(key);
```

---

### Optimisations de performance

#### 1. Partitionnement virtuel (Simulé)

Pour les tables volumineuses (SkeletonFrames, Falls), utiliser des requêtes filtrées par date :

```sql
-- Requête optimisée avec filtre de date
SELECT * FROM SkeletonFrames 
WHERE session_id = ? AND timestamp >= ? AND timestamp < ?
ORDER BY timestamp;
```

#### 2. Index de couverture

Créer des index qui couvrent les colonnes fréquemment interrogées ensemble :

```sql
-- Index de couverture pour les sessions actives
CREATE INDEX idx_sessions_active ON MonitoringSessions(status, start_time, patient_id, camera_id);
```

#### 3. Préparation des requêtes

Utiliser des prepared statements pour les requêtes répétitives :

```python
# Exemple Python
stmt = db.prepare("SELECT * FROM Falls WHERE session_id = ? ORDER BY detection_time")
```

#### 4. Nettoyage périodique

```sql
-- Archivage des anciennes trames squelette (plus de 90 jours)
DELETE FROM SkeletonFrames 
WHERE timestamp < datetime('now', '-90 days');

-- Archivage des anciens logs (plus de 365 jours)
DELETE FROM AuditLogs 
WHERE timestamp < datetime('now', '-365 days');

DELETE FROM SecurityLogs 
WHERE timestamp < datetime('now', '-365 days');
```

---

### Stratégie de sauvegarde

#### 1. Sauvegarde en ligne (Online Backup)

```sql
-- Sauvegarde vers un fichier
VACUUM INTO 'backup_falldetection_YYYYMMDD.db';
```

#### 2. Sauvegarde incrémentale

```sql
-- Point de restauration
SAVEPOINT backup_point;

-- Opérations...
-- ...

-- Si succès
RELEASE SAVEPOINT backup_point;

-- Si échec
ROLLBACK TO SAVEPOINT backup_point;
```

#### 3. Export des données

```sql
-- Export en CSV
.mode csv
.output export_patients.csv
SELECT * FROM Patients;
.output

-- Export en JSON
.mode json
.output export_falls.json
SELECT * FROM Falls;
.output
```

---

### Maintenance

#### 1. VACUUM

```sql
-- Reconstruction de la base de données (optimisation)
VACUUM;
```

#### 2. ANALYZE

```sql
-- Mise à jour des statistiques pour l'optimiseur de requêtes
ANALYZE;
```

#### 3. REINDEX

```sql
-- Reconstruction des index
REINDEX;
```

#### 4. Intégrité référentielle

```sql
-- Vérification de l'intégrité
PRAGMA integrity_check;
```

---

### Sécurité

#### 1. Chiffrement

Utiliser SQLCipher pour le chiffrement de la base de données :

```bash
# Installation de SQLCipher
# Configuration avec clé de chiffrement
PRAGMA key = 'votre_cle_secrete';
```

#### 2. Permissions

```sql
-- En production, limiter les permissions
-- Utiliser un utilisateur avec droits restreints
```

#### 3. Journalisation

Toutes les modifications sont automatiquement journalisées via les tables AuditLogs et SecurityLogs.
