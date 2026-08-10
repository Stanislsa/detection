# 02 - Linear Algebra

## Algèbre Linéaire

---

## Addition de Vecteurs

### Nom
Addition de Vecteurs

### Formule
$$\mathbf{a} + \mathbf{b} = (a_x + b_x, a_y + b_y, a_z + b_z)$$

### Définition
L'addition de deux vecteurs se fait composante par composante. Le résultat est un vecteur dont chaque composante est la somme des composantes correspondantes.

### Démonstration
Propriété fondamentale de l'espace vectoriel. La commutativité et l'associativité découlent de celles des nombres réels.

### Unités SI
Même unité que les vecteurs (m si vecteurs en mètres)

### Variables
- $\mathbf{a} = (a_x, a_y, a_z)$ : Premier vecteur
- $\mathbf{b} = (b_x, b_y, b_z)$ : Deuxième vecteur
- $\mathbf{a} + \mathbf{b}$ : Vecteur résultant

### Origine Scientifique
Hermann Grassmann

### Date
1844

### Publication
Die Lineale Ausdehnungslehre

### DOI
N/A

### Utilisation dans le Projet
Combinaison de vecteurs de déplacement (ex: déplacement total = déplacement épaule + déplacement coude). Calcul de vecteurs résultants pour l'analyse du mouvement.

### Implémentation Python
`formulas/vectors.py` - fonction `vector_add()`

---

## Soustraction de Vecteurs

### Nom
Soustraction de Vecteurs

### Formule
$$\mathbf{a} - \mathbf{b} = (a_x - b_x, a_y - b_y, a_z - b_z)$$

### Définition
La soustraction de deux vecteurs est équivalente à l'addition du premier vecteur avec l'opposé du second.

### Démonstration
$\mathbf{a} - \mathbf{b} = \mathbf{a} + (-\mathbf{b})$ où $-\mathbf{b} = (-b_x, -b_y, -b_z)$

### Unités SI
Même unité que les vecteurs (m si vecteurs en mètres)

### Variables
- $\mathbf{a} = (a_x, a_y, a_z)$ : Premier vecteur
- $\mathbf{b} = (b_x, b_y, b_z)$ : Deuxième vecteur
- $\mathbf{a} - \mathbf{b}$ : Vecteur résultant

### Origine Scientifique
Hermann Grassmann

### Date
1844

### Publication
Die Lineale Ausdehnungslehre

### DOI
N/A

### Utilisation dans le Projet
Calcul du vecteur de déplacement entre deux positions (ex: vecteur épaule → coude). Utilisé pour calculer les vitesses et accélérations.

### Implémentation Python
`formulas/vectors.py` - fonction `vector_subtract()`

---

## Multiplication Scalaire

### Nom
Multiplication par un Scalaire

### Formule
$$k\mathbf{a} = (k a_x, k a_y, k a_z)$$

### Définition
La multiplication d'un vecteur par un scalaire multiplie chaque composante par ce scalaire.

### Démonstration
Propriété de linéarité de l'espace vectoriel.

### Unités SI
Unité du scalaire × unité du vecteur

### Variables
- $k$ : Scalaire (nombre réel)
- $\mathbf{a} = (a_x, a_y, a_z)$ : Vecteur
- $k\mathbf{a}$ : Vecteur résultant

### Origine Scientifique
Hermann Grassmann

### Date
1844

### Publication
Die Lineale Ausdehnungslehre

### DOI
N/A

### Utilisation dans le Projet
Normalisation des vecteurs (division par la norme). Mise à l'échelle des vecteurs de vitesse ou d'accélération. Interpolation entre positions.

### Implémentation Python
`formulas/vectors.py` - fonction `scalar_multiply()`

---

## Division Scalaire

### Nom
Division par un Scalaire

### Formule
$$\frac{\mathbf{a}}{k} = \left(\frac{a_x}{k}, \frac{a_y}{k}, \frac{a_z}{k}\right)$$

### Définition
La division d'un vecteur par un scalaire est équivalente à la multiplication par l'inverse du scalaire.

### Démonstration
$\frac{\mathbf{a}}{k} = \mathbf{a} \times \frac{1}{k}$

### Unités SI
Unité du vecteur / unité du scalaire

### Variables
- $k$ : Scalaire (nombre réel, $k \neq 0$)
- $\mathbf{a} = (a_x, a_y, a_z)$ : Vecteur
- $\frac{\mathbf{a}}{k}$ : Vecteur résultant

### Origine Scientifique
Hermann Grassmann

### Date
1844

### Publication
Die Lineale Ausdehnungslehre

### DOI
N/A

### Utilisation dans le Projet
Normalisation des vecteurs (division par la norme). Calcul de vecteurs unitaires. Mise à l'échelle inverse pour les calculs de temps.

### Implémentation Python
`formulas/vectors.py` - fonction `scalar_divide()`

---

## Produit Scalaire (Dot Product)

### Nom
Produit Scalaire

### Formule Algébrique
$$\mathbf{a} \cdot \mathbf{b} = a_x b_x + a_y b_y + a_z b_z$$

### Formule Géométrique
$$\mathbf{a} \cdot \mathbf{b} = \|\mathbf{a}\| \|\mathbf{b}\| \cos(\theta)$$

### Définition
Le produit scalaire de deux vecteurs est un scalaire égal au produit de leurs normes par le cosinus de l'angle entre eux.

### Démonstration
Dérivé de la loi des cosinus et de la définition de la norme euclidienne.

### Unités SI
Produit des unités des vecteurs (m² si vecteurs en mètres)

### Variables
- $\mathbf{a} = (a_x, a_y, a_z)$ : Premier vecteur
- $\mathbf{b} = (b_x, b_y, b_z)$ : Deuxième vecteur
- $\theta$ : Angle entre les vecteurs
- $\|\mathbf{a}\|$ : Norme du vecteur $\mathbf{a}$

### Origine Scientifique
Josiah Willard Gibbs / Oliver Heaviside

### Date
1880s

### Publication
Vector Analysis (1901)

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'angle entre deux segments du corps (ex: angle tronc-cuisse). Détection de l'alignement ou de la divergence des articulations. Calcul de la similarité de direction.

### Implémentation Python
`formulas/vectors.py` - fonction `dot_product()`

---

## Produit Vectoriel (Cross Product)

### Nom
Produit Vectoriel

### Formule
$$\mathbf{a} \times \mathbf{b} = \begin{vmatrix} \mathbf{i} & \mathbf{j} & \mathbf{k} \\ a_x & a_y & a_z \\ b_x & b_y & b_z \end{vmatrix}$$

### Composantes
$$\mathbf{a} \times \mathbf{b} = (a_y b_z - a_z b_y, a_z b_x - a_x b_z, a_x b_y - a_y b_x)$$

### Norme
$$\|\mathbf{a} \times \mathbf{b}\| = \|\mathbf{a}\| \|\mathbf{b}\| \sin(\theta)$$

### Définition
Le produit vectoriel de deux vecteurs est un vecteur perpendiculaire au plan formé par les deux vecteurs, dont la norme est égale à l'aire du parallélogramme formé.

### Démonstration
Dérivé des propriétés algébriques et géométriques des vecteurs en 3D.

### Unités SI
Produit des unités des vecteurs (m² si vecteurs en mètres)

### Variables
- $\mathbf{a} = (a_x, a_y, a_z)$ : Premier vecteur
- $\mathbf{b} = (b_x, b_y, b_z)$ : Deuxième vecteur
- $\theta$ : Angle entre les vecteurs
- $\mathbf{i}, \mathbf{j}, \mathbf{k}$ : Vecteurs unitaires de la base canonique

### Origine Scientifique
Josiah Willard Gibbs / Oliver Heaviside

### Date
1880s

### Publication
Vector Analysis (1901)

### DOI
N/A

### Utilisation dans le Projet
Calcul de vecteurs normaux pour déterminer l'orientation du plan du corps. Détection des rotations du tronc. Calcul de l'aire formée par trois points.

### Implémentation Python
`formulas/vectors.py` - fonction `cross_product()`

---

## Produit Mixte (Scalar Triple Product)

### Nom
Produit Mixte

### Formule
$$[\mathbf{a}, \mathbf{b}, \mathbf{c}] = \mathbf{a} \cdot (\mathbf{b} \times \mathbf{c})$$

### Formule Déterminant
$$[\mathbf{a}, \mathbf{b}, \mathbf{c}] = \begin{vmatrix} a_x & a_y & a_z \\ b_x & b_y & b_z \\ c_x & c_y & c_z \end{vmatrix}$$

### Définition
Le produit mixte de trois vecteurs est un scalaire égal au volume du parallélépipède formé par les trois vecteurs.

### Démonstration
Propriété du déterminant et interprétation géométrique comme volume.

### Unités SI
Produit des unités des trois vecteurs (m³ si vecteurs en mètres)

### Variables
- $\mathbf{a}, \mathbf{b}, \mathbf{c}$ : Trois vecteurs
- $[\mathbf{a}, \mathbf{b}, \mathbf{c}]$ : Produit mixte

### Origine Scientifique
William Rowan Hamilton

### Date
1843

### Publication
Lectures on Quaternions

### DOI
N/A

### Utilisation dans le Projet
Calcul du volume occupé par le corps humain dans l'espace 3D. Détection de la coplanarité de points (produit mixte = 0 si coplanaire).

### Implémentation Python
`formulas/vectors.py` - fonction `scalar_triple_product()`

---

## Norme d'un Vecteur

### Nom
Norme Euclidienne

### Formule
$$\|\mathbf{v}\| = \sqrt{v_x^2 + v_y^2 + v_z^2}$$

### Formule Carrée
$$\|\mathbf{v}\|^2 = v_x^2 + v_y^2 + v_z^2 = \mathbf{v} \cdot \mathbf{v}$$

### Définition
La norme d'un vecteur est sa longueur dans l'espace euclidien.

### Démonstration
Application directe du théorème de Pythagore en 3 dimensions.

### Unités SI
Même unité que les composantes du vecteur (m si vecteur en mètres)

### Variables
- $\mathbf{v} = (v_x, v_y, v_z)$ : Vecteur
- $\|\mathbf{v}\|$ : Norme du vecteur

### Origine Scientifique
Euclide

### Date
≈ 300 avant J.-C.

### Publication
Éléments (Elements)

### DOI
N/A

### Utilisation dans le Projet
Calcul de la longueur des segments du corps. Normalisation des vecteurs pour le calcul d'angles. Calcul des distances entre articulations.

### Implémentation Python
`formulas/vectors.py` - fonction `norm()`

---

## Normalisation d'un Vecteur

### Nom
Vecteur Unitaire (Normalization)

### Formule
$$\hat{\mathbf{v}} = \frac{\mathbf{v}}{\|\mathbf{v}\|}$$

### Définition
La normalisation d'un vecteur consiste à le diviser par sa norme pour obtenir un vecteur unitaire (de norme 1) ayant la même direction.

### Démonstration
$\|\hat{\mathbf{v}}\| = \left\|\frac{\mathbf{v}}{\|\mathbf{v}\|}\right\| = \frac{\|\mathbf{v}\|}{\|\mathbf{v}\|} = 1$

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\mathbf{v}$ : Vecteur à normaliser
- $\|\mathbf{v}\|$ : Norme du vecteur
- $\hat{\mathbf{v}}$ : Vecteur unitaire

### Origine Scientifique
Hermann Grassmann

### Date
1844

### Publication
Die Lineale Ausdehnungslehre

### DOI
N/A

### Utilisation dans le Projet
Normalisation des vecteurs de direction pour le calcul d'angles. Comparaison de directions indépendamment de la magnitude. Calcul des cosinus directeurs.

### Implémentation Python
`formulas/vectors.py` - fonction `normalize()`

---

## Angle entre Deux Vecteurs

### Nom
Angle entre Vecteurs

### Formule
$$\cos(\theta) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|}$$

### Angle
$$\theta = \arccos\left(\frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \|\mathbf{b}\|}\right)$$

### Définition
L'angle entre deux vecteurs est l'angle formé par leurs directions, calculé à partir du produit scalaire.

### Démonstration
Dérivé de la formule géométrique du produit scalaire.

### Unités SI
Radian (rad) ou degré (°)

### Variables
- $\mathbf{a}, \mathbf{b}$ : Deux vecteurs
- $\theta$ : Angle entre les vecteurs
- $\mathbf{a} \cdot \mathbf{b}$ : Produit scalaire
- $\|\mathbf{a}\|, \|\mathbf{b}\|$ : Normes des vecteurs

### Origine Scientifique
Euclide

### Date
≈ 300 avant J.-C.

### Publication
Éléments (Elements)

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'angle du tronc par rapport à la verticale. Angle entre le bras et l'avant-bras. Détection des anomalies posturales.

### Implémentation Python
`formulas/angles.py` - fonction `angle_between_vectors()`

---

## Projection Orthogonale

### Nom
Projection Orthogonale

### Formule
$$\text{proj}_{\mathbf{b}} \mathbf{a} = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{b}\|^2} \mathbf{b}$$

### Composante Parallèle
$$\mathbf{a}_{\parallel} = \text{proj}_{\mathbf{b}} \mathbf{a}$$

### Composante Perpendiculaire
$$\mathbf{a}_{\perp} = \mathbf{a} - \mathbf{a}_{\parallel}$$

### Définition
La projection orthogonale d'un vecteur sur un autre est le composant du premier vecteur parallèle au second.

### Démonstration
Dérivé du produit scalaire et de la propriété d'orthogonalité ($\mathbf{a}_{\perp} \cdot \mathbf{b} = 0$).

### Unités SI
Même unité que les vecteurs (m si vecteurs en mètres)

### Variables
- $\mathbf{a}$ : Vecteur à projeter
- $\mathbf{b}$ : Vecteur sur lequel projeter
- $\text{proj}_{\mathbf{b}} \mathbf{a}$ : Projection de $\mathbf{a}$ sur $\mathbf{b}$

### Origine Scientifique
Hermann Grassmann

### Date
1844

### Publication
Die Lineale Ausdehnungslehre

### DOI
N/A

### Utilisation dans le Projet
Projection du vecteur gravité sur le vecteur tronc. Séparation des composantes verticales et horizontales du mouvement. Calcul de la composante verticale de la vitesse.

### Implémentation Python
`formulas/vectors.py` - fonction `projection()`

---

## Matrice de Rotation 2D

### Nom
Matrice de Rotation 2D

### Formule
$$R(\theta) = \begin{pmatrix} \cos(\theta) & -\sin(\theta) \\ \sin(\theta) & \cos(\theta) \end{pmatrix}$$

### Rotation d'un Vecteur
$$\begin{pmatrix} x' \\ y' \end{pmatrix} = \begin{pmatrix} \cos(\theta) & -\sin(\theta) \\ \sin(\theta) & \cos(\theta) \end{pmatrix} \begin{pmatrix} x \\ y \end{pmatrix}$$

### Définition
La matrice de rotation permet de faire pivoter un vecteur dans le plan d'un angle $\theta$ autour de l'origine.

### Démonstration
Dérivé des formules trigonométriques de rotation et de la préservation de la norme.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\theta$ : Angle de rotation (rad)
- $(x, y)$ : Coordonnées initiales
- $(x', y')$ : Coordonnées après rotation
- $R(\theta)$ : Matrice de rotation

### Origine Scientifique
Leonhard Euler

### Date
1748

### Publication
Introductio in analysin infinitorum

### DOI
N/A

### Utilisation dans le Projet
Rotation des coordonnées MediaPipe pour aligner le repère du corps. Correction de l'orientation de la caméra. Normalisation de la posture.

### Implémentation Python
`formulas/vectors.py` - fonction `rotation_matrix_2d()`

---

## Matrice de Rotation 3D (Axe Z)

### Nom
Matrice de Rotation 3D (Axe Z)

### Formule
$$R_z(\theta) = \begin{pmatrix} \cos(\theta) & -\sin(\theta) & 0 \\ \sin(\theta) & \cos(\theta) & 0 \\ 0 & 0 & 1 \end{pmatrix}$$

### Définition
Rotation autour de l'axe Z d'un angle $\theta$.

### Démonstration
Extension de la rotation 2D à l'espace 3D.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\theta$ : Angle de rotation (rad)
- $R_z(\theta)$ : Matrice de rotation autour de Z

### Origine Scientifique
Leonhard Euler

### Date
1748

### Publication
Introductio in analysin infinitorum

### DOI
N/A

### Utilisation dans le Projet
Rotation des coordonnées 3D MediaPipe. Correction de l'orientation du corps dans l'espace. Normalisation de la posture 3D.

### Implémentation Python
`formulas/vectors.py` - fonction `rotation_matrix_3d_z()`

---

## Matrice de Rotation 3D (Axe Y)

### Nom
Matrice de Rotation 3D (Axe Y)

### Formule
$$R_y(\theta) = \begin{pmatrix} \cos(\theta) & 0 & \sin(\theta) \\ 0 & 1 & 0 \\ -\sin(\theta) & 0 & \cos(\theta) \end{pmatrix}$$

### Définition
Rotation autour de l'axe Y d'un angle $\theta$.

### Démonstration
Extension de la rotation 2D à l'espace 3D.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\theta$ : Angle de rotation (rad)
- $R_y(\theta)$ : Matrice de rotation autour de Y

### Origine Scientifique
Leonhard Euler

### Date
1748

### Publication
Introductio in analysin infinitorum

### DOI
N/A

### Utilisation dans le Projet
Rotation des coordonnées 3D pour corriger l'inclinaison latérale. Normalisation de la posture par rapport au plan sagittal.

### Implémentation Python
`formulas/vectors.py` - fonction `rotation_matrix_3d_y()`

---

## Matrice de Rotation 3D (Axe X)

### Nom
Matrice de Rotation 3D (Axe X)

### Formule
$$R_x(\theta) = \begin{pmatrix} 1 & 0 & 0 \\ 0 & \cos(\theta) & -\sin(\theta) \\ 0 & \sin(\theta) & \cos(\theta) \end{pmatrix}$$

### Définition
Rotation autour de l'axe X d'un angle $\theta$.

### Démonstration
Extension de la rotation 2D à l'espace 3D.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $\theta$ : Angle de rotation (rad)
- $R_x(\theta)$ : Matrice de rotation autour de X

### Origine Scientifique
Leonhard Euler

### Date
1748

### Publication
Introductio in analysin infinitorum

### DOI
N/A

### Utilisation dans le Projet
Rotation des coordonnées 3D pour corriger l'inclinaison antéro-postérieure. Normalisation de la posture par rapport au plan frontal.

### Implémentation Python
`formulas/vectors.py` - fonction `rotation_matrix_3d_x()`

---

## Angles d'Euler

### Nom
Angles d'Euler (Roll, Pitch, Yaw)

### Formule
$$\mathbf{v}' = R_z(\psi) R_y(\theta) R_x(\phi) \mathbf{v}$$

### Où
- $\phi$ (phi) : Roll (rotation autour de X)
- $\theta$ (theta) : Pitch (rotation autour de Y)
- $\psi$ (psi) : Yaw (rotation autour de Z)

### Définition
Les angles d'Euler décrivent l'orientation d'un corps dans l'espace 3D par trois rotations successives.

### Démonstration
Composition de trois rotations élémentaires.

### Unités SI
Radian (rad) ou degré (°)

### Variables
- $\phi, \theta, \psi$ : Angles d'Euler
- $\mathbf{v}$ : Vecteur initial
- $\mathbf{v}'$ : Vecteur après rotation
- $R_x, R_y, R_z$ : Matrices de rotation

### Origine Scientifique
Leonhard Euler

### Date
1775

### Publication
Nova methodus motum corporum rigidorum determinandi

### DOI
N/A

### Utilisation dans le Projet
Description de l'orientation du tronc dans l'espace 3D. Détection des rotations anormales du corps. Normalisation de la posture indépendamment de l'orientation de la caméra.

### Implémentation Python
`formulas/vectors.py` - fonction `euler_angles()`

---

## Déterminant 2x2

### Nom
Déterminant d'une Matrice 2x2

### Formule
$$\det(A) = \det\begin{pmatrix} a & b \\ c & d \end{pmatrix} = ad - bc$$

### Définition
Le déterminant d'une matrice 2x2 est un scalaire qui donne l'aire (signée) du parallélogramme formé par les vecteurs colonnes.

### Démonstration
Propriété algébrique fondamentale des déterminants.

### Unités SI
Produit des unités des éléments (m² si vecteurs en mètres)

### Variables
- $A$ : Matrice 2x2
- $a, b, c, d$ : Éléments de la matrice
- $\det(A)$ : Déterminant

### Origine Scientifique
Gotthold Eisenstein

### Date
1843

### Publication
Eine neue Theorie der Determinanten

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'aire formée par deux vecteurs dans le plan. Test de colinéarité (déterminant = 0 si colinéaire).

### Implémentation Python
`formulas/vectors.py` - fonction `determinant_2x2()`

---

## Déterminant 3x3

### Nom
Déterminant d'une Matrice 3x3

### Formule
$$\det(A) = \det\begin{pmatrix} a & b & c \\ d & e & f \\ g & h & i \end{pmatrix} = a(ei - fh) - b(di - fg) + c(dh - eg)$$

### Définition
Le déterminant d'une matrice 3x3 est un scalaire qui donne le volume (signé) du parallélépipède formé par les vecteurs colonnes.

### Démonstration
Développement selon la première ligne (règle de Sarrus).

### Unités SI
Produit des unités des éléments (m³ si vecteurs en mètres)

### Variables
- $A$ : Matrice 3x3
- $a, b, c, d, e, f, g, h, i$ : Éléments de la matrice
- $\det(A)$ : Déterminant

### Origine Scientifique
Gotthold Eisenstein

### Date
1843

### Publication
Eine neue Theorie der Determinanten

### DOI
N/A

### Utilisation dans le Projet
Calcul du volume formé par trois vecteurs. Test de coplanarité (déterminant = 0 si coplanaire). Calcul du produit mixte.

### Implémentation Python
`formulas/vectors.py` - fonction `determinant_3x3()`

---

## Système Linéaire 2x2

### Nom
Système d'Équations Linéaires 2x2

### Formule (Règle de Cramer)
$$x = \frac{\det\begin{pmatrix} e & b \\ f & d \end{pmatrix}}{\det\begin{pmatrix} a & b \\ c & d \end{pmatrix}}$$

$$y = \frac{\det\begin{pmatrix} a & e \\ c & f \end{pmatrix}}{\det\begin{pmatrix} a & b \\ c & d \end{pmatrix}}$$

### Système
$$ax + by = e$$
$$cx + dy = f$$

### Définition
La règle de Cramer permet de résoudre un système linéaire en utilisant les déterminants.

### Démonstration
Propriété des déterminants et des systèmes linéaires.

### Unités SI
Dépend des unités des coefficients et des constantes

### Variables
- $a, b, c, d$ : Coefficients
- $e, f$ : Constantes
- $x, y$ : Inconnues

### Origine Scientifique
Gabriel Cramer

### Date
1750

### Publication
Introduction à l'analyse des lignes courbes algébriques

### DOI
N/A

### Utilisation dans le Projet
Résolution de systèmes pour trouver les points d'intersection. Calcul des paramètres de transformation affine entre repères.

### Implémentation Python
`formulas/vectors.py` - fonction `solve_linear_system_2x2()`

---

## Références

1. Grassmann - Die Lineale Ausdehnungslehre (1844)
2. Gibbs, Heaviside - Vector Analysis (1901)
3. Hamilton - Lectures on Quaternions (1853)
4. Euler - Introductio in analysin infinitorum (1748)
5. Euler - Nova methodus motum corporum rigidorum determinandi (1775)
6. Cramer - Introduction à l'analyse des lignes courbes algébriques (1750)
7. Eisenstein - Eine neue Theorie der Determinanten (1843)

---

## Implémentations Python Associées

- `formulas/vectors.py` : opérations vectorielles, produits, matrices de rotation
- `formulas/angles.py` : calculs d'angles dérivés de l'algèbre linéaire
- `formulas/distance.py` : calculs de déterminants pour aires et volumes
