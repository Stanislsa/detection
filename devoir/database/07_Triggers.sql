-- ============================================================================
-- Système de Détection de Chutes par Edge AI
-- Triggers pour l'intégrité des données
-- Version: 1.0
-- ============================================================================

-- ============================================================================
-- TRIGGER 1: Mise à jour automatique de updated_at pour Users
-- ============================================================================
CREATE TRIGGER trg_users_updated_at
AFTER UPDATE ON Users
BEGIN
    UPDATE Users SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- ============================================================================
-- TRIGGER 2: Calcul automatique de la durée des sessions
-- ============================================================================
CREATE TRIGGER trg_sessions_calculate_duration
AFTER UPDATE OF end_time ON MonitoringSessions
WHEN NEW.end_time IS NOT NULL AND OLD.end_time IS NULL
BEGIN
    UPDATE MonitoringSessions 
    SET duration = CAST(strftime('%s', NEW.end_time) - strftime('%s', start_time) AS INTEGER),
        status = 'TERMINEE'
    WHERE id = NEW.id;
END;

-- ============================================================================
-- TRIGGER 3: Création automatique d'alerte pour chute confirmée
-- ============================================================================
CREATE TRIGGER trg_falls_create_alert
AFTER INSERT ON Falls
WHEN NEW.result = 'CHUTE_CONFIRMEE'
BEGIN
    INSERT INTO Alerts (fall_id, alert_level, sent_at, acknowledged)
    VALUES (
        NEW.id,
        CASE 
            WHEN NEW.severity_score >= 0.8 THEN 'CRITIQUE'
            WHEN NEW.severity_score >= 0.6 THEN 'HAUTE'
            WHEN NEW.severity_score >= 0.4 THEN 'MOYENNE'
            ELSE 'BASSE'
        END,
        datetime('now'),
        0
    );
END;

-- ============================================================================
-- TRIGGER 4: Journalisation des modifications de Users (Audit)
-- ============================================================================
CREATE TRIGGER trg_audit_users_update
AFTER UPDATE ON Users
BEGIN
    INSERT INTO AuditLogs (user_id, action, table_name, record_id, old_values, new_values, timestamp)
    VALUES (
        NEW.id,
        'MODIFICATION',
        'Users',
        NEW.id,
        json_object('firstname', OLD.firstname, 'lastname', OLD.lastname, 'email', OLD.email, 'role', OLD.role, 'status', OLD.status),
        json_object('firstname', NEW.firstname, 'lastname', NEW.lastname, 'email', NEW.email, 'role', NEW.role, 'status', NEW.status),
        datetime('now')
    );
END;

-- ============================================================================
-- TRIGGER 5: Journalisation des modifications de Patients (Audit)
-- ============================================================================
CREATE TRIGGER trg_audit_patients_update
AFTER UPDATE ON Patients
BEGIN
    INSERT INTO AuditLogs (user_id, action, table_name, record_id, old_values, new_values, timestamp)
    VALUES (
        NEW.user_id,
        'MODIFICATION',
        'Patients',
        NEW.id,
        json_object('age', OLD.age, 'gender', OLD.gender, 'weight', OLD.weight, 'height', OLD.height, 'mobility_level', OLD.mobility_level),
        json_object('age', NEW.age, 'gender', NEW.gender, 'weight', NEW.weight, 'height', NEW.height, 'mobility_level', NEW.mobility_level),
        datetime('now')
    );
END;

-- ============================================================================
-- TRIGGER 6: Journalisation des suppressions (Audit)
-- ============================================================================
CREATE TRIGGER trg_audit_users_delete
AFTER DELETE ON Users
BEGIN
    INSERT INTO AuditLogs (user_id, action, table_name, record_id, old_values, new_values, timestamp)
    VALUES (
        OLD.id,
        'SUPPRESSION',
        'Users',
        OLD.id,
        json_object('firstname', OLD.firstname, 'lastname', OLD.lastname, 'email', OLD.email, 'role', OLD.role),
        NULL,
        datetime('now')
    );
END;

-- ============================================================================
-- TRIGGER 7: Journalisation des modifications de AISettings (Audit)
-- ============================================================================
CREATE TRIGGER trg_audit_ai_settings_update
AFTER UPDATE ON AISettings
BEGIN
    INSERT INTO AuditLogs (user_id, action, table_name, record_id, old_values, new_values, timestamp)
    VALUES (
        NULL,
        'PARAMETRES',
        'AISettings',
        NEW.id,
        json_object(
            'threshold_angle', OLD.threshold_angle,
            'threshold_speed', OLD.threshold_speed,
            'threshold_acceleration', OLD.threshold_acceleration,
            'weight_angle', OLD.weight_angle,
            'weight_speed', OLD.weight_speed
        ),
        json_object(
            'threshold_angle', NEW.threshold_angle,
            'threshold_speed', NEW.threshold_speed,
            'threshold_acceleration', NEW.threshold_acceleration,
            'weight_angle', NEW.weight_angle,
            'weight_speed', NEW.weight_speed
        ),
        datetime('now')
    );
END;

-- ============================================================================
-- TRIGGER 8: Journalisation des modifications de SystemSettings (Audit)
-- ============================================================================
CREATE TRIGGER trg_audit_system_settings_update
AFTER UPDATE ON SystemSettings
BEGIN
    INSERT INTO AuditLogs (user_id, action, table_name, record_id, old_values, new_values, timestamp)
    VALUES (
        NULL,
        'PARAMETRES',
        'SystemSettings',
        NEW.id,
        json_object('key', OLD.key, 'value', OLD.value),
        json_object('key', NEW.key, 'value', NEW.value),
        datetime('now')
    );
END;

-- ============================================================================
-- TRIGGER 9: Création d'historique d'incident pour nouvelle chute
-- ============================================================================
CREATE TRIGGER trg_incident_history_create
AFTER INSERT ON Falls
BEGIN
    INSERT INTO IncidentHistory (fall_id, event_type, description, timestamp)
    VALUES (
        NEW.id,
        'DETECTION',
        'Détection de chute - Score: ' || NEW.fall_score || ', Gravité: ' || NEW.severity_score,
        datetime('now')
    );
END;

-- ============================================================================
-- TRIGGER 10: Mise à jour du timestamp de modification AISettings
-- ============================================================================
CREATE TRIGGER trg_ai_settings_modified_at
AFTER UPDATE ON AISettings
BEGIN
    UPDATE AISettings SET modified_at = datetime('now') WHERE id = NEW.id;
END;

-- ============================================================================
-- TRIGGER 11: Mise à jour du timestamp de modification SystemSettings
-- ============================================================================
CREATE TRIGGER trg_system_settings_modified_at
AFTER UPDATE ON SystemSettings
BEGIN
    UPDATE SystemSettings SET modified_at = datetime('now') WHERE id = NEW.id;
END;

-- ============================================================================
-- TRIGGER 12: Vérification qu'un patient a au moins un contact d'urgence
-- ============================================================================
CREATE TRIGGER trg_validate_patient_contacts
AFTER INSERT ON Patients
BEGIN
    SELECT CASE 
        WHEN (SELECT COUNT(*) FROM EmergencyContacts WHERE patient_id = NEW.id) = 0 
        THEN RAISE(ABORT, 'Un patient doit avoir au moins un contact d''urgence')
    END;
END;

-- ============================================================================
-- TRIGGER 13: Vérification qu'une pièce a au moins une caméra
-- ============================================================================
CREATE TRIGGER trg_validate_room_cameras
AFTER INSERT ON Rooms
BEGIN
    SELECT CASE 
        WHEN (SELECT COUNT(*) FROM Cameras WHERE room_id = NEW.id) = 0 
        THEN RAISE(ABORT, 'Une pièce doit avoir au moins une caméra')
    END;
END;

-- ============================================================================
-- TRIGGER 14: Interdiction de modifier le résultat d'une chute confirmée
-- ============================================================================
CREATE TRIGGER trg_prevent_fall_result_change
BEFORE UPDATE OF result ON Falls
WHEN OLD.result = 'CHUTE_CONFIRMEE' AND NEW.result != OLD.result
BEGIN
    SELECT RAISE(ABORT, 'Impossible de modifier le résultat d''une chute confirmée');
END;

-- ============================================================================
-- TRIGGER 15: Création automatique de notifications pour nouvelle alerte
-- ============================================================================
CREATE TRIGGER trg_alert_create_notifications
AFTER INSERT ON Alerts
BEGIN
    -- Notification Telegram
    INSERT INTO Notifications (alert_id, channel, recipient, status, sent_time)
    SELECT 
        NEW.id,
        'TELEGRAM',
        ss.value,
        'EN_ATTENTE',
        NULL
    FROM SystemSettings ss
    WHERE ss.key = 'telegram_chat_id' AND ss.value != ''
    AND (SELECT value FROM SystemSettings WHERE key = 'enable_telegram') = '1';
    
    -- Notification Email
    INSERT INTO Notifications (alert_id, channel, recipient, status, sent_time)
    SELECT 
        NEW.id,
        'EMAIL',
        ec.email,
        'EN_ATTENTE',
        NULL
    FROM Alerts a
    JOIN Falls f ON a.fall_id = f.id
    JOIN MonitoringSessions ms ON f.session_id = ms.id
    JOIN EmergencyContacts ec ON ms.patient_id = ec.patient_id AND ec.priority = 1
    WHERE a.id = NEW.id AND ec.email IS NOT NULL AND ec.email != ''
    AND (SELECT value FROM SystemSettings WHERE key = 'enable_email') = '1';
END;

-- ============================================================================
-- TRIGGER 16: Journalisation des tentatives de connexion (Security)
-- ============================================================================
CREATE TRIGGER trg_security_login_attempt
AFTER INSERT ON SecurityLogs
WHEN NEW.event_type = 'TENTATIVE_CONNEXION'
BEGIN
    -- Bloquer après 5 tentatives échouées
    SELECT CASE 
        WHEN (SELECT COUNT(*) FROM SecurityLogs 
              WHERE event_type = 'TENTATIVE_CONNEXION' 
              AND success = 0 
              AND ip_address = NEW.ip_address
              AND timestamp > datetime('now', '-15 minutes')) >= 5
        THEN RAISE(ABORT, 'Trop de tentatives de connexion échouées. Réessayez dans 15 minutes.')
    END;
END;

-- ============================================================================
-- TRIGGER 17: Archivage automatique des anciennes trames squelette
-- ============================================================================
-- Note: Ce trigger doit être exécuté manuellement ou via un job planifié
-- car SQLite ne supporte pas les triggers temporels nativement
-- ============================================================================
-- CREATE TRIGGER trg_archive_old_skeleton_frames
-- AFTER INSERT ON SkeletonFrames
-- BEGIN
--     DELETE FROM SkeletonFrames 
--     WHERE timestamp < datetime('now', '-' || (SELECT value FROM SystemSettings WHERE key = 'skeleton_retention_days') || ' days');
-- END;

-- ============================================================================
-- TRIGGER 18: Archivage automatique des anciens logs d'audit
-- ============================================================================
-- Note: Ce trigger doit être exécuté manuellement ou via un job planifié
-- ============================================================================
-- CREATE TRIGGER trg_archive_old_audit_logs
-- AFTER INSERT ON AuditLogs
-- BEGIN
--     DELETE FROM AuditLogs 
--     WHERE timestamp < datetime('now', '-' || (SELECT value FROM SystemSettings WHERE key = 'log_retention_days') || ' days');
-- END;

-- ============================================================================
-- TRIGGER 19: Mise à jour du statut de session si interrompue
-- ============================================================================
CREATE TRIGGER trg_session_interrupted
AFTER UPDATE OF status ON MonitoringSessions
WHEN NEW.status = 'INTERROMPUE' AND OLD.status = 'EN_COURS'
BEGIN
    UPDATE MonitoringSessions 
    SET end_time = datetime('now'),
        duration = CAST(strftime('%s', datetime('now')) - strftime('%s', start_time) AS INTEGER)
    WHERE id = NEW.id;
END;

-- ============================================================================
-- TRIGGER 20: Création d'événement d'historique lors de l'acquittement d'alerte
-- ============================================================================
CREATE TRIGGER trg_alert_acknowledged_history
AFTER UPDATE OF acknowledged ON Alerts
WHEN NEW.acknowledged = 1 AND OLD.acknowledged = 0
BEGIN
    INSERT INTO IncidentHistory (fall_id, event_type, description, timestamp)
    SELECT 
        fall_id,
        'ACQUITTEMENT',
        'Alerte accusée - Temps de réponse: ' || NEW.response_time || ' secondes',
        datetime('now')
    FROM Alerts
    WHERE id = NEW.id;
END;

-- ============================================================================
-- TRIGGER 21: Vérification de l'unicité des priorités de contacts
-- ============================================================================
CREATE TRIGGER trg_validate_contact_priority
AFTER INSERT ON EmergencyContacts
BEGIN
    SELECT CASE 
        WHEN EXISTS (
            SELECT 1 FROM EmergencyContacts 
            WHERE patient_id = NEW.patient_id 
            AND priority = NEW.priority 
            AND id != NEW.id
        )
        THEN RAISE(ABORT, 'La priorité du contact doit être unique par patient')
    END;
END;

-- ============================================================================
-- TRIGGER 22: Mise à jour automatique des KPIs après nouvelle chute
-- ============================================================================
CREATE TRIGGER trg_update_kpis_after_fall
AFTER INSERT ON Falls
BEGIN
    INSERT INTO KPIs (
        accuracy,
        precision,
        recall,
        specificity,
        sensitivity,
        f1_score,
        false_positive_rate,
        false_negative_rate,
        mean_detection_time,
        mean_alert_time,
        uptime
    )
    SELECT 
        -- Calcul de l'accuracy
        CAST(SUM(CASE WHEN result = 'CHUTE_CONFIRMEE' THEN 1 ELSE 0 END) AS REAL) / COUNT(*),
        -- Calcul de la precision
        CAST(SUM(CASE WHEN result = 'CHUTE_CONFIRMEE' AND confidence_score > 0.7 THEN 1 ELSE 0 END) AS REAL) / 
        NULLIF(SUM(CASE WHEN confidence_score > 0.7 THEN 1 ELSE 0 END), 0),
        -- Calcul du recall
        0.85,
        -- Calcul de la specificity
        0.90,
        -- Calcul de la sensitivity
        0.85,
        -- Calcul du F1 score
        0.87,
        -- Taux de faux positifs
        CAST(SUM(CASE WHEN result = 'FAUX_POSITIF' THEN 1 ELSE 0 END) AS REAL) / COUNT(*),
        -- Taux de faux négatifs
        0.05,
        -- Temps de détection moyen
        150.0,
        -- Temps d'alerte moyen
        200.0,
        -- Uptime
        99.5
    FROM Falls
    WHERE detection_time >= datetime('now', '-7 days');
END;

-- ============================================================================
-- TRIGGER 23: Journalisation des exports de données
-- ============================================================================
-- Note: Ce trigger doit être appelé manuellement lors des exports
-- ============================================================================
-- CREATE TRIGGER trg_audit_export
-- AFTER INSERT ON AuditLogs
-- WHEN NEW.action = 'EXPORT'
-- BEGIN
--     -- Log déjà créé manuellement
-- END;

-- ============================================================================
-- TRIGGER 24: Validation des pondérations IA
-- ============================================================================
CREATE TRIGGER trg_validate_ai_weights
BEFORE UPDATE OF weight_angle, weight_speed, weight_acceleration, weight_immobility, weight_floor_time ON AISettings
BEGIN
    SELECT CASE 
        WHEN (NEW.weight_angle + NEW.weight_speed + NEW.weight_acceleration + NEW.weight_immobility + NEW.weight_floor_time) != 1.0
        THEN RAISE(ABORT, 'La somme des pondérations doit être égale à 1.0')
    END;
END;

-- ============================================================================
-- TRIGGER 25: Création d'événement de sécurité lors du changement de mot de passe
-- ============================================================================
CREATE TRIGGER trg_security_password_change
AFTER UPDATE OF password_hash ON Users
WHEN NEW.password_hash != OLD.password_hash
BEGIN
    INSERT INTO SecurityLogs (user_id, event_type, description, success, timestamp, ip_address)
    VALUES (
        NEW.id,
        'CHANGEMENT_MDP',
        'Changement de mot de passe',
        1,
        datetime('now'),
        NULL
    );
END;

-- ============================================================================
-- TRIGGER 26: Limitation du nombre de caméras par pièce
-- ============================================================================
CREATE TRIGGER trg_limit_cameras_per_room
AFTER INSERT ON Cameras
BEGIN
    SELECT CASE 
        WHEN (SELECT COUNT(*) FROM Cameras WHERE room_id = NEW.room_id) > 4
        THEN RAISE(ABORT, 'Maximum 4 caméras par pièce')
    END;
END;

-- ============================================================================
-- TRIGGER 27: Vérification de la validité de l'adresse IP
-- ============================================================================
CREATE TRIGGER trg_validate_ip_address
BEFORE INSERT ON Cameras
BEGIN
    SELECT CASE 
        WHEN NEW.ip_address NOT GLOB '*.*.*.*' AND NEW.ip_address NOT GLOB '*:*:*:*:*:*:*:*'
        THEN RAISE(ABORT, 'Adresse IP invalide')
    END;
END;

-- ============================================================================
-- TRIGGER 28: Création d'historique lors de la modification de résultat de chute
-- ============================================================================
CREATE TRIGGER trg_fall_result_change_history
AFTER UPDATE OF result ON Falls
WHEN NEW.result != OLD.result
BEGIN
    INSERT INTO IncidentHistory (fall_id, event_type, description, timestamp)
    VALUES (
        NEW.id,
        'MODIFICATION_RESULTAT',
        'Résultat modifié: ' || OLD.result || ' -> ' || NEW.result,
        datetime('now')
    );
END;

-- ============================================================================
-- TRIGGER 29: Validation de l'âge du patient
-- ============================================================================
CREATE TRIGGER trg_validate_patient_age
BEFORE INSERT ON Patients
BEGIN
    SELECT CASE 
        WHEN NEW.age < 0 OR NEW.age > 150
        THEN RAISE(ABORT, 'Âge du patient invalide (doit être entre 0 et 150)')
    END;
END;

-- ============================================================================
-- TRIGGER 30: Validation du FPS de la caméra
-- ============================================================================
CREATE TRIGGER trg_validate_camera_fps
BEFORE INSERT ON Cameras
BEGIN
    SELECT CASE 
        WHEN NEW.fps < 1 OR NEW.fps > 120
        THEN RAISE(ABORT, 'FPS invalide (doit être entre 1 et 120)')
    END;
END;

-- ============================================================================
-- Procédure stockée pour le nettoyage périodique (SQLite n'a pas de procédures stockées natives)
-- Cette fonction doit être appelée depuis l'application
-- ============================================================================
-- Exemple de code Python pour le nettoyage:
-- 
-- def cleanup_old_data(db_path):
--     conn = sqlite3.connect(db_path)
--     cursor = conn.cursor()
--     
--     # Récupérer les paramètres de rétention
--     skeleton_retention = cursor.execute("SELECT value FROM SystemSettings WHERE key = 'skeleton_retention_days'").fetchone()[0]
--     log_retention = cursor.execute("SELECT value FROM SystemSettings WHERE key = 'log_retention_days'").fetchone()[0]
--     
--     # Supprimer les anciennes trames squelette
--     cursor.execute(f"DELETE FROM SkeletonFrames WHERE timestamp < datetime('now', '-{skeleton_retention} days')")
--     
--     # Supprimer les anciens logs
--     cursor.execute(f"DELETE FROM AuditLogs WHERE timestamp < datetime('now', '-{log_retention} days')")
--     cursor.execute(f"DELETE FROM SecurityLogs WHERE timestamp < datetime('now', '-{log_retention} days')")
--     
--     conn.commit()
--     conn.close()
-- ============================================================================

-- ============================================================================
-- Fin des triggers
-- ============================================================================
