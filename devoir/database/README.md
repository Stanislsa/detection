# Base de Données - Système de Détection de Chutes par Edge AI

## 📋 Description

Base de données professionnelle normalisée (3NF) pour un système intelligent d'estimation en temps réel de la détection des chutes à domicile basé sur l'Edge AI.

**Technologies :**
- SQLite
- OpenCV
- MediaPipe Pose
- FastAPI
- PyQt6
- Telegram Bot API

---

## 📁 Structure des Fichiers

```
database/
├── README.md                                    # Ce fichier
├── 01_MCD_Merise.md                            # Modèle Conceptuel de Données (Merise)
├── 02_MLD_Merise.md                            # Modèle Logique de Données (Merise)
├── 03_MPD_Merise.md                            # Modèle Physique de Données (Merise)
├── 04_UML_Class_Diagram_PlantUML.puml          # Diagramme de classes UML (PlantUML)
├── 05_Schema_Complet_SQLite.sql                # Schéma SQL complet (18 tables)
├── 06_Vues_SQL.sql                             # 25 vues SQL utiles
├── 07_Triggers.sql                             # 30 triggers pour l'intégrité
├── 08_Procedures_Sauvegarde.sql                # Procédures de sauvegarde
├── 09_Donnees_Test.sql                         # Données de test
└── 10_Requetes_SQL_Principales.sql             # Requêtes CRUD et statistiques
```

---

## 🗄️ Tables de la Base de Données (18 tables)

| # | Table | Description |
|---|-------|-------------|
| 1 | Users | Utilisateurs du système (mot de passe optionnel) |
| 2 | Patients | Patients surveillés |
| 3 | EmergencyContacts | Contacts d'urgence des patients |
| 4 | Rooms | Pièces du domicile |
| 5 | Cameras | Caméras de surveillance |
| 6 | MonitoringSessions | Sessions de surveillance |
| 7 | SkeletonFrames | Trames squelette (33 points MediaPipe) |
| 8 | Falls | Détections de chute |
| 9 | Alerts | Alertes générées |
| 10 | Notifications | Notifications envoyées |
| 11 | IncidentHistory | Historique des incidents |
| 12 | SimulationVideos | Vidéos de simulation |
| 13 | SimulationResults | Résultats de simulation |
| 14 | AISettings | Paramètres de l'IA |
| 15 | KPIs | Indicateurs de performance |
| 16 | AuditLogs | Journal d'audit |
| 17 | SecurityLogs | Journal de sécurité |
| 18 | SystemSettings | Paramètres système |

---

## 🚀 Installation Rapide

### 1. Créer la base de données

```bash
# Naviguer vers le répertoire database
cd database

# Créer la base de données avec le schéma complet
sqlite3 falldetection.db < 05_Schema_Complet_SQLite.sql
```

### 2. Appliquer les vues

```bash
sqlite3 falldetection.db < 06_Vues_SQL.sql
```

### 3. Appliquer les triggers

```bash
sqlite3 falldetection.db < 07_Triggers.sql
```

### 4. Insérer les données de test

```bash
sqlite3 falldetection.db < 09_Donnees_Test.sql
```

### 5. Vérifier l'installation

```bash
sqlite3 falldetection.db
> .tables
> SELECT COUNT(*) FROM Users;
> SELECT COUNT(*) FROM Patients;
> .quit
```

---

## 📊 Diagramme des Relations

```
Users (1) → (N) Patients
Patients (1) → (N) EmergencyContacts
Patients (1) → (N) Rooms
Rooms (1) → (N) Cameras
Cameras (1) → (N) MonitoringSessions
Patients (1) → (N) MonitoringSessions
MonitoringSessions (1) → (N) SkeletonFrames
MonitoringSessions (1) → (N) Falls
Falls (1) → (N) Alerts
Alerts (1) → (N) Notifications
Falls (1) → (N) IncidentHistory
SimulationVideos (1) → (N) SimulationResults
Users (1) → (N) AuditLogs
Users (1) → (N) SecurityLogs
```

---

## 🔧 Configuration

### Paramètres IA par défaut

| Paramètre | Valeur par défaut | Description |
|-----------|-------------------|-------------|
| threshold_angle | 45.0° | Seuil d'angle du tronc |
| threshold_speed | 2.0 m/s | Seuil de vitesse verticale |
| threshold_acceleration | 5.0 m/s² | Seuil d'accélération |
| threshold_immobility | 30.0 s | Seuil d'immobilité |
| threshold_floor_time | 60.0 s | Seuil de temps au sol |
| threshold_severity | 0.7 | Seuil de gravité |

### Pondérations IA par défaut

| Pondération | Valeur |
|-------------|--------|
| weight_angle | 0.20 |
| weight_speed | 0.25 |
| weight_acceleration | 0.20 |
| weight_immobility | 0.15 |
| weight_floor_time | 0.20 |

---

## 📈 Vues SQL Disponibles (25 vues)

| Vue | Description |
|-----|-------------|
| View_Patients_Complet | Patients avec informations utilisateur |
| View_Contacts_Urgence | Contacts d'urgence par patient |
| View_Cameras_Detail | Caméras avec détails de pièce et patient |
| View_Sessions_Actives | Sessions de surveillance actives |
| View_Chutes_Detectees | Chutes détectées avec détails |
| View_Alertes_Actives | Alertes non accusées |
| View_Notifications_Statut | Statistiques des notifications |
| View_Statistiques_Chutes_Patient | Statistiques de chutes par patient |
| View_Statistiques_Chutes_Piece | Statistiques de chutes par pièce |
| View_Temps_Reponse_Alerte | Temps de réponse par niveau d'alerte |
| View_Sessions_Par_Jour | Sessions par jour |
| View_Chutes_Par_Jour | Chutes par jour |
| View_Performances_Detection | Performances de détection (KPIs) |
| View_Utilisateurs_Par_Role | Utilisateurs par rôle |
| View_Cameras_Par_Statut | Caméras par statut |
| View_Audit_Recents | Logs d'audit récents |
| View_Securite_Evenements | Événements de sécurité |
| View_Connexions_Echouees | Tentatives de connexion échouées |
| View_Simulations_Resultats | Simulations et résultats |
| View_Historique_Incident | Historique des incidents |
| View_Alertes_Non_Acusees | Alertes non accusées par criticité |
| View_Notifications_Echouees | Notifications échouées |
| View_Resume_Quotidien | Résumé quotidien |
| View_Patients_Risque_Eleve | Patients à risque élevé |
| View_Statistiques_Notifications | Statistiques de notifications |

---

## 🔐 Sécurité

### Contraintes d'intégrité

- **Clés étrangères** avec CASCADE DELETE
- **Contraintes CHECK** sur toutes les colonnes numériques
- **Contraintes UNIQUE** sur les emails et adresses IP
- **Contraintes NOT NULL** sur les colonnes obligatoires

### Triggers de sécurité

- Blocage après 5 tentatives de connexion échouées
- Journalisation de toutes les modifications
- Validation des pondérations IA (somme = 1.0)
- Interdiction de modifier les chutes confirmées

---

## 💾 Sauvegarde et Restauration

### Sauvegarde complète

```bash
sqlite3 falldetection.db "VACUUM INTO backup_$(date +%Y%m%d).db"
```

### Sauvegarde incrémentielle

```bash
sqlite3 falldetection.db < 08_Procedures_Sauvegarde.sql
```

### Export CSV

```bash
sqlite3 falldetection.db
> .headers on
> .mode csv
> .output export_patients.csv
> SELECT * FROM Patients;
> .quit
```

---

## 📝 Requêtes Utiles

### Lister les chutes confirmées

```sql
SELECT * FROM Falls WHERE result = 'CHUTE_CONFIRMEE' ORDER BY detection_time DESC;
```

### Lister les alertes non accusées

```sql
SELECT * FROM Alerts WHERE acknowledged = 0 ORDER BY sent_at DESC;
```

### Statistiques de chutes par patient

```sql
SELECT * FROM View_Statistiques_Chutes_Patient;
```

### Résumé quotidien

```sql
SELECT * FROM View_Resume_Quotidien;
```

---

## 🧪 Tests

### Exécuter les tests

```bash
# Charger les données de test
sqlite3 falldetection.db < 09_Donnees_Test.sql

# Vérifier les données
sqlite3 falldetection.db
> SELECT COUNT(*) FROM Users;  -- Doit retourner 8
> SELECT COUNT(*) FROM Patients;  -- Doit retourner 4
> SELECT COUNT(*) FROM Falls;  -- Doit retourner 12
> SELECT COUNT(*) FROM Alerts;  -- Doit retourner 12
> .quit
```

---

## 📚 Documentation

### Modélisation Merise

- **01_MCD_Merise.md** : Modèle Conceptuel de Données
- **02_MLD_Merise.md** : Modèle Logique de Données
- **03_MPD_Merise.md** : Modèle Physique de Données

### Diagramme UML

- **04_UML_Class_Diagram_PlantUML.puml** : Diagramme de classes

Pour visualiser le diagramme UML :
```bash
# Installer PlantUML
# Ouvrir le fichier .puml dans un éditeur compatible PlantUML
# Ou utiliser : http://www.plantuml.com/plantuml/
```

---

## 🔍 Maintenance

### Nettoyage des anciennes données

```sql
-- Supprimer les trames squelette de plus de 30 jours
DELETE FROM SkeletonFrames WHERE timestamp < datetime('now', '-30 days');

-- Supprimer les logs de plus de 365 jours
DELETE FROM AuditLogs WHERE timestamp < datetime('now', '-365 days');
DELETE FROM SecurityLogs WHERE timestamp < datetime('now', '-365 days');
```

### Optimisation

```sql
-- Analyser les tables
ANALYZE;

-- Reconstruire la base de données
VACUUM;

-- Reconstruire les index
REINDEX;
```

### Vérification de l'intégrité

```sql
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

---

## 🐛 Dépannage

### Erreur : "FOREIGN KEY constraint failed"

**Solution :** Vérifier que les clés étrangères référencent des enregistrements existants.

```sql
PRAGMA foreign_keys = ON;
```

### Erreur : "UNIQUE constraint failed"

**Solution :** Vérifier que l'email ou l'adresse IP n'est pas déjà utilisé.

### Erreur : "CHECK constraint failed"

**Solution :** Vérifier que les valeurs respectent les contraintes CHECK (âge entre 0-150, etc.).

---

## 📞 Support

Pour toute question ou problème concernant la base de données, consultez :

1. La documentation Merise (fichiers 01-03)
2. Le schéma SQL complet (fichier 05)
3. Les exemples de requêtes (fichier 10)

---

## 📄 Licence

Ce projet est confidentiel et propriétaire.

---

## 🔄 Version

**Version :** 1.0  
**Date :** Juillet 2026  
**Auteur :** Architecte de Bases de Données Senior

---

## ✅ Checklist de déploiement

- [ ] Exécuter le schéma SQL complet
- [ ] Appliquer les vues SQL
- [ ] Appliquer les triggers
- [ ] Insérer les données de test
- [ ] Configurer les paramètres système
- [ ] Configurer les paramètres IA
- [ ] Configurer le token Telegram
- [ ] Configurer le serveur SMTP
- [ ] Tester les sauvegardes
- [ ] Vérifier l'intégrité de la base de données
- [ ] Documenter les procédures de maintenance

---

**Fin de la documentation**
