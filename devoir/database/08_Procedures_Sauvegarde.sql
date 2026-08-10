-- ============================================================================
-- Système de Détection de Chutes par Edge AI
-- Procédures de Sauvegarde et Restauration
-- Version: 1.0
-- ============================================================================

-- ============================================================================
-- REMARQUE IMPORTANTE
-- SQLite ne supporte pas les procédures stockées natives.
-- Les procédures suivantes sont fournies sous forme de scripts SQL
-- qui doivent être exécutés depuis l'application (Python, etc.)
-- ============================================================================

-- ============================================================================
-- PROCÉDURE 1: Sauvegarde complète de la base de données
-- ============================================================================
-- Script SQL pour sauvegarde complète
-- Usage: sqlite3 falldetection.db ".backup backup_falldetection_YYYYMMDD.db"
-- ============================================================================
-- Alternative avec VACUUM INTO:
VACUUM INTO 'backup_falldetection_' || strftime('%Y%m%d_%H%M%S', 'now') || '.db';

-- ============================================================================
-- PROCÉDURE 2: Sauvegarde incrémentielle (tables spécifiques)
-- ============================================================================
-- Sauvegarde des tables critiques
-- ============================================================================
ATTACH DATABASE 'backup_falldetection_incremental.db' AS backup;

-- Copie des tables de surveillance
INSERT INTO backup.MonitoringSessions SELECT * FROM main.MonitoringSessions WHERE start_time >= datetime('now', '-1 day');
INSERT INTO backup.SkeletonFrames SELECT * FROM main.SkeletonFrames WHERE timestamp >= datetime('now', '-1 day');
INSERT INTO backup.Falls SELECT * FROM main.Falls WHERE detection_time >= datetime('now', '-1 day');
INSERT INTO backup.Alerts SELECT * FROM main.Alerts WHERE sent_at >= datetime('now', '-1 day');
INSERT INTO backup.Notifications SELECT * FROM main.Notifications WHERE sent_time >= datetime('now', '-1 day');

-- Copie des tables de configuration
INSERT INTO backup.AISettings SELECT * FROM main.AISettings;
INSERT INTO backup.SystemSettings SELECT * FROM main.SystemSettings;

DETACH DATABASE backup;

-- ============================================================================
-- PROCÉDURE 3: Export des données en CSV
-- ============================================================================
-- Export de chaque table en CSV
-- ============================================================================
.mode csv
.headers on

-- Export Users
.output 'export_users_' || strftime('%Y%m%d', 'now') || '.csv'
SELECT * FROM Users;
.output

-- Export Patients
.output 'export_patients_' || strftime('%Y%m%d', 'now') || '.csv'
SELECT * FROM Patients;
.output

-- Export EmergencyContacts
.output 'export_contacts_' || strftime('%Y%m%d', 'now') || '.csv'
SELECT * FROM EmergencyContacts;
.output

-- Export Falls
.output 'export_falls_' || strftime('%Y%m%d', 'now') || '.csv'
SELECT * FROM Falls;
.output

-- Export Alerts
.output 'export_alerts_' || strftime('%Y%m%d', 'now') || '.csv'
SELECT * FROM Alerts;
.output

-- ============================================================================
-- PROCÉDURE 4: Export des données en JSON
-- ============================================================================
-- Export en JSON pour intégration API
-- ============================================================================
.mode json
.output 'export_falls_' || strftime('%Y%m%d', 'now') || '.json'
SELECT * FROM Falls WHERE detection_time >= datetime('now', '-7 days');
.output

.output 'export_alerts_' || strftime('%Y%m%d', 'now') || '.json'
SELECT * FROM Alerts WHERE sent_at >= datetime('now', '-7 days');
.output

-- ============================================================================
-- PROCÉDURE 5: Sauvegarde des paramètres système
-- ============================================================================
-- Export des paramètres de configuration
-- ============================================================================
.output 'export_settings_' || strftime('%Y%m%d', 'now') || '.sql'
SELECT 
    'INSERT OR REPLACE INTO SystemSettings (key, value, description, modified_at) VALUES (' ||
    quote(key) || ', ' ||
    quote(value) || ', ' ||
    quote(description) || ', ' ||
    quote(modified_at) || ');' AS sql_statement
FROM SystemSettings;
.output

-- ============================================================================
-- PROCÉDURE 6: Restauration depuis une sauvegarde
-- ============================================================================
-- Restauration complète
-- ============================================================================
-- Étape 1: Fermer toutes les connexions
-- Étape 2: Remplacer le fichier de base de données
-- Étape 3: Vérifier l'intégrité
PRAGMA integrity_check;

-- ============================================================================
-- PROCÉDURE 7: Restauration incrémentielle
-- ============================================================================
ATTACH DATABASE 'backup_falldetection_incremental.db' AS backup;

-- Restauration des tables
INSERT OR REPLACE INTO main.MonitoringSessions SELECT * FROM backup.MonitoringSessions;
INSERT OR REPLACE INTO main.SkeletonFrames SELECT * FROM backup.SkeletonFrames;
INSERT OR REPLACE INTO main.Falls SELECT * FROM backup.Falls;
INSERT OR REPLACE INTO main.Alerts SELECT * FROM backup.Alerts;
INSERT OR REPLACE INTO main.Notifications SELECT * FROM backup.Notifications;

DETACH DATABASE backup;

-- ============================================================================
-- PROCÉDURE 8: Nettoyage des anciennes données (Archivage)
-- ============================================================================
-- Archivage des trames squelette anciennes
-- ============================================================================
-- Créer une table d'archive si elle n'existe pas
CREATE TABLE IF NOT EXISTS SkeletonFrames_Archive (
    LIKE SkeletonFrames INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING INDEXES
);

-- Déplacer les anciennes données vers l'archive
INSERT INTO SkeletonFrames_Archive 
SELECT * FROM SkeletonFrames 
WHERE timestamp < datetime('now', '-' || (SELECT value FROM SystemSettings WHERE key = 'skeleton_retention_days') || ' days');

-- Supprimer les données archivées
DELETE FROM SkeletonFrames 
WHERE timestamp < datetime('now', '-' || (SELECT value FROM SystemSettings WHERE key = 'skeleton_retention_days') || ' days');

-- Archivage des logs d'audit
CREATE TABLE IF NOT EXISTS AuditLogs_Archive (
    LIKE AuditLogs INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING INDEXES
);

INSERT INTO AuditLogs_Archive 
SELECT * FROM AuditLogs 
WHERE timestamp < datetime('now', '-' || (SELECT value FROM SystemSettings WHERE key = 'log_retention_days') || ' days');

DELETE FROM AuditLogs 
WHERE timestamp < datetime('now', '-' || (SELECT value FROM SystemSettings WHERE key = 'log_retention_days') || ' days');

-- ============================================================================
-- PROCÉDURE 9: Compression des archives
-- ============================================================================
-- Note: SQLite ne supporte pas la compression native
-- Utiliser un script externe (Python) pour compresser les archives
-- ============================================================================
-- Exemple Python:
-- import shutil
-- import gzip
-- 
-- def compress_file(file_path):
--     with open(file_path, 'rb') as f_in:
--         with gzip.open(file_path + '.gz', 'wb') as f_out:
--             shutil.copyfileobj(f_in, f_out)

-- ============================================================================
-- PROCÉDURE 10: Vérification de l'intégrité avant sauvegarde
-- ============================================================================
PRAGMA integrity_check;
PRAGMA foreign_key_check;

-- Si les checks passent, procéder à la sauvegarde
-- Sinon, journaliser l'erreur et alerter l'administrateur

-- ============================================================================
-- PROCÉDURE 11: Sauvegarde différentielle (delta)
-- ============================================================================
-- Sauvegarder uniquement les modifications depuis la dernière sauvegarde
-- ============================================================================
-- Créer une table pour tracker la dernière sauvegarde
CREATE TABLE IF NOT EXISTS BackupLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_type TEXT NOT NULL,
    backup_path TEXT NOT NULL,
    backup_time TEXT NOT NULL DEFAULT (datetime('now')),
    tables_backed_up TEXT,
    size_bytes INTEGER,
    status TEXT
);

-- Enregistrer la sauvegarde
INSERT INTO BackupLog (backup_type, backup_path, tables_backed_up, status)
VALUES (
    'INCREMENTAL',
    'backup_falldetection_incremental.db',
    'MonitoringSessions,SkeletonFrames,Falls,Alerts,Notifications',
    'SUCCESS'
);

-- ============================================================================
-- PROCÉDURE 12: Rotation des sauvegardes
-- ============================================================================
-- Garder seulement les N dernières sauvegardes
-- ============================================================================
-- Supprimer les sauvegardes plus anciennes que 30 jours
-- Note: Ceci doit être exécuté au niveau du système de fichiers
-- ============================================================================
-- Exemple de commande shell:
-- find /path/to/backups -name "backup_falldetection_*.db" -mtime +30 -delete

-- ============================================================================
-- PROCÉDURE 13: Sauvegarde avant modification critique
-- ============================================================================
-- Point de restauration avant modification importante
-- ============================================================================
SAVEPOINT before_critical_update;

-- Effectuer les modifications
-- UPDATE AISettings SET threshold_angle = 50.0;

-- Si succès
-- RELEASE SAVEPOINT before_critical_update;

-- Si échec
-- ROLLBACK TO SAVEPOINT before_critical_update;

-- ============================================================================
-- PROCÉDURE 14: Export du schéma de base de données
-- ============================================================================
.output 'schema_export_' || strftime('%Y%m%d', 'now') || '.sql'
.schema
.output

-- ============================================================================
-- PROCÉDURE 15: Sauvegarde des données anonymisées
-- ============================================================================
-- Export des données sans informations personnelles
-- ============================================================================
.output 'export_anonymized_falls_' || strftime('%Y%m%d', 'now') || '.csv'
SELECT 
    id,
    session_id,
    detection_time,
    trunk_angle,
    body_height,
    vertical_speed,
    acceleration,
    center_gravity_x,
    center_gravity_y,
    center_gravity_speed,
    immobility_duration,
    floor_time,
    kinetic_energy,
    confidence_score,
    fall_score,
    severity_score,
    injury_probability,
    result
FROM Falls;
.output

-- ============================================================================
-- SCRIPT PYTHON POUR SAUVEGARDE AUTOMATIQUE
-- ============================================================================
"""
import sqlite3
import shutil
import os
from datetime import datetime
import schedule
import time

class DatabaseBackup:
    def __init__(self, db_path, backup_dir):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def full_backup(self):
        \"\"\"Sauvegarde complète de la base de données\"\"\"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'backup_falldetection_{timestamp}.db')
        
        try:
            # Vérifier l'intégrité avant sauvegarde
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA integrity_check')
            conn.close()
            
            # Effectuer la sauvegarde
            shutil.copy2(self.db_path, backup_path)
            
            # Logger la sauvegarde
            self.log_backup('FULL', backup_path, os.path.getsize(backup_path))
            
            return True, backup_path
        except Exception as e:
            print(f\"Erreur de sauvegarde: {e}\")
            return False, str(e)
    
    def incremental_backup(self):
        \"\"\"Sauvegarde incrémentielle des données récentes\"\"\"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'backup_incremental_{timestamp}.db')
        
        try:
            # Créer une nouvelle base de données pour l'incrémental
            conn_src = sqlite3.connect(self.db_path)
            conn_dst = sqlite3.connect(backup_path)
            
            # Copier le schéma
            with open(self.db_path, 'r') as f:
                schema = f.read()
            conn_dst.executescript(schema)
            
            # Copier les données récentes (7 jours)
            cursor_src = conn_src.cursor()
            cursor_dst = conn_dst.cursor()
            
            tables = ['MonitoringSessions', 'SkeletonFrames', 'Falls', 'Alerts', 'Notifications']
            for table in tables:
                cursor_src.execute(f\"SELECT * FROM {table} WHERE timestamp >= datetime('now', '-7 days')\")
                columns = [description[0] for description in cursor_src.description]
                placeholders = ','.join(['?'] * len(columns))
                cursor_dst.executemany(
                    f\"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})\",
                    cursor_src.fetchall()
                )
            
            conn_dst.commit()
            conn_src.close()
            conn_dst.close()
            
            self.log_backup('INCREMENTAL', backup_path, os.path.getsize(backup_path))
            return True, backup_path
        except Exception as e:
            print(f\"Erreur de sauvegarde incrémentielle: {e}\")
            return False, str(e)
    
    def export_csv(self, table, output_dir=None):
        \"\"\"Export d'une table en CSV\"\"\"
        if output_dir is None:
            output_dir = self.backup_dir
        
        timestamp = datetime.now().strftime('%Y%m%d')
        csv_path = os.path.join(output_dir, f'export_{table}_{timestamp}.csv')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f\"SELECT * FROM {table}\")
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                # En-têtes
                writer.writerow([description[0] for description in cursor.description])
                # Données
                writer.writerows(cursor.fetchall())
            
            conn.close()
            return True, csv_path
        except Exception as e:
            print(f\"Erreur d'export CSV: {e}\")
            return False, str(e)
    
    def cleanup_old_backups(self, days=30):
        \"\"\"Supprimer les sauvegardes plus anciennes que X jours\"\"\"
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for filename in os.listdir(self.backup_dir):
            filepath = os.path.join(self.backup_dir, filename)
            if os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
                print(f\"Sauvegarde supprimée: {filename}\")
    
    def log_backup(self, backup_type, backup_path, size):
        \"\"\"Logger la sauvegarde dans la base de données\"\"\"
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO BackupLog (backup_type, backup_path, backup_time, size_bytes, status)
            VALUES (?, ?, ?, ?, 'SUCCESS')
        ''', (backup_type, backup_path, datetime.now().isoformat(), size))
        conn.commit()
        conn.close()

# Configuration
DB_PATH = 'falldetection.db'
BACKUP_DIR = './backups'

# Créer l'instance de sauvegarde
backup_manager = DatabaseBackup(DB_PATH, BACKUP_DIR)

# Planifier les sauvegardes
schedule.every().day.at('02:00').do(backup_manager.full_backup)
schedule.every(6).hours.do(backup_manager.incremental_backup)
schedule.every().sunday.do(backup_manager.cleanup_old_backups, days=30)

# Boucle principale
while True:
    schedule.run_pending()
    time.sleep(60)
"""

-- ============================================================================
-- SCRIPT BASH POUR SAUVEGARDE AUTOMATIQUE (Linux/Mac)
-- ============================================================================
#!/bin/bash
# backup_script.sh

DB_PATH="/path/to/falldetection.db"
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Créer le répertoire de sauvegarde
mkdir -p "$BACKUP_DIR"

# Sauvegarde complète
sqlite3 "$DB_PATH" "VACUUM INTO '$BACKUP_DIR/backup_falldetection_$TIMESTAMP.db'"

# Vérifier l'intégrité
sqlite3 "$BACKUP_DIR/backup_falldetection_$TIMESTAMP.db" "PRAGMA integrity_check;"

# Compresser la sauvegarde
gzip "$BACKUP_DIR/backup_falldetection_$TIMESTAMP.db"

# Nettoyer les sauvegardes de plus de 30 jours
find "$BACKUP_DIR" -name "backup_falldetection_*.db.gz" -mtime +30 -delete

echo "Sauvegarde terminée: backup_falldetection_$TIMESTAMP.db.gz"

-- ============================================================================
-- SCRIPT POWERSHELL POUR SAUVEGARDE AUTOMATIQUE (Windows)
-- ============================================================================
# backup_script.ps1

$DB_PATH = "C:\path\to\falldetection.db"
$BACKUP_DIR = "C:\path\to\backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"

# Créer le répertoire de sauvegarde
New-Item -ItemType Directory -Force -Path $BACKUP_DIR

# Sauvegarde complète
$BACKUP_PATH = "$BACKUP_DIR\backup_falldetection_$TIMESTAMP.db"
Copy-Item -Path $DB_PATH -Destination $BACKUP_PATH

# Vérifier l'intégrité
& sqlite3 $BACKUP_PATH "PRAGMA integrity_check;"

# Compresser la sauvegarde
Compress-Archive -Path $BACKUP_PATH -DestinationPath "$BACKUP_PATH.zip"
Remove-Item $BACKUP_PATH

# Nettoyer les sauvegardes de plus de 30 jours
Get-ChildItem $BACKUP_DIR -Filter "backup_falldetection_*.zip" | 
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | 
    Remove-Item

Write-Host "Sauvegarde terminée: backup_falldetection_$TIMESTAMP.zip"

-- ============================================================================
-- Fin des procédures de sauvegarde
-- ============================================================================
