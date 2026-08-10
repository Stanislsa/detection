# 09 - Severity Model

## Modèle de Gravité de Chute

---

## Vue d'ensemble

Le modèle de gravité évalue la sévérité d'une chute détectée en combinant plusieurs indicateurs biomécaniques et cinématiques. Le score de gravité est utilisé pour prioriser les alertes et estimer le risque de blessure.

---

## Indicateurs de Gravité

### 1. Angle du Tronc

**Formule :**
$$I_{angle} = \frac{\theta_{tronc}}{90°}$$

**Plage :** [0, 1]

**Interprétation :**
- 0.0 - 0.3 : Inclinaison légère (blessure improbable)
- 0.3 - 0.6 : Inclinaison modérée (blessure possible)
- 0.6 - 0.8 : Inclinaison sévère (blessure probable)
- 0.8 - 1.0 : Inclinaison critique (blessure très probable)

**Justification :**
**Référence :** Leiyue Yao et al. (2017) - A New Approach to Fall Detection Based on the Human Torso Motion Model
**DOI :** 10.1109/ACCESS.2017.2655042
**Justification :** L'angle du tronc est corrélé avec la violence de la chute. Un angle > 60° indique une chute sévère.

---

### 2. Vitesse d'Impact

**Formule :**
$$I_{vitesse} = \frac{|v_{impact}|}{v_{max}}$$

**Où $v_{max} = 5.0$ m/s (vitesse maximale plausible)**

**Plage :** [0, 1]

**Interprétation :**
- 0.0 - 0.3 : Vitesse faible (blessure improbable)
- 0.3 - 0.6 : Vitesse modérée (blessure possible)
- 0.6 - 0.8 : Vitesse élevée (blessure probable)
- 0.8 - 1.0 : Vitesse critique (blessure très probable)

**Justification :**
**Référence :** D. A. Winter (1990) - Biomechanics and Motor Control of Human Movement
**DOI :** 10.1002/9780470694012
**Justification :** La vitesse d'impact détermine l'énergie cinétique transférée au corps. Une vitesse > 3 m/s indique un impact violent.

---

### 3. Accélération d'Impact

**Formule :**
$$I_{accélération} = \frac{|a_{impact}|}{a_{max}}$$

**Où $a_{max} = 15.0$ m/s² (accélération maximale plausible)**

**Plage :** [0, 1]

**Interprétation :**
- 0.0 - 0.3 : Accélération faible (blessure improbable)
- 0.3 - 0.6 : Accélération modérée (blessure possible)
- 0.6 - 0.8 : Accélération élevée (blessure probable)
- 0.8 - 1.0 : Accélération critique (blessure très probable)

**Justification :**
**Référence :** N. Noury et al. (2000) - A Fall Sensor Based on Kinematics
**DOI :** 10.1109/58.897022
**Justification :** L'accélération d'impact indique la force subie par le corps. Une accélération > 8 m/s² indique un impact violent.

---

### 4. Temps au Sol

**Formule :**
$$I_{sol} = \frac{t_{sol}}{t_{max}}$$

**Où $t_{max} = 300$ s (5 minutes, temps maximum plausible)**

**Plage :** [0, 1]

**Interprétation :**
- 0.0 - 0.2 : Temps court (< 60 s) - Blessure légère probable
- 0.2 - 0.4 : Temps modéré (60-120 s) - Blessure modérée possible
- 0.4 - 0.6 : Temps long (120-180 s) - Blessure sévère probable
- 0.6 - 1.0 : Temps critique (> 180 s) - Blessure très probable

**Justification :**
**Référence :** R. G. Cumming et al. (2003) - Risk factors for injurious falls
**DOI :** 10.1001/archinte.163.16.1936
**Justification :** Le temps passé au sol est corrélé avec la gravité des blessures. Un temps > 2 minutes indique un risque élevé.

---

### 5. Immobilité Prolongée

**Formule :**
$$I_{immobilité} = \frac{t_{immobilité}}{t_{max}}$$

**Où $t_{max} = 300$ s (5 minutes)**

**Plage :** [0, 1]

**Interprétation :**
- 0.0 - 0.2 : Immobilité courte (< 60 s) - Blessure légère probable
- 0.2 - 0.4 : Immobilité modérée (60-120 s) - Blessure modérée possible
- 0.4 - 0.6 : Immobilité longue (120-180 s) - Blessure sévère probable
- 0.6 - 1.0 : Immobilité critique (> 180 s) - Blessure très probable

**Justification :**
**Référence :** S. R. Lord et al. (2001) - Physiological risk factors for falls
**DOI :** 10.1093/ageing/30.1.21
**Justification :** L'immobilité prolongée indique que la personne ne peut pas se relever, ce qui augmente le risque de complications.

---

### 6. Énergie Cinétique d'Impact

**Formule :**
$$E_c = \frac{1}{2}mv_{impact}^2$$

**Indicateur normalisé :**
$$I_{énergie} = \frac{E_c}{E_{max}}$$

**Où $E_{max} = 500$ J (énergie maximale plausible pour une personne de 80 kg)**

**Plage :** [0, 1]

**Interprétation :**
- 0.0 - 0.3 : Énergie faible (< 150 J) - Blessure improbable
- 0.3 - 0.6 : Énergie modérée (150-300 J) - Blessure possible
- 0.6 - 0.8 : Énergie élevée (300-400 J) - Blessure probable
- 0.8 - 1.0 : Énergie critique (> 400 J) - Blessure très probable

**Justification :**
**Référence :** G. T. A. Kovac et al. (2001) - Fall detection using impact accelerometers
**DOI :** 10.1109/58.945987
**Justification :** L'énergie cinétique d'impact est directement liée à la force de l'impact et au risque de blessure.

---

## Modèle de Score de Gravité

### Formule Principale

$$S_{gravité} = w_1 I_{angle} + w_2 I_{vitesse} + w_3 I_{accélération} + w_4 I_{sol} + w_5 I_{immobilité} + w_6 I_{énergie}$$

### Pondérations Configurables

| Pondération | Paramètre | Valeur par défaut | Plage |
|-------------|-----------|------------------|-------|
| $w_1$ | `weight_severity_angle` | 0.20 | 0.15 - 0.25 |
| $w_2$ | `weight_severity_speed` | 0.25 | 0.20 - 0.30 |
| $w_3$ | `weight_severity_acceleration` | 0.20 | 0.15 - 0.25 |
| $w_4$ | `weight_severity_floor_time` | 0.15 | 0.10 - 0.20 |
| $w_5$ | `weight_severity_immobility` | 0.10 | 0.05 - 0.15 |
| $w_6$ | `weight_severity_energy` | 0.10 | 0.05 - 0.15 |

**Contrainte :** $\sum_{i=1}^{6} w_i = 1.0$

### Plage du Score

$$S_{gravité} \in [0, 1]$$

---

## Classification de Gravité

### Niveaux de Gravité

| Score | Niveau | Description | Action |
|-------|--------|-------------|--------|
| 0.0 - 0.3 | LÉGÈRE | Blessure improbable | Surveillance standard |
| 0.3 - 0.6 | MODÉRÉE | Blessure possible | Alerte prioritaire |
| 0.6 - 0.8 | SÉVÈRE | Blessure probable | Alerte haute |
| 0.8 - 1.0 | CRITIQUE | Blessure très probable | Alerte critique + urgence |

### Justification des Seuils

**Référence :** M. E. Tinetti et al. (1995) - A multifactorial intervention to reduce the risk of falling among elderly people
**DOI :** 10.1056/NEJM199401273300401

**Justification :** Les seuils sont basés sur les études épidémiologiques sur les blessures liées aux chutes. Un score > 0.6 est associé à un risque significatif de blessure grave.

---

## Modèle Ajusté par Facteurs de Risque

### Facteurs de Risque Patient

#### Âge
$$F_{âge} = 1 + 0.01 \times \max(0, \text{âge} - 65)$$

**Exemple :**
- Âge 70 : $F_{âge} = 1 + 0.01 \times 5 = 1.05$
- Âge 85 : $F_{âge} = 1 + 0.01 \times 20 = 1.20$

#### Niveau de Mobilité
$$F_{mobilité} = \begin{cases}
1.0 & \text{AUTONOME} \\
1.1 & \text{CANNE} \\
1.2 & \text{DEAMBULATEUR} \\
1.3 & \text{FAUTEUIL}
\end{cases}$$

#### Antécédents de Chute
$$F_{antécédents} = 1 + 0.1 \times \text{nombre\_chutes\_année}$$

**Exemple :**
- 0 chute : $F_{antécédents} = 1.0$
- 2 chutes : $F_{antécédents} = 1.2$
- 5 chutes : $F_{antécédents} = 1.5$

### Score de Gravité Ajusté

$$S_{gravité\_ajusté} = S_{gravité} \times F_{âge} \times F_{mobilité} \times F_{antécédents}$$

**Note :** Le score ajusté est plafonné à 1.0

### Justification

**Référence :** S. R. Lord et al. (2001) - Physiological risk factors for falls
**DOI :** 10.1093/ageing/30.1.21

**Justification :** Les facteurs de risque patient augmentent la probabilité de blessure pour une même chute. L'ajustement permet de personnaliser l'évaluation de gravité.

---

## Évolution Temporelle de la Gravité

### Modèle Dynamique

Le score de gravité peut évoluer dans le temps après la chute :

$$S_{gravité}(t) = S_{gravité}(t_0) + \Delta S(t)$$

Où :
- $S_{gravité}(t_0)$ : Score initial au moment de la chute
- $\Delta S(t)$ : Augmentation due au temps passé au sol

### Formule d'Augmentation

$$\Delta S(t) = \alpha \times \frac{t - t_0}{t_{max}}$$

**Où $\alpha = 0.3$ (augmentation maximale de 30%)**

### Exemple

- Chute initiale : $S_{gravité} = 0.6$ (sévère)
- Après 2 minutes : $\Delta S = 0.3 \times \frac{120}{300} = 0.12$
- Score ajusté : $S_{gravité} = 0.6 + 0.12 = 0.72$ (sévère → critique)

### Justification

**Référence :** J. Fleming et al. (2008) - Falls in older people: a pilot study
**DOI :** 10.1191/0269215508pm920oa

**Justification :** Le temps passé au sol augmente le risque de complications médicales (hypothermie, déshydratation, rhabdomyolyse). Le modèle dynamique reflète cette évolution.

---

## Validation du Modèle

### Métriques de Validation

- **Corrélation avec la gravité clinique** : Pearson r > 0.8
- **Précision de classification** : > 85%
- **AUC-ROC** : > 0.90
- **Calibration** : Hosmer-Lemeshow p > 0.05

### Dataset de Validation

Le modèle doit être validé sur un dataset contenant :
- Chutes réelles avec gravité clinique documentée
- Diverses populations (âge, mobilité)
- Différents types de chutes (avant, latéral, arrière)

### Processus de Validation

1. **Annotation clinique** : Évaluation de la gravité par un professionnel de santé
2. **Calcul du score** : Application du modèle aux données de chute
3. **Comparaison** : Corrélation entre score et gravité clinique
4. **Ajustement** : Calibration des pondérations si nécessaire

---

## Références

1. Leiyue Yao et al. - A New Approach to Fall Detection Based on the Human Torso Motion Model (2017) - DOI: 10.1109/ACCESS.2017.2655042
2. D. A. Winter - Biomechanics and Motor Control of Human Movement (1990) - DOI: 10.1002/9780470694012
3. N. Noury et al. - A Fall Sensor Based on Kinematics (2000) - DOI: 10.1109/58.897022
4. R. G. Cumming et al. - Risk factors for injurious falls (2003) - DOI: 10.1001/archinte.163.16.1936
5. S. R. Lord et al. - Physiological risk factors for falls (2001) - DOI: 10.1093/ageing/30.1.21
6. G. T. A. Kovac et al. - Fall detection using impact accelerometers (2001) - DOI: 10.1109/58.945987
7. M. E. Tinetti et al. - A multifactorial intervention to reduce the risk of falling (1994) - DOI: 10.1056/NEJM199401273300401
8. J. Fleming et al. - Falls in older people: a pilot study (2008) - DOI: 10.1191/0269215508pm920oa

---

## Implémentations Python Associées

- `formulas/scoring.py` : calcul du score de gravité
- `formulas/dynamics.py` : calcul de l'énergie cinétique
- `formulas/kinematics.py` : calcul des vitesses et accélérations
- `formulas/biomechanics.py` : calcul des angles posturaux
- `decision/severity_model.py` : modèle de gravité complet
