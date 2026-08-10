-- ============================================================================
-- Système de Détection de Chutes par Edge AI
-- Requêtes SQL Principales (CRUD et Statistiques)
-- Version: 1.0
-- ============================================================================

-- ============================================================================
-- REQUÊTES CRUD (Create, Read, Update, Delete)
-- ============================================================================

-- ============================================================================
-- USERS - CRUD
-- ============================================================================

-- CREATE: Ajouter un nouvel utilisateur (avec mot de passe)
INSERT INTO Users (firstname, lastname, email, password_hash, phone, role, status)
VALUES ('Jean', 'Dupont', 'jean.dupont@email.com', '$2b$12$hash', '+33612345678', 'ADMIN', 'ACTIF');

-- CREATE: Ajouter un nouvel utilisateur (sans mot de passe - pour compte temporaire ou invité)
INSERT INTO Users (firstname, lastname, email, phone, role, status)
VALUES ('Dr. Test', 'Medical', 'dr.test@medical.com', '+33699999999', 'MEDECIN', 'ACTIF');

-- READ: Lister tous les utilisateurs
SELECT * FROM Users;

-- READ: Récupérer un utilisateur par ID
SELECT * FROM Users WHERE id = 1;

-- READ: Récupérer un utilisateur par email
SELECT * FROM Users WHERE email = 'jean.dupont@email.com';

-- READ: Lister les utilisateurs actifs par rôle
SELECT * FROM Users WHERE status = 'ACTIF' AND role = 'ADMIN';

-- UPDATE: Mettre à jour un utilisateur
UPDATE Users 
SET firstname = 'Jean-Pierre', phone = '+33687654321', updated_at = datetime('now')
WHERE id = 1;

-- UPDATE: Désactiver un utilisateur
UPDATE Users 
SET status = 'INACTIF', updated_at = datetime('now')
WHERE id = 1;

-- DELETE: Supprimer un utilisateur (CASCADE supprimera les données liées)
DELETE FROM Users WHERE id = 1;

-- ============================================================================
-- PATIENTS - CRUD
-- ============================================================================

-- CREATE: Ajouter un nouveau patient
INSERT INTO Patients (user_id, age, gender, weight, height, mobility_level, medical_notes, address, latitude, longitude)
VALUES (1, 78, 'F', 62.5, 165.0, 'CANNE', 'Hypertension', '15 Rue de la Paix, Paris', 48.8684, 2.3441);

-- READ: Lister tous les patients avec informations utilisateur
SELECT p.*, u.firstname, u.lastname, u.email, u.phone
FROM Patients p
JOIN Users u ON p.user_id = u.id;

-- READ: Récupérer un patient par ID
SELECT * FROM Patients WHERE id = 1;

-- READ: Récupérer les patients par niveau de mobilité
SELECT * FROM Patients WHERE mobility_level = 'FAUTEUIL';

-- UPDATE: Mettre à jour un patient
UPDATE Patients 
SET age = 79, weight = 63.0, medical_notes = 'Hypertension, arthrite'
WHERE id = 1;

-- DELETE: Supprimer un patient
DELETE FROM Patients WHERE id = 1;

-- ============================================================================
-- EMERGENCY CONTACTS - CRUD
-- ============================================================================

-- CREATE: Ajouter un contact d'urgence
INSERT INTO EmergencyContacts (patient_id, fullname, relationship, phone, email, priority)
VALUES (1, 'Pierre Martin', 'Fils', '+33611111111', 'pierre.martin@email.com', 1);

-- READ: Lister les contacts d'un patient
SELECT * FROM EmergencyContacts WHERE patient_id = 1 ORDER BY priority;

-- READ: Récupérer le contact principal d'un patient
SELECT * FROM EmergencyContacts WHERE patient_id = 1 AND priority = 1;

-- UPDATE: Mettre à jour un contact
UPDATE EmergencyContacts 
SET phone = '+33699999999', email = 'new.email@email.com'
WHERE id = 1;

-- DELETE: Supprimer un contact
DELETE FROM EmergencyContacts WHERE id = 1;

-- ============================================================================
-- ROOMS - CRUD
-- ============================================================================

-- CREATE: Ajouter une pièce
INSERT INTO Rooms (patient_id, room_name, floor, description)
VALUES (1, 'Salon', 0, 'Pièce principale');

-- READ: Lister les pièces d'un patient
SELECT * FROM Rooms WHERE patient_id = 1;

-- READ: Lister toutes les pièces avec nom du patient
SELECT r.*, u.firstname, u.lastname
FROM Rooms r
JOIN Patients p ON r.patient_id = p.id
JOIN Users u ON p.user_id = u.id;

-- UPDATE: Mettre à jour une pièce
UPDATE Rooms 
SET description = 'Salon rénové avec canapé neuf'
WHERE id = 1;

-- DELETE: Supprimer une pièce
DELETE FROM Rooms WHERE id = 1;

-- ============================================================================
-- CAMERAS - CRUD
-- ============================================================================

-- CREATE: Ajouter une caméra
INSERT INTO Cameras (room_id, camera_name, ip_address, rtsp_url, resolution, fps, status)
VALUES (1, 'Caméra Salon', '192.168.1.101', 'rtsp://192.168.1.101:554/stream1', '1080p', 30, 'ACTIVE');

-- READ: Lister toutes les caméras
SELECT * FROM Cameras;

-- READ: Lister les caméras actives
SELECT * FROM Cameras WHERE status = 'ACTIVE';

-- READ: Lister les caméras d'une pièce
SELECT * FROM Cameras WHERE room_id = 1;

-- READ: Lister les caméras avec informations de pièce et patient
SELECT c.*, r.room_name, r.floor, u.firstname AS patient_firstname, u.lastname AS patient_lastname
FROM Cameras c
JOIN Rooms r ON c.room_id = r.id
JOIN Patients p ON r.patient_id = p.id
JOIN Users u ON p.user_id = u.id;

-- UPDATE: Mettre à jour une caméra
UPDATE Cameras 
SET status = 'MAINTENANCE', resolution = '720p'
WHERE id = 1;

-- UPDATE: Activer une caméra
UPDATE Cameras 
SET status = 'ACTIVE'
WHERE id = 1;

-- DELETE: Supprimer une caméra
DELETE FROM Cameras WHERE id = 1;

-- ============================================================================
-- MONITORING SESSIONS - CRUD
-- ============================================================================

-- CREATE: Démarrer une nouvelle session
INSERT INTO MonitoringSessions (camera_id, patient_id, start_time, status)
VALUES (1, 1, datetime('now'), 'EN_COURS');

-- READ: Lister toutes les sessions
SELECT * FROM MonitoringSessions;

-- READ: Lister les sessions actives
SELECT * FROM MonitoringSessions WHERE status = 'EN_COURS';

-- READ: Lister les sessions d'un patient
SELECT * FROM MonitoringSessions WHERE patient_id = 1;

-- READ: Lister les sessions avec détails
SELECT ms.*, c.camera_name, r.room_name, u.firstname AS patient_firstname, u.lastname AS patient_lastname
FROM MonitoringSessions ms
JOIN Cameras c ON ms.camera_id = c.id
JOIN Rooms r ON c.room_id = r.id
JOIN Patients p ON ms.patient_id = p.id
JOIN Users u ON p.user_id = u.id;

-- UPDATE: Terminer une session
UPDATE MonitoringSessions 
SET end_time = datetime('now'), 
    duration = CAST(strftime('%s', datetime('now')) - strftime('%s', start_time) AS INTEGER),
    status = 'TERMINEE'
WHERE id = 1;

-- UPDATE: Interrompre une session
UPDATE MonitoringSessions 
SET end_time = datetime('now'), 
    duration = CAST(strftime('%s', datetime('now')) - strftime('%s', start_time) AS INTEGER),
    status = 'INTERROMPUE'
WHERE id = 1;

-- DELETE: Supprimer une session
DELETE FROM MonitoringSessions WHERE id = 1;

-- ============================================================================
-- SKELETON FRAMES - CRUD
-- ============================================================================

-- CREATE: Ajouter une trame squelette
INSERT INTO SkeletonFrames (session_id, timestamp, frame_number, 
    nose_x, nose_y, nose_z,
    left_shoulder_x, left_shoulder_y, left_shoulder_z,
    right_shoulder_x, right_shoulder_y, right_shoulder_z,
    left_elbow_x, left_elbow_y, left_elbow_z,
    right_elbow_x, right_elbow_y, right_elbow_z,
    left_wrist_x, left_wrist_y, left_wrist_z,
    right_wrist_x, right_wrist_y, right_wrist_z,
    left_hip_x, left_hip_y, left_hip_z,
    right_hip_x, right_hip_y, right_hip_z,
    left_knee_x, left_knee_y, left_knee_z,
    right_knee_x, right_knee_y, right_knee_z,
    left_ankle_x, left_ankle_y, left_ankle_z,
    right_ankle_x, right_ankle_y, right_ankle_z)
VALUES (1, datetime('now'), 1, 0.5, 0.3, 0.8, 0.4, 0.5, 0.7, 0.6, 0.5, 0.7, 0.35, 0.6, 0.6, 0.65, 0.6, 0.6, 0.3, 0.7, 0.5, 0.7, 0.7, 0.5, 0.45, 0.6, 0.8, 0.55, 0.6, 0.8, 0.4, 0.75, 0.7, 0.6, 0.75, 0.7, 0.35, 0.85, 0.6, 0.65, 0.85, 0.6);

-- READ: Lister les trames d'une session
SELECT * FROM SkeletonFrames WHERE session_id = 1 ORDER BY timestamp;

-- READ: Récupérer les N dernières trames d'une session
SELECT * FROM SkeletonFrames 
WHERE session_id = 1 
ORDER BY timestamp DESC 
LIMIT 100;

-- READ: Récupérer les trames sur une période
SELECT * FROM SkeletonFrames 
WHERE session_id = 1 
AND timestamp BETWEEN '2026-01-15 08:00:00' AND '2026-01-15 18:00:00'
ORDER BY timestamp;

-- DELETE: Supprimer les anciennes trames (archivage)
DELETE FROM SkeletonFrames 
WHERE timestamp < datetime('now', '-30 days');

-- ============================================================================
-- FALLS - CRUD
-- ============================================================================

-- CREATE: Enregistrer une chute détectée
INSERT INTO Falls (session_id, detection_time, trunk_angle, body_height, vertical_speed, acceleration, 
    center_gravity_x, center_gravity_y, center_gravity_speed, immobility_duration, floor_time, 
    kinetic_energy, confidence_score, fall_score, severity_score, injury_probability, result)
VALUES (1, datetime('now'), 85.5, 1200.0, 3.2, 8.5, 0.5, 0.85, 2.8, 45.0, 120.0, 450.5, 0.95, 0.92, 0.88, 75.0, 'CHUTE_CONFIRMEE');

-- READ: Lister toutes les chutes
SELECT * FROM Falls ORDER BY detection_time DESC;

-- READ: Lister les chutes confirmées
SELECT * FROM Falls WHERE result = 'CHUTE_CONFIRMEE' ORDER BY detection_time DESC;

-- READ: Lister les chutes d'un patient
SELECT f.* 
FROM Falls f
JOIN MonitoringSessions ms ON f.session_id = ms.id
WHERE ms.patient_id = 1
ORDER BY f.detection_time DESC;

-- READ: Lister les chutes avec détails
SELECT f.*, ms.id AS session_id, c.camera_name, r.room_name, 
       u.firstname AS patient_firstname, u.lastname AS patient_lastname
FROM Falls f
JOIN MonitoringSessions ms ON f.session_id = ms.id
JOIN Cameras c ON ms.camera_id = c.id
JOIN Rooms r ON c.room_id = r.id
JOIN Patients p ON ms.patient_id = p.id
JOIN Users u ON p.user_id = u.id
ORDER BY f.detection_time DESC;

-- READ: Récupérer les chutes sur une période
SELECT * FROM Falls 
WHERE detection_time BETWEEN '2026-01-01' AND '2026-01-31'
ORDER BY detection_time DESC;

-- UPDATE: Mettre à jour le résultat d'une chute
UPDATE Falls 
SET result = 'CHUTE_CONFIRMEE', severity_score = 0.90
WHERE id = 1;

-- DELETE: Supprimer une chute
DELETE FROM Falls WHERE id = 1;

-- ============================================================================
-- ALERTS - CRUD
-- ============================================================================

-- CREATE: Créer une alerte
INSERT INTO Alerts (fall_id, alert_level, sent_at, acknowledged)
VALUES (1, 'CRITIQUE', datetime('now'), 0);

-- READ: Lister toutes les alertes
SELECT * FROM Alerts ORDER BY sent_at DESC;

-- READ: Lister les alertes non accusées
SELECT * FROM Alerts WHERE acknowledged = 0 ORDER BY sent_at DESC;

-- READ: Lister les alertes critiques
SELECT * FROM Alerts WHERE alert_level = 'CRITIQUE' AND acknowledged = 0;

-- READ: Lister les alertes avec détails
SELECT a.*, f.detection_time, f.severity_score, f.result,
       u.firstname AS patient_firstname, u.lastname AS patient_lastname
FROM Alerts a
JOIN Falls f ON a.fall_id = f.id
JOIN MonitoringSessions ms ON f.session_id = ms.id
JOIN Patients p ON ms.patient_id = p.id
JOIN Users u ON p.user_id = u.id
ORDER BY a.sent_at DESC;

-- UPDATE: Accuser réception d'une alerte
UPDATE Alerts 
SET acknowledged = 1, response_time = CAST(strftime('%s', datetime('now')) - strftime('%s', sent_at) AS INTEGER)
WHERE id = 1;

-- DELETE: Supprimer une alerte
DELETE FROM Alerts WHERE id = 1;

-- ============================================================================
-- NOTIFICATIONS - CRUD
-- ============================================================================

-- CREATE: Créer une notification
INSERT INTO Notifications (alert_id, channel, recipient, status, sent_time)
VALUES (1, 'TELEGRAM', 'pierre.martin@email.com', 'ENVOYE', datetime('now'));

-- READ: Lister toutes les notifications
SELECT * FROM Notifications ORDER BY sent_time DESC;

-- READ: Lister les notifications en attente
SELECT * FROM Notifications WHERE status = 'EN_ATTENTE';

-- READ: Lister les notifications échouées
SELECT * FROM Notifications WHERE status = 'EN_ECHEC' ORDER BY sent_time DESC;

-- READ: Lister les notifications par canal
SELECT * FROM Notifications WHERE channel = 'TELEGRAM';

-- UPDATE: Marquer une notification comme envoyée
UPDATE Notifications 
SET status = 'ENVOYE', sent_time = datetime('now')
WHERE id = 1;

-- UPDATE: Marquer une notification comme échouée
UPDATE Notifications 
SET status = 'EN_ECHEC', sent_time = datetime('now')
WHERE id = 1;

-- DELETE: Supprimer une notification
DELETE FROM Notifications WHERE id = 1;

-- ============================================================================
-- AI SETTINGS - CRUD
-- ============================================================================

-- READ: Récupérer les paramètres IA actuels
SELECT * FROM AISettings LIMIT 1;

-- UPDATE: Mettre à jour un seuil
UPDATE AISettings 
SET threshold_angle = 50.0, modified_at = datetime('now')
WHERE id = 1;

-- UPDATE: Mettre à jour une pondération
UPDATE AISettings 
SET weight_angle = 0.25, weight_speed = 0.20, modified_at = datetime('now')
WHERE id = 1;

-- UPDATE: Réinitialiser aux valeurs par défaut
UPDATE AISettings 
SET threshold_angle = 45.0,
    threshold_speed = 2.0,
    threshold_acceleration = 5.0,
    threshold_immobility = 30.0,
    threshold_floor_time = 60.0,
    threshold_severity = 0.7,
    weight_angle = 0.2,
    weight_speed = 0.25,
    weight_acceleration = 0.2,
    weight_immobility = 0.15,
    weight_floor_time = 0.2,
    modified_at = datetime('now')
WHERE id = 1;

-- ============================================================================
-- SYSTEM SETTINGS - CRUD
-- ============================================================================

-- CREATE: Ajouter un paramètre système
INSERT INTO SystemSettings (key, value, description)
VALUES ('new_param', 'value', 'Description du paramètre');

-- READ: Récupérer tous les paramètres système
SELECT * FROM SystemSettings;

-- READ: Récupérer un paramètre par clé
SELECT * FROM SystemSettings WHERE key = 'telegram_bot_token';

-- UPDATE: Mettre à jour un paramètre
UPDATE SystemSettings 
SET value = 'new_value', modified_at = datetime('now')
WHERE key = 'telegram_bot_token';

-- DELETE: Supprimer un paramètre
DELETE FROM SystemSettings WHERE key = 'new_param';

-- ============================================================================
-- REQUÊTES STATISTIQUES
-- ============================================================================

-- ============================================================================
-- STATISTIQUES GÉNÉRALES
-- ============================================================================

-- Nombre total d'utilisateurs par rôle
SELECT role, COUNT(*) AS count 
FROM Users 
GROUP BY role;

-- Nombre total de patients
SELECT COUNT(*) AS total_patients FROM Patients;

-- Nombre de patients par niveau de mobilité
SELECT mobility_level, COUNT(*) AS count 
FROM Patients 
GROUP BY mobility_level;

-- Nombre total de caméras par statut
SELECT status, COUNT(*) AS count 
FROM Cameras 
GROUP BY status;

-- Nombre total de sessions par statut
SELECT status, COUNT(*) AS count 
FROM MonitoringSessions 
GROUP BY status;

-- ============================================================================
-- STATISTIQUES DE CHUTES
-- ============================================================================

-- Nombre total de chutes par résultat
SELECT result, COUNT(*) AS count 
FROM Falls 
GROUP BY result;

-- Nombre de chutes par patient
SELECT p.id, u.firstname, u.lastname, COUNT(f.id) AS fall_count
FROM Patients p
JOIN Users u ON p.user_id = u.id
LEFT JOIN MonitoringSessions ms ON p.id = ms.patient_id
LEFT JOIN Falls f ON ms.id = f.session_id
GROUP BY p.id, u.firstname, u.lastname
ORDER BY fall_count DESC;

-- Nombre de chutes par jour (30 derniers jours)
SELECT DATE(detection_time) AS date, COUNT(*) AS fall_count
FROM Falls
WHERE detection_time >= datetime('now', '-30 days')
GROUP BY DATE(detection_time)
ORDER BY date DESC;

-- Gravité moyenne des chutes par patient
SELECT p.id, u.firstname, u.lastname, AVG(f.severity_score) AS avg_severity
FROM Patients p
JOIN Users u ON p.user_id = u.id
LEFT JOIN MonitoringSessions ms ON p.id = ms.patient_id
LEFT JOIN Falls f ON ms.id = f.session_id AND f.result = 'CHUTE_CONFIRMEE'
GROUP BY p.id, u.firstname, u.lastname
HAVING AVG(f.severity_score) IS NOT NULL
ORDER BY avg_severity DESC;

-- Distribution des niveaux de gravité
SELECT 
    CASE 
        WHEN severity_score >= 0.8 THEN 'CRITIQUE'
        WHEN severity_score >= 0.6 THEN 'HAUTE'
        WHEN severity_score >= 0.4 THEN 'MOYENNE'
        ELSE 'BASSE'
    END AS severity_level,
    COUNT(*) AS count
FROM Falls
WHERE result = 'CHUTE_CONFIRMEE'
GROUP BY severity_level;

-- ============================================================================
-- STATISTIQUES D'ALERTES
-- ============================================================================

-- Nombre d'alertes par niveau
SELECT alert_level, COUNT(*) AS count 
FROM Alerts 
GROUP BY alert_level;

-- Taux d'alertes accusées
SELECT 
    COUNT(*) AS total_alerts,
    SUM(CASE WHEN acknowledged = 1 THEN 1 ELSE 0 END) AS acknowledged_alerts,
    ROUND(SUM(CASE WHEN acknowledged = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS acknowledgment_rate
FROM Alerts;

-- Temps de réponse moyen par niveau d'alerte
SELECT alert_level, AVG(response_time) AS avg_response_time
FROM Alerts
WHERE acknowledged = 1 AND response_time IS NOT NULL
GROUP BY alert_level;

-- Nombre d'alertes non accusées par niveau
SELECT alert_level, COUNT(*) AS unacknowledged_count
FROM Alerts
WHERE acknowledged = 0
GROUP BY alert_level;

-- ============================================================================
-- STATISTIQUES DE NOTIFICATIONS
-- ============================================================================

-- Nombre de notifications par canal
SELECT channel, COUNT(*) AS count 
FROM Notifications 
GROUP BY channel;

-- Taux de succès des notifications par canal
SELECT 
    channel,
    COUNT(*) AS total,
    SUM(CASE WHEN status = 'ENVOYE' THEN 1 ELSE 0 END) AS sent,
    SUM(CASE WHEN status = 'EN_ECHEC' THEN 1 ELSE 0 END) AS failed,
    ROUND(SUM(CASE WHEN status = 'ENVOYE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate
FROM Notifications
GROUP BY channel;

-- Notifications en attente par canal
SELECT channel, COUNT(*) AS pending_count
FROM Notifications
WHERE status = 'EN_ATTENTE'
GROUP BY channel;

-- ============================================================================
-- STATISTIQUES DE SESSIONS
-- ============================================================================

-- Durée moyenne des sessions par patient
SELECT p.id, u.firstname, u.lastname, AVG(ms.duration) AS avg_duration
FROM Patients p
JOIN Users u ON p.user_id = u.id
JOIN MonitoringSessions ms ON p.id = ms.patient_id
WHERE ms.duration IS NOT NULL
GROUP BY p.id, u.firstname, u.lastname;

-- Nombre d'heures de surveillance par jour
SELECT DATE(start_time) AS date, SUM(duration) / 3600.0 AS total_hours
FROM MonitoringSessions
WHERE duration IS NOT NULL
GROUP BY DATE(start_time)
ORDER BY date DESC;

-- Taux de sessions interrompues
SELECT 
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN status = 'INTERROMPUE' THEN 1 ELSE 0 END) AS interrupted,
    SUM(CASE WHEN status = 'TERMINEE' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status = 'EN_COURS' THEN 1 ELSE 0 END) AS active,
    ROUND(SUM(CASE WHEN status = 'INTERROMPUE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS interruption_rate
FROM MonitoringSessions;

-- ============================================================================
-- STATISTIQUES DE PERFORMANCE (KPIs)
-- ============================================================================

-- Derniers KPIs calculés
SELECT * FROM KPIs ORDER BY calculated_at DESC LIMIT 10;

-- Évolution de l'accuracy sur 30 jours
SELECT calculated_at, accuracy
FROM KPIs
WHERE calculated_at >= datetime('now', '-30 days')
ORDER BY calculated_at;

-- Évolution du F1-score sur 30 jours
SELECT calculated_at, f1_score
FROM KPIs
WHERE calculated_at >= datetime('now', '-30 days')
ORDER BY calculated_at;

-- ============================================================================
-- STATISTIQUES DE SIMULATION
-- ============================================================================

-- Résultats de simulation par vidéo
SELECT sv.filename, sv.expected_result, sr.precision, sr.recall, sr.f1_score, sr.detection_time
FROM SimulationVideos sv
LEFT JOIN SimulationResults sr ON sv.id = sr.simulation_id
ORDER BY sv.upload_date DESC;

-- Moyenne des métriques de simulation
SELECT 
    AVG(precision) AS avg_precision,
    AVG(recall) AS avg_recall,
    AVG(f1_score) AS avg_f1,
    AVG(detection_time) AS avg_detection_time,
    SUM(false_positive) AS total_false_positives,
    SUM(false_negative) AS total_false_negatives
FROM SimulationResults;

-- ============================================================================
-- STATISTIQUES DE SÉCURITÉ
-- ============================================================================

-- Tentatives de connexion par jour
SELECT DATE(timestamp) AS date, 
       COUNT(*) AS total_attempts,
       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) AS successful,
       SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) AS failed
FROM SecurityLogs
WHERE event_type = 'TENTATIVE_CONNEXION'
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Événements de sécurité par type
SELECT event_type, COUNT(*) AS count
FROM SecurityLogs
GROUP BY event_type;

-- Tentatives échouées par adresse IP
SELECT ip_address, COUNT(*) AS failed_attempts
FROM SecurityLogs
WHERE success = 0 AND event_type = 'TENTATIVE_CONNEXION'
GROUP BY ip_address
HAVING COUNT(*) >= 3
ORDER BY failed_attempts DESC;

-- ============================================================================
-- REQUÊTES DE RAPPORT
-- ============================================================================

-- Rapport quotidien complet
SELECT 
    DATE('now') AS date,
    (SELECT COUNT(*) FROM Users WHERE status = 'ACTIF') AS active_users,
    (SELECT COUNT(*) FROM Patients) AS total_patients,
    (SELECT COUNT(*) FROM Cameras WHERE status = 'ACTIVE') AS active_cameras,
    (SELECT COUNT(*) FROM MonitoringSessions WHERE status = 'EN_COURS') AS active_sessions,
    (SELECT COUNT(*) FROM Falls WHERE DATE(detection_time) = DATE('now')) AS falls_today,
    (SELECT COUNT(*) FROM Alerts WHERE acknowledged = 0) AS pending_alerts,
    (SELECT COUNT(*) FROM Notifications WHERE status = 'EN_ECHEC') AS failed_notifications,
    (SELECT uptime FROM KPIs ORDER BY calculated_at DESC LIMIT 1) AS system_uptime;

-- Rapport hebdomadaire des chutes
SELECT 
    strftime('%Y-%W', detection_time) AS week,
    COUNT(*) AS total_falls,
    SUM(CASE WHEN result = 'CHUTE_CONFIRMEE' THEN 1 ELSE 0 END) AS confirmed_falls,
    SUM(CASE WHEN result = 'FAUX_POSITIF' THEN 1 ELSE 0 END) AS false_positives,
    AVG(severity_score) AS avg_severity,
    AVG(injury_probability) AS avg_injury_probability
FROM Falls
WHERE detection_time >= datetime('now', '-7 days')
GROUP BY strftime('%Y-%W', detection_time);

-- Rapport mensuel des performances
SELECT 
    strftime('%Y-%m', calculated_at) AS month,
    AVG(accuracy) AS avg_accuracy,
    AVG(precision) AS avg_precision,
    AVG(recall) AS avg_recall,
    AVG(f1_score) AS avg_f1,
    AVG(mean_detection_time) AS avg_detection_time,
    AVG(uptime) AS avg_uptime
FROM KPIs
WHERE calculated_at >= datetime('now', '-30 days')
GROUP BY strftime('%Y-%m', calculated_at);

-- ============================================================================
-- REQUÊTES DE RECHERCHE
-- ============================================================================

-- Rechercher des chutes par plage de gravité
SELECT * FROM Falls
WHERE severity_score BETWEEN 0.7 AND 1.0
ORDER BY severity_score DESC;

-- Rechercher des chutes par plage de dates
SELECT * FROM Falls
WHERE detection_time BETWEEN '2026-01-01' AND '2026-01-31'
ORDER BY detection_time DESC;

-- Rechercher des patients par nom
SELECT p.*, u.firstname, u.lastname
FROM Patients p
JOIN Users u ON p.user_id = u.id
WHERE u.lastname LIKE '%Martin%';

-- Rechercher des caméras par adresse IP
SELECT * FROM Cameras WHERE ip_address LIKE '192.168.1.%';

-- ============================================================================
-- REQUÊTES D'ANALYSE AVANCÉE
-- ============================================================================

-- Analyse des patterns de chutes par heure de la journée
SELECT 
    strftime('%H', detection_time) AS hour,
    COUNT(*) AS fall_count,
    AVG(severity_score) AS avg_severity
FROM Falls
WHERE result = 'CHUTE_CONFIRMEE'
GROUP BY strftime('%H', detection_time)
ORDER BY hour;

-- Analyse des chutes par pièce
SELECT 
    r.room_name,
    COUNT(f.id) AS fall_count,
    AVG(f.severity_score) AS avg_severity
FROM Falls f
JOIN MonitoringSessions ms ON f.session_id = ms.id
JOIN Cameras c ON ms.camera_id = c.id
JOIN Rooms r ON c.room_id = r.id
WHERE f.result = 'CHUTE_CONFIRMEE'
GROUP BY r.room_name
ORDER BY fall_count DESC;

-- Corrélation entre mobilité et nombre de chutes
SELECT 
    p.mobility_level,
    COUNT(f.id) AS fall_count,
    AVG(f.severity_score) AS avg_severity
FROM Patients p
LEFT JOIN MonitoringSessions ms ON p.id = ms.patient_id
LEFT JOIN Falls f ON ms.id = f.session_id AND f.result = 'CHUTE_CONFIRMEE'
GROUP BY p.mobility_level
ORDER BY fall_count DESC;

-- Analyse des temps de réponse par canal de notification
SELECT 
    n.channel,
    AVG(a.response_time) AS avg_response_time,
    COUNT(*) AS alert_count
FROM Notifications n
JOIN Alerts a ON n.alert_id = a.id
WHERE a.acknowledged = 1 AND a.response_time IS NOT NULL
GROUP BY n.channel;

-- ============================================================================
-- REQUÊTES DE MAINTENANCE
-- ============================================================================

-- Vérifier l'intégrité de la base de données
PRAGMA integrity_check;

-- Vérifier les clés étrangères
PRAGMA foreign_key_check;

-- Analyser les tables pour l'optimisation
ANALYZE;

-- Vérifier la taille de la base de données
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();

-- Lister les tables et leur nombre d'enregistrements
SELECT name, (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=main.name) as row_count
FROM sqlite_master WHERE type='table';

-- ============================================================================
-- Fin des requêtes SQL principales
-- ============================================================================
