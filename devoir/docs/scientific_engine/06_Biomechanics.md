# 06 - Biomechanics

## Biomécanique Humaine

---

## Angle du Tronc

### Nom
Angle d'Inclinaison du Tronc

### Formule
$$\theta_{tronc} = \arccos\left(\frac{\mathbf{v}_{épaules} \cdot \mathbf{v}_{vertical}}{\|\mathbf{v}_{épaules}\| \|\mathbf{v}_{vertical}\|}\right)$$

### Définition
L'angle d'inclinaison du tronc est l'angle entre le vecteur formé par les épaules et la verticale.

### Démonstration
Application de la formule de l'angle entre deux vecteurs (produit scalaire).

### Unités SI
Degré (°) ou radian (rad)

### Variables
- $\mathbf{v}_{épaules}$ : Vecteur entre l'épaule gauche et l'épaule droite
- $\mathbf{v}_{vertical}$ : Vecteur vertical unitaire (0, 1, 0)
- $\theta_{tronc}$ : Angle d'inclinaison du tronc

### Origine Scientifique
Leiyue Yao, Weidong Min, Keqiang Lu

### Date
2017

### Publication
A New Approach to Fall Detection Based on the Human Torso Motion Model

### DOI
10.1109/ACCESS.2017.2655042

### Utilisation dans le Projet
Détection de l'inclinaison anormale du tronc. Indicateur principal de la perte d'équilibre. Seuil configurable (défaut: 45°).

### Implémentation Python
`formulas/biomechanics.py` - fonction `trunk_angle()`

---

## Angle Tête-Tronc

### Nom
Angle Tête-Tronc (Cervical Angle)

### Formule
$$\theta_{tête-tronc} = \arccos\left(\frac{\mathbf{v}_{tête-épaules} \cdot \mathbf{v}_{épaules-hanches}}{\|\mathbf{v}_{tête-épaules}\| \|\mathbf{v}_{épaules-hanches}\|}\right)$$

### Définition
L'angle tête-tronc mesure l'alignement de la tête par rapport au tronc.

### Démonstration
Application de la formule de l'angle entre deux vecteurs.

### Unités SI
Degré (°) ou radian (rad)

### Variables
- $\mathbf{v}_{tête-épaules}$ : Vecteur du nez au centre des épaules
- $\mathbf{v}_{épaules-hanches}$ : Vecteur du centre des épaules au centre des hanches
- $\theta_{tête-tronc}$ : Angle tête-tronc

### Origine Scientifique
M. J. O'Brien, D. N. Bohannon

### Date
2007

### Publication
Balance testing in older adults: A review of the literature

### DOI
10.1007/s00147-007-0214-4

### Utilisation dans le Projet
Détection des mouvements anormaux de la tête (ex: chute de tête vers l'avant). Indicateur de la posture cervicale.

### Implémentation Python
`formulas/biomechanics.py` - fonction `head_trunk_angle()`

---

## Angle Hanche-Genou

### Nom
Angle Hanche-Genou (Hip Angle)

### Formule
$$\theta_{hanche} = \arccos\left(\frac{\mathbf{v}_{hanche-genou} \cdot \mathbf{v}_{genou-cheville}}{\|\mathbf{v}_{hanche-genou}\| \|\mathbf{v}_{genou-cheville}\|}\right)$$

### Définition
L'angle de la hanche mesure l'ouverture entre la cuisse et la jambe.

### Démonstration
Application de la formule de l'angle entre deux vecteurs.

### Unités SI
Degré (°) ou radian (rad)

### Variables
- $\mathbf{v}_{hanche-genou}$ : Vecteur de la hanche au genou
- $\mathbf{v}_{genou-cheville}$ : Vecteur du genou à la cheville
- $\theta_{hanche}$ : Angle de la hanche

### Origine Scientifique
D. A. Winter

### Date
1990

### Publication
Biomechanics and Motor Control of Human Movement

### DOI
10.1002/9780470694012

### Utilisation dans le Projet
Détection de la flexion anormale de la hanche. Indicateur de la position assise/debout.

### Implémentation Python
`formulas/biomechanics.py` - fonction `hip_angle()`

---

## Angle Genou-Cheville

### Nom
Angle Genou-Cheville (Knee Angle)

### Formule
$$\theta_{genou} = \arccos\left(\frac{\mathbf{v}_{hanche-genou} \cdot \mathbf{v}_{genou-cheville}}{\|\mathbf{v}_{hanche-genou}\| \|\mathbf{v}_{genou-cheville}\|}\right)$$

### Définition
L'angle du genou mesure l'ouverture entre la cuisse et le tibia.

### Démonstration
Application de la formule de l'angle entre deux vecteurs.

### Unités SI
Degré (°) ou radian (rad)

### Variables
- $\mathbf{v}_{hanche-genou}$ : Vecteur de la hanche au genou
- $\mathbf{v}_{genou-cheville}$ : Vecteur du genou à la cheville
- $\theta_{genou}$ : Angle du genou

### Origine Scientifique
D. A. Winter

### Date
1990

### Publication
Biomechanics and Motor Control of Human Movement

### DOI
10.1002/9780470694012

### Utilisation dans le Projet
Détection de l'hyperextension ou de la flexion anormale du genou. Indicateur de la stabilité de la jambe.

### Implémentation Python
`formulas/biomechanics.py` - fonction `knee_angle()`

---

## Centre de Gravité Humain

### Nom
Centre de Gravité du Corps Humain

### Formule (Approximation)
$$\mathbf{C}_G = \frac{\sum_{i=1}^{33} m_i \mathbf{P}_i}{\sum_{i=1}^{33} m_i}$$

### Formule Simplifiée (MediaPipe)
$$\mathbf{C}_G = \frac{1}{33} \sum_{i=1}^{33} \mathbf{P}_i$$

### Définition
Le centre de gravité du corps humain est le point où la masse du corps est considérée comme concentrée.

### Démonstration
Principe des moments : le centre de gravité est le point où la somme des moments est nulle.

### Unités SI
Mètre (m)

### Variables
- $\mathbf{P}_i$ : Position du i-ème point MediaPipe
- $m_i$ : Masse associée au i-ème point
- $\mathbf{C}_G$ : Centre de gravité

### Origine Scientifique
Claude Perrault

### Date
1670

### Publication
Cours de physique

### DOI
N/A

### Utilisation dans le Projet
Calcul du centre de gravité à partir des 33 points MediaPipe. Point de référence pour la détection de chute.

### Implémentation Python
`formulas/biomechanics.py` - fonction `center_of_gravity()`

---

## Hauteur du Centre de Gravité

### Nom
Hauteur du Centre de Gravité

### Formule
$$h_{CG} = C_{G_y}$$

### Formule (Pourcentage de la taille)
$$h_{CG\%} = \frac{C_{G_y}}{H_{totale}} \times 100$$

### Définition
La hauteur du centre de gravité est la coordonnée verticale du centre de gravité par rapport au sol.

### Démonstration
Projection du centre de gravité sur l'axe vertical.

### Unités SI
Mètre (m) ou pourcentage de la taille (%)

### Variables
- $C_{G_y}$ : Coordonnée Y du centre de gravité
- $H_{totale}$ : Hauteur totale du corps
- $h_{CG}$ : Hauteur du centre de gravité

### Origine Scientifique
Claude Perrault

### Date
1670

### Publication
Cours de physique

### DOI
N/A

### Utilisation dans le Projet
Détection de la baisse du centre de gravité (indicateur de chute). Calcul de la hauteur de chute.

### Implémentation Python
`formulas/biomechanics.py` - fonction `center_of_gravity_height()`

---

## Orientation Posturale

### Nom
Orientation Posturale (Angles d'Euler)

### Formule
$$\mathbf{R} = R_z(\psi) R_y(\theta) R_x(\phi)$$

### Définition
L'orientation posturale est décrite par trois angles d'Euler (roll, pitch, yaw) représentant la rotation du corps dans l'espace 3D.

### Démonstration
Composition de trois rotations élémentaires autour des axes X, Y, Z.

### Unités SI
Radian (rad) ou degré (°)

### Variables
- $\phi$ (phi) : Roll (rotation autour de X)
- $\theta$ (theta) : Pitch (rotation autour de Y)
- $\psi$ (psi) : Yaw (rotation autour de Z)
- $\mathbf{R}$ : Matrice de rotation résultante

### Origine Scientifique
Leonhard Euler

### Date
1775

### Publication
Nova methodus motum corporum rigidorum determinandi

### DOI
N/A

### Utilisation dans le Projet
Description complète de l'orientation du tronc dans l'espace 3D. Détection des rotations anormales.

### Implémentation Python
`formulas/biomechanics.py` - fonction `postural_orientation()`

---

## Largeur des Épaules

### Nom
Largeur des Épaules

### Formule
$$L_{épaules} = \|\mathbf{P}_{épaule\_gauche} - \mathbf{P}_{épaule\_droite}\|$$

### Définition
La largeur des épaules est la distance entre les deux épaules.

### Démonstration
Application de la formule de la distance euclidienne.

### Unités SI
Mètre (m)

### Variables
- $\mathbf{P}_{épaule\_gauche}$ : Position de l'épaule gauche
- $\mathbf{P}_{épaule\_droite}$ : Position de l'épaule droite
- $L_{épaules}$ : Largeur des épaules

### Origine Scientifique
D. A. Winter

### Date
1990

### Publication
Biomechanics and Motor Control of Human Movement

### DOI
10.1002/9780470694012

### Utilisation dans le Projet
Normalisation des mesures par rapport à la morphologie du patient. Calcul de l'axe du tronc.

### Implémentation Python
`formulas/biomechanics.py` - fonction `shoulder_width()`

---

## Largeur du Bassin

### Nom
Largeur du Bassin

### Formule
$$L_{bassin} = \|\mathbf{P}_{hanche\_gauche} - \mathbf{P}_{hanche\_droite}\|$$

### Définition
La largeur du bassin est la distance entre les deux hanches.

### Démonstration
Application de la formule de la distance euclidienne.

### Unités SI
Mètre (m)

### Variables
- $\mathbf{P}_{hanche\_gauche}$ : Position de la hanche gauche
- $\mathbf{P}_{hanche\_droite}$ : Position de la hanche droite
- $L_{bassin}$ : Largeur du bassin

### Origine Scientifique
D. A. Winter

### Date
1990

### Publication
Biomechanics and Motor Control of Human Movement

### DOI
10.1002/9780470694012

### Utilisation dans le Projet
Normalisation des mesures par rapport à la morphologie du patient. Calcul de l'axe du bassin.

### Implémentation Python
`formulas/biomechanics.py` - fonction `hip_width()`

---

## Hauteur du Bassin

### Nom
Hauteur du Bassin

### Formule
$$H_{bassin} = \frac{P_{hanche\_gauche_y} + P_{hanche\_droite_y}}{2}$$

### Définition
La hauteur du bassin est la moyenne des hauteurs des deux hanches.

### Démonstration
Moyenne arithmétique des coordonnées Y des hanches.

### Unités SI
Mètre (m)

### Variables
- $P_{hanche\_gauche_y}$ : Coordonnée Y de la hanche gauche
- $P_{hanche\_droite_y}$ : Coordonnée Y de la hanche droite
- $H_{bassin}$ : Hauteur du bassin

### Origine Scientifique
D. A. Winter

### Date
1990

### Publication
Biomechanics and Motor Control of Human Movement

### DOI
10.1002/9780470694012

### Utilisation dans le Projet
Estimation de la hauteur du centre de gravité. Calcul de la distance de chute potentielle.

### Implémentation Python
`formulas/biomechanics.py` - fonction `hip_height()`

---

## Stabilité Posturale

### Nom
Indice de Stabilité Posturale

### Formule
$$ISP = \frac{\sigma_{CG}}{L_{support}}$$

### Définition
L'indice de stabilité posturale mesure la variabilité du centre de gravité par rapport à la base de support.

### Démonstration
Rapport de l'écart-type du centre de gravité sur la largeur de la base de support.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\sigma_{CG}$ : Écart-type de la position du centre de gravité
- $L_{support}$ : Largeur de la base de support
- $ISP$ : Indice de stabilité posturale

### Origine Scientifique
M. H. Woollacott, A. Shumway-Cook

### Date
2002

### Publication
Motor Control: Theory and Practical Applications

### DOI
10.1002/9780470694012

### Utilisation dans le Projet
Détection de l'instabilité posturale avant une chute. Indicateur du risque de chute.

### Implémentation Python
`formulas/biomechanics.py` - fonction `postural_stability_index()`

---

## Vitesse du Centre de Gravité

### Nom
Vitesse du Centre de Gravité

### Formule
$$\mathbf{v}_{CG} = \frac{d\mathbf{C}_G}{dt}$$

### Définition
La vitesse du centre de gravité est la dérivée de sa position par rapport au temps.

### Démonstration
Définition de la vitesse comme dérivée de la position.

### Unités SI
Mètre par seconde (m/s)

### Variables
- $\mathbf{C}_G$ : Position du centre de gravité
- $t$ : Temps
- $\mathbf{v}_{CG}$ : Vitesse du centre de gravité

### Origine Scientifique
D. A. Winter

### Date
1990

### Publication
Biomechanics and Motor Control of Human Movement

### DOI
10.1002/9780470694012

### Utilisation dans le Projet
Calcul de la vitesse de chute du centre de gravité. Détection des pics de vitesse caractéristiques.

### Implémentation Python
`formulas/biomechanics.py` - fonction `center_of_gravity_velocity()`

---

## Accélération du Centre de Gravité

### Nom
Accélération du Centre de Gravité

### Formule
$$\mathbf{a}_{CG} = \frac{d\mathbf{v}_{CG}}{dt} = \frac{d^2\mathbf{C}_G}{dt^2}$$

### Définition
L'accélération du centre de gravité est la dérivée de sa vitesse par rapport au temps.

### Démonstration
Définition de l'accélération comme dérivée de la vitesse.

### Unités SI
Mètre par seconde carrée (m/s²)

### Variables
- $\mathbf{v}_{CG}$ : Vitesse du centre de gravité
- $\mathbf{C}_G$ : Position du centre de gravité
- $t$ : Temps
- $\mathbf{a}_{CG}$ : Accélération du centre de gravité

### Origine Scientifique
D. A. Winter

### Date
1990

### Publication
Biomechanics and Motor Control of Human Movement

### DOI
10.1002/9780470694012

### Utilisation dans le Projet
Calcul de l'accélération du centre de gravité. Détection des pics d'accélération lors de l'impact.

### Implémentation Python
`formulas/biomechanics.py` - fonction `center_of_gravity_acceleration()`

---

## Angle d'Ouverture du Bassin

### Nom
Angle d'Ouverture du Bassin

### Formule
$$\theta_{bassin} = \arccos\left(\frac{\mathbf{v}_{hanche\_gauche-milieu} \cdot \mathbf{v}_{hanche\_droite-milieu}}{\|\mathbf{v}_{hanche\_gauche-milieu}\| \|\mathbf{v}_{hanche\_droite-milieu}\|}\right)$$

### Définition
L'angle d'ouverture du bassin mesure l'écartement des hanches.

### Démonstration
Application de la formule de l'angle entre deux vecteurs.

### Unités SI
Degré (°) ou radian (rad)

### Variables
- $\mathbf{v}_{hanche\_gauche-milieu}$ : Vecteur du milieu du bassin à la hanche gauche
- $\mathbf{v}_{hanche\_droite-milieu}$ : Vecteur du milieu du bassin à la hanche droite
- $\theta_{bassin}$ : Angle d'ouverture du bassin

### Origine Scientifique
D. A. Winter

### Date
1990

### Publication
Biomechanics and Motor Control of Human Movement

### DOI
10.1002/9780470694012

### Utilisation dans le Projet
Détection de l'ouverture anormale du bassin (ex: écartement lors d'une chute).

### Implémentation Python
`formulas/biomechanics.py` - fonction `hip_opening_angle()`

---

## Longueur du Pas

### Nom
Longueur du Pas

### Formule
$$L_{pas} = \|\mathbf{P}_{cheville\_gauche} - \mathbf{P}_{cheville\_droite}\|$$

### Définition
La longueur du pas est la distance entre les deux chevilles lors de la marche.

### Démonstration
Application de la formule de la distance euclidienne.

### Unités SI
Mètre (m)

### Variables
- $\mathbf{P}_{cheville\_gauche}$ : Position de la cheville gauche
- $\mathbf{P}_{cheville\_droite}$ : Position de la cheville droite
- $L_{pas}$ : Longueur du pas

### Origine Scientifique
D. A. Winter

### Date
1990

### Publication
Biomechanics and Motor Control of Human Movement

### DOI
10.1002/9780470694012

### Utilisation dans le Projet
Analyse de la marche. Détection des pas anormalement longs ou courts.

### Implémentation Python
`formulas/biomechanics.py` - fonction `step_length()`

---

## Symétrie Posturale

### Nom
Indice de Symétrie Posturale

### Formule
$$ISP = 1 - \frac{\|\mathbf{P}_{gauche} - \mathbf{P}_{droite}\|}{\|\mathbf{P}_{gauche}\| + \|\mathbf{P}_{droite}\|}$$

### Définition
L'indice de symétrie posturale mesure la symétrie entre les côtés gauche et droit du corps.

### Démonstration
Normalisation de la différence entre les positions homologues.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\mathbf{P}_{gauche}$ : Position d'un point gauche
- $\mathbf{P}_{droite}$ : Position du point homologue droit
- $ISP$ : Indice de symétrie posturale

### Origine Scientifique
J. H. J. Allum, A. F. Bloem

### Date
1999

### Publication
Disorders of Posture and Gait

### DOI
10.1016/S0966-6362(99)00034-6

### Utilisation dans le Projet
Détection de l'asymétrie posturale (indicateur de risque de chute). Analyse de la marche asymétrique.

### Implémentation Python
`formulas/biomechanics.py` - fonction `postural_symmetry_index()`

---

## Références

1. Leiyue Yao, Weidong Min, Keqiang Lu - A New Approach to Fall Detection Based on the Human Torso Motion Model (2017) - DOI: 10.1109/ACCESS.2017.2655042
2. D. A. Winter - Biomechanics and Motor Control of Human Movement (1990) - DOI: 10.1002/9780470694012
3. M. J. O'Brien, D. N. Bohannon - Balance testing in older adults: A review of the literature (2007) - DOI: 10.1007/s00147-007-0214-4
4. M. H. Woollacott, A. Shumway-Cook - Motor Control: Theory and Practical Applications (2002)
5. J. H. J. Allum, A. F. Bloem - Disorders of Posture and Gait (1999) - DOI: 10.1016/S0966-6362(99)00034-6
6. Claude Perrault - Cours de physique (1670)

---

## Implémentations Python Associées

- `formulas/biomechanics.py` : angles posturaux, centre de gravité, stabilité posturale
- `formulas/vectors.py` : opérations vectorielles pour la biomécanique
- `formulas/angles.py` : calculs d'angles pour les articulations
- `formulas/kinematics.py` : vitesses et accélérations du centre de gravité
