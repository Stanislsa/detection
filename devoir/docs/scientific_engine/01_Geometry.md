# 01 - Geometry

## Géométrie Euclidienne

---

## Distance Euclidienne

### Nom
Distance Euclidienne

### Auteur
Euclide

### Date
≈ 300 avant J.-C.

### Publication
Éléments (Elements), Livre I

### Principe
Calcul de la distance entre deux points dans un espace euclidien.

### Formule
**2D:**
$$d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$

**3D:**
$$d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2 + (z_2 - z_1)^2}$$

### Variables
- $x_1, y_1, z_1$ : Coordonnées du premier point
- $x_2, y_2, z_2$ : Coordonnées du deuxième point
- $d$ : Distance entre les deux points

### Unité
Mètre (m)

### Hypothèses
Espace euclidien.

### Utilisation dans le projet
Distance entre les articulations du squelette MediaPipe.

### Implémentation
`ai_engine/geometry/distance.py` - fonction `euclidean_distance_2d()`, `euclidean_distance_3d()`

### Complexité
O(1)

---

## Produit Scalaire

### Nom
Produit Scalaire (Dot Product)

### Auteur
Josiah Willard Gibbs / Oliver Heaviside

### Date
1880s (formalisation moderne)

### Publication
Vector Analysis (1901)

### Principe
Le produit scalaire de deux vecteurs est égal au produit de leurs normes par le cosinus de l'angle entre eux.

### Formule
**Algébrique:**
$$\mathbf{a} \cdot \mathbf{b} = a_x b_x + a_y b_y + a_z b_z$$

**Géométrique:**
$$\mathbf{a} \cdot \mathbf{b} = \|\mathbf{a}\| \|\mathbf{b}\| \cos(\theta)$$

### Variables
- $\mathbf{a} = (a_x, a_y, a_z)$ : Premier vecteur
- $\mathbf{b} = (b_x, b_y, b_z)$ : Deuxième vecteur
- $\theta$ : Angle entre les vecteurs
- $\|\mathbf{a}\|$ : Norme du vecteur $\mathbf{a}$

### Unité
Dépend des unités des vecteurs (m² si vecteurs en mètres)

### Hypothèses
Espace euclidien.

### Utilisation dans le projet
Calcul de l'angle entre deux segments du corps (ex: angle entre le bras et l'avant-bras). Utilisé pour détecter les anomalies posturales.

### Implémentation
`ai_engine/geometry/vectors.py` - fonction `dot_product()`

### Complexité
O(1)

---

## Produit Vectoriel

### Nom
Produit Vectoriel (Cross Product)

### Auteur
Josiah Willard Gibbs / Oliver Heaviside

### Date
1880s

### Publication
Vector Analysis (1901)

### Principe
Le produit vectoriel de deux vecteurs est un vecteur perpendiculaire au plan formé par les deux vecteurs initiaux, dont la norme est égale à l'aire du parallélogramme formé.

### Formule
**Déterminant:**
$$\mathbf{a} \times \mathbf{b} = \begin{vmatrix} \mathbf{i} & \mathbf{j} & \mathbf{k} \\ a_x & a_y & a_z \\ b_x & b_y & b_z \end{vmatrix}$$

**Composantes:**
$$\mathbf{a} \times \mathbf{b} = (a_y b_z - a_z b_y, a_z b_x - a_x b_z, a_x b_y - a_y b_x)$$

### Variables
- $\mathbf{a} = (a_x, a_y, a_z)$ : Premier vecteur
- $\mathbf{b} = (b_x, b_y, b_z)$ : Deuxième vecteur
- $\mathbf{i}, \mathbf{j}, \mathbf{k}$ : Vecteurs unitaires de la base canonique

### Unité
Dépend des unités des vecteurs (m² si vecteurs en mètres)

### Hypothèses
Espace euclidien 3D.

### Utilisation dans le projet
Calcul de vecteurs normaux pour déterminer l'orientation du plan du corps (ex: plan formé par les épaules). Utilisé pour détecter les rotations du tronc.

### Implémentation
`ai_engine/geometry/vectors.py` - fonction `cross_product()`

### Complexité
O(1)

---

## Norme Vectorielle

### Nom
Norme Euclidienne (Magnitude)

### Auteur
Euclide

### Date
≈ 300 avant J.-C.

### Publication
Éléments (Elements)

### Principe
La norme d'un vecteur est sa longueur dans l'espace euclidien.

### Formule
$$\|\mathbf{v}\| = \sqrt{v_x^2 + v_y^2 + v_z^2}$$

### Variables
- $\mathbf{v} = (v_x, v_y, v_z)$ : Vecteur
- $\|\mathbf{v}\|$ : Norme du vecteur

### Unité
Même unité que les composantes du vecteur (m si vecteur en mètres)

### Hypothèses
Espace euclidien.

### Utilisation dans le projet
Calcul de la longueur des segments du corps (ex: longueur du bras, de la jambe). Utilisé pour normaliser les vecteurs.

### Implémentation
`ai_engine/geometry/vectors.py` - fonction `norm()`

### Complexité
O(1)

---

## Projection

### Nom
Projection Orthogonale

### Auteur
Hermann Grassmann

### Date
1844

### Publication
Die Lineale Ausdehnungslehre

### Principe
La projection orthogonale d'un vecteur $\mathbf{a}$ sur un vecteur $\mathbf{b}$ est le composant de $\mathbf{a}$ parallèle à $\mathbf{b}$.

### Formule
$$\text{proj}_{\mathbf{b}} \mathbf{a} = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{b}\|^2} \mathbf{b}$$

### Variables
- $\mathbf{a}$ : Vecteur à projeter
- $\mathbf{b}$ : Vecteur sur lequel projeter
- $\text{proj}_{\mathbf{b}} \mathbf{a}$ : Projection de $\mathbf{a}$ sur $\mathbf{b}$

### Unité
Même unité que les vecteurs (m si vecteurs en mètres)

### Hypothèses
Espace euclidien.

### Utilisation dans le projet
Projection du vecteur gravité sur le vecteur tronc pour calculer l'angle d'inclinaison. Séparation des composantes verticales et horizontales du mouvement.

### Implémentation
`ai_engine/geometry/vectors.py` - fonction `projection()`

### Complexité
O(1)

---

## Centre Géométrique (Centroid)

### Nom
Centre Géométrique

### Formule
$$\mathbf{C} = \frac{1}{n} \sum_{i=1}^{n} \mathbf{P}_i$$

### Composantes
$$C_x = \frac{1}{n} \sum_{i=1}^{n} x_i$$
$$C_y = \frac{1}{n} \sum_{i=1}^{n} y_i$$
$$C_z = \frac{1}{n} \sum_{i=1}^{n} z_i$$

### Définition
Le centre géométrique d'un ensemble de points est la moyenne arithmétique de leurs coordonnées.

### Démonstration
Propriété linéaire de la moyenne arithmétique.

### Unités SI
Même unité que les points (m si points en mètres)

### Variables
- $\mathbf{P}_i = (x_i, y_i, z_i)$ : i-ème point
- $n$ : Nombre de points
- $\mathbf{C} = (C_x, C_y, C_z)$ : Centre géométrique

### Origine Scientifique
Archimède

### Date
≈ 250 avant J.-C.

### Publication
Sur les équilibres des plans (On the Equilibrium of Planes)

### DOI
N/A

### Utilisation dans le Projet
Calcul du centre approximatif du corps humain à partir des 33 points MediaPipe. Estimation du centre de masse pour la détection de chute.

### Implémentation Python
`formulas/distance.py` - fonction `centroid()`

---

## Point Milieu

### Nom
Point Milieu (Midpoint)

### Formule
$$M = \left( \frac{x_1 + x_2}{2}, \frac{y_1 + y_2}{2},\frac{z_1 + z_2}{2} \right)$$

### Définition
Le point milieu est le point équidistant de deux extrémités d'un segment.

### Démonstration
Propriété de symétrie et moyenne arithmétique.

### Unités SI
Même unité que les points (m si points en mètres)

### Variables
- $(x_1, y_1, z_1)$ : Coordonnées du premier point
- $(x_2, y_2, z_2)$ : Coordonnées du deuxième point
- $M$ : Point milieu

### Origine Scientifique
Euclide

### Date
≈ 300 avant J.-C.

### Publication
Éléments (Elements)

### DOI
N/A

### Utilisation dans le Projet
Calcul du centre des épaules, du centre des hanches. Utilisé pour définir l'axe du tronc et du bassin.

### Implémentation Python
`formulas/distance.py` - fonction `midpoint()`

---

## Distance Point-Plan

### Nom
Distance d'un Point à un Plan

### Formule
$$d = \frac{|ax_0 + by_0 + cz_0 + d|}{\sqrt{a^2 + b^2 + c^2}}$$

### Définition
La distance d'un point à un plan est la longueur du segment perpendiculaire au plan reliant le point au plan.

### Démonstration
Projection orthogonale du point sur le plan et calcul de la norme.

### Unités SI
Mètre (m)

### Variables
- $(x_0, y_0, z_0)$ : Coordonnées du point
- $ax + by + cz + d = 0$ : Équation du plan
- $d$ : Distance du point au plan

### Origine Scientifique
Joseph-Louis Lagrange

### Date
1773

### Publication
Sur la construction des équations

### DOI
N/A

### Utilisation dans le Projet
Calcul de la distance du centre de gravité au plan horizontal (sol). Indicateur de la hauteur du corps par rapport au sol.

### Implémentation Python
`formulas/distance.py` - fonction `point_to_plane_distance()`

---

## Distance Point-Ligne

### Nom
Distance d'un Point à une Ligne

### Formule 2D
$$d = \frac{|(y_2 - y_1)x_0 - (x_2 - x_1)y_0 + x_2 y_1 - y_2 x_1|}{\sqrt{(y_2 - y_1)^2 + (x_2 - x_1)^2}}$$

### Formule 3D
$$d = \frac{\|(\mathbf{P}_0 - \mathbf{P}_1) \times (\mathbf{P}_0 - \mathbf{P}_2)\|}{\|\mathbf{P}_2 - \mathbf{P}_1\|}$$

### Définition
La distance d'un point à une ligne est la longueur du segment perpendiculaire à la ligne reliant le point à la ligne.

### Démonstration
Utilisation du produit vectoriel pour trouver la distance perpendiculaire.

### Unités SI
Mètre (m)

### Variables
- $\mathbf{P}_0 = (x_0, y_0, z_0)$ : Point
- $\mathbf{P}_1 = (x_1, y_1, z_1)$ : Premier point de la ligne
- $\mathbf{P}_2 = (x_2, y_2, z_2)$ : Deuxième point de la ligne
- $d$ : Distance

### Origine Scientifique
René Descartes

### Date
1637

### Publication
La Géométrie

### DOI
N/A

### Utilisation dans le Projet
Calcul de la déviation d'une articulation par rapport à l'axe idéal du segment. Détection d'anomalies dans la posture.

### Implémentation Python
`formulas/distance.py` - fonction `point_to_line_distance()`

---

## Aire du Triangle

### Nom
Aire du Triangle (Formule de Héron)

### Formule
$$A = \sqrt{s(s-a)(s-b)(s-c)}$$

### Où
$$s = \frac{a + b + c}{2}$$

### Formule Vectorielle
$$A = \frac{1}{2} \|\mathbf{a} \times \mathbf{b}\|$$

### Définition
L'aire d'un triangle peut être calculée à partir de la longueur de ses côtés (formule de Héron) ou du produit vectoriel de deux côtés.

### Démonstration
Formule de Héron : dérivée du théorème de Pythagore. Formule vectorielle : propriété du produit vectoriel.

### Unités SI
Mètre carré (m²)

### Variables
- $a, b, c$ : Longueurs des côtés
- $s$ : Semi-périmètre
- $A$ : Aire du triangle
- $\mathbf{a}, \mathbf{b}$ : Vecteurs représentant deux côtés

### Origine Scientifique
Héron d'Alexandrie

### Date
≈ 60 après J.-C.

### Publication
Métrica

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'aire formée par trois articulations (ex: triangle épaule-coude-poignet). Indicateur de l'ouverture ou de la fermeture des articulations.

### Implémentation Python
`formulas/distance.py` - fonction `triangle_area()`

---

## Volume du Tétraèdre

### Nom
Volume du Tétraèdre

### Formule
$$V = \frac{1}{6} |(\mathbf{a} \times \mathbf{b}) \cdot \mathbf{c}|$$

### Définition
Le volume d'un tétraèdre formé par six arêtes peut être calculé à partir du produit mixte de trois vecteurs.

### Démonstration
Propriété du produit mixte (produit scalaire du produit vectoriel).

### Unités SI
Mètre cube (m³)

### Variables
- $\mathbf{a}, \mathbf{b}, \mathbf{c}$ : Vecteurs arêtes du tétraèdre
- $V$ : Volume

### Origine Scientifique
Archimède

### Date
≈ 250 avant J.-C.

### Publication
De la sphère et du cylindre

### DOI
N/A

### Utilisation dans le Projet
Estimation du volume occupé par le corps humain dans l'espace 3D. Calcul de l'encombrement pour la détection d'obstacles.

### Implémentation Python
`formulas/distance.py` - fonction `tetrahedron_volume()`

---

## Références

1. Euclid - Elements (~300 av. J.-C.)
2. Archimedes - On the Equilibrium of Planes (~250 av. J.-C.)
3. Descartes - La Géométrie (1637)
4. Lagrange - Sur la construction des équations (1773)
5. Grassmann - Die Lineale Ausdehnungslehre (1844)
6. Gibbs, Heaviside - Vector Analysis (1901)
7. Heron - Metrica (~60 ap. J.-C.)

---

## Implémentations Python Associées

- `formulas/distance.py` : distances, centroides, aires, volumes
- `formulas/vectors.py` : opérations vectorielles, produits, projections
- `formulas/angles.py` : calculs d'angles dérivés de la géométrie
