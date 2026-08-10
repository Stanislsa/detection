# 04 - Kinematics

## Cinématique

---

## Vitesse Moyenne

### Nom
Vitesse Moyenne

### Formule
$$\bar{v} = \frac{\Delta d}{\Delta t} = \frac{d_2 - d_1}{t_2 - t_1}$$

### Formule Vectorielle
$$\bar{\mathbf{v}} = \frac{\Delta \mathbf{r}}{\Delta t} = \frac{\mathbf{r}_2 - \mathbf{r}_1}{t_2 - t_1}$$

### Définition
La vitesse moyenne est le rapport du déplacement total sur le temps écoulé.

### Démonstration
Définition fondamentale de la vitesse comme taux de changement de position.

### Unités SI
Mètre par seconde (m/s)

### Variables
- $\Delta d$ : Déplacement (m)
- $\Delta t$ : Intervalle de temps (s)
- $\Delta \mathbf{r}$ : Vecteur déplacement (m)
- $\bar{v}$ : Vitesse moyenne (m/s)
- $\bar{\mathbf{v}}$ : Vecteur vitesse moyenne (m/s)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Calcul de la vitesse moyenne du centre de gravité pendant une chute. Estimation de la vitesse de déplacement des articulations.

### Implémentation Python
`formulas/kinematics.py` - fonction `average_velocity()`

---

## Vitesse Instantanée

### Nom
Vitesse Instantanée

### Formule
$$v = \lim_{\Delta t \to 0} \frac{\Delta d}{\Delta t} = \frac{dd}{dt}$$

### Formule Vectorielle
$$\mathbf{v} = \lim_{\Delta t \to 0} \frac{\Delta \mathbf{r}}{\Delta t} = \frac{d\mathbf{r}}{dt}$$

### Définition
La vitesse instantanée est la dérivée de la position par rapport au temps.

### Démonstration
Définition du calcul différentiel et de la dérivée.

### Unités SI
Mètre par seconde (m/s)

### Variables
- $d$ : Position (m)
- $t$ : Temps (s)
- $\mathbf{r}$ : Vecteur position (m)
- $v$ : Vitesse instantanée (m/s)
- $\mathbf{v}$ : Vecteur vitesse instantanée (m/s)

### Origine Scientifique
Isaac Newton / Gottfried Wilhelm Leibniz

### Date
1687 (Newton) / 1684 (Leibniz)

### Publication
Principia Mathematica (Newton) / Nova Methodus (Leibniz)

### DOI
N/A

### Utilisation dans le Projet
Calcul de la vitesse instantanée du centre de gravité à chaque trame MediaPipe. Détection des pics de vitesse caractéristiques d'une chute.

### Implémentation Python
`formulas/kinematics.py` - fonction `instantaneous_velocity()`

---

## Accélération Moyenne

### Nom
Accélération Moyenne

### Formule
$$\bar{a} = \frac{\Delta v}{\Delta t} = \frac{v_2 - v_1}{t_2 - t_1}$$

### Formule Vectorielle
$$\bar{\mathbf{a}} = \frac{\Delta \mathbf{v}}{\Delta t} = \frac{\mathbf{v}_2 - \mathbf{v}_1}{t_2 - t_1}$$

### Définition
L'accélération moyenne est le rapport du changement de vitesse sur le temps écoulé.

### Démonstration
Définition de l'accélération comme taux de changement de vitesse.

### Unités SI
Mètre par seconde carrée (m/s²)

### Variables
- $\Delta v$ : Changement de vitesse (m/s)
- $\Delta t$ : Intervalle de temps (s)
- $\Delta \mathbf{v}$ : Changement de vecteur vitesse (m/s)
- $\bar{a}$ : Accélération moyenne (m/s²)
- $\bar{\mathbf{a}}$ : Vecteur accélération moyenne (m/s²)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'accélération moyenne pendant une chute. Détection des changements brusques de vitesse.

### Implémentation Python
`formulas/kinematics.py` - fonction `average_acceleration()`

---

## Accélération Instantanée

### Nom
Accélération Instantanée

### Formule
$$a = \lim_{\Delta t \to 0} \frac{\Delta v}{\Delta t} = \frac{dv}{dt} = \frac{d^2d}{dt^2}$$

### Formule Vectorielle
$$\mathbf{a} = \lim_{\Delta t \to 0} \frac{\Delta \mathbf{v}}{\Delta t} = \frac{d\mathbf{v}}{dt} = \frac{d^2\mathbf{r}}{dt^2}$$

### Définition
L'accélération instantanée est la dérivée de la vitesse par rapport au temps, ou la dérivée seconde de la position.

### Démonstration
Définition du calcul différentiel et de la dérivée seconde.

### Unités SI
Mètre par seconde carrée (m/s²)

### Variables
- $v$ : Vitesse (m/s)
- $t$ : Temps (s)
- $\mathbf{v}$ : Vecteur vitesse (m/s)
- $\mathbf{r}$ : Vecteur position (m)
- $a$ : Accélération instantanée (m/s²)
- $\mathbf{a}$ : Vecteur accélération instantanée (m/s²)

### Origine Scientifique
Isaac Newton / Gottfried Wilhelm Leibniz

### Date
1687 (Newton) / 1684 (Leibniz)

### Publication
Principia Mathematica (Newton) / Nova Methodus (Leibniz)

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'accélération instantanée du centre de gravité. Détection des pics d'accélération caractéristiques de l'impact au sol.

### Implémentation Python
`formulas/kinematics.py` - fonction `instantaneous_acceleration()`

---

## Vitesse Angulaire

### Nom
Vitesse Angulaire

### Formule
$$\omega = \frac{d\theta}{dt}$$

### Définition
La vitesse angulaire est le taux de changement de l'angle par rapport au temps.

### Démonstration
Définition de la vitesse angulaire comme dérivée de l'angle.

### Unités SI
Radian par seconde (rad/s)

### Variables
- $\theta$ : Angle (rad)
- $t$ : Temps (s)
- $\omega$ : Vitesse angulaire (rad/s)

### Origine Scientifique
Leonhard Euler

### Date
1765

### Publication
Theoria Motus Corporum Solidorum seu Rigidorum

### DOI
N/A

### Utilisation dans le Projet
Calcul de la vitesse de rotation du tronc. Détection des rotations rapides caractéristiques d'une perte d'équilibre.

### Implémentation Python
`formulas/kinematics.py` - fonction `angular_velocity()`

---

## Accélération Angulaire

### Nom
Accélération Angulaire

### Formule
$$\alpha = \frac{d\omega}{dt} = \frac{d^2\theta}{dt^2}$$

### Définition
L'accélération angulaire est le taux de changement de la vitesse angulaire par rapport au temps.

### Démonstration
Définition de l'accélération angulaire comme dérivée de la vitesse angulaire.

### Unités SI
Radian par seconde carrée (rad/s²)

### Variables
- $\omega$ : Vitesse angulaire (rad/s)
- $\theta$ : Angle (rad)
- $t$ : Temps (s)
- $\alpha$ : Accélération angulaire (rad/s²)

### Origine Scientifique
Leonhard Euler

### Date
1765

### Publication
Theoria Motus Corporum Solidorum seu Rigidorum

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'accélération de rotation du tronc. Détection des changements brusques d'orientation.

### Implémentation Python
`formulas/kinematics.py` - fonction `angular_acceleration()`

---

## Déplacement

### Nom
Déplacement

### Formule
$$\Delta \mathbf{r} = \mathbf{r}_2 - \mathbf{r}_1$$

### Formule Scalaire
$$\Delta d = \|\Delta \mathbf{r}\|$$

### Définition
Le déplacement est le changement de position d'un objet, représenté par un vecteur.

### Démonstration
Définition vectorielle du changement de position.

### Unités SI
Mètre (m)

### Variables
- $\mathbf{r}_1$ : Position initiale (m)
- $\mathbf{r}_2$ : Position finale (m)
- $\Delta \mathbf{r}$ : Vecteur déplacement (m)
- $\Delta d$ : Distance parcourue (m)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Calcul du déplacement du centre de gravité entre deux trames. Estimation de la distance de chute.

### Implémentation Python
`formulas/kinematics.py` - fonction `displacement()`

---

## Vitesse Verticale

### Nom
Vitesse Verticale

### Formule
$$v_y = \frac{dy}{dt}$$

### Définition
La vitesse verticale est la composante verticale de la vitesse, correspondant au mouvement dans la direction de la gravité.

### Démonstration
Projection du vecteur vitesse sur l'axe vertical.

### Unités SI
Mètre par seconde (m/s)

### Variables
- $y$ : Coordonnée verticale (m)
- $t$ : Temps (s)
- $v_y$ : Vitesse verticale (m/s)

### Origine Scientifique
Galileo Galilei

### Date
1638

### Publication
Discorsi e dimostrazioni matematiche intorno a due nuove scienze

### DOI
N/A

### Utilisation dans le Projet
Calcul de la vitesse de chute du centre de gravité. Détection des chutes par la vitesse verticale négative rapide.

### Implémentation Python
`formulas/kinematics.py` - fonction `vertical_velocity()`

---

## Accélération Verticale

### Nom
Accélération Verticale

### Formule
$$a_y = \frac{dv_y}{dt} = \frac{d^2y}{dt^2}$$

### Définition
L'accélération verticale est la composante verticale de l'accélération.

### Démonstration
Projection du vecteur accélération sur l'axe vertical.

### Unités SI
Mètre par seconde carrée (m/s²)

### Variables
- $v_y$ : Vitesse verticale (m/s)
- $y$ : Coordonnée verticale (m)
- $t$ : Temps (s)
- $a_y$ : Accélération verticale (m/s²)

### Origine Scientifique
Galileo Galilei

### Date
1638

### Publication
Discorsi e dimostrazioni matematiche intorno a due nuove scienze

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'accélération de chute. Détection de l'impact au sol (pic d'accélération négative).

### Implémentation Python
`formulas/kinematics.py` - fonction `vertical_acceleration()`

---

## Vitesse Horizontale

### Nom
Vitesse Horizontale

### Formule
$$v_x = \frac{dx}{dt}$$

### Formule 2D
$$\mathbf{v}_h = \sqrt{v_x^2 + v_z^2}$$

### Définition
La vitesse horizontale est la composante horizontale de la vitesse.

### Démonstration
Projection du vecteur vitesse sur le plan horizontal.

### Unités SI
Mètre par seconde (m/s)

### Variables
- $x$ : Coordonnée horizontale (m)
- $z$ : Coordonnée de profondeur (m)
- $t$ : Temps (s)
- $v_x$ : Vitesse horizontale selon X (m/s)
- $\mathbf{v}_h$ : Vitesse horizontale totale (m/s)

### Origine Scientifique
Galileo Galilei

### Date
1638

### Publication
Discorsi e dimostrazioni matematiche intorno a due nuove scienze

### DOI
N/A

### Utilisation dans le Projet
Calcul de la vitesse de déplacement latéral. Distinction entre chute verticale et mouvement horizontal normal.

### Implémentation Python
`formulas/kinematics.py` - fonction `horizontal_velocity()`

---

## Vitesse Résultante

### Nom
Vitesse Résultante (Magnitude)

### Formule
$$v = \sqrt{v_x^2 + v_y^2 + v_z^2} = \|\mathbf{v}\|$$

### Définition
La vitesse résultante est la magnitude du vecteur vitesse.

### Démonstration
Application du théorème de Pythagore en 3 dimensions.

### Unités SI
Mètre par seconde (m/s)

### Variables
- $v_x, v_y, v_z$ : Composantes de la vitesse (m/s)
- $\mathbf{v}$ : Vecteur vitesse (m/s)
- $v$ : Vitesse résultante (m/s)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Calcul de la vitesse totale du mouvement. Détection des mouvements rapides dans toutes les directions.

### Implémentation Python
`formulas/kinematics.py` - fonction `resultant_velocity()`

---

## Accélération Résultante

### Nom
Accélération Résultante (Magnitude)

### Formule
$$a = \sqrt{a_x^2 + a_y^2 + a_z^2} = \|\mathbf{a}\|$$

### Définition
L'accélération résultante est la magnitude du vecteur accélération.

### Démonstration
Application du théorème de Pythagore en 3 dimensions.

### Unités SI
Mètre par seconde carrée (m/s²)

### Variables
- $a_x, a_y, a_z$ : Composantes de l'accélération (m/s²)
- $\mathbf{a}$ : Vecteur accélération (m/s²)
- $a$ : Accélération résultante (m/s²)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'accélération totale du mouvement. Détection des impacts violents.

### Implémentation Python
`formulas/kinematics.py` - fonction `resultant_acceleration()`

---

## Chute Libre

### Nom
Chute Libre (Vitesse)

### Formule
$$v(t) = v_0 + gt$$

### Formule (Position)
$$y(t) = y_0 + v_0 t + \frac{1}{2}gt^2$$

### Définition
La chute libre est le mouvement d'un objet sous l'effet de la gravité seule, sans résistance de l'air.

### Démonstration
Intégration de l'accélération constante $g$.

### Unités SI
Vitesse : m/s, Position : m

### Variables
- $v_0$ : Vitesse initiale (m/s)
- $g$ : Accélération gravitationnelle (9.81 m/s²)
- $t$ : Temps (s)
- $y_0$ : Position initiale (m)
- $y(t)$ : Position au temps t (m)

### Origine Scientifique
Galileo Galilei

### Date
1638

### Publication
Discorsi e dimostrazioni matematiche intorno a due nuove scienze

### DOI
N/A

### Utilisation dans le Projet
Modélisation théorique de la chute d'une personne. Comparaison avec les données MediaPipe réelles.

### Implémentation Python
`formulas/kinematics.py` - fonction `free_fall_velocity()`, `free_fall_position()`

---

## Temps de Chute

### Nom
Temps de Chute

### Formule
$$t = \sqrt{\frac{2h}{g}}$$

### Définition
Le temps de chute est la durée nécessaire pour un objet en chute libre de parcourir une hauteur h.

### Démonstration
Dérivé de l'équation de la chute libre avec $v_0 = 0$ et $y_0 = h$.

### Unités SI
Seconde (s)

### Variables
- $h$ : Hauteur de chute (m)
- $g$ : Accélération gravitationnelle (9.81 m/s²)
- $t$ : Temps de chute (s)

### Origine Scientifique
Galileo Galilei

### Date
1638

### Publication
Discorsi e dimostrazioni matematiche intorno a due nuove scienze

### DOI
N/A

### Utilisation dans le Projet
Estimation du temps de chute théorique à partir de la hauteur du centre de gravité. Validation des données MediaPipe.

### Implémentation Python
`formulas/kinematics.py` - fonction `fall_time()`

---

## Vitesse d'Impact

### Nom
Vitesse d'Impact

### Formule
$$v_{impact} = \sqrt{2gh}$$

### Définition
La vitesse d'impact est la vitesse atteinte par un objet en chute libre après avoir parcouru une hauteur h.

### Démonstration
Dérivé de l'équation de la chute libre avec $v_0 = 0$.

### Unités SI
Mètre par seconde (m/s)

### Variables
- $h$ : Hauteur de chute (m)
- $g$ : Accélération gravitationnelle (9.81 m/s²)
- $v_{impact}$ : Vitesse d'impact (m/s)

### Origine Scientifique
Galileo Galilei

### Date
1638

### Publication
Discorsi e dimostrazioni matematiche intorno a due nuove scienze

### DOI
N/A

### Utilisation dans le Projet
Estimation de la vitesse d'impact au sol. Calcul de l'énergie cinétique d'impact.

### Implémentation Python
`formulas/kinematics.py` - fonction `impact_velocity()`

---

## Mouvement Rectiligne Uniforme (MRU)

### Nom
Mouvement Rectiligne Uniforme

### Formule
$$x(t) = x_0 + vt$$

### Définition
Le MRU est un mouvement à vitesse constante sur une ligne droite.

### Démonstration
Intégration de la vitesse constante.

### Unités SI
Position : m, Vitesse : m/s

### Variables
- $x_0$ : Position initiale (m)
- $v$ : Vitesse constante (m/s)
- $t$ : Temps (s)
- $x(t)$ : Position au temps t (m)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Modélisation des mouvements normaux (marche, déplacement). Détection des écarts par rapport au MRU (chutes).

### Implémentation Python
`formulas/kinematics.py` - fonction `uniform_linear_motion()`

---

## Mouvement Rectiligne Uniformément Accéléré (MRUA)

### Nom
Mouvement Rectiligne Uniformément Accéléré

### Formule (Position)
$$x(t) = x_0 + v_0 t + \frac{1}{2}at^2$$

### Formule (Vitesse)
$$v(t) = v_0 + at$$

### Définition
Le MRUA est un mouvement à accélération constante sur une ligne droite.

### Démonstration
Intégration de l'accélération constante.

### Unités SI
Position : m, Vitesse : m/s, Accélération : m/s²

### Variables
- $x_0$ : Position initiale (m)
- $v_0$ : Vitesse initiale (m/s)
- $a$ : Accélération constante (m/s²)
- $t$ : Temps (s)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Modélisation de la phase d'accélération pendant une chute. Ajustement des courbes de vitesse.

### Implémentation Python
`formulas/kinematics.py` - fonction `uniformly_accelerated_motion()`

---

## Vitesse Relative

### Nom
Vitesse Relative

### Formule
$$\mathbf{v}_{rel} = \mathbf{v}_A - \mathbf{v}_B$$

### Définition
La vitesse relative de l'objet A par rapport à l'objet B est la différence de leurs vecteurs vitesse.

### Démonstration
Principe de relativité galiléenne.

### Unités SI
Mètre par seconde (m/s)

### Variables
- $\mathbf{v}_A$ : Vitesse de l'objet A (m/s)
- $\mathbf{v}_B$ : Vitesse de l'objet B (m/s)
- $\mathbf{v}_{rel}$ : Vitesse relative (m/s)

### Origine Scientifique
Galileo Galilei

### Date
1632

### Publication
Dialogue sur les deux grands systèmes du monde

### DOI
N/A

### Utilisation dans le Projet
Calcul de la vitesse relative entre deux articulations (ex: épaule par rapport au bassin). Détection des mouvements anormaux.

### Implémentation Python
`formulas/kinematics.py` - fonction `relative_velocity()`

---

## Trajectoire

### Nom
Trajectoire Paramétrique

### Formule
$$\mathbf{r}(t) = (x(t), y(t), z(t))$$

### Définition
La trajectoire est l'ensemble des positions occupées par un objet au cours du temps.

### Démonstration
Définition paramétrique de la courbe.

### Unités SI
Mètre (m)

### Variables
- $x(t), y(t), z(t)$ : Coordonnées en fonction du temps
- $\mathbf{r}(t)$ : Vecteur position

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Reconstruction de la trajectoire du centre de gravité pendant une chute. Analyse du pattern de mouvement.

### Implémentation Python
`formulas/kinematics.py` - fonction `trajectory()`

---

## Courbure

### Nom
Courbure d'une Trajectoire

### Formule
$$\kappa = \frac{\|\mathbf{v} \times \mathbf{a}\|}{\|\mathbf{v}\|^3}$$

### Rayon de Courbure
$$R = \frac{1}{\kappa}$$

### Définition
La courbure mesure à quel point une courbe s'écarte d'une ligne droite.

### Démonstration
Dérivé de la définition géométrique de la courbure.

### Unités SI
Courbure : m⁻¹, Rayon : m

### Variables
- $\mathbf{v}$ : Vecteur vitesse (m/s)
- $\mathbf{a}$ : Vecteur accélération (m/s²)
- $\kappa$ : Courbure (m⁻¹)
- $R$ : Rayon de courbure (m)

### Origine Scientifique
Augustin-Louis Cauchy

### Date
1826

### Publication
Leçons sur les applications du calcul infinitésimal

### DOI
N/A

### Utilisation dans le Projet
Analyse de la courbure de la trajectoire du centre de gravité. Détection des changements brusques de direction.

### Implémentation Python
`formulas/kinematics.py` - fonction `curvature()`

---

## Références

1. Galileo Galilei - Discorsi e dimostrazioni matematiche (1638)
2. Isaac Newton - Philosophiæ Naturalis Principia Mathematica (1687)
3. Gottfried Leibniz - Nova Methodus (1684)
4. Leonhard Euler - Theoria Motus Corporum Solidorum (1765)
5. Augustin Cauchy - Leçons sur les applications du calcul (1826)

---

## Implémentations Python Associées

- `formulas/kinematics.py` : vitesses, accélérations, déplacements, trajectoires
- `formulas/vectors.py` : opérations vectorielles pour la cinématique
- `formulas/angles.py` : calculs de vitesses et accélérations angulaires
