-- ============================================================================
-- Système de Détection de Chutes par Edge AI
-- Vues SQL Utiles
-- Version: 1.0
-- ============================================================================

-- ============================================================================
-- VUE 1: Vue complète des patients avec leurs informations utilisateur
-- ============================================================================
CREATE VIEW View_Patients_Complet AS
SELECT 
    p.id AS patient_id,
    u.firstname,
    u.lastname,
    u.email,
    u.phone,
    p.age,
    p.gender,
    p.weight,
    p.height,
    p.mobility_level,
    p.medical_notes,
    p.address,
    p.latitude,
    p.longitude,
    u.status AS user_status,
    u.role
FROM Patients p
JOIN Users u ON p.user_id = u.id;

-- ============================================================================
-- VUE 2: Vue des contacts d'urgence par patient
-- ============================================================================
CREATE VIEW View_Contacts_Urgence AS
SELECT 
    p.id AS patient_id,
    u.firstname AS patient_firstname,
    u.lastname AS patient_lastname,
    ec.id AS contact_id,
    ec.fullname,
    ec.relationship,
    ec.phone,
    ec.email,
    ec.priority
FROM Patients p
JOIN Users u ON p.user_id = u.id
JOIN EmergencyContacts ec ON p.id = ec.patient_id
ORDER BY p.id, ec.priority;

-- ============================================================================
-- VUE 3: Vue des caméras avec informations de pièce et patient
-- ============================================================================
CREATE VIEW View_Cameras_Detail AS
SELECT 
    c.id AS camera_id,
    c.camera_name,
    c.ip_address,
    c.rtsp_url,
    c.resolution,
    c.fps,
    c.status AS camera_status,
    c.installation_date,
    r.id AS room_id,
    r.room_name,
    r.floor,
    r.description AS room_description,
    p.id AS patient_id,
    u.firstname AS patient_firstname,
    u.lastname AS patient_lastname
FROM Cameras c
JOIN Rooms r ON c.room_id = r.id
JOIN Patients p ON r.patient_id = p.id
JOIN Users u ON p.user_id = u.id;

-- ============================================================================
-- VUE 4: Vue des sessions de surveillance actives
-- ============================================================================
CREATE VIEW View_Sessions_Actives AS
SELECT 
    ms.id AS session_id,
    ms.start_time,
    ms.end_time,
    ms.duration,
    ms.status,
    c.id AS camera_id,
    c.camera_name,
    c.ip_address,
    r.room_name,
    p.id AS patient_id,
    u.firstname AS patient_firstname,
    u.lastname AS patient_lastname
FROM MonitoringSessions ms
JOIN Cameras c ON ms.camera_id = c.id
JOIN Rooms r ON c.room_id = r.id
JOIN Patients p ON ms.patient_id = p.id
JOIN Users u ON p.user_id = u.id
WHERE ms.status = 'EN_COURS';

-- ============================================================================
-- VUE 5: Vue des chutes détectées avec détails
-- ============================================================================
CREATE VIEW View_Chutes_Detectees AS
SELECT 
    f.id AS fall_id,
    f.detection_time,
    f.trunk_angle,
    f.body_height,
    f.vertical_speed,
    f.acceleration,
    f.immobility_duration,
    f.floor_time,
    f.confidence_score,
    f.fall_score,
    f.severity_score,
    f.injury_probability,
    f.result,
    ms.id AS session_id,
    c.camera_name,
    r.room_name,
    p.id AS patient_id,
    u.firstname AS patient_firstname,
    u.lastname AS patient_lastname
FROM Falls f
JOIN MonitoringSessions ms ON f.session_id = ms.id
JOIN Cameras c ON ms.camera_id = c.id
JOIN Rooms r ON c.room_id = r.id
JOIN Patients p ON ms.patient_id = p.id
JOIN Users u ON p.user_id = u.id
ORDER BY f.detection_time DESC;

-- ============================================================================
-- VUE 6: Vue des alertes avec informations de chute
-- ============================================================================
CREATE VIEW View_Alertes_Actives AS
SELECT 
    a.id AS alert_id,
    a.alert_level,
    a.sent_at,
    a.acknowledged,
    a.response_time,
    f.id AS fall_id,
    f.detection_time,
    f.severity_score,
    f.injury_probability,
    f.result,
    p.id AS patient_id,
    u.firstname AS patient_firstname,
    u.lastname AS patient_lastname
FROM Alerts a
JOIN Falls f ON a.fall_id = f.id
JOIN MonitoringSessions ms ON f.session_id = ms.id
JOIN Patients p ON ms.patient_id = p.id
JOIN Users u ON p.user_id = u.id
WHERE a.acknowledged = 0
ORDER BY a.sent_at DESC;

-- ============================================================================
-- VUE 7: Vue des notifications par canal
-- ============================================================================
CREATE VIEW View_Notifications_Statut AS
SELECT 
    channel,
    status,
    COUNT(*) AS nombre,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Notifications), 2) AS pourcentage
FROM Notifications
GROUP BY channel, status
ORDER BY channel, status;

-- ============================================================================
-- VUE 8: Vue des statistiques de chutes par patient
-- ============================================================================
CREATE VIEW View_Statistiques_Chutes_Patient AS
SELECT 
    p.id AS patient_id,
    u.firstname AS patient_firstname,
    u.lastname AS patient_lastname,
    COUNT(f.id) AS total_chutes,
    SUM(CASE WHEN f.result = 'CHUTE_CONFIRMEE' THEN 1 ELSE 0 END) AS chutes_confirmees,
    SUM(CASE WHEN f.result = 'FAUX_POSITIF' THEN 1 ELSE 0 END) AS faux_positifs,
    AVG(f.severity_score) AS gravite_moyenne,
    AVG(f.injury_probability) AS blessure_probabilite_moyenne,
    MAX(f.detection_time) AS derniere_chute
FROM Patients p
JOIN Users u ON p.user_id = u.id
LEFT JOIN MonitoringSessions ms ON p.id = ms.patient_id
LEFT JOIN Falls f ON ms.id = f.session_id
GROUP BY p.id, u.firstname, u.lastname
ORDER BY total_chutes DESC;

-- ============================================================================
-- VUE 9: Vue des statistiques de chutes par pièce
-- ============================================================================
CREATE VIEW View_Statistiques_Chutes_Piece AS
SELECT 
    r.id AS room_id,
    r.room_name,
    r.floor,
    p.id AS patient_id,
    u.firstname AS patient_firstname,
    u.lastname AS patient_lastname,
    COUNT(f.id) AS total_chutes,
    SUM(CASE WHEN f.result = 'CHUTE_CONFIRMEE' THEN 1 ELSE 0 END) AS chutes_confirmees,
    AVG(f.severity_score) AS gravite_moyenne
FROM Rooms r
JOIN Patients p ON r.patient_id = p.id
JOIN Users u ON p.user_id = u.id
JOIN Cameras c ON r.id = c.room_id
JOIN MonitoringSessions ms ON c.id = ms.camera_id
LEFT JOIN Falls f ON ms.id = f.session_id
GROUP BY r.id, r.room_name, r.floor, p.id, u.firstname, u.lastname
ORDER BY total_chutes DESC;

-- ============================================================================
-- VUE 10: Vue du temps de réponse moyen par niveau d'alerte
-- ============================================================================
CREATE VIEW View_Temps_Reponse_Alerte AS
SELECT 
    alert_level,
    AVG(response_time) AS temps_reponse_moyen,
    MIN(response_time) AS temps_reponse_min,
    MAX(response_time) AS temps_reponse_max,
    COUNT(*) AS nombre_alertes
FROM Alerts
WHERE acknowledged = 1 AND response_time IS NOT NULL
GROUP BY alert_level
ORDER BY temps_reponse_moyen;

-- ============================================================================
-- VUE 11: Vue des sessions de surveillance par jour
-- ============================================================================
CREATE VIEW View_Sessions_Par_Jour AS
SELECT 
    DATE(start_time) AS date,
    COUNT(*) AS nombre_sessions,
    SUM(duration) AS duree_totale,
    AVG(duration) AS duree_moyenne,
    SUM(CASE WHEN status = 'TERMINEE' THEN 1 ELSE 0 END) AS sessions_terminees,
    SUM(CASE WHEN status = 'INTERROMPUE' THEN 1 ELSE 0 END) AS sessions_interrompues,
    SUM(CASE WHEN status = 'EN_COURS' THEN 1 ELSE 0 END) AS sessions_en_cours
FROM MonitoringSessions
GROUP BY DATE(start_time)
ORDER BY date DESC;

-- ============================================================================
-- VUE 12: Vue des chutes par jour
-- ============================================================================
CREATE VIEW View_Chutes_Par_Jour AS
SELECT 
    DATE(detection_time) AS date,
    COUNT(*) AS total_chutes,
    SUM(CASE WHEN result = 'CHUTE_CONFIRMEE' THEN 1 ELSE 0 END) AS chutes_confirmees,
    SUM(CASE WHEN result = 'FAUX_POSITIF' THEN 1 ELSE 0 END) AS faux_positifs,
    SUM(CASE WHEN result = 'INDETERMINE' THEN 1 ELSE 0 END) AS indetermines,
    AVG(severity_score) AS gravite_moyenne,
    AVG(injury_probability) AS blessure_probabilite_moyenne
FROM Falls
GROUP BY DATE(detection_time)
ORDER BY date DESC;

-- ============================================================================
-- VUE 13: Vue des performances de détection (KPIs)
-- ============================================================================
CREATE VIEW View_Performances_Detection AS
SELECT 
    calculated_at,
    accuracy,
    precision,
    recall,
    f1_score,
    false_positive_rate,
    false_negative_rate,
    mean_detection_time,
    mean_alert_time,
    uptime
FROM KPIs
ORDER BY calculated_at DESC
LIMIT 30;

-- ============================================================================
-- VUE 14: Vue des utilisateurs par rôle
-- ============================================================================
CREATE VIEW View_Utilisateurs_Par_Role AS
SELECT 
    role,
    COUNT(*) AS nombre_utilisateurs,
    SUM(CASE WHEN status = 'ACTIF' THEN 1 ELSE 0 END) AS actifs,
    SUM(CASE WHEN status = 'INACTIF' THEN 1 ELSE 0 END) AS inactifs,
    SUM(CASE WHEN status = 'SUSPENDU' THEN 1 ELSE 0 END) AS suspendus
FROM Users
GROUP BY role
ORDER BY nombre_utilisateurs DESC;

-- ============================================================================
-- VUE 15: Vue des caméras par statut
-- ============================================================================
CREATE VIEW View_Cameras_Par_Statut AS
SELECT 
    status,
    COUNT(*) AS nombre_cameras,
    COUNT(DISTINCT room_id) AS nombre_pieces,
    COUNT(DISTINCT patient_id) AS nombre_patients
FROM Cameras c
JOIN Rooms r ON c.room_id = r.id
GROUP BY status;

-- ============================================================================
-- VUE 16: Vue des logs d'audit récents
-- ============================================================================
CREATE VIEW View_Audit_Recents AS
SELECT 
    al.id,
    al.action,
    al.table_name,
    al.record_id,
    al.timestamp,
    u.firstname,
    u.lastname,
    u.email,
    al.ip_address
FROM AuditLogs al
LEFT JOIN Users u ON al.user_id = u.id
ORDER BY al.timestamp DESC
LIMIT 100;

-- ============================================================================
-- VUE 17: Vue des événements de sécurité
-- ============================================================================
CREATE VIEW View_Securite_Evenements AS
SELECT 
    sl.id,
    sl.event_type,
    sl.description,
    sl.success,
    sl.timestamp,
    u.firstname,
    u.lastname,
    u.email,
    sl.ip_address
FROM SecurityLogs sl
LEFT JOIN Users u ON sl.user_id = u.id
ORDER BY sl.timestamp DESC
LIMIT 100;

-- ============================================================================
-- VUE 18: Vue des tentatives de connexion échouées
-- ============================================================================
CREATE VIEW View_Connexions_Echouees AS
SELECT 
    sl.id,
    sl.event_type,
    sl.description,
    sl.timestamp,
    sl.ip_address,
    COUNT(*) OVER (PARTITION BY sl.ip_address ORDER BY sl.timestamp 
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS tentatives_consecutives
FROM SecurityLogs sl
WHERE sl.event_type = 'TENTATIVE_CONNEXION' AND sl.success = 0
ORDER BY sl.timestamp DESC;

-- ============================================================================
-- VUE 19: Vue des simulations et résultats
-- ============================================================================
CREATE VIEW View_Simulations_Resultats AS
SELECT 
    sv.id AS simulation_id,
    sv.filename,
    sv.description,
    sv.expected_result,
    sv.upload_date,
    sr.id AS result_id,
    sr.precision,
    sr.recall,
    sr.f1_score,
    sr.false_positive,
    sr.false_negative,
    sr.detection_time
FROM SimulationVideos sv
LEFT JOIN SimulationResults sr ON sv.id = sr.simulation_id
ORDER BY sv.upload_date DESC;

-- ============================================================================
-- VUE 20: Vue de l'historique des incidents pour une chute
-- ============================================================================
CREATE VIEW View_Historique_Incident AS
SELECT 
    ih.id AS history_id,
    ih.event_type,
    ih.description,
    ih.timestamp,
    f.id AS fall_id,
    f.detection_time,
    f.result,
    f.severity_score,
    p.id AS patient_id,
    u.firstname AS patient_firstname,
    u.lastname AS patient_lastname
FROM IncidentHistory ih
JOIN Falls f ON ih.fall_id = f.id
JOIN MonitoringSessions ms ON f.session_id = ms.id
JOIN Patients p ON ms.patient_id = p.id
JOIN Users u ON p.user_id = u.id
ORDER BY f.detection_time DESC, ih.timestamp;

-- ============================================================================
-- VUE 21: Vue des alertes non accusées par criticité
-- ============================================================================
CREATE VIEW View_Alertes_Non_Acusees AS
SELECT 
    a.alert_level,
    COUNT(*) AS nombre_alertes,
    MIN(a.sent_at) AS premiere_alerte,
    MAX(a.sent_at) AS derniere_alerte,
    AVG(julianday('now') - julianday(a.sent_at)) * 24 * 60 AS delai_moyen_minutes
FROM Alerts a
WHERE a.acknowledged = 0
GROUP BY a.alert_level
ORDER BY 
    CASE a.alert_level
        WHEN 'CRITIQUE' THEN 1
        WHEN 'HAUTE' THEN 2
        WHEN 'MOYENNE' THEN 3
        WHEN 'BASSE' THEN 4
    END;

-- ============================================================================
-- VUE 22: Vue des notifications échouées
-- ============================================================================
CREATE VIEW View_Notifications_Echouees AS
SELECT 
    n.id AS notification_id,
    n.channel,
    n.recipient,
    n.sent_time,
    a.alert_level,
    f.detection_time,
    p.id AS patient_id,
    u.firstname AS patient_firstname,
    u.lastname AS patient_lastname
FROM Notifications n
JOIN Alerts a ON n.alert_id = a.id
JOIN Falls f ON a.fall_id = f.id
JOIN MonitoringSessions ms ON f.session_id = ms.id
JOIN Patients p ON ms.patient_id = p.id
JOIN Users u ON p.user_id = u.id
WHERE n.status = 'EN_ECHEC'
ORDER BY n.sent_time DESC;

-- ============================================================================
-- VUE 23: Vue du résumé quotidien
-- ============================================================================
CREATE VIEW View_Resume_Quotidien AS
SELECT 
    DATE('now') AS date,
    (SELECT COUNT(*) FROM Users WHERE status = 'ACTIF') AS utilisateurs_actifs,
    (SELECT COUNT(*) FROM Patients) AS patients_total,
    (SELECT COUNT(*) FROM Cameras WHERE status = 'ACTIVE') AS cameras_actives,
    (SELECT COUNT(*) FROM MonitoringSessions WHERE status = 'EN_COURS') AS sessions_en_cours,
    (SELECT COUNT(*) FROM Falls WHERE DATE(detection_time) = DATE('now')) AS chutes_aujourdhui,
    (SELECT COUNT(*) FROM Alerts WHERE acknowledged = 0) AS alertes_en_attente,
    (SELECT COUNT(*) FROM Notifications WHERE status = 'EN_ECHEC') AS notifications_echouees,
    (SELECT uptime FROM KPIs ORDER BY calculated_at DESC LIMIT 1) AS uptime_systeme;

-- ============================================================================
-- VUE 24: Vue des patients à risque élevé
-- ============================================================================
CREATE VIEW View_Patients_Risque_Eleve AS
SELECT 
    p.id AS patient_id,
    u.firstname,
    u.lastname,
    p.age,
    p.mobility_level,
    COUNT(f.id) AS nombre_chutes,
    AVG(f.severity_score) AS gravite_moyenne,
    MAX(f.detection_time) AS derniere_chute
FROM Patients p
JOIN Users u ON p.user_id = u.id
LEFT JOIN MonitoringSessions ms ON p.id = ms.patient_id
LEFT JOIN Falls f ON ms.id = f.session_id AND f.result = 'CHUTE_CONFIRMEE'
WHERE f.detection_time >= datetime('now', '-30 days')
GROUP BY p.id, u.firstname, u.lastname, p.age, p.mobility_level
HAVING COUNT(f.id) >= 3 OR AVG(f.severity_score) >= 0.7
ORDER BY nombre_chutes DESC, gravite_moyenne DESC;

-- ============================================================================
-- VUE 25: Vue des statistiques de notification envoyées
-- ============================================================================
CREATE VIEW View_Statistiques_Notifications AS
SELECT 
    channel,
    COUNT(*) AS total_envoyees,
    SUM(CASE WHEN status = 'ENVOYE' THEN 1 ELSE 0 END) AS envoyees,
    SUM(CASE WHEN status = 'EN_ECHEC' THEN 1 ELSE 0 END) AS echouees,
    SUM(CASE WHEN status = 'EN_ATTENTE' THEN 1 ELSE 0 END) AS en_attente,
    ROUND(SUM(CASE WHEN status = 'ENVOYE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS taux_succes
FROM Notifications
GROUP BY channel
ORDER BY total_envoyees DESC;
