# 03 - Trigonometry

## Trigonométrie

---

## Sinus

### Nom
Sinus

### Formule
$$\sin(\theta) = \frac{\text{côté opposé}}{\text{hypoténuse}}$$

### Définition
Dans un triangle rectangle, le sinus d'un angle est le rapport du côté opposé à l'hypoténuse.

### Démonstration
Définition fondamentale des fonctions trigonométriques dans le triangle rectangle.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\theta$ : Angle (rad ou °)
- $\sin(\theta)$ : Sinus de l'angle

### Origine Scientifique
Hipparque de Nicée

### Date
≈ 190 avant J.-C.

### Publication
Tables trigonométriques (perdues, citées par Ptolémée)

### DOI
N/A

### Utilisation dans le Projet
Calcul de la composante verticale d'un vecteur. Décomposition des vecteurs de mouvement. Calcul des angles d'inclinaison du tronc.

### Implémentation Python
`formulas/angles.py` - fonction `sin()`

---

## Cosinus

### Nom
Cosinus

### Formule
$$\cos(\theta) = \frac{\text{côté adjacent}}{\text{hypoténuse}}$$

### Définition
Dans un triangle rectangle, le cosinus d'un angle est le rapport du côté adjacent à l'hypoténuse.

### Démonstration
Définition fondamentale des fonctions trigonométriques dans le triangle rectangle.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\theta$ : Angle (rad ou °)
- $\cos(\theta)$ : Cosinus de l'angle

### Origine Scientifique
Hipparque de Nicée

### Date
≈ 190 avant J.-C.

### Publication
Tables trigonométriques (perdues, citées par Ptolémée)

### DOI
N/A

### Utilisation dans le Projet
Calcul de la composante horizontale d'un vecteur. Calcul de l'angle entre deux vecteurs via le produit scalaire. Normalisation des vecteurs.

### Implémentation Python
`formulas/angles.py` - fonction `cos()`

---

## Tangente

### Nom
Tangente

### Formule
$$\tan(\theta) = \frac{\sin(\theta)}{\cos(\theta)} = \frac{\text{côté opposé}}{\text{côté adjacent}}$$

### Définition
Dans un triangle rectangle, la tangente d'un angle est le rapport du côté opposé au côté adjacent.

### Démonstration
Dérivé des définitions du sinus et du cosinus.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\theta$ : Angle (rad ou °)
- $\tan(\theta)$ : Tangente de l'angle

### Origine Scientifique
Hipparque de Nicée

### Date
≈ 190 avant J.-C.

### Publication
Tables trigonométriques (perdues, citées par Ptolémée)

### DOI
N/A

### Utilisation dans le Projet
Calcul de la pente d'un segment. Détermination de l'angle d'inclinaison à partir du rapport des composantes. Calcul de l'angle du tronc.

### Implémentation Python
`formulas/angles.py` - fonction `tan()`

---

## Arcsinus

### Nom
Arcsinus (Inverse Sinus)

### Formule
$$\theta = \arcsin(x) \iff \sin(\theta) = x$$

### Définition
L'arcsinus est la fonction inverse du sinus, donnant l'angle dont le sinus est la valeur donnée.

### Démonstration
Définition de la fonction inverse.

### Unités SI
Radian (rad) ou degré (°)

### Variables
- $x$ : Valeur dans [-1, 1]
- $\theta$ : Angle résultant

### Origine Scientifique
Carl Friedrich Gauss

### Date
1799

### Publication
Disquisitiones Arithmeticae

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'angle à partir du rapport des composantes verticales. Détermination de l'angle d'inclinaison du tronc.

### Implémentation Python
`formulas/angles.py` - fonction `arcsin()`

---

## Arccosinus

### Nom
Arccosinus (Inverse Cosinus)

### Formule
$$\theta = \arccos(x) \iff \cos(\theta) = x$$

### Définition
L'arccosinus est la fonction inverse du cosinus, donnant l'angle dont le cosinus est la valeur donnée.

### Démonstration
Définition de la fonction inverse.

### Unités SI
Radian (rad) ou degré (°)

### Variables
- $x$ : Valeur dans [-1, 1]
- $\theta$ : Angle résultant

### Origine Scientifique
Carl Friedrich Gauss

### Date
1799

### Publication
Disquisitiones Arithmeticae

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'angle entre deux vecteurs via le produit scalaire. Détermination de l'angle d'ouverture des articulations.

### Implémentation Python
`formulas/angles.py` - fonction `arccos()`

---

## Arctangente

### Nom
Arctangente (Inverse Tangente)

### Formule
$$\theta = \arctan(x) \iff \tan(\theta) = x$$

### Définition
L'arctangente est la fonction inverse de la tangente, donnant l'angle dont la tangente est la valeur donnée.

### Démonstration
Définition de la fonction inverse.

### Unités SI
Radian (rad) ou degré (°)

### Variables
- $x$ : Valeur réelle
- $\theta$ : Angle résultant

### Origine Scientifique
Carl Friedrich Gauss

### Date
1799

### Publication
Disquisitiones Arithmeticae

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'angle à partir du rapport des composantes. Détermination de l'angle d'inclinaison à partir de la pente.

### Implémentation Python
`formulas/angles.py` - fonction `arctan()`

---

## Arctangente à Deux Arguments

### Nom
Arctangente à Deux Arguments (atan2)

### Formule
$$\theta = \operatorname{atan2}(y, x)$$

### Définition
L'arctangente à deux arguments donne l'angle entre l'axe X positif et le point (x, y), en tenant compte du quadrant.

### Valeurs
- $\operatorname{atan2}(y, x) = \arctan(y/x)$ si $x > 0$
- $\operatorname{atan2}(y, x) = \arctan(y/x) + \pi$ si $x < 0$ et $y \geq 0$
- $\operatorname{atan2}(y, x) = \arctan(y/x) - \pi$ si $x < 0$ et $y < 0$

### Démonstration
Extension de l'arctangente pour couvrir tous les quadrants.

### Unités SI
Radian (rad) ou degré (°)

### Variables
- $x, y$ : Coordonnées du point
- $\theta$ : Angle résultant dans $[-\pi, \pi]$

### Origine Scientifique
IBM Fortran

### Date
1961

### Publication
Fortran Automatic Coding System

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'angle complet d'un vecteur dans le plan. Détermination de l'orientation du tronc dans toutes les directions. Calcul des angles MediaPipe.

### Implémentation Python
`formulas/angles.py` - fonction `atan2()`

---

## Théorème de Pythagore

### Nom
Théorème de Pythagore

### Formule
$$a^2 + b^2 = c^2$$

### Définition
Dans un triangle rectangle, le carré de l'hypoténuse est égal à la somme des carrés des deux autres côtés.

### Démonstration
Preuve géométrique par réarrangement de carrés. Preuve algébrique utilisant des triangles similaires.

### Unités SI
Carré de l'unité de longueur (m²)

### Variables
- $a, b$ : Cathètes (côtés de l'angle droit)
- $c$ : Hypoténuse

### Origine Scientifique
Pythagore de Samos

### Date
≈ 570-495 avant J.-C.

### Publication
Éléments (Euclide, Livre I, Proposition 47)

### DOI
N/A

### Utilisation dans le Projet
Calcul de la distance euclidienne. Calcul de la norme vectorielle. Vérification de la perpendicularité.

### Implémentation Python
`formulas/distance.py` - fonction `pythagorean_theorem()`

---

## Loi des Cosinus

### Nom
Loi des Cosinus (Théorème d'Al-Kashi)

### Formule
$$c^2 = a^2 + b^2 - 2ab \cos(\gamma)$$

### Définition
Dans un triangle quelconque, le carré d'un côté est égal à la somme des carrés des deux autres côtés moins deux fois leur produit par le cosinus de l'angle entre eux.

### Démonstration
Généralisation du théorème de Pythagore utilisant la projection d'un côté sur l'autre.

### Unités SI
Carré de l'unité de longueur (m²)

### Variables
- $a, b, c$ : Longueurs des côtés
- $\gamma$ : Angle opposé au côté $c$

### Origine Scientifique
Al-Kashi (Jamshīd al-Kāshī)

### Date
1427

### Publication
Miftāḥ al-ḥisāb (La Clé de l'arithmétique)

### DOI
N/A

### Utilisation dans le Projet
Calcul de la distance entre deux points quand l'angle est connu. Calcul de l'angle entre deux vecteurs. Détermination de la longueur des segments du corps.

### Implémentation Python
`formulas/angles.py` - fonction `law_of_cosines()`

---

## Loi des Sinus

### Nom
Loi des Sinus

### Formule
$$\frac{a}{\sin(\alpha)} = \frac{b}{\sin(\beta)} = \frac{c}{\sin(\gamma)} = 2R$$

### Définition
Dans un triangle quelconque, le rapport entre la longueur d'un côté et le sinus de l'angle opposé est constant et égal au diamètre du cercle circonscrit.

### Démonstration
Utilisation du cercle circonscrit et de la propriété des angles inscrits.

### Unités SI
Rapport de longueur (m) sur sans dimension = m

### Variables
- $a, b, c$ : Longueurs des côtés
- $\alpha, \beta, \gamma$ : Angles opposés
- $R$ : Rayon du cercle circonscrit

### Origine Scientifique
Nasir al-Din al-Tusi

### Date
13ème siècle

### Publication
Traité du quadrilatère complet

### DOI
N/A

### Utilisation dans le Projet
Calcul des angles d'un triangle quand les côtés sont connus. Détermination de l'orientation des segments du corps.

### Implémentation Python
`formulas/angles.py` - fonction `law_of_sines()`

---

## Identité Fondamentale

### Nom
Identité Trigonométrique Fondamentale

### Formule
$$\sin^2(\theta) + \cos^2(\theta) = 1$$

### Définition
Pour tout angle, la somme des carrés du sinus et du cosinus est égale à 1.

### Démonstration
Dérivé du théorème de Pythagore appliqué au cercle unité.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\theta$ : Angle quelconque

### Origine Scientifique
Euclide

### Date
≈ 300 avant J.-C.

### Publication
Éléments (Elements)

### DOI
N/A

### Utilisation dans le Projet
Normalisation des vecteurs. Vérification de la cohérence des calculs d'angles. Conversion entre sinus et cosinus.

### Implémentation Python
`formulas/angles.py` - fonction `trigonometric_identity()`

---

## Formules d'Addition

### Nom
Formules d'Addition

### Sinus
$$\sin(\alpha + \beta) = \sin(\alpha)\cos(\beta) + \cos(\alpha)\sin(\beta)$$

### Cosinus
$$\cos(\alpha + \beta) = \cos(\alpha)\cos(\beta) - \sin(\alpha)\sin(\beta)$$

### Définition
Les formules d'addition permettent d'exprimer le sinus et le cosinus d'une somme d'angles en fonction des sinus et cosinus des angles individuels.

### Démonstration
Preuve géométrique utilisant des rotations dans le plan.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\alpha, \beta$ : Angles

### Origine Scientifique
Ptolémée

### Date
≈ 150 après J.-C.

### Publication
Almageste

### DOI
N/A

### Utilisation dans le Projet
Composition de rotations. Calcul d'angles résultants. Interpolation angulaire.

### Implémentation Python
`formulas/angles.py` - fonction `addition_formulas()`

---

## Formules de Soustraction

### Nom
Formules de Soustraction

### Sinus
$$\sin(\alpha - \beta) = \sin(\alpha)\cos(\beta) - \cos(\alpha)\sin(\beta)$$

### Cosinus
$$\cos(\alpha - \beta) = \cos(\alpha)\cos(\beta) + \sin(\alpha)\sin(\beta)$$

### Définition
Les formules de soustraction permettent d'exprimer le sinus et le cosinus d'une différence d'angles.

### Démonstration
Dérivé des formules d'addition en utilisant $\sin(-\beta) = -\sin(\beta)$ et $\cos(-\beta) = \cos(\beta)$.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\alpha, \beta$ : Angles

### Origine Scientifique
Ptolémée

### Date
≈ 150 après J.-C.

### Publication
Almageste

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'angle relatif entre deux orientations. Différence angulaire pour la détection de mouvement.

### Implémentation Python
`formulas/angles.py` - fonction `subtraction_formulas()`

---

## Formules du Double Angle

### Nom
Formules du Double Angle

### Sinus
$$\sin(2\theta) = 2\sin(\theta)\cos(\theta)$$

### Cosinus
$$\cos(2\theta) = \cos^2(\theta) - \sin^2(\theta) = 2\cos^2(\theta) - 1 = 1 - 2\sin^2(\theta)$$

### Définition
Les formules du double angle expriment les fonctions trigonométriques de $2\theta$ en fonction de celles de $\theta$.

### Démonstration
Dérivé des formules d'addition avec $\alpha = \beta = \theta$.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\theta$ : Angle

### Origine Scientifique
Ptolémée

### Date
≈ 150 après J.-C.

### Publication
Almageste

### DOI
N/A

### Utilisation dans le Projet
Calcul d'angles doubles pour l'analyse des mouvements complexes. Détection des changements de direction rapides.

### Implémentation Python
`formulas/angles.py` - fonction `double_angle_formulas()`

---

## Formules de Moitié d'Angle

### Nom
Formules de Moitié d'Angle

### Sinus
$$\sin\left(\frac{\theta}{2}\right) = \pm\sqrt{\frac{1 - \cos(\theta)}{2}}$$

### Cosinus
$$\cos\left(\frac{\theta}{2}\right) = \pm\sqrt{\frac{1 + \cos(\theta)}{2}}$$

### Définition
Les formules de moitié d'angle expriment les fonctions trigonométriques de $\theta/2$ en fonction de $\cos(\theta)$.

### Démonstration
Dérivé des formules du double angle.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\theta$ : Angle

### Origine Scientifique
Viète

### Date
1590s

### Publication
Canon Mathematicus

### DOI
N/A

### Utilisation dans le Projet
Interpolation angulaire fine. Calcul d'angles intermédiaires pour l'analyse du mouvement.

### Implémentation Python
`formulas/angles.py` - fonction `half_angle_formulas()`

---

## Formules de Produit

### Nom
Formules de Produit en Somme

### Sinus × Cosinus
$$\sin(\alpha)\cos(\beta) = \frac{1}{2}[\sin(\alpha + \beta) + \sin(\alpha - \beta)]$$

### Cosinus × Cosinus
$$\cos(\alpha)\cos(\beta) = \frac{1}{2}[\cos(\alpha + \beta) + \cos(\alpha - \beta)]$$

### Sinus × Sinus
$$\sin(\alpha)\sin(\beta) = \frac{1}{2}[\cos(\alpha - \beta) - \cos(\alpha + \beta)]$$

### Définition
Les formules de produit transforment un produit de fonctions trigonométriques en une somme.

### Démonstration
Dérivé des formules d'addition et de soustraction.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\alpha, \beta$ : Angles

### Origine Scientifique
Ptolémée

### Date
≈ 150 après J.-C.

### Publication
Almageste

### DOI
N/A

### Utilisation dans le Projet
Analyse fréquentielle du mouvement. Décomposition des mouvements complexes.

### Implémentation Python
`formulas/angles.py` - fonction `product_to_sum_formulas()`

---

## Conversion Degrés-Radians

### Nom
Conversion Degrés en Radians

### Formule
$$\theta_{\text{rad}} = \theta_{\text{deg}} \times \frac{\pi}{180}$$

### Conversion Radians en Degrés
$$\theta_{\text{deg}} = \theta_{\text{rad}} \times \frac{180}{\pi}$$

### Définition
Conversion entre les unités d'angle degrés et radians.

### Démonstration
Définition du radian comme l'angle sous-tendu par un arc de longueur égale au rayon.

### Unités SI
Radian (rad) pour le système SI

### Variables
- $\theta_{\text{deg}}$ : Angle en degrés
- $\theta_{\text{rad}}$ : Angle en radians
- $\pi$ : Constante pi ≈ 3.14159

### Origine Scientifique
Roger Cotes

### Date
1714

### Publication
Harmonia Mensurarum

### DOI
N/A

### Utilisation dans le Projet
Conversion des angles MediaPipe (radians) en degrés pour l'affichage. Conversion pour les calculs trigonométriques.

### Implémentation Python
`formulas/angles.py` - fonction `deg_to_rad()`, `rad_to_deg()`

---

## Angle d'Inclinaison

### Nom
Angle d'Inclinaison par Rapport à la Verticale

### Formule
$$\theta = \arctan\left(\frac{\Delta x}{\Delta y}\right)$$

### Définition
L'angle d'inclinaison d'un segment par rapport à la verticale est calculé à partir du rapport des composantes horizontale et verticale.

### Démonstration
Application de la définition de la tangente dans un triangle rectangle.

### Unités SI
Radian (rad) ou degré (°)

### Variables
- $\Delta x$ : Composante horizontale
- $\Delta y$ : Composante verticale
- $\theta$ : Angle d'inclinaison

### Origine Scientifique
Euclide

### Date
≈ 300 avant J.-C.

### Publication
Éléments (Elements)

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'angle du tronc par rapport à la verticale. Détection des inclinaisons anormales du corps.

### Implémentation Python
`formulas/angles.py` - fonction `inclination_angle()`

---

## Angle entre Deux Segments

### Nom
Angle entre Deux Segments

### Formule
$$\theta = \arccos\left(\frac{\mathbf{v}_1 \cdot \mathbf{v}_2}{\|\mathbf{v}_1\| \|\mathbf{v}_2\|}\right)$$

### Définition
L'angle entre deux segments est calculé à partir du produit scalaire des vecteurs correspondants.

### Démonstration
Dérivé de la formule géométrique du produit scalaire.

### Unités SI
Radian (rad) ou degré (°)

### Variables
- $\mathbf{v}_1, \mathbf{v}_2$ : Vecteurs représentant les segments
- $\theta$ : Angle entre les segments

### Origine Scientifique
Euclide

### Date
≈ 300 avant J.-C.

### Publication
Éléments (Elements)

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'angle du coude (bras-avant-bras). Angle du genou (cuisse-jambe). Angle du tronc (épaules-hanches).

### Implémentation Python
`formulas/angles.py` - fonction `angle_between_segments()`

---

## Angle Dièdre

### Nom
Angle Dièdre (Angle entre Deux Plans)

### Formule
$$\theta = \arccos\left(\frac{\mathbf{n}_1 \cdot \mathbf{n}_2}{\|\mathbf{n}_1\| \|\mathbf{n}_2\|}\right)$$

### Définition
L'angle dièdre est l'angle entre deux plans, calculé à partir de leurs vecteurs normaux.

### Démonstration
L'angle entre deux plans est égal à l'angle entre leurs vecteurs normaux.

### Unités SI
Radian (rad) ou degré (°)

### Variables
- $\mathbf{n}_1, \mathbf{n}_2$ : Vecteurs normaux des plans
- $\theta$ : Angle dièdre

### Origine Scientifique
Gaspard Monge

### Date
1795

### Publication
Géométrie Descriptive

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'angle entre le plan du tronc et le plan vertical. Détection des rotations du corps dans l'espace 3D.

### Implémentation Python
`formulas/angles.py` - fonction `dihedral_angle()`

---

## Références

1. Hipparchus - Trigonometric Tables (~190 BC)
2. Ptolemy - Almagest (~150 AD)
3. Al-Kashi - Miftāḥ al-ḥisāb (1427)
4. Al-Tusi - Treatise on the Complete Quadrilateral (13th century)
5. Viète - Canon Mathematicus (1590s)
6. Cotes - Harmonia Mensurarum (1714)
7. Monge - Géométrie Descriptive (1795)

---

## Implémentations Python Associées

- `formulas/angles.py` : fonctions trigonométriques, calculs d'angles, conversions
- `formulas/vectors.py` : calculs d'angles entre vecteurs
- `formulas/distance.py` : théorème de Pythagore pour les distances
