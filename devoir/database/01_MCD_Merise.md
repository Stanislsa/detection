# MCD - Modèle Conceptuel de Données (Merise)
## Système de Détection de Chutes par Edge AI

---

### Entités et leurs propriétés

#### 1. UTILISATEUR
- **id_utilisateur** (Identifiant unique)
- **prenom** (Prénom de l'utilisateur)
- **nom** (Nom de l'utilisateur)
- **email** (Adresse email unique)
- **mot_de_passe_hash** (Mot de passe haché, optionnel)
- **telephone** (Numéro de téléphone)
- **role** (Rôle: ADMIN, MEDECIN, FAMILLE, TECHNICIEN)
- **statut** (Statut: ACTIF, INACTIF, SUSPENDU)
- **date_creation** (Date de création du compte)
- **date_modification** (Date de dernière modification)

#### 2. PATIENT
- **id_patient** (Identifiant unique)
- **#id_utilisateur** (Référence vers UTILISATEUR)
- **age** (Âge du patient)
- **genre** (Genre: H, F, AUTRE)
- **poids** (Poids en kg)
- **taille** (Taille en cm)
- **niveau_mobilite** (Niveau de mobilité: AUTONOME, CANNE, DEAMBULATEUR, FAUTEUIL)
- **notes_medicales** (Notes médicales)
- **adresse** (Adresse du domicile)
- **latitude** (Coordonnée GPS latitude)
- **longitude** (Coordonnée GPS longitude)

#### 3. CONTACT_URGENCE
- **id_contact** (Identifiant unique)
- **#id_patient** (Référence vers PATIENT)
- **nom_complet** (Nom complet du contact)
- **relation** (Relation avec le patient)
- **telephone** (Numéro de téléphone)
- **email** (Adresse email)
- **priorite** (Priorité: 1=Primaire, 2=Secondaire, 3=Tertiaire)

#### 4. PIECE
- **id_piece** (Identifiant unique)
- **#id_patient** (Référence vers PATIENT)
- **nom_piece** (Nom de la pièce: Salon, Cuisine, Chambre, SDB)
- **etage** (Étage: 0=RDC, 1, 2, etc.)
- **description** (Description de la pièce)

#### 5. CAMERA
- **id_camera** (Identifiant unique)
- **#id_piece** (Référence vers PIECE)
- **nom_camera** (Nom de la caméra)
- **adresse_ip** (Adresse IP de la caméra)
- **url_rtsp** (URL du flux RTSP)
- **resolution** (Résolution: 1080p, 720p, etc.)
- **fps** (Images par seconde)
- **statut** (Statut: ACTIVE, INACTIVE, MAINTENANCE)
- **date_installation** (Date d'installation)

#### 6. SESSION_SURVEILLANCE
- **id_session** (Identifiant unique)
- **#id_camera** (Référence vers CAMERA)
- **#id_patient** (Référence vers PATIENT)
- **heure_debut** (Heure de début de session)
- **heure_fin** (Heure de fin de session)
- **duree** (Durée en secondes)
- **statut** (Statut: EN_COURS, TERMINEE, INTERROMPUE)

#### 7. TRAME_SQUELETTE
- **id_trame** (Identifiant unique)
- **#id_session** (Référence vers SESSION_SURVEILLANCE)
- **horodatage** (Horodatage de la trame)
- **numero_trame** (Numéro de la trame)
- **33 points MediaPipe** (x, y, z pour chaque point du squelette)

#### 8. CHUTE
- **id_chute** (Identifiant unique)
- **#id_session** (Référence vers SESSION_SURVEILLANCE)
- **heure_detection** (Heure de détection)
- **angle_tronc** (Angle du tronc en degrés)
- **hauteur_corps** (Hauteur du corps en pixels)
- **vitesse_verticale** (Vitesse verticale en m/s)
- **acceleration** (Accélération en m/s²)
- **centre_gravite_x** (Coordonnée X du centre de gravité)
- **centre_gravite_y** (Coordonnée Y du centre de gravité)
- **vitesse_centre_gravite** (Vitesse du centre de gravité)
- **duree_immobilite** (Durée d'immobilité en secondes)
- **temps_au_sol** (Temps passé au sol en secondes)
- **energie_cinetique** (Énergie cinétique)
- **score_confiance** (Score de confiance IA)
- **score_chute** (Score de chute calculé)
- **score_gravite** (Score de gravité)
- **probabilite_blessure** (Probabilité de blessure en %)
- **resultat** (Résultat: CHUTE_CONFIRMEE, FAUX_POSITIF, INDETERMINE)

#### 9. ALERTE
- **id_alerte** (Identifiant unique)
- **#id_chute** (Référence vers CHUTE)
- **niveau_alerte** (Niveau: CRITIQUE, HAUTE, MOYENNE, BASSE)
- **heure_envoi** (Heure d'envoi de l'alerte)
- **accuse_reception** (Booléen: alerte accusée ou non)
- **temps_reponse** (Temps de réponse en secondes)

#### 10. NOTIFICATION
- **id_notification** (Identifiant unique)
- **#id_alerte** (Référence vers ALERTE)
- **canal** (Canal: TELEGRAM, EMAIL, SMS, PUSH)
- **destinataire** (Destinataire de la notification)
- **statut** (Statut: ENVOYE, EN_ECHEC, EN_ATTENTE)
- **heure_envoi** (Heure d'envoi)

#### 11. HISTORIQUE_INCIDENT
- **id_historique** (Identifiant unique)
- **#id_chute** (Référence vers CHUTE)
- **type_evenement** (Type d'événement)
- **description** (Description de l'événement)
- **horodatage** (Horodatage de l'événement)

#### 12. VIDEO_SIMULATION
- **id_video** (Identifiant unique)
- **nom_fichier** (Nom du fichier vidéo)
- **description** (Description de la simulation)
- **resultat_attendu** (Résultat attendu: CHUTE, PAS_CHUTE)
- **date_upload** (Date d'upload)

#### 13. RESULTAT_SIMULATION
- **id_resultat** (Identifiant unique)
- **#id_video** (Référence vers VIDEO_SIMULATION)
- **precision** (Précision)
- **rappel** (Rappel/Recall)
- **score_f1** (Score F1)
- **faux_positif** (Nombre de faux positifs)
- **faux_negatif** (Nombre de faux négatifs)
- **temps_detection** (Temps de détection en ms)

#### 14. PARAMETRES_IA
- **id_parametre** (Identifiant unique)
- **seuil_angle** (Seuil d'angle en degrés)
- **seuil_vitesse** (Seuil de vitesse en m/s)
- **seuil_acceleration** (Seuil d'accélération en m/s²)
- **seuil_immobilite** (Seuil d'immobilité en secondes)
- **seuil_temps_sol** (Seuil de temps au sol en secondes)
- **seuil_gravite** (Seuil de gravité)
- **ponderation_angle** (Pondération angle)
- **ponderation_vitesse** (Pondération vitesse)
- **ponderation_acceleration** (Pondération accélération)
- **ponderation_immobilite** (Pondération immobilité)
- **ponderation_temps_sol** (Pondération temps au sol)
- **date_modification** (Date de dernière modification)

#### 15. KPI
- **id_kpi** (Identifiant unique)
- **exactitude** (Accuracy)
- **precision** (Precision)
- **rappel** (Recall)
- **specificite** (Specificity)
- **sensibilite** (Sensitivity)
- **score_f1** (F1-Score)
- **taux_faux_positif** (False Positive Rate)
- **taux_faux_negatif** (False Negative Rate)
- **temps_detection_moyen** (Mean Detection Time)
- **temps_alerte_moyen** (Mean Alert Time)
- **disponibilite** (Uptime en %)
- **date_calcul** (Date de calcul)

#### 16. JOURNAL_AUDIT
- **id_audit** (Identifiant unique)
- **#id_utilisateur** (Référence vers UTILISATEUR)
- **action** (Action: CONNEXION, MODIFICATION, SUPPRESSION, EXPORT, PARAMETRES)
- **table_concernee** (Table concernée)
- **enregistrement_id** (ID de l'enregistrement)
- **anciennes_valeurs** (Anciennes valeurs JSON)
- **nouvelles_valeurs** (Nouvelles valeurs JSON)
- **horodatage** (Horodatage de l'action)
- **adresse_ip** (Adresse IP de la source)

#### 17. JOURNAL_SECURITE
- **id_securite** (Identifiant unique)
- **#id_utilisateur** (Référence vers UTILISATEUR)
- **type_evenement** (Type: TENTATIVE_CONNEXION, MFA, CHANGEMENT_MDP, ROTATION_CLES, ACCES_VIDEO)
- **description** (Description de l'événement)
- **reussi** (Booléen: succès ou échec)
- **horodatage** (Horodatage)
- **adresse_ip** (Adresse IP)

#### 18. PARAMETRES_SYSTEME
- **id_parametre** (Identifiant unique)
- **cle** (Clé du paramètre)
- **valeur** (Valeur du paramètre)
- **description** (Description)
- **date_modification** (Date de modification)

---

### Relations entre entités

#### Relations 1:N (Un vers plusieurs)

1. **UTILISATEUR (1) → PATIENT (N)**
   - Un utilisateur peut être associé à plusieurs patients
   - Un patient est associé à un seul utilisateur

2. **PATIENT (1) → CONTACT_URGENCE (N)**
   - Un patient peut avoir plusieurs contacts d'urgence
   - Un contact d'urgence appartient à un seul patient

3. **PATIENT (1) → PIECE (N)**
   - Un patient peut avoir plusieurs pièces
   - Une pièce appartient à un seul patient

4. **PIECE (1) → CAMERA (N)**
   - Une pièce peut avoir plusieurs caméras
   - Une caméra est installée dans une seule pièce

5. **CAMERA (1) → SESSION_SURVEILLANCE (N)**
   - Une caméra peut avoir plusieurs sessions
   - Une session est liée à une seule caméra

6. **PATIENT (1) → SESSION_SURVEILLANCE (N)**
   - Un patient peut avoir plusieurs sessions
   - Une session est liée à un seul patient

7. **SESSION_SURVEILLANCE (1) → TRAME_SQUELETTE (N)**
   - Une session peut avoir plusieurs trames
   - Une trame appartient à une seule session

8. **SESSION_SURVEILLANCE (1) → CHUTE (N)**
   - Une session peut avoir plusieurs détections de chute
   - Une chute est détectée dans une seule session

9. **CHUTE (1) → ALERTE (N)**
   - Une chute peut générer plusieurs alertes
   - Une alerte est liée à une seule chute

10. **ALERTE (1) → NOTIFICATION (N)**
    - Une alerte peut avoir plusieurs notifications
    - Une notification est liée à une seule alerte

11. **CHUTE (1) → HISTORIQUE_INCIDENT (N)**
    - Une chute peut avoir plusieurs entrées d'historique
    - Une entrée d'historique est liée à une seule chute

12. **VIDEO_SIMULATION (1) → RESULTAT_SIMULATION (N)**
    - Une vidéo peut avoir plusieurs résultats de simulation
    - Un résultat est lié à une seule vidéo

13. **UTILISATEUR (1) → JOURNAL_AUDIT (N)**
    - Un utilisateur peut avoir plusieurs entrées d'audit
    - Une entrée d'audit est liée à un utilisateur

14. **UTILISATEUR (1) → JOURNAL_SECURITE (N)**
    - Un utilisateur peut avoir plusieurs entrées de sécurité
    - Une entrée de sécurité est liée à un utilisateur

#### Relations 1:1 (Un vers un)

- **PARAMETRES_IA** : Singleton (un seul enregistrement)
- **PARAMETRES_SYSTEME** : Plusieurs enregistrements uniques par clé

#### Relations N:N (Plusieurs vers plusieurs)

Aucune relation N:N directe dans ce modèle.

---

### Cardinalités

```
UTILISATEUR 1,n ---- 1,1 PATIENT
PATIENT 1,n ---- 1,1 CONTACT_URGENCE
PATIENT 1,n ---- 1,1 PIECE
PIECE 1,n ---- 1,1 CAMERA
CAMERA 1,n ---- 1,1 SESSION_SURVEILLANCE
PATIENT 1,n ---- 1,1 SESSION_SURVEILLANCE
SESSION_SURVEILLANCE 1,n ---- 1,1 TRAME_SQUELETTE
SESSION_SURVEILLANCE 0,n ---- 1,1 CHUTE
CHUTE 1,n ---- 1,1 ALERTE
ALERTE 1,n ---- 1,1 NOTIFICATION
CHUTE 0,n ---- 1,1 HISTORIQUE_INCIDENT
VIDEO_SIMULATION 1,n ---- 1,1 RESULTAT_SIMULATION
UTILISATEUR 0,n ---- 1,1 JOURNAL_AUDIT
UTILISATEUR 0,n ---- 1,1 JOURNAL_SECURITE
```

---

### Contraintes d'intégrité

#### Contraintes d'entité
- Toutes les entités ont un identifiant unique
- Les clés primaires sont uniques et non nulles

#### Contraintes de référence
- Toutes les clés étrangères doivent référencer une clé primaire existante
- Intégrité référentielle sur toutes les relations

#### Contraintes de domaine
- **genre** ∈ {H, F, AUTRE}
- **role** ∈ {ADMIN, MEDECIN, FAMILLE, TECHNICIEN}
- **statut** (utilisateur) ∈ {ACTIF, INACTIF, SUSPENDU}
- **statut** (caméra) ∈ {ACTIVE, INACTIVE, MAINTENANCE}
- **statut** (session) ∈ {EN_COURS, TERMINEE, INTERROMPUE}
- **niveau_mobilite** ∈ {AUTONOME, CANNE, DEAMBULATEUR, FAUTEUIL}
- **niveau_alerte** ∈ {CRITIQUE, HAUTE, MOYENNE, BASSE}
- **canal** ∈ {TELEGRAM, EMAIL, SMS, PUSH}
- **statut** (notification) ∈ {ENVOYE, EN_ECHEC, EN_ATTENTE}
- **resultat** (chute) ∈ {CHUTE_CONFIRMEE, FAUX_POSITIF, INDETERMINE}
- **resultat_attendu** ∈ {CHUTE, PAS_CHUTE}
- **action** (audit) ∈ {CONNEXION, MODIFICATION, SUPPRESSION, EXPORT, PARAMETRES}
- **type_evenement** (sécurité) ∈ {TENTATIVE_CONNEXION, MFA, CHANGEMENT_MDP, ROTATION_CLES, ACCES_VIDEO}

#### Contraintes de valeur
- **age** ≥ 0 et ≤ 150
- **poids** ≥ 0 et ≤ 300
- **taille** ≥ 0 et ≤ 250
- **priorite** ∈ {1, 2, 3}
- **score_confiance** ∈ [0, 1]
- **score_chute** ∈ [0, 1]
- **score_gravite** ∈ [0, 1]
- **probabilite_blessure** ∈ [0, 100]
- **precision** ∈ [0, 1]
- **rappel** ∈ [0, 1]
- **score_f1** ∈ [0, 1]
- **disponibilite** ∈ [0, 100]

---

### Règles de gestion

#### RG1 - Gestion des utilisateurs
- Un utilisateur doit avoir un email unique
- Un mot de passe doit être haché avant stockage
- Un utilisateur ne peut avoir qu'un seul rôle

#### RG2 - Gestion des patients
- Un patient doit être associé à un utilisateur
- Un patient doit avoir au moins un contact d'urgence
- Un patient doit avoir au moins une pièce configurée

#### RG3 - Gestion des caméras
- Une caméra doit être installée dans une pièce
- Une caméra doit avoir une adresse IP unique
- Le flux RTSP doit être valide

#### RG4 - Gestion des sessions
- Une session doit être liée à une caméra et un patient
- L'heure de fin doit être postérieure à l'heure de début
- La durée est calculée automatiquement

#### RG5 - Gestion des chutes
- Une chute est détectée lors d'une session
- Le score de gravité est calculé automatiquement
- La probabilité de blessure est estimée par l'IA

#### RG6 - Gestion des alertes
- Une chute confirmée génère automatiquement une alerte
- Une alerte critique doit être envoyée immédiatement
- Le temps de réponse est calculé à la réception

#### RG7 - Gestion des notifications
- Une alerte génère des notifications sur plusieurs canaux
- Les notifications Telegram utilisent le bot API
- Les notifications échouées doivent être réessayées

#### RG8 - Gestion des paramètres IA
- Les seuils de détection sont modifiables
- Les pondérations sont ajustables
- Toute modification est journalisée

#### RG9 - Gestion de la sécurité
- Toute tentative de connexion est journalisée
- Les changements de mot de passe sont tracés
- L'accès aux vidéos est surveillé

#### RG10 - Gestion des audits
- Toute modification de données est auditée
- Les exports sont tracés
- Les suppressions sont journalisées
