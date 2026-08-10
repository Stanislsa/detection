-- ============================================================================
-- Système de Détection de Chutes par Edge AI
-- Schéma SQLite Complet
-- Version: 1.0
-- Date: 2026
-- ============================================================================

-- Activation des pragmas SQLite
PRAGMA foreign_keys = ON;
PRAGMA strict = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -10000;
PRAGMA temp_store = MEMORY;
PRAGMA page_size = 4096;

-- ============================================================================
-- TABLE 1: Users
-- ============================================================================
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

-- ============================================================================
-- TABLE 2: Patients
-- ============================================================================
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

-- ============================================================================
-- TABLE 3: EmergencyContacts
-- ============================================================================
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

-- ============================================================================
-- TABLE 4: Rooms
-- ============================================================================
CREATE TABLE Rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    room_name TEXT NOT NULL,
    floor INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(id) ON DELETE CASCADE
);

CREATE INDEX idx_rooms_patient_id ON Rooms(patient_id);

-- ============================================================================
-- TABLE 5: Cameras
-- ============================================================================
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

-- ============================================================================
-- TABLE 6: MonitoringSessions
-- ============================================================================
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

-- ============================================================================
-- TABLE 7: SkeletonFrames (33 MediaPipe Pose Landmarks)
-- ============================================================================
CREATE TABLE SkeletonFrames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    frame_number INTEGER NOT NULL,
    -- Nose (1 landmark)
    nose_x REAL,
    nose_y REAL,
    nose_z REAL,
    -- Left Eye (3 landmarks)
    left_eye_inner_x REAL,
    left_eye_inner_y REAL,
    left_eye_inner_z REAL,
    left_eye_x REAL,
    left_eye_y REAL,
    left_eye_z REAL,
    left_eye_outer_x REAL,
    left_eye_outer_y REAL,
    left_eye_outer_z REAL,
    -- Right Eye (3 landmarks)
    right_eye_inner_x REAL,
    right_eye_inner_y REAL,
    right_eye_inner_z REAL,
    right_eye_x REAL,
    right_eye_y REAL,
    right_eye_z REAL,
    right_eye_outer_x REAL,
    right_eye_outer_y REAL,
    right_eye_outer_z REAL,
    -- Ears (2 landmarks)
    left_ear_x REAL,
    left_ear_y REAL,
    left_ear_z REAL,
    right_ear_x REAL,
    right_ear_y REAL,
    right_ear_z REAL,
    -- Mouth (2 landmarks)
    mouth_left_x REAL,
    mouth_left_y REAL,
    mouth_left_z REAL,
    mouth_right_x REAL,
    mouth_right_y REAL,
    mouth_right_z REAL,
    -- Left Shoulder (1 landmark)
    left_shoulder_x REAL,
    left_shoulder_y REAL,
    left_shoulder_z REAL,
    -- Right Shoulder (1 landmark)
    right_shoulder_x REAL,
    right_shoulder_y REAL,
    right_shoulder_z REAL,
    -- Left Elbow (1 landmark)
    left_elbow_x REAL,
    left_elbow_y REAL,
    left_elbow_z REAL,
    -- Right Elbow (1 landmark)
    right_elbow_x REAL,
    right_elbow_y REAL,
    right_elbow_z REAL,
    -- Left Wrist (1 landmark)
    left_wrist_x REAL,
    left_wrist_y REAL,
    left_wrist_z REAL,
    -- Right Wrist (1 landmark)
    right_wrist_x REAL,
    right_wrist_y REAL,
    right_wrist_z REAL,
    -- Left Pinky (1 landmark)
    left_pinky_x REAL,
    left_pinky_y REAL,
    left_pinky_z REAL,
    -- Right Pinky (1 landmark)
    right_pinky_x REAL,
    right_pinky_y REAL,
    right_pinky_z REAL,
    -- Left Index (1 landmark)
    left_index_x REAL,
    left_index_y REAL,
    left_index_z REAL,
    -- Right Index (1 landmark)
    right_index_x REAL,
    right_index_y REAL,
    right_index_z REAL,
    -- Left Thumb (1 landmark)
    left_thumb_x REAL,
    left_thumb_y REAL,
    left_thumb_z REAL,
    -- Right Thumb (1 landmark)
    right_thumb_x REAL,
    right_thumb_y REAL,
    right_thumb_z REAL,
    -- Left Hip (1 landmark)
    left_hip_x REAL,
    left_hip_y REAL,
    left_hip_z REAL,
    -- Right Hip (1 landmark)
    right_hip_x REAL,
    right_hip_y REAL,
    right_hip_z REAL,
    -- Left Knee (1 landmark)
    left_knee_x REAL,
    left_knee_y REAL,
    left_knee_z REAL,
    -- Right Knee (1 landmark)
    right_knee_x REAL,
    right_knee_y REAL,
    right_knee_z REAL,
    -- Left Ankle (1 landmark)
    left_ankle_x REAL,
    left_ankle_y REAL,
    left_ankle_z REAL,
    -- Right Ankle (1 landmark)
    right_ankle_x REAL,
    right_ankle_y REAL,
    right_ankle_z REAL,
    -- Left Heel (1 landmark)
    left_heel_x REAL,
    left_heel_y REAL,
    left_heel_z REAL,
    -- Right Heel (1 landmark)
    right_heel_x REAL,
    right_heel_y REAL,
    right_heel_z REAL,
    -- Left Foot Index (1 landmark)
    left_foot_index_x REAL,
    left_foot_index_y REAL,
    left_foot_index_z REAL,
    -- Right Foot Index (1 landmark)
    right_foot_index_x REAL,
    right_foot_index_y REAL,
    right_foot_index_z REAL,
    FOREIGN KEY (session_id) REFERENCES MonitoringSessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_frames_session_id ON SkeletonFrames(session_id);
CREATE INDEX idx_frames_timestamp ON SkeletonFrames(session_id, timestamp);

-- ============================================================================
-- TABLE 8: Falls
-- ============================================================================
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

-- ============================================================================
-- TABLE 9: Alerts
-- ============================================================================
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

-- ============================================================================
-- TABLE 10: Notifications
-- ============================================================================
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

-- ============================================================================
-- TABLE 11: IncidentHistory
-- ============================================================================
CREATE TABLE IncidentHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fall_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (fall_id) REFERENCES Falls(id) ON DELETE CASCADE
);

CREATE INDEX idx_history_fall_id ON IncidentHistory(fall_id);

-- ============================================================================
-- TABLE 12: SimulationVideos
-- ============================================================================
CREATE TABLE SimulationVideos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    description TEXT,
    expected_result TEXT NOT NULL CHECK(expected_result IN ('CHUTE', 'PAS_CHUTE')),
    upload_date TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================================
-- TABLE 13: SimulationResults
-- ============================================================================
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

-- ============================================================================
-- TABLE 14: AISettings
-- ============================================================================
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

-- ============================================================================
-- TABLE 15: KPIs
-- ============================================================================
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

-- ============================================================================
-- TABLE 16: AuditLogs
-- ============================================================================
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

-- ============================================================================
-- TABLE 17: SecurityLogs
-- ============================================================================
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

-- ============================================================================
-- TABLE 18: SystemSettings
-- ============================================================================
CREATE TABLE SystemSettings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    modified_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_settings_key ON SystemSettings(key);

-- ============================================================================
-- Initialisation des paramètres par défaut
-- ============================================================================

-- Insertion des paramètres IA par défaut
INSERT INTO AISettings (
    threshold_angle, threshold_speed, threshold_acceleration,
    threshold_immobility, threshold_floor_time, threshold_severity,
    weight_angle, weight_speed, weight_acceleration,
    weight_immobility, weight_floor_time
) VALUES (
    45.0, 2.0, 5.0,
    30.0, 60.0, 0.7,
    0.2, 0.25, 0.2,
    0.15, 0.2
);

-- Insertion des paramètres système par défaut
INSERT INTO SystemSettings (key, value, description) VALUES
('telegram_bot_token', '', 'Token du bot Telegram'),
('telegram_chat_id', '', 'ID du chat Telegram par défaut'),
('smtp_server', 'smtp.gmail.com', 'Serveur SMTP'),
('smtp_port', '587', 'Port SMTP'),
('smtp_username', '', 'Nom d utilisateur SMTP'),
('smtp_password', '', 'Mot de passe SMTP'),
('smtp_from', '', 'Adresse email expéditeur'),
('backup_frequency', '86400', 'Fréquence de sauvegarde en secondes (24h)'),
('video_retention_days', '90', 'Durée de conservation des vidéos en jours'),
('skeleton_retention_days', '30', 'Durée de conservation des trames squelette en jours'),
('log_retention_days', '365', 'Durée de conservation des logs en jours'),
('max_alert_retry', '3', 'Nombre maximum de tentatives d envoi d alerte'),
('alert_retry_delay', '60', 'Délai entre tentatives d envoi d alerte en secondes'),
('session_timeout', '300', 'Délai d expiration de session en secondes (5min)'),
('enable_telegram', '1', 'Activer les notifications Telegram (0/1)'),
('enable_email', '1', 'Activer les notifications email (0/1)'),
('enable_sms', '0', 'Activer les notifications SMS (0/1)'),
('enable_push', '0', 'Activer les notifications push (0/1)'),
('critical_alert_timeout', '300', 'Délai d escalade alerte critique en secondes (5min)'),
('high_alert_timeout', '600', 'Délai d escalade alerte haute en secondes (10min)'),
('medium_alert_timeout', '1800', 'Délai d escalade alerte moyenne en secondes (30min)'),
('low_alert_timeout', '3600', 'Délai d escalade alerte basse en secondes (1h)');

-- ============================================================================
-- Fin du schéma
-- ============================================================================
