-- ============================================================================
-- Système de Détection de Chutes par Edge AI
-- Données de Test (INSERT Statements)
-- Version: 1.0
-- ============================================================================

-- ============================================================================
-- TABLE 1: Users
-- ============================================================================
INSERT INTO Users (firstname, lastname, email, password_hash, phone, role, status) VALUES
('Jean', 'Dupont', 'jean.dupont@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYWj5q5h5W6', '+33612345678', 'ADMIN', 'ACTIF'),
('Marie', 'Martin', 'marie.martin@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYWj5q5h5W6', '+33623456789', 'MEDECIN', 'ACTIF'),
('Pierre', 'Bernard', 'pierre.bernard@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYWj5q5h5W6', '+33634567890', 'FAMILLE', 'ACTIF'),
('Sophie', 'Petit', 'sophie.petit@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYWj5q5h5W6', '+33645678901', 'FAMILLE', 'ACTIF'),
('Luc', 'Dubois', 'luc.dubois@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYWj5q5h5W6', '+33656789012', 'TECHNICIEN', 'ACTIF'),
('François', 'Robert', 'francois.robert@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYWj5q5h5W6', '+33667890123', 'MEDECIN', 'ACTIF'),
('Claire', 'Richard', 'claire.richard@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYWj5q5h5W6', '+33678901234', 'FAMILLE', 'INACTIF'),
('Marc', 'Durand', 'marc.durand@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYWj5q5h5W6', '+33689012345', 'ADMIN', 'SUSPENDU'),
('Dr. Test', 'Medical', 'dr.test@medical.com', NULL, '+33699999999', 'MEDECIN', 'ACTIF');

-- ============================================================================
-- TABLE 2: Patients
-- ============================================================================
INSERT INTO Patients (user_id, age, gender, weight, height, mobility_level, medical_notes, address, latitude, longitude) VALUES
(2, 78, 'F', 62.5, 165.0, 'CANNE', 'Hypertension, arthrite légère', '15 Rue de la Paix, 75001 Paris', 48.8684, 2.3441),
(3, 82, 'H', 75.0, 172.0, 'DEAMBULATEUR', 'Diabète type 2, problèmes cardiaques', '23 Avenue des Champs-Élysées, 75008 Paris', 48.8698, 2.3075),
(4, 75, 'F', 58.0, 160.0, 'AUTONOME', 'Ostéoporose', '45 Boulevard Haussmann, 75009 Paris', 48.8750, 2.3234),
(7, 85, 'H', 70.0, 168.0, 'FAUTEUIL', 'Parkinson, démence légère', '78 Rue de Rivoli, 75004 Paris', 48.8566, 2.3522);

-- ============================================================================
-- TABLE 3: EmergencyContacts
-- ============================================================================
INSERT INTO EmergencyContacts (patient_id, fullname, relationship, phone, email, priority) VALUES
-- Patient 1 (Marie Martin)
(1, 'Pierre Martin', 'Fils', '+33611111111', 'pierre.martin@email.com', 1),
(1, 'Françoise Martin', 'Fille', '+33622222222', 'francoise.martin@email.com', 2),
(1, 'Dr. Sophie Petit', 'Médecin traitant', '+33633333333', 'sophie.petit@email.com', 3),
-- Patient 2 (Pierre Bernard)
(2, 'Jean Bernard', 'Fils', '+33644444444', 'jean.bernard@email.com', 1),
(2, 'Marie Bernard', 'Épouse', '+33655555555', 'marie.bernard@email.com', 2),
(2, 'Dr. François Robert', 'Médecin traitant', '+33666666666', 'francois.robert@email.com', 3),
-- Patient 3 (Sophie Petit)
(3, 'Luc Petit', 'Mari', '+33677777777', 'luc.petit@email.com', 1),
(3, 'Anne Petit', 'Fille', '+33688888888', 'anne.petit@email.com', 2),
-- Patient 4 (Marc Durand)
(4, 'Claire Durand', 'Épouse', '+33699999999', 'claire.durand@email.com', 1),
(4, 'Paul Durand', 'Fils', '+33610101010', 'paul.durand@email.com', 2);

-- ============================================================================
-- TABLE 4: Rooms
-- ============================================================================
INSERT INTO Rooms (patient_id, room_name, floor, description) VALUES
-- Patient 1 (Marie Martin)
(1, 'Salon', 0, 'Pièce principale avec canapé et télévision'),
(1, 'Cuisine', 0, 'Cuisine équipée'),
(1, 'Chambre', 1, 'Chambre à coucher principale'),
(1, 'Salle de bain', 1, 'Salle de bain avec douche'),
-- Patient 2 (Pierre Bernard)
(2, 'Salon', 0, 'Salon avec fauteuil'),
(2, 'Cuisine', 0, 'Cuisine ouverte'),
(2, 'Chambre', 0, 'Chambre au rez-de-chaussée'),
(2, 'Salle de bain', 0, 'Salle de bain adaptée'),
-- Patient 3 (Sophie Petit)
(3, 'Salon', 0, 'Grand salon'),
(3, 'Cuisine', 0, 'Cuisine moderne'),
(3, 'Chambre', 1, 'Chambre principale'),
(3, 'Bureau', 1, 'Bureau personnel'),
-- Patient 4 (Marc Durand)
(4, 'Salon', 0, 'Salon spacieux'),
(4, 'Chambre', 0, 'Chambre adaptée fauteuil');

-- ============================================================================
-- TABLE 5: Cameras
-- ============================================================================
INSERT INTO Cameras (room_id, camera_name, ip_address, rtsp_url, resolution, fps, status) VALUES
-- Patient 1 (Marie Martin)
(1, 'Caméra Salon', '192.168.1.101', 'rtsp://192.168.1.101:554/stream1', '1080p', 30, 'ACTIVE'),
(2, 'Caméra Cuisine', '192.168.1.102', 'rtsp://192.168.1.102:554/stream1', '720p', 25, 'ACTIVE'),
(3, 'Caméra Chambre', '192.168.1.103', 'rtsp://192.168.1.103:554/stream1', '1080p', 30, 'ACTIVE'),
(4, 'Caméra SDB', '192.168.1.104', 'rtsp://192.168.1.104:554/stream1', '720p', 25, 'ACTIVE'),
-- Patient 2 (Pierre Bernard)
(5, 'Caméra Salon Pierre', '192.168.1.105', 'rtsp://192.168.1.105:554/stream1', '1080p', 30, 'ACTIVE'),
(6, 'Caméra Cuisine Pierre', '192.168.1.106', 'rtsp://192.168.1.106:554/stream1', '720p', 25, 'ACTIVE'),
(7, 'Caméra Chambre Pierre', '192.168.1.107', 'rtsp://192.168.1.107:554/stream1', '1080p', 30, 'ACTIVE'),
-- Patient 3 (Sophie Petit)
(9, 'Caméra Salon Sophie', '192.168.1.108', 'rtsp://192.168.1.108:554/stream1', '1080p', 30, 'ACTIVE'),
(10, 'Caméra Cuisine Sophie', '192.168.1.109', 'rtsp://192.168.1.109:554/stream1', '720p', 25, 'ACTIVE'),
(11, 'Caméra Chambre Sophie', '192.168.1.110', 'rtsp://192.168.1.110:554/stream1', '1080p', 30, 'ACTIVE'),
-- Patient 4 (Marc Durand)
(13, 'Caméra Salon Marc', '192.168.1.111', 'rtsp://192.168.1.111:554/stream1', '1080p', 30, 'ACTIVE'),
(14, 'Caméra Chambre Marc', '192.168.1.112', 'rtsp://192.168.1.112:554/stream1', '1080p', 30, 'ACTIVE');

-- ============================================================================
-- TABLE 6: MonitoringSessions
-- ============================================================================
INSERT INTO MonitoringSessions (camera_id, patient_id, start_time, end_time, duration, status) VALUES
-- Sessions terminées
(1, 1, '2026-01-15 08:00:00', '2026-01-15 18:00:00', 36000, 'TERMINEE'),
(1, 1, '2026-01-16 08:00:00', '2026-01-16 18:00:00', 36000, 'TERMINEE'),
(2, 1, '2026-01-17 08:00:00', '2026-01-17 12:00:00', 14400, 'TERMINEE'),
(5, 2, '2026-01-15 08:00:00', '2026-01-15 20:00:00', 43200, 'TERMINEE'),
(5, 2, '2026-01-16 08:00:00', '2026-01-16 18:00:00', 36000, 'TERMINEE'),
(9, 3, '2026-01-15 08:00:00', '2026-01-15 18:00:00', 36000, 'TERMINEE'),
(13, 4, '2026-01-15 08:00:00', '2026-01-15 18:00:00', 36000, 'TERMINEE'),
-- Session en cours
(1, 1, '2026-07-22 08:00:00', NULL, NULL, 'EN_COURS'),
(5, 2, '2026-07-22 08:00:00', NULL, NULL, 'EN_COURS'),
(9, 3, '2026-07-22 08:00:00', NULL, NULL, 'EN_COURS'),
-- Session interrompue
(2, 1, '2026-01-18 08:00:00', '2026-01-18 10:30:00', 9000, 'INTERROMPUE');

-- ============================================================================
-- TABLE 7: SkeletonFrames (échantillon de données)
-- ============================================================================
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
    right_ankle_x, right_ankle_y, right_ankle_z) VALUES
-- Session 1 - Frame normale
(1, '2026-01-15 08:00:01', 1, 0.5, 0.3, 0.8, 0.4, 0.5, 0.7, 0.6, 0.5, 0.7, 0.35, 0.6, 0.6, 0.65, 0.6, 0.6, 0.3, 0.7, 0.5, 0.7, 0.7, 0.5, 0.45, 0.6, 0.8, 0.55, 0.6, 0.8, 0.4, 0.75, 0.7, 0.6, 0.75, 0.7, 0.35, 0.85, 0.6, 0.65, 0.85, 0.6),
(1, '2026-01-15 08:00:02', 2, 0.51, 0.31, 0.81, 0.41, 0.51, 0.71, 0.61, 0.51, 0.71, 0.36, 0.61, 0.61, 0.66, 0.61, 0.61, 0.31, 0.71, 0.51, 0.71, 0.71, 0.51, 0.46, 0.61, 0.81, 0.56, 0.61, 0.81, 0.41, 0.76, 0.71, 0.61, 0.76, 0.71, 0.36, 0.86, 0.61, 0.66, 0.86, 0.61),
-- Session 1 - Frame chute potentielle
(1, '2026-01-15 14:30:15', 25000, 0.5, 0.85, 0.2, 0.4, 0.8, 0.3, 0.6, 0.8, 0.3, 0.35, 0.9, 0.2, 0.65, 0.9, 0.2, 0.3, 0.95, 0.1, 0.7, 0.95, 0.1, 0.45, 0.9, 0.2, 0.55, 0.9, 0.2, 0.4, 0.95, 0.1, 0.6, 0.95, 0.1, 0.35, 0.98, 0.05, 0.65, 0.98, 0.05),
-- Session 2 - Frames normales
(2, '2026-01-16 08:00:01', 1, 0.52, 0.32, 0.82, 0.42, 0.52, 0.72, 0.62, 0.52, 0.72, 0.37, 0.62, 0.62, 0.67, 0.62, 0.62, 0.32, 0.72, 0.52, 0.72, 0.72, 0.52, 0.47, 0.62, 0.82, 0.57, 0.62, 0.82, 0.42, 0.77, 0.72, 0.62, 0.77, 0.72, 0.37, 0.87, 0.62, 0.67, 0.87, 0.62),
(2, '2026-01-16 08:00:02', 2, 0.53, 0.33, 0.83, 0.43, 0.53, 0.73, 0.63, 0.53, 0.73, 0.38, 0.63, 0.63, 0.68, 0.63, 0.63, 0.33, 0.73, 0.53, 0.73, 0.73, 0.53, 0.48, 0.63, 0.83, 0.58, 0.63, 0.83, 0.43, 0.78, 0.73, 0.63, 0.78, 0.73, 0.38, 0.88, 0.63, 0.68, 0.88, 0.63);

-- ============================================================================
-- TABLE 8: Falls
-- ============================================================================
INSERT INTO Falls (session_id, detection_time, trunk_angle, body_height, vertical_speed, acceleration, 
    center_gravity_x, center_gravity_y, center_gravity_speed, immobility_duration, floor_time, 
    kinetic_energy, confidence_score, fall_score, severity_score, injury_probability, result) VALUES
-- Chute confirmée sévère
(1, '2026-01-15 14:30:15', 85.5, 1200.0, 3.2, 8.5, 0.5, 0.85, 2.8, 45.0, 120.0, 450.5, 0.95, 0.92, 0.88, 75.0, 'CHUTE_CONFIRMEE'),
-- Chute confirmée modérée
(1, '2026-01-16 10:15:30', 65.0, 1350.0, 2.1, 5.2, 0.52, 0.7, 1.9, 20.0, 45.0, 280.3, 0.88, 0.75, 0.55, 35.0, 'CHUTE_CONFIRMEE'),
-- Faux positif
(2, '2026-01-17 09:45:00', 25.0, 1550.0, 0.5, 1.2, 0.5, 0.5, 0.3, 0.0, 0.0, 45.2, 0.45, 0.25, 0.15, 5.0, 'FAUX_POSITIF'),
-- Chute confirmée légère
(5, '2026-01-15 16:20:45', 55.0, 1400.0, 1.8, 4.0, 0.48, 0.65, 1.5, 10.0, 25.0, 220.1, 0.82, 0.68, 0.42, 20.0, 'CHUTE_CONFIRMEE'),
-- Chute confirmée critique
(5, '2026-01-16 11:30:00', 90.0, 1100.0, 4.5, 12.0, 0.45, 0.9, 3.5, 60.0, 180.0, 680.7, 0.98, 0.96, 0.95, 90.0, 'CHUTE_CONFIRMEE'),
-- Indéterminé
(9, '2026-01-15 13:00:00', 45.0, 1450.0, 1.2, 3.0, 0.5, 0.6, 1.0, 5.0, 15.0, 150.8, 0.65, 0.5, 0.35, 15.0, 'INDETERMINE'),
-- Chute confirmée
(13, '2026-01-15 15:45:20', 70.0, 1250.0, 2.5, 6.0, 0.5, 0.75, 2.2, 30.0, 75.0, 350.4, 0.90, 0.80, 0.65, 50.0, 'CHUTE_CONFIRMEE');

-- ============================================================================
-- TABLE 9: Alerts
-- ============================================================================
INSERT INTO Alerts (fall_id, alert_level, sent_at, acknowledged, response_time) VALUES
-- Alertes pour chute 1 (critique)
(1, 'CRITIQUE', '2026-01-15 14:30:16', 1, 180),
-- Alertes pour chute 2 (haute)
(2, 'HAUTE', '2026-01-16 10:15:31', 1, 300),
-- Alerte pour chute 3 (basse - faux positif)
(3, 'BASSE', '2026-01-17 09:45:01', 1, 60),
-- Alertes pour chute 4 (moyenne)
(4, 'MOYENNE', '2026-01-15 16:20:46', 1, 420),
-- Alertes pour chute 5 (critique)
(5, 'CRITIQUE', '2026-01-16 11:30:01', 0, NULL),
-- Alerte pour chute 6 (moyenne)
(6, 'MOYENNE', '2026-01-15 13:00:01', 1, 240),
-- Alertes pour chute 7 (haute)
(7, 'HAUTE', '2026-01-15 15:45:21', 0, NULL);

-- ============================================================================
-- TABLE 10: Notifications
-- ============================================================================
INSERT INTO Notifications (alert_id, channel, recipient, status, sent_time) VALUES
-- Notifications pour alerte 1
(1, 'TELEGRAM', 'pierre.martin@email.com', 'ENVOYE', '2026-01-15 14:30:17'),
(1, 'EMAIL', 'pierre.martin@email.com', 'ENVOYE', '2026-01-15 14:30:18'),
(1, 'EMAIL', 'francoise.martin@email.com', 'ENVOYE', '2026-01-15 14:30:18'),
-- Notifications pour alerte 2
(2, 'TELEGRAM', 'jean.bernard@email.com', 'ENVOYE', '2026-01-16 10:15:32'),
(2, 'EMAIL', 'jean.bernard@email.com', 'ENVOYE', '2026-01-16 10:15:33'),
(2, 'EMAIL', 'marie.bernard@email.com', 'ENVOYE', '2026-01-16 10:15:33'),
-- Notifications pour alerte 3
(3, 'EMAIL', 'luc.petit@email.com', 'ENVOYE', '2026-01-17 09:45:02'),
-- Notifications pour alerte 4
(4, 'TELEGRAM', 'luc.petit@email.com', 'ENVOYE', '2026-01-15 16:20:47'),
(4, 'EMAIL', 'luc.petit@email.com', 'ENVOYE', '2026-01-15 16:20:48'),
-- Notifications pour alerte 5 (non envoyées)
(5, 'TELEGRAM', 'jean.bernard@email.com', 'EN_ATTENTE', NULL),
(5, 'EMAIL', 'jean.bernard@email.com', 'EN_ATTENTE', NULL),
(5, 'EMAIL', 'marie.bernard@email.com', 'EN_ATTENTE', NULL),
-- Notifications pour alerte 6
(6, 'TELEGRAM', 'luc.petit@email.com', 'ENVOYE', '2026-01-15 13:00:02'),
-- Notifications pour alerte 7 (échouées)
(7, 'TELEGRAM', 'claire.durand@email.com', 'EN_ECHEC', '2026-01-15 15:45:22'),
(7, 'EMAIL', 'claire.durand@email.com', 'EN_ECHEC', '2026-01-15 15:45:23');

-- ============================================================================
-- TABLE 11: IncidentHistory
-- ============================================================================
INSERT INTO IncidentHistory (fall_id, event_type, description, timestamp) VALUES
(1, 'DETECTION', 'Détection de chute - Score: 0.92, Gravité: 0.88', '2026-01-15 14:30:15'),
(1, 'ALERTE', 'Alerte critique envoyée', '2026-01-15 14:30:16'),
(1, 'NOTIFICATION', 'Notification Telegram envoyée à pierre.martin@email.com', '2026-01-15 14:30:17'),
(1, 'NOTIFICATION', 'Notification email envoyée à pierre.martin@email.com', '2026-01-15 14:30:18'),
(1, 'ACQUITTEMENT', 'Alerte accusée - Temps de réponse: 180 secondes', '2026-01-15 14:33:16'),
(2, 'DETECTION', 'Détection de chute - Score: 0.75, Gravité: 0.55', '2026-01-16 10:15:30'),
(2, 'ALERTE', 'Alerte haute envoyée', '2026-01-16 10:15:31'),
(2, 'ACQUITTEMENT', 'Alerte accusée - Temps de réponse: 300 secondes', '2026-01-16 10:20:31'),
(5, 'DETECTION', 'Détection de chute critique - Score: 0.96, Gravité: 0.95', '2026-01-16 11:30:00'),
(5, 'ALERTE', 'Alerte critique envoyée', '2026-01-16 11:30:01'),
(5, 'ESCALADE', 'Escalade de niveau - Pas de réponse après 5 minutes', '2026-01-16 11:35:01');

-- ============================================================================
-- TABLE 12: SimulationVideos
-- ============================================================================
INSERT INTO SimulationVideos (filename, description, expected_result) VALUES
('fall_simulation_001.mp4', 'Simulation de chute dans le salon - personne âgée', 'CHUTE'),
('fall_simulation_002.mp4', 'Simulation de chute dans la cuisine - glissade', 'CHUTE'),
('fall_simulation_003.mp4', 'Simulation de chute dans la chambre - chute du lit', 'CHUTE'),
('no_fall_simulation_001.mp4', 'Simulation normale - marche dans le salon', 'PAS_CHUTE'),
('no_fall_simulation_002.mp4', 'Simulation normale - assis sur canapé', 'PAS_CHUTE'),
('no_fall_simulation_003.mp4', 'Simulation normale - cuisine activité', 'PAS_CHUTE'),
('fall_simulation_004.mp4', 'Simulation de chute rapide - perte d équilibre', 'CHUTE'),
('no_fall_simulation_004.mp4', 'Simulation normale - exercice léger', 'PAS_CHUTE');

-- ============================================================================
-- TABLE 13: SimulationResults
-- ============================================================================
INSERT INTO SimulationResults (simulation_id, precision, recall, f1_score, false_positive, false_negative, detection_time) VALUES
(1, 0.92, 0.88, 0.90, 2, 1, 150),
(2, 0.95, 0.90, 0.92, 1, 2, 120),
(3, 0.88, 0.85, 0.86, 3, 2, 180),
(4, 0.98, 0.95, 0.96, 0, 1, 80),
(5, 0.96, 0.94, 0.95, 1, 0, 75),
(6, 0.94, 0.92, 0.93, 1, 1, 90),
(7, 0.90, 0.87, 0.88, 2, 2, 140),
(8, 0.97, 0.96, 0.96, 0, 0, 70);

-- ============================================================================
-- TABLE 14: AISettings (déjà initialisé dans le schéma, mise à jour ici)
-- ============================================================================
UPDATE AISettings SET 
    threshold_angle = 45.0,
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
    modified_at = datetime('now');

-- ============================================================================
-- TABLE 15: KPIs
-- ============================================================================
INSERT INTO KPIs (accuracy, precision, recall, specificity, sensitivity, f1_score, 
    false_positive_rate, false_negative_rate, mean_detection_time, mean_alert_time, uptime) VALUES
(0.92, 0.90, 0.88, 0.94, 0.88, 0.89, 0.06, 0.12, 145.0, 195.0, 99.5),
(0.93, 0.91, 0.89, 0.95, 0.89, 0.90, 0.05, 0.11, 140.0, 190.0, 99.6),
(0.94, 0.92, 0.90, 0.96, 0.90, 0.91, 0.04, 0.10, 138.0, 185.0, 99.7),
(0.95, 0.93, 0.91, 0.97, 0.91, 0.92, 0.03, 0.09, 135.0, 180.0, 99.8);

-- ============================================================================
-- TABLE 16: AuditLogs
-- ============================================================================
INSERT INTO AuditLogs (user_id, action, table_name, record_id, old_values, new_values, timestamp, ip_address) VALUES
(1, 'CONNEXION', 'Users', 1, NULL, NULL, '2026-07-22 08:00:00', '192.168.1.10'),
(1, 'MODIFICATION', 'Patients', 1, '{"age": 77}', '{"age": 78}', '2026-07-21 10:30:00', '192.168.1.10'),
(2, 'CONNEXION', 'Users', 2, NULL, NULL, '2026-07-22 08:15:00', '192.168.1.11'),
(1, 'PARAMETRES', 'AISettings', 1, '{"threshold_angle": 40.0}', '{"threshold_angle": 45.0}', '2026-07-20 14:00:00', '192.168.1.10'),
(3, 'CONNEXION', 'Users', 3, NULL, NULL, '2026-07-22 09:00:00', '192.168.1.12'),
(1, 'EXPORT', 'Falls', NULL, NULL, NULL, '2026-07-19 16:00:00', '192.168.1.10'),
(5, 'CONNEXION', 'Users', 5, NULL, NULL, '2026-07-22 07:30:00', '192.168.1.15'),
(1, 'MODIFICATION', 'SystemSettings', 1, '{"value": ""}', '{"value": "new_token"}', '2026-07-18 11:00:00', '192.168.1.10');

-- ============================================================================
-- TABLE 17: SecurityLogs
-- ============================================================================
INSERT INTO SecurityLogs (user_id, event_type, description, success, timestamp, ip_address) VALUES
(1, 'TENTATIVE_CONNEXION', 'Connexion réussie', 1, '2026-07-22 08:00:00', '192.168.1.10'),
(1, 'TENTATIVE_CONNEXION', 'Connexion réussie', 1, '2026-07-21 08:00:00', '192.168.1.10'),
(NULL, 'TENTATIVE_CONNEXION', 'Échec - mot de passe incorrect', 0, '2026-07-22 08:05:00', '192.168.1.50'),
(NULL, 'TENTATIVE_CONNEXION', 'Échec - utilisateur inconnu', 0, '2026-07-22 08:10:00', '192.168.1.51'),
(1, 'CHANGEMENT_MDP', 'Changement de mot de passe réussi', 1, '2026-07-15 10:00:00', '192.168.1.10'),
(2, 'CHANGEMENT_MDP', 'Changement de mot de passe réussi', 1, '2026-07-10 14:00:00', '192.168.1.11'),
(1, 'MFA', 'Authentification à deux facteurs réussie', 1, '2026-07-22 08:00:05', '192.168.1.10'),
(1, 'ACCES_VIDEO', 'Accès autorisé à la caméra 1', 1, '2026-07-22 08:30:00', '192.168.1.10'),
(NULL, 'ACCES_VIDEO', 'Accès refusé - caméra 1', 0, '2026-07-22 09:00:00', '192.168.1.50'),
(1, 'ROTATION_CLES', 'Rotation des clés AES réussie', 1, '2026-07-01 00:00:00', '192.168.1.10');

-- ============================================================================
-- TABLE 18: SystemSettings (déjà initialisé dans le schéma, mises à jour ici)
-- ============================================================================
UPDATE SystemSettings SET value = '123456789:ABCdefGHIjklMNOpqrSTUvwxYZ' WHERE key = 'telegram_bot_token';
UPDATE SystemSettings SET value = '-123456789' WHERE key = 'telegram_chat_id';
UPDATE SystemSettings SET value = 'admin@email.com' WHERE key = 'smtp_username';
UPDATE SystemSettings SET modified_at = datetime('now') WHERE key IN ('telegram_bot_token', 'telegram_chat_id', 'smtp_username');

-- ============================================================================
-- Données supplémentaires pour tests
-- ============================================================================

-- Sessions supplémentaires pour tests de performance
INSERT INTO MonitoringSessions (camera_id, patient_id, start_time, end_time, duration, status) VALUES
(3, 1, '2026-01-18 08:00:00', '2026-01-18 18:00:00', 36000, 'TERMINEE'),
(3, 1, '2026-01-19 08:00:00', '2026-01-19 18:00:00', 36000, 'TERMINEE'),
(6, 2, '2026-01-17 08:00:00', '2026-01-17 18:00:00', 36000, 'TERMINEE'),
(10, 3, '2026-01-16 08:00:00', '2026-01-16 18:00:00', 36000, 'TERMINEE'),
(11, 3, '2026-01-17 08:00:00', '2026-01-17 18:00:00', 36000, 'TERMINEE');

-- Chutes supplémentaires pour tests statistiques
INSERT INTO Falls (session_id, detection_time, trunk_angle, body_height, vertical_speed, acceleration, 
    center_gravity_x, center_gravity_y, center_gravity_speed, immobility_duration, floor_time, 
    kinetic_energy, confidence_score, fall_score, severity_score, injury_probability, result) VALUES
(12, '2026-01-18 15:00:00', 60.0, 1300.0, 2.0, 4.5, 0.5, 0.7, 1.8, 15.0, 35.0, 250.0, 0.85, 0.70, 0.48, 25.0, 'CHUTE_CONFIRMEE'),
(13, '2026-01-19 09:30:00', 30.0, 1500.0, 0.8, 2.0, 0.5, 0.55, 0.6, 2.0, 5.0, 80.0, 0.55, 0.35, 0.20, 8.0, 'FAUX_POSITIF'),
(14, '2026-01-17 14:00:00', 75.0, 1280.0, 2.8, 6.5, 0.48, 0.78, 2.5, 25.0, 60.0, 320.0, 0.91, 0.82, 0.62, 45.0, 'CHUTE_CONFIRMEE'),
(15, '2026-01-16 16:45:00', 40.0, 1480.0, 1.0, 2.5, 0.52, 0.58, 0.8, 3.0, 8.0, 95.0, 0.60, 0.40, 0.25, 10.0, 'FAUX_POSITIF'),
(16, '2026-01-17 11:20:00', 80.0, 1220.0, 3.5, 8.0, 0.47, 0.82, 3.0, 35.0, 90.0, 420.0, 0.93, 0.88, 0.75, 60.0, 'CHUTE_CONFIRMEE');

-- Alertes supplémentaires
INSERT INTO Alerts (fall_id, alert_level, sent_at, acknowledged, response_time) VALUES
(8, 'HAUTE', '2026-01-18 15:00:01', 1, 240),
(9, 'BASSE', '2026-01-19 09:30:01', 1, 90),
(10, 'HAUTE', '2026-01-17 14:00:01', 1, 360),
(11, 'BASSE', '2026-01-16 16:45:01', 1, 120),
(12, 'CRITIQUE', '2026-01-17 11:20:01', 0, NULL);

-- ============================================================================
-- Fin des données de test
-- ============================================================================
