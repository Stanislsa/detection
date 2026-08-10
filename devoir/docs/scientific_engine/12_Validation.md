# 12 - Validation

## Validation et Tests

---

## Vue d'ensemble

La validation du système de détection de chute assure que le système fonctionne correctement, atteint les objectifs de performance et est fiable dans des conditions réelles. Ce document décrit les méthodes de validation, les critères d'acceptation et les procédures de test.

---

## Méthodes de Validation

### 1. Validation Croisée (Cross-Validation)

**Méthode :**
$$CV_k = \frac{1}{k} \sum_{i=1}^{k} Performance(D_i)$$

**Définition :**
Le dataset est divisé en k parties (folds). Le modèle est entraîné sur k-1 parties et testé sur la partie restante. Le processus est répété k fois.

**Valeur typique de k :** 5 ou 10

**Avantages :**
- Utilisation efficace des données
- Réduction de la variance de l'estimation
- Évaluation robuste de la performance

**Justification :**
**Référence :** R. Kohavi (1995) - A Study of Cross-Validation and Bootstrap for Accuracy Estimation
**DOI :** 10.1145/300343.300375

---

### 2. Validation Hold-Out

**Méthode :**
Division du dataset en :
- 70% entraînement
- 15% validation
- 15% test

**Définition :**
Le modèle est entraîné sur le dataset d'entraînement, les hyperparamètres sont ajustés sur le dataset de validation, et la performance finale est évaluée sur le dataset de test.

**Avantages :**
- Simple à mettre en œuvre
- Séparation claire des données
- Évaluation réaliste de la performance

**Justification :**
**Référence :** T. Hastie et al. (2009) - The Elements of Statistical Learning
**DOI :** 10.1007/978-0-387-84858-7

---

### 3. Validation Temporelle

**Méthode :**
Division chronologique du dataset :
- Entraînement : données antérieures
- Test : données ultérieures

**Définition :**
Le modèle est entraîné sur les données passées et testé sur les données futures, simulant un déploiement réel.

**Avantages :**
- Évaluation réaliste pour les systèmes en temps réel
- Détection du drift temporel
- Simulation de conditions réelles

**Justification :**
**Référence :** G. C. Cawley et al. (2010) - On Over-fitting in Model Selection and Subsequent Selection Bias
**DOI :** 10.1016/j.patcog.2010.09.005

---

## Critères de Validation

### Critères de Performance

| Métrique | Objectif Minimum | Objectif Idéal | Justification |
|----------|-----------------|----------------|---------------|
| Accuracy | ≥ 0.85 | ≥ 0.92 | Exactitude globale |
| Precision | ≥ 0.85 | ≥ 0.90 | Minimiser faux positifs |
| Recall | ≥ 0.80 | ≥ 0.85 | Maximiser détection |
| Specificity | ≥ 0.90 | ≥ 0.95 | Minimiser fausses alertes |
| F1-Score | ≥ 0.82 | ≥ 0.87 | Équilibre optimal |
| AUC-ROC | ≥ 0.85 | ≥ 0.92 | Performance globale |

### Critères Temporels

| Métrique | Objectif | Justification |
|----------|----------|---------------|
| Temps de détection | ≤ 200 ms | Intervention rapide |
| Temps d'alerte | ≤ 5 s | Notification rapide |
| Temps de réponse | ≤ 300 s | Intervention médicale |

### Critères de Qualité des Données

| Métrique | Objectif | Justification |
|----------|----------|---------------|
| Frame rate | ≥ 25 fps | Détection fluide |
| Confiance pose | ≥ 0.90 | Détection fiable |
| Complétude données | ≥ 0.95 | Analyse complète |

---

## Procédures de Test

### Test 1 : Détection de Chute

**Objectif :**
Vérifier que le système détecte correctement les chutes.

**Procédure :**
1. Charger une vidéo de chute annotée
2. Exécuter le pipeline de détection
3. Comparer le résultat avec l'annotation
4. Calculer les métriques de performance

**Critère de succès :**
- Recall ≥ 0.85
- Precision ≥ 0.85

**Justification :**
**Référence :** M. Kepski et al. (2012) - Fall detection using Kinect sensor
**DOI :** 10.1109/MBRA.2012.6222177

---

### Test 2 : Faux Positifs

**Objectif :**
Vérifier que le système ne génère pas de fausses alertes lors de mouvements normaux.

**Procédure :**
1. Charger des vidéos de mouvements normaux (marche, assis/debout)
2. Exécuter le pipeline de détection
3. Compter les fausses alertes
4. Calculer le taux de faux positifs

**Critère de succès :**
- FPR ≤ 0.05

**Justification :**
**Référence :** A. Bourke et al. (2010) - Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm
**DOI :** 10.1016/j.gaitpost.2009.10.004

---

### Test 3 : Temps de Détection

**Objectif :**
Vérifier que le système détecte les chutes rapidement.

**Procédure :**
1. Charger une vidéo de chute avec timestamps
2. Exécuter le pipeline de détection
3. Mesurer le temps entre le début de la chute et la détection
4. Calculer le temps moyen de détection

**Critère de succès :**
- Temps de détection ≤ 200 ms

**Justification :**
**Référence :** N. Noury et al. (2000) - A Fall Sensor Based on Kinematics
**DOI :** 10.1109/58.897022

---

### Test 4 : Robustesse aux Conditions d'Éclairage

**Objectif :**
Vérifier que le système fonctionne dans différentes conditions d'éclairage.

**Procédure :**
1. Tester avec des vidéos sous éclairage normal
2. Tester avec des vidéos sous faible éclairage
3. Tester avec des vidéos sous éclairage variable
4. Comparer les performances

**Critère de succès :**
- Variation de performance < 10%

**Justification :**
**Référence :** Google Research - MediaPipe Pose (2020)
**DOI :** 10.1145/3383090

---

### Test 5 : Robustesse aux Occlusions

**Objectif :**
Vérifier que le système fonctionne malgré les occlusions partielles.

**Procédure :**
1. Tester avec des vidéos sans occlusion
2. Tester avec des vidéos avec occlusion partielle (ex: bras caché)
3. Tester avec des vidéos avec occlusion sévère
4. Comparer les performances

**Critère de succès :**
- Performance avec occlusion légère ≥ 80% de la performance normale

**Justification :**
**Référence :** Google Research - MediaPipe Pose (2020)
**DOI :** 10.1145/3383090

---

## Dataset de Validation

### Composition du Dataset

| Type | Nombre de vidéos | Durée totale | Description |
|------|------------------|--------------|-------------|
| Chutes réelles | 100 | 10 min | Chutes annotées par des professionnels |
| Chutes simulées | 200 | 20 min | Chutes simulées par des acteurs |
| Mouvements normaux | 300 | 30 min | Marche, assis/debout, mouvements quotidiens |
| Activités ambiguës | 100 | 10 min | Mouvements qui ressemblent à des chutes |

### Sources de Données

1. **UP-Fall Detection Dataset**
   - 100 chutes réelles
   - 200 mouvements normaux
   - DOI : 10.1109/ACCESS.2020.3009606

2. **UR Fall Detection Dataset**
   - 70 chutes réelles
   - 40 mouvements normaux
   - DOI : 10.1016/j.bspc.2016.01.007

3. **MobiAct Dataset**
   - 600 activités
   - 40 chutes
   - DOI : 10.1371/journal.pone.0184474

### Annotation

Chaque vidéo est annotée avec :
- Type d'activité (chute/non-chute)
- Timestamp de début de chute
- Type de chute (avant, latéral, arrière)
- Gravité de la chute (légère, modérée, sévère)

---

## Analyse des Erreurs

### Types d'Erreurs

#### Erreur Type 1 : Faux Positif
**Définition :** Le système détecte une chute alors qu'il n'y en a pas.

**Causes possibles :**
- Mouvement rapide normal
- Seuils trop sensibles
- Occlusion partielle

**Correction :**
- Ajuster les seuils
- Ajouter des règles de filtrage
- Améliorer la robustesse aux occlusions

---

#### Erreur Type 2 : Faux Négatif
**Définition :** Le système ne détecte pas une chute réelle.

**Causes possibles :**
- Chute lente progressive
- Seuils trop élevés
- Mauvaise qualité de détection de pose

**Correction :**
- Abaisser les seuils
- Ajouter des règles pour les chutes lentes
- Améliorer la qualité de détection de pose

---

#### Erreur Type 3 : Retard de Détection
**Définition :** Le système détecte la chute mais avec un retard significatif.

**Causes possibles :**
- Latence du pipeline
- Taux de trames insuffisant
- Algorithme de détection lent

**Correction :**
- Optimiser le pipeline
- Augmenter le taux de trames
- Optimiser l'algorithme

---

### Matrice de Confusion

| Prédit \ Réel | Chute | Non-Chute |
|---------------|-------|-----------|
| Chute | TP | FP |
| Non-Chute | FN | TN |

**Calcul des métriques :**
- Accuracy = (TP + TN) / (TP + TN + FP + FN)
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- Specificity = TN / (TN + FP)

---

## Calibration des Seuils

### Méthode de Calibration

1. **Collecte de données** : Enregistrer les indicateurs pour chaque événement
2. **Analyse ROC** : Générer la courbe ROC pour chaque seuil
3. **Optimisation** : Choisir le seuil qui maximise le F1-score
4. **Validation** : Valider sur un dataset indépendant

### Courbe ROC

La courbe ROC (Receiver Operating Characteristic) trace le taux de vrais positifs en fonction du taux de faux positifs pour différents seuils.

**AUC-ROC (Area Under Curve) :**
- AUC = 0.5 : Performance aléatoire
- AUC = 0.7 : Performance acceptable
- AUC = 0.8 : Performance bonne
- AUC = 0.9 : Performance excellente
- AUC = 1.0 : Performance parfaite

**Objectif :** AUC-ROC ≥ 0.92

---

### Courbe Precision-Recall

La courbe Precision-Recall trace la précision en fonction du recall pour différents seuils.

**AP (Average Precision) :**
- AP = 0.5 : Performance aléatoire
- AP = 0.7 : Performance acceptable
- AP = 0.8 : Performance bonne
- AP = 0.9 : Performance excellente
- AP = 1.0 : Performance parfaite

**Objectif :** AP ≥ 0.90

---

## Validation sur le Terrain

### Déploiement Pilote

**Durée :** 3 mois

**Lieux :**
- 5 foyers de personnes âgées
- 10 patients avec différents niveaux de mobilité

**Objectifs :**
- Valider le système en conditions réelles
- Collecter des données de performance
- Identifier les problèmes d'acceptation

**Métriques à suivre :**
- Taux de détection
- Taux de fausses alertes
- Temps de réponse
- Satisfaction des utilisateurs

---

### Feedback des Utilisateurs

**Méthode :**
- Questionnaires mensuels
- Entretiens avec les patients
- Entretiens avec les soignants
- Analyse des logs système

**Critères d'Acceptation :**
- Satisfaction ≥ 80%
- Taux d'utilisation ≥ 90%
- Taux de fausses alertes < 10%

---

## Maintenance de la Validation

### Validation Continue

**Fréquence :** Mensuelle

**Procédure :**
1. Collecter les nouvelles données de détection
2. Comparer avec les annotations (si disponibles)
3. Calculer les métriques de performance
4. Ajuster les seuils si nécessaire

**Alerte :** Si la performance chute de plus de 5% par rapport à la baseline

---

### Recalibration Périodique

**Fréquence :** Trimestrielle

**Procédure :**
1. Analyser les données accumulées
2. Recalculer les seuils optimaux
3. Tester les nouveaux seuils sur un dataset de validation
4. Déployer si amélioration > 2%

---

## Références

1. R. Kohavi - A Study of Cross-Validation and Bootstrap for Accuracy Estimation (1995) - DOI: 10.1145/300343.300375
2. T. Hastie et al. - The Elements of Statistical Learning (2009) - DOI: 10.1007/978-0-387-84858-7
3. G. C. Cawley et al. - On Over-fitting in Model Selection (2010) - DOI: 10.1016/j.patcog.2010.09.005
4. M. Kepski et al. - Fall detection using Kinect sensor (2012) - DOI: 10.1109/MBRA.2012.6222177
5. A. Bourke et al. - Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm (2010) - DOI: 10.1016/j.gaitpost.2009.10.004
6. N. Noury et al. - A Fall Sensor Based on Kinematics (2000) - DOI: 10.1109/58.897022
7. Google Research - MediaPipe Pose (2020) - DOI: 10.1145/3383090
8. UP-Fall Detection Dataset - DOI: 10.1109/ACCESS.2020.3009606
9. UR Fall Detection Dataset - DOI: 10.1016/j.bspc.2016.01.007
10. MobiAct Dataset - DOI: 10.1371/journal.pone.0184474

---

## Implémentations Python Associées

- `tests/validation.py` : procédures de validation
- `tests/cross_validation.py` : validation croisée
- `tests/error_analysis.py` : analyse des erreurs
- `tests/roc_analysis.py` : analyse ROC et Precision-Recall
- `tests/threshold_calibration.py` : calibration des seuils
