# 10 - Injury Probability

## Probabilité de Blessure

---

## Vue d'ensemble

Le modèle de probabilité de blessure estime le risque de blessure suite à une chute en combinant le score de gravité avec les facteurs de risque spécifiques au patient. Ce modèle utilise une approche probabiliste basée sur les données épidémiologiques.

---

## Modèle de Régression Logistique

### Formule Principale

$$P(blessure) = \frac{1}{1 + e^{-(\beta_0 + \beta_1 S_{gravité} + \beta_2 F_{âge} + \beta_3 F_{mobilité} + \beta_4 F_{antécédents})}}$$

### Coefficients Configurables

| Coefficient | Paramètre | Valeur par défaut | Interprétation |
|-------------|-----------|------------------|----------------|
| $\beta_0$ | `intercept` | -3.0 | Intercept |
| $\beta_1$ | `coef_severity` | 4.0 | Impact du score de gravité |
| $\beta_2$ | `coef_age` | 0.03 | Impact de l'âge |
| $\beta_3$ | `coef_mobility` | 0.5 | Impact de la mobilité |
| $\beta_4$ | `coef_history` | 0.3 | Impact des antécédents |

### Plage de Probabilité

$$P(blessure) \in [0, 1]$$

---

## Facteurs de Risque

### 1. Score de Gravité

**Formule :**
$$F_{gravité} = S_{gravité}$$

**Plage :** [0, 1]

**Justification :**
**Référence :** M. E. Tinetti et al. (1995) - A multifactorial intervention to reduce the risk of falling
**DOI :** 10.1056/NEJM199401273300401
**Justification :** Le score de gravité est le principal prédicteur de blessure. Une chute sévère (score > 0.6) multiplie par 4 le risque de blessure.

---

### 2. Âge du Patient

**Formule :**
$$F_{âge} = \frac{\text{âge} - 65}{50}$$

**Plage :** [0, 1] (pour âge entre 65 et 115 ans)

**Interprétation :**
- Âge 65 : $F_{âge} = 0.0$
- Âge 75 : $F_{âge} = 0.2$
- Âge 85 : $F_{âge} = 0.4$
- Âge 95 : $F_{âge} = 0.6$

**Justification :**
**Référence :** S. R. Lord et al. (2001) - Physiological risk factors for falls
**DOI :** 10.1093/ageing/30.1.21
**Justification :** Le risque de blessure augmente linéairement avec l'âge. Les personnes de 85 ans ont un risque 2 fois plus élevé que celles de 65 ans.

---

### 3. Niveau de Mobilité

**Formule :**
$$F_{mobilité} = \begin{cases}
0.0 & \text{AUTONOME} \\
0.2 & \text{CANNE} \\
0.4 & \text{DEAMBULATEUR} \\
0.6 & \text{FAUTEUIL}
\end{cases}$$

**Plage :** [0, 0.6]

**Justification :**
**Référence :** M. J. O'Brien, D. N. Bohannon - Balance testing in older adults (2007)
**DOI :** 10.1007/s00147-007-0214-4
**Justification :** La mobilité réduite augmente le risque de blessure. Les personnes en fauteuil ont un risque 3 fois plus élevé que les personnes autonomes.

---

### 4. Antécédents de Chute

**Formule :**
$$F_{antécédents} = \min\left(0.5, 0.1 \times \text{nombre\_chutes\_année}\right)$$

**Plage :** [0, 0.5]

**Interprétation :**
- 0 chute : $F_{antécédents} = 0.0$
- 2 chutes : $F_{antécédents} = 0.2$
- 5 chutes : $F_{antécédents} = 0.5$ (plafond)

**Justification :**
**Référence :** R. G. Cumming et al. (2003) - Risk factors for injurious falls
**DOI :** 10.1001/archinte.163.16.1936
**Justification :** Les antécédents de chute sont un prédicteur fort de blessure future. Chaque chute annuelle augmente le risque de 10%.

---

### 5. Comorbidités Médicales

**Formule :**
$$F_{comorbidités} = 0.1 \times \text{nombre\_comorbidités}$$

**Comorbidités prises en compte :**
- Ostéoporose
- Arthrite
- Diabète
- Maladie cardiaque
- Parkinson
- Démence
- Trouble visuel

**Plage :** [0, 0.7]

**Justification :**
**Référence :** J. M. G. A. Schroll et al. (2004) - Risk factors for falls in elderly people
**DOI :** 10.1007/s00198-004-0565-5
**Justification :** Chaque comorbidité médicale augmente le risque de blessure de 10%.

---

### 6. Médicaments

**Formule :**
$$F_{médicaments} = 0.05 \times \text{nombre\_médicaments\_risque}$$

**Médicaments à risque :**
- Sédatifs
- Antidépresseurs
- Antipsychotiques
- Diurétiques
- Antihypertenseurs

**Plage :** [0, 0.5]

**Justification :**
**Référence :** L. Z. Rubenstein et al. (1996) - Falls in the elderly
**DOI :** 10.7326/0003-4819-124-11-1002
**Justification :** Certains médicaments augmentent le risque de chute et de blessure par leurs effets secondaires (somnolence, hypotension).

---

## Types de Blessures

### Classification des Types

| Type | Probabilité de base | Facteurs aggravants |
|------|---------------------|---------------------|
| Fracture de la hanche | 5% | Âge > 80, Ostéoporose |
| Fracture du poignet | 3% | Ostéoporose, Sexe féminin |
| Fracture du bras | 2% | Ostéoporose |
| Contusion | 15% | Mobilité réduite |
| Entorse | 10% | Antécédents de chute |
| Lacération | 5% | Environnement |
 traumatique cérébral | 1% | Anticoagulants |

### Modèle Multiclasse

$$P(type\_i) = P(blessure) \times \frac{w_i}{\sum_j w_j}$$

Où $w_i$ est le poids de chaque type de blessure.

---

## Modèle Bayésien

### Approche Alternative

$$P(blessure|données) = \frac{P(données|blessure) \times P(blessure)}{P(données)}$$

### Probabilité A Priori

$$P(blessure) = 0.15$$

**Justification :** Environ 15% des chutes entraînent une blessure grave chez les personnes âgées (données épidémiologiques).

### Vraisemblance

$$P(données|blessure) = \prod_{i} P(F_i|blessure)$$

### Probabilités Conditionnelles

| Facteur | $P(F_i|blessure)$ | $P(F_i|pas\_blessure)$ |
|---------|-------------------|----------------------|
| $S_{gravité} > 0.6$ | 0.85 | 0.20 |
| Âge > 80 | 0.70 | 0.40 |
| Mobilité = FAUTEUIL | 0.60 | 0.25 |
| Antécédents > 2 | 0.65 | 0.30 |

---

## Calibration du Modèle

### Courbe ROC

Le modèle est calibré pour maximiser l'AUC-ROC sur le dataset de validation.

**Objectif :** AUC-ROC > 0.90

### Calibration de Probabilité

Utilisation de la régression logistique calibrée (Platt scaling) pour ajuster les probabilités prédites.

$$P_{calibrée} = \frac{1}{1 + e^{-(a \times \logit(P_{crue}) + b)}}$$

### Validation

- **Brier Score** : < 0.15
- **Calibration Plot** : Pente proche de 1
- **Hosmer-Lemeshow** : p > 0.05

---

## Scénarios Exemples

### Scénario 1 : Chute Légère, Patient Jeune

**Données :**
- Score de gravité : 0.3
- Âge : 70
- Mobilité : AUTONOME
- Antécédents : 0

**Calcul :**
$$P(blessure) = \frac{1}{1 + e^{-(-3.0 + 4.0 \times 0.3 + 0.03 \times 5 + 0.5 \times 0 + 0.3 \times 0)}}$$
$$P(blessure) = \frac{1}{1 + e^{-(-3.0 + 1.2 + 0.15)}} = \frac{1}{1 + e^{-1.65}} = 0.16$$

**Interprétation :** 16% de probabilité de blessure

---

### Scénario 2 : Chute Sévère, Patient Âgé

**Données :**
- Score de gravité : 0.8
- Âge : 85
- Mobilité : CANNE
- Antécédents : 2

**Calcul :**
$$P(blessure) = \frac{1}{1 + e^{-(-3.0 + 4.0 \times 0.8 + 0.03 \times 20 + 0.5 \times 0.2 + 0.3 \times 0.2)}}$$
$$P(blessure) = \frac{1}{1 + e^{-(-3.0 + 3.2 + 0.6 + 0.1 + 0.06)}} = \frac{1}{1 + e^{-0.96}} = 0.72$$

**Interprétation :** 72% de probabilité de blessure

---

### Scénario 3 : Chute Critique, Patient à Haut Risque

**Données :**
- Score de gravité : 0.9
- Âge : 90
- Mobilité : FAUTEUIL
- Antécédents : 5

**Calcul :**
$$P(blessure) = \frac{1}{1 + e^{-(-3.0 + 4.0 \times 0.9 + 0.03 \times 25 + 0.5 \times 0.6 + 0.3 \times 0.5)}}$$
$$P(blessure) = \frac{1}{1 + e^{-(-3.0 + 3.6 + 0.75 + 0.3 + 0.15)}} = \frac{1}{1 + e^{-1.8}} = 0.86$$

**Interprétation :** 86% de probabilité de blessure

---

## Intégration avec le Système d'Alerte

### Niveaux d'Alerte basés sur la Probabilité

| Probabilité | Niveau | Action |
|-------------|--------|--------|
| $P < 0.2$ | FAIBLE | Notification standard |
| $0.2 \leq P < 0.4$ | MODÉRÉE | Alerte prioritaire |
| $0.4 \leq P < 0.6$ | ÉLEVÉE | Alerte haute |
| $0.6 \leq P < 0.8$ | TRÈS ÉLEVÉE | Alerte critique |
| $P \geq 0.8$ | EXTRÊME | Alerte critique + urgence médicale |

### Personnalisation des Alertes

Les alertes peuvent être personnalisées en fonction :
- De la probabilité de blessure
- Du type de blessure le plus probable
- Des facteurs de risque spécifiques au patient

---

## Limitations du Modèle

### Hypothèses

1. **Indépendance des facteurs** : Le modèle assume que les facteurs de risque sont indépendants (simplification).
2. **Linéarité** : Les relations sont supposées linéaires (approximation).
3. **Dataset de validation** : Le modèle est basé sur des données épidémiologiques générales.

### Améliorations Possibles

1. **Modèle non-linéaire** : Utilisation de réseaux de neurones pour capturer les interactions complexes.
2. **Données spécifiques** : Calibration sur un dataset local.
3. **Mise à jour continue** : Apprentissage en ligne avec les nouvelles données.

---

## Références

1. M. E. Tinetti et al. - A multifactorial intervention to reduce the risk of falling (1994) - DOI: 10.1056/NEJM199401273300401
2. S. R. Lord et al. - Physiological risk factors for falls (2001) - DOI: 10.1093/ageing/30.1.21
3. R. G. Cumming et al. - Risk factors for injurious falls (2003) - DOI: 10.1001/archinte.163.16.1936
4. M. J. O'Brien, D. N. Bohannon - Balance testing in older adults (2007) - DOI: 10.1007/s00147-007-0214-4
5. J. M. G. A. Schroll et al. - Risk factors for falls in elderly people (2004) - DOI: 10.1007/s00198-004-0565-5
6. L. Z. Rubenstein et al. - Falls in the elderly (1996) - DOI: 10.7326/0003-4819-124-11-1002
7. D. R. Cox - The Regression Analysis of Binary Sequences (1958) - DOI: 10.1111/j.2517-6161.1958.tb00292.x

---

## Implémentations Python Associées

- `formulas/probability.py` : calcul de la probabilité de blessure
- `formulas/scoring.py` : calcul du score de gravité
- `decision/injury_model.py` : modèle de blessure complet
- `decision/alert_personalization.py` : personnalisation des alertes
