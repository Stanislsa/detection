# ScientificEngine - Index

## 📚 Documentation Scientifique

Système de Détection de Chutes par Edge AI - Moteur Scientifique

---

## 🎯 Objectif

Ce dossier contient la documentation scientifique complète du moteur de détection de chutes. Chaque formule, algorithme et décision est justifié par la littérature scientifique et traçable jusqu'à son implémentation Python.

---

## 📖 Structure de la Documentation

| Fichier | Contenu | Implémentation Python |
|---------|---------|----------------------|
| **00_Index.md** | Index principal (ce fichier) | - |
| **01_Geometry.md** | Géométrie euclidienne, distances, centres | `formulas/distance.py`, `formulas/vectors.py` |
| **02_LinearAlgebra.md** | Algèbre linéaire, vecteurs, matrices | `formulas/vectors.py` |
| **03_Trigonometry.md** | Trigonométrie, angles, rotations | `formulas/angles.py` |
| **04_Kinematics.md** | Cinématique, vitesse, accélération | `formulas/kinematics.py` |
| **05_Dynamics.md** | Dynamique, forces, énergie | `formulas/dynamics.py` |
| **06_Biomechanics.md** | Biomécanique humaine, posture | `formulas/biomechanics.py` |
| **07_FallDetectionLogic.md** | Logique de détection de chute | `ai/fall_detector.py` |
| **08_DecisionEngine.md** | Moteur de décision, seuils | `decision/decision_engine.py` |
| **09_SeverityModel.md** | Modèle de gravité de chute | `formulas/scoring.py` |
| **10_InjuryProbability.md** | Probabilité de blessure | `formulas/probability.py` |
| **11_KPI.md** | Indicateurs de performance | `metrics/kpi.py` |
| **12_Validation.md** | Validation et tests | `tests/validation.py` |
| **13_References.md** | Bibliographie scientifique | - |

---

## 🔗 Flux de Documentation vers Code

```
ScientificEngine/01_Geometry.md
        │
        ▼
math/distance.py
math/vectors.py
math/angles.py

ScientificEngine/04_Kinematics.md
        │
        ▼
physics/velocity.py
physics/acceleration.py

ScientificEngine/06_Biomechanics.md
        │
        ▼
biomechanics/posture.py
biomechanics/center_of_gravity.py

ScientificEngine/07_FallDetectionLogic.md
        │
        ▼
ai/fall_detector.py

ScientificEngine/08_DecisionEngine.md
        │
        ▼
decision/decision_engine.py

ScientificEngine/09_SeverityModel.md
        │
        ▼
decision/severity.py

ScientificEngine/10_InjuryProbability.md
        │
        ▼
decision/injury_probability.py
```

---

## 📐 Formules Documentées

### Géométrie (01_Geometry.md)
- Distance euclidienne
- Produit scalaire
- Produit vectoriel
- Norme vectorielle
- Projection
- Centre géométrique

### Algèbre Linéaire (02_LinearAlgebra.md)
- Addition de vecteurs
- Multiplication scalaire
- Produit scalaire
- Produit vectoriel
- Matrice de rotation

### Trigonométrie (03_Trigonometry.md)
- Fonctions trigonométriques
- Théorème de Pythagore
- Loi des cosinus
- Calcul d'angles
- Rotations 2D/3D

### Cinématique (04_Kinematics.md)
- Vitesse moyenne
- Vitesse instantanée
- Accélération
- Vitesse angulaire
- Déplacement

### Dynamique (05_Dynamics.md)
- Deuxième loi de Newton
- Énergie cinétique
- Travail
- Impulsion
- Moment cinétique

### Biomécanique (06_Biomechanics.md)
- Angle du tronc
- Angle tête-tronc
- Centre de gravité humain
- Hauteur du bassin
- Orientation posturale

---

## 🧠 Logique de Détection (07_FallDetectionLogic.md)

### Pipeline de Détection

1. **Extraction des 33 points MediaPipe**
2. **Calcul des vecteurs**
3. **Calcul des angles**
4. **Calcul des vitesses**
5. **Calcul des accélérations**
6. **Calcul du centre de gravité**
7. **Détection d'immobilité**
8. **Fusion multicritère**
9. **Décision finale**

Chaque étape est justifiée par la littérature scientifique.

---

## ⚙️ Moteur de Décision (08_DecisionEngine.md)

### Règles de Décision

- **Angle du tronc** : Seuil configurable (défaut: 45°)
- **Vitesse verticale** : Seuil configurable (défaut: 2.0 m/s)
- **Accélération** : Seuil configurable (défaut: 5.0 m/s²)
- **Immobilite** : Seuil configurable (défaut: 30 s)
- **Temps au sol** : Seuil configurable (défaut: 60 s)

### Fusion Multicritère

Score de chute = Σ(pondération_i × indicateur_i)

Les pondérations sont configurables et leur somme doit égaler 1.0.

---

## 📊 Modèle de Gravité (09_SeverityModel.md)

### Indicateurs de Gravité

- Angle du tronc
- Vitesse d'impact
- Temps au sol
- Immobilité prolongée
- Énergie cinétique

### Score de Gravité

Score ∈ [0, 1] où :
- 0.0 - 0.3 : Blessure légère
- 0.3 - 0.6 : Blessure modérée
- 0.6 - 0.8 : Blessure sévère
- 0.8 - 1.0 : Blessure critique

---

## 🏥 Probabilité de Blessure (10_InjuryProbability.md)

### Modèle Probabiliste

Basé sur :
- Âge du patient
- Niveau de mobilité
- Score de gravité
- Historique des chutes

### Références

- Études épidémiologiques sur les chutes
- Statistiques de blessures chez les personnes âgées
- Facteurs de risque identifiés

---

## 📈 Indicateurs de Performance (11_KPI.md)

### Métriques

- **Accuracy** : Exactitude globale
- **Precision** : Précision des détections positives
- **Recall** : Taux de détection des chutes réelles
- **F1-Score** : Moyenne harmonique precision/recall
- **Specificity** : Taux de bonnes détections négatives
- **False Positive Rate** : Taux de faux positifs
- **False Negative Rate** : Taux de faux négatifs
- **Mean Detection Time** : Temps moyen de détection
- **Mean Alert Time** : Temps moyen d'alerte
- **Uptime** : Disponibilité du système

---

## ✅ Validation (12_Validation.md)

### Méthodes de Validation

- Validation croisée
- Tests sur dataset de simulation
- Comparaison avec littérature
- Analyse des erreurs
- Calibration des seuils

### Critères de Validation

- Sensibilité ≥ 85%
- Spécificité ≥ 90%
- F1-Score ≥ 0.87
- Temps de détection < 200 ms

---

## 📚 Bibliographie (13_References.md)

### Références Scientifiques

- Euclid – Elements (~300 av. J.-C.)
- Isaac Newton – Philosophiæ Naturalis Principia Mathematica (1687)
- Google Research – MediaPipe Pose (2020)
- Articles récents sur la détection de chutes avec MediaPipe
- Publications sur la biomécanique des chutes
- Études sur les facteurs de risque de chute

---

## 🔧 Implémentations Python (formulas/)

### Fichiers Python

| Fichier | Formules implémentées |
|---------|----------------------|
| `distance.py` | Distance euclidienne, distance 3D |
| `vectors.py` | Opérations vectorielles, produit scalaire |
| `angles.py` | Calcul d'angles, rotations |
| `kinematics.py` | Vitesse, accélération |
| `dynamics.py` | Forces, énergie cinétique |
| `biomechanics.py` | Centre de gravité, angles posturaux |
| `scoring.py` | Score de chute, score de gravité |
| `probability.py` | Probabilité de blessure |

---

## 🎓 Traçabilité Scientifique

Chaque formule implémentée dans le code fait référence à :

1. **Définition** : Description mathématique
2. **Formule** : Expression mathématique
3. **Démonstration** : Preuve ou justification
4. **Unités SI** : Unités du Système International
5. **Variables** : Description des variables
6. **Origine** : Scientifique à l'origine
7. **Auteur** : Auteur de la formule
8. **Année** : Année de publication
9. **Publication** : Ouvrage ou article
10. **DOI** : Digital Object Identifier (si disponible)
11. **Utilisation** : Utilisation dans le projet
12. **Implémentation** : Fichier Python associé

---

## 🚀 Utilisation

### Pour les développeurs

1. Consulter le fichier markdown correspondant à la formule
2. Vérifier la justification scientifique
3. Implémenter ou utiliser la fonction Python correspondante
4. Référencer le fichier markdown dans les commentaires du code

### Pour les chercheurs

1. Consulter 13_References.md pour la bibliographie
2. Vérifier les justifications scientifiques dans chaque fichier
3. Consulter les DOI pour accéder aux articles originaux

### Pour les évaluateurs (mémoire MIAGE)

1. Vérifier la traçabilité : chaque formule → documentation → référence
2. Identifier les choix propres au projet (seuils configurables)
3. Distinguer les formules établies des paramètres calibrés

---

## 📝 Conventions

### Paramètres Configurable vs Établis

- **Établi** : Formule scientifique avec référence bibliographique
- **Configurable** : Paramètre du projet (seuil, pondération) identifié comme tel

### Notation Mathématique

- Variables en italique : *v*, *a*, *t*
- Vecteurs en gras : **v**, **a**
- Constantes en majuscules : *G*, *π*
- Fonctions : sin(), cos(), sqrt()

### Unités SI

Toutes les formules utilisent les unités du Système International :
- Mètre (m)
- Seconde (s)
- Kilogramme (kg)
- Radian (rad)
- Newton (N)
- Joule (J)

---

## 📞 Support

Pour toute question sur la documentation scientifique :
- Consulter d'abord le fichier markdown correspondant
- Vérifier les références dans 13_References.md
- Consulter l'implémentation Python dans formulas/

---

**Version** : 1.0  
**Date** : Juillet 2026  
**Projet** : Système de Détection de Chutes par Edge AI
