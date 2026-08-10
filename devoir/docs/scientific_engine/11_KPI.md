# 11 - KPI

## Indicateurs de Performance (Key Performance Indicators)

---

## Vue d'ensemble

Les KPIs (Key Performance Indicators) mesurent la performance du système de détection de chute. Ils sont calculés périodiquement (quotidiennement, hebdomadairement, mensuellement) pour suivre l'évolution du système et identifier les axes d'amélioration.

---

## KPIs de Détection

### 1. Accuracy (Exactitude)

**Formule :**
$$Accuracy = \frac{TP + TN}{TP + TN + FP + FN}$$

**Définition :**
Pourcentage de prédictions correctes (vrais positifs + vrais négatifs) sur le total des prédictions.

**Variables :**
- $TP$ : Vrais Positifs (chutes correctement détectées)
- $TN$ : Vrais Négatifs (non-chutes correctement identifiées)
- $FP$ : Faux Positifs (fausses alarmes)
- $FN$ : Faux Négatifs (chutes manquées)

**Plage :** [0, 1]

**Objectif :** ≥ 0.92

**Justification :**
**Référence :** G. M. Weiss et al. (2012) - A smartphone-based system for detecting falls
**DOI :** 10.1186/1475-925X-11-115
**Justification :** Une accuracy > 92% est considérée comme excellente pour les systèmes de détection de chute.

---

### 2. Precision (Précision)

**Formule :**
$$Precision = \frac{TP}{TP + FP}$$

**Définition :**
Pourcentage de chutes détectées qui sont réellement des chutes (vrais positifs sur tous les positifs prédits).

**Plage :** [0, 1]

**Objectif :** ≥ 0.90

**Justification :**
**Référence :** A. Bourke et al. (2010) - Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm
**DOI :** 10.1016/j.gaitpost.2009.10.004
**Justification :** Une précision > 90% minimise les fausses alertes, ce qui est crucial pour l'acceptation du système.

---

### 3. Recall (Sensibilité)

**Formule :**
$$Recall = \frac{TP}{TP + FN}$$

**Définition :**
Pourcentage de chutes réelles correctement détectées (vrais positifs sur toutes les chutes réelles).

**Plage :** [0, 1]

**Objectif :** ≥ 0.85

**Justification :**
**Référence :** M. Kepski et al. (2012) - Fall detection using Kinect sensor
**DOI :** 10.1109/MBRA.2012.6222177
**Justification :** Une sensibilité > 85% assure que la majorité des chutes sont détectées, ce qui est essentiel pour la sécurité.

---

### 4. Specificity (Spécificité)

**Formule :**
$$Specificity = \frac{TN}{TN + FP}$$

**Définition :**
Pourcentage de non-chutes correctement identifiées (vrais négatifs sur tous les négatifs réels).

**Plage :** [0, 1]

**Objectif :** ≥ 0.95

**Justification :**
**Référence :** G. M. Weiss et al. (2012) - A smartphone-based system for detecting falls
**DOI :** 10.1186/1475-925X-11-115
**Justification :** Une spécificité > 95% minimise les fausses alertes lors des mouvements normaux.

---

### 5. F1-Score

**Formule :**
$$F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}$$

**Définition :**
Moyenne harmonique de la précision et du recall. Balance entre les deux métriques.

**Plage :** [0, 1]

**Objectif :** ≥ 0.87

**Justification :**
**Référence :** D. M. Powers (2011) - Evaluation: From Precision, Recall and F-Measure to ROC
**DOI :** 10.1145/2003476.2003486
**Justification :** Le F1-score est la métrique la plus équilibrée pour les systèmes de détection de chute.

---

### 6. False Positive Rate (FPR)

**Formule :**
$$FPR = \frac{FP}{FP + TN}$$

**Définition :**
Pourcentage de non-chutes incorrectement classées comme chutes.

**Plage :** [0, 1]

**Objectif :** ≤ 0.05

**Justification :**
**Référence :** A. Bourke et al. (2010) - Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm
**DOI :** 10.1016/j.gaitpost.2009.10.004
**Justification :** Un FPR < 5% assure moins de 5 fausses alertes pour 100 mouvements normaux.

---

### 7. False Negative Rate (FNR)

**Formule :**
$$FNR = \frac{FN}{FN + TP}$$

**Définition :**
Pourcentage de chutes réelles non détectées.

**Plage :** [0, 1]

**Objectif :** ≤ 0.15

**Justification :**
**Référence :** M. Kepski et al. (2012) - Fall detection using Kinect sensor
**DOI :** 10.1109/MBRA.2012.6222177
**Justification :** Un FNR < 15% assure que moins de 15% des chutes sont manquées.

---

## KPIs de Performance Temporelle

### 8. Mean Detection Time (Temps Moyen de Détection)

**Formule :**
$$MDT = \frac{1}{N} \sum_{i=1}^{N} (t_{détection_i} - t_{début\_chute_i})$$

**Définition :**
Temps moyen écoulé entre le début de la chute et sa détection.

**Unité SI :** Seconde (s) ou milliseconde (ms)

**Objectif :** ≤ 200 ms

**Justification :**
**Référence :** N. Noury et al. (2000) - A Fall Sensor Based on Kinematics
**DOI :** 10.1109/58.897022
**Justification :** Un temps de détection < 200 ms permet une intervention rapide avant l'impact au sol.

---

### 9. Mean Alert Time (Temps Moyen d'Alerte)

**Formule :**
$$MAT = \frac{1}{N} \sum_{i=1}^{N} (t_{alerte_i} - t_{détection_i})$$

**Définition :**
Temps moyen écoulé entre la détection de la chute et l'envoi de l'alerte.

**Unité SI :** Seconde (s)

**Objectif :** ≤ 5 s

**Justification :**
**Référence :** J. Fleming et al. (2008) - Falls in older people: a pilot study
**DOI :** 10.1191/0269215508pm920oa
**Justification :** Un temps d'alerte < 5 secondes assure une notification rapide aux contacts d'urgence.

---

### 10. Alert Response Time (Temps de Réponse aux Alertes)

**Formule :**
$$ART = \frac{1}{N} \sum_{i=1}^{N} (t_{accusé_i} - t_{alerte_i})$$

**Définition :**
Temps moyen écoulé entre l'envoi de l'alerte et son accusé de réception.

**Unité SI :** Seconde (s)

**Objectif :** ≤ 300 s (5 minutes)

**Justification :**
**Référence :** R. G. Cumming et al. (2003) - Risk factors for injurious falls
**DOI :** 10.1001/archinte.163.16.1936
**Justification :** Un temps de réponse < 5 minutes réduit le risque de complications médicales.

---

## KPIs de Disponibilité

### 11. Uptime (Disponibilité)

**Formule :**
$$Uptime = \frac{T_{fonctionnement}}{T_{total}} \times 100$$

**Définition :**
Pourcentage de temps où le système est opérationnel.

**Unité SI :** Pourcentage (%)

**Objectif :** ≥ 99.5%

**Justification :**
**Référence :** ITIL v4 - Service Availability
**Justification :** Une disponibilité > 99.5% assure moins de 44 minutes d'indisponibilité par mois.

---

### 12. Downtime (Indisponibilité)

**Formule :**
$$Downtime = T_{total} - T_{fonctionnement}$$

**Définition :**
Temps total où le système n'est pas opérationnel.

**Unité SI :** Seconde (s) ou heure (h)

**Objectif :** ≤ 3.65 jours/an

**Justification :**
**Référence :** ITIL v4 - Service Availability
**Justification :** Correspond à une disponibilité de 99%.

---

## KPIs de Qualité des Données

### 13. Frame Rate (Taux de Trames)

**Formule :**
$$FR = \frac{N_{trames}}{T_{durée}}$$

**Définition**
Nombre de trames traitées par seconde.

**Unité SI :** Trames par seconde (fps)

**Objectif :** ≥ 25 fps

**Justification :**
**Référence :** Google Research - MediaPipe Pose (2020)
**DOI :** 10.1145/3383090
**Justification :** Un taux de trames ≥ 25 fps assure une détection fluide et précise.

---

### 14. Pose Detection Confidence (Confiance de Détection)

**Formule :**
$$PDC = \frac{1}{N} \sum_{i=1}^{N} C_{pose_i}$$

**Définition :**
Confiance moyenne de la détection de pose MediaPipe.

**Plage :** [0, 1]

**Objectif :** ≥ 0.90

**Justification :**
**Référence :** Google Research - MediaPipe Pose (2020)
**DOI :** 10.1145/3383090
**Justification :** Une confiance > 90% assure une détection fiable du squelette.

---

### 15. Data Completeness (Complétude des Données)

**Formule :**
$$DC = \frac{N_{points\_valides}}{N_{points\_total}}$$

**Définition :**
Pourcentage de points MediaPipe valides (non manquants) sur le total des points.

**Plage :** [0, 1]

**Objectif :** ≥ 0.95

**Justification :**
**Référence :** D. A. Winter - Biomechanics and Motor Control of Human Movement (1990)
**DOI :** 10.1002/9780470694012
**Justification :** Une complétude > 95% assure que suffisamment de points sont disponibles pour l'analyse.

---

## KPIs d'Utilisation

### 16. Active Sessions (Sessions Actives)

**Formule :**
$$AS = \sum_{i=1}^{N} \mathbb{I}(status_i = EN\_COURS)$$

**Définition :**
Nombre de sessions de surveillance actives à un instant donné.

**Unité SI :** Nombre (sans dimension)

**Objectif :** ≥ 1 (au moins une session active)

**Justification :**
**Référence :** Spécification du système
**Justification :** Au moins une session active est nécessaire pour assurer la surveillance continue.

---

### 17. Monitoring Coverage (Couverture de Surveillance)

**Formule :**
$$MC = \frac{T_{surveillance}}{T_{total}} \times 100$$

**Définition :**
Pourcentage de temps où au moins une session de surveillance est active.

**Unité SI :** Pourcentage (%)

**Objectif :** ≥ 95%

**Justification :**
**Référence :** Spécification du système
**Justification :** Une couverture > 95% assure une surveillance quasi continue.

---

## KPIs de Qualité des Alertes

### 18. Alert Acknowledgment Rate (Taux d'Accusé d'Alerte)

**Formule :**
$$AAR = \frac{N_{alertes\_accusées}}{N_{alertes\_totales}}$$

**Définition :**
Pourcentage d'alertes accusées par les contacts.

**Plage :** [0, 1]

**Objectif :** ≥ 0.90

**Justification :**
**Référence :** J. Fleming et al. (2008) - Falls in older people: a pilot study
**DOI :** 10.1191/0269215508pm920oa
**Justification :** Un taux d'accusé > 90% assure que la majorité des alertes sont traitées.

---

### 19. False Alert Rate (Taux de Fausse Alerte)

**Formule :**
$$FAR = \frac{N_{fausses\_alertes}}{N_{alertes\_totales}}$$

**Définition :**
Pourcentage d'alertes qui ne correspondent pas à une chute réelle.

**Plage :** [0, 1]

**Objectif :** ≤ 0.10

**Justification :**
**Référence :** A. Bourke et al. (2010) - Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm
**DOI :** 10.1016/j.gaitpost.2009.10.004
**Justification :** Un taux de fausse alerte < 10% assure l'acceptation du système.

---

## KPIs de Performance du Système

### 20. CPU Usage (Utilisation CPU)

**Formule :**
$$CPU = \frac{T_{CPU\_busy}}{T_{total}} \times 100$$

**Définition :**
Pourcentage de temps CPU utilisé par le système.

**Unité SI :** Pourcentage (%)

**Objectif :** ≤ 80%

**Justification :**
**Référence :** Spécification du système
**Justification :** Une utilisation CPU < 80% assure une marge pour les pics de charge.

---

### 21. Memory Usage (Utilisation Mémoire)

**Formule :**
$$Memory = \frac{M_{utilisée}}{M_{totale}} \times 100$$

**Définition :**
Pourcentage de mémoire utilisée par le système.

**Unité SI :** Pourcentage (%)

**Objectif :** ≤ 70%

**Justification :**
**Référence :** Spécification du système
**Justification :** Une utilisation mémoire < 70% assure une marge pour les pics de charge.

---

### 22. Storage Usage (Utilisation Stockage)

**Formule :**
$$Storage = \frac{S_{utilisée}}{S_{totale}} \times 100$$

**Définition :**
Pourcentage d'espace de stockage utilisé par le système.

**Unité SI :** Pourcentage (%)

**Objectif :** ≤ 80%

**Justification :**
**Référence :** Spécification du système
**Justification :** Une utilisation stockage < 80% assure une marge pour les données futures.

---

## Calcul et Stockage des KPIs

### Fréquence de Calcul

| KPI | Fréquence de calcul | Stockage |
|-----|-------------------|----------|
| Accuracy, Precision, Recall, F1-Score | Quotidien | 365 jours |
| Mean Detection Time | Quotidien | 365 jours |
| Mean Alert Time | Quotidien | 365 jours |
| Uptime | Continu | 365 jours |
| Frame Rate | Continu | 7 jours |
| CPU/Memory Usage | Continu | 7 jours |

### Table de Stockage

```sql
CREATE TABLE KPIs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accuracy REAL,
    precision REAL,
    recall REAL,
    specificity REAL,
    sensitivity REAL,
    f1_score REAL,
    false_positive_rate REAL,
    false_negative_rate REAL,
    mean_detection_time REAL,
    mean_alert_time REAL,
    uptime REAL,
    calculated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

---

## Références

1. G. M. Weiss et al. - A smartphone-based system for detecting falls (2012) - DOI: 10.1186/1475-925X-11-115
2. A. Bourke et al. - Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm (2010) - DOI: 10.1016/j.gaitpost.2009.10.004
3. M. Kepski et al. - Fall detection using Kinect sensor (2012) - DOI: 10.1109/MBRA.2012.6222177
4. D. M. Powers - Evaluation: From Precision, Recall and F-Measure to ROC (2011) - DOI: 10.1145/2003476.2003486
5. N. Noury et al. - A Fall Sensor Based on Kinematics (2000) - DOI: 10.1109/58.897022
6. J. Fleming et al. - Falls in older people: a pilot study (2008) - DOI: 10.1191/0269215508pm920oa
7. R. G. Cumming et al. - Risk factors for injurious falls (2003) - DOI: 10.1001/archinte.163.16.1936
8. Google Research - MediaPipe Pose (2020) - DOI: 10.1145/3383090

---

## Implémentations Python Associées

- `metrics/kpi.py` : calcul des KPIs
- `metrics/performance.py` : métriques de détection
- `metrics/temporal.py` : métriques temporelles
- `metrics/quality.py` : métriques de qualité des données
- `metrics/system.py` : métriques système
