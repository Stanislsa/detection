# 05 - Dynamics

## Dynamique

---

## Deuxième Loi de Newton

### Nom
Deuxième Loi de Newton (Principe Fondamental de la Dynamique)

### Formule
$$\mathbf{F} = m\mathbf{a}$$

### Formule Scalaire
$$F = ma$$

### Définition
La force appliquée à un objet est égale à la masse de l'objet multipliée par son accélération.

### Démonstration
Loi fondamentale déduite des observations expérimentales et de la première loi de Newton.

### Unités SI
Force : Newton (N), Masse : kilogramme (kg), Accélération : m/s²

### Variables
- $\mathbf{F}$ : Force (N)
- $m$ : Masse (kg)
- $\mathbf{a}$ : Accélération (m/s²)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Calcul de la force d'impact au sol lors d'une chute. Estimation de la force subie par le corps.

### Implémentation Python
`formulas/dynamics.py` - fonction `newton_second_law()`

---

## Poids

### Nom
Poids (Force de Gravité)

### Formule
$$\mathbf{P} = m\mathbf{g}$$

### Formule Scalaire
$$P = mg$$

### Définition
Le poids est la force exercée par la gravité sur un objet de masse m.

### Démonstration
Application de la deuxième loi de Newton avec l'accélération gravitationnelle g.

### Unités SI
Newton (N)

### Variables
- $m$ : Masse (kg)
- $g$ : Accélération gravitationnelle (9.81 m/s²)
- $\mathbf{P}$ : Poids (N)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Calcul du poids du patient pour l'estimation des forces d'impact. Normalisation des forces par rapport au poids.

### Implémentation Python
`formulas/dynamics.py` - fonction `weight()`

---

## Énergie Cinétique

### Nom
Énergie Cinétique

### Formule
$$E_c = \frac{1}{2}mv^2$$

### Formule Vectorielle
$$E_c = \frac{1}{2}m\|\mathbf{v}\|^2$$

### Définition
L'énergie cinétique est l'énergie possédée par un corps du fait de son mouvement.

### Démonstration
Dérivée du travail d'une force constante : $W = Fd = mad = m \cdot \frac{v^2}{2}$

### Unités SI
Joule (J)

### Variables
- $m$ : Masse (kg)
- $v$ : Vitesse (m/s)
- $\mathbf{v}$ : Vecteur vitesse (m/s)
- $E_c$ : Énergie cinétique (J)

### Origine Scientifique
Gottfried Wilhelm Leibniz / Isaac Newton

### Date
1686 (Leibniz) / 1687 (Newton)

### Publication
Brevis demonstratio (Leibniz) / Principia Mathematica (Newton)

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'énergie cinétique du centre de gravité pendant une chute. Indicateur de la violence de l'impact.

### Implémentation Python
`formulas/dynamics.py` - fonction `kinetic_energy()`

---

## Énergie Potentielle Gravitationnelle

### Nom
Énergie Potentielle Gravitationnelle

### Formule
$$E_p = mgh$$

### Définition
L'énergie potentielle gravitationnelle est l'énergie possédée par un corps du fait de sa position dans un champ gravitationnel.

### Démonstration
Intégrale du travail contre la force gravitationnelle : $W = \int_0^h mg \, dy = mgh$

### Unités SI
Joule (J)

### Variables
- $m$ : Masse (kg)
- $g$ : Accélération gravitationnelle (9.81 m/s²)
- $h$ : Hauteur (m)
- $E_p$ : Énergie potentielle (J)

### Origine Scientifique
William Rankine

### Date
1853

### Publication
On the Mechanical Action of Heat

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'énergie potentielle perdue pendant une chute. Estimation de l'énergie disponible pour l'impact.

### Implémentation Python
`formulas/dynamics.py` - fonction `potential_energy()`

---

## Énergie Mécanique Totale

### Nom
Énergie Mécanique

### Formule
$$E_m = E_c + E_p$$

### Définition
L'énergie mécanique est la somme de l'énergie cinétique et de l'énergie potentielle.

### Démonstration
Principe de conservation de l'énergie mécanique (système conservatif).

### Unités SI
Joule (J)

### Variables
- $E_c$ : Énergie cinétique (J)
- $E_p$ : Énergie potentielle (J)
- $E_m$ : Énergie mécanique (J)

### Origine Scientifique
William Rankine

### Date
1853

### Publication
On the Mechanical Action of Heat

### DOI
N/A

### Utilisation dans le Projet
Analyse du bilan énergétique pendant une chute. Conversion de l'énergie potentielle en énergie cinétique.

### Implémentation Python
`formulas/dynamics.py` - fonction `mechanical_energy()`

---

## Travail d'une Force

### Nom
Travail d'une Force

### Formule
$$W = \mathbf{F} \cdot \mathbf{d} = Fd\cos(\theta)$$

### Définition
Le travail d'une force est le produit de la force par le déplacement dans la direction de la force.

### Démonstration
Définition du travail comme transfert d'énergie par une force.

### Unités SI
Joule (J)

### Variables
- $\mathbf{F}$ : Force (N)
- $\mathbf{d}$ : Déplacement (m)
- $\theta$ : Angle entre force et déplacement
- $W$ : Travail (J)

### Origine Scientifique
Gaspard-Gustave Coriolis

### Date
1829

### Publication
Du Calcul de l'Effet des Machines

### DOI
N/A

### Utilisation dans le Projet
Calcul du travail effectué par la gravité pendant la chute. Analyse des forces de freinage au sol.

### Implémentation Python
`formulas/dynamics.py` - fonction `work()`

---

## Impulsion

### Nom
Impulsion (Quantité de Mouvement)

### Formule
$$\mathbf{p} = m\mathbf{v}$$

### Variation d'Impulsion
$$\Delta \mathbf{p} = \mathbf{F}\Delta t$$

### Définition
L'impulsion (ou quantité de mouvement) est le produit de la masse par la vitesse.

### Démonstration
Dérivé de la deuxième loi de Newton : $\mathbf{F} = \frac{d\mathbf{p}}{dt}$

### Unités SI
kg·m/s

### Variables
- $m$ : Masse (kg)
- $\mathbf{v}$ : Vitesse (m/s)
- $\mathbf{F}$ : Force (N)
- $\Delta t$ : Intervalle de temps (s)
- $\mathbf{p}$ : Impulsion (kg·m/s)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'impulsion lors de l'impact au sol. Estimation de la force d'impact à partir du changement d'impulsion.

### Implémentation Python
`formulas/dynamics.py` - fonction `momentum()`

---

## Moment Cinétique

### Nom
Moment Cinétique (Moment Angulaire)

### Formule
$$\mathbf{L} = \mathbf{r} \times \mathbf{p} = \mathbf{r} \times m\mathbf{v}$$

### Formule Scalaire
$$L = I\omega$$

### Définition
Le moment cinétique est le produit vectoriel de la position par l'impulsion.

### Démonstration
Dérivé de la définition du moment de force et de l'impulsion.

### Unités SI
kg·m²/s

### Variables
- $\mathbf{r}$ : Vecteur position (m)
- $\mathbf{p}$ : Impulsion (kg·m/s)
- $m$ : Masse (kg)
- $\mathbf{v}$ : Vitesse (m/s)
- $I$ : Moment d'inertie (kg·m²)
- $\omega$ : Vitesse angulaire (rad/s)
- $\mathbf{L}$ : Moment cinétique (kg·m²/s)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Analyse des rotations du corps pendant une chute. Détection des mouvements de rotation anormaux.

### Implémentation Python
`formulas/dynamics.py` - fonction `angular_momentum()`

---

## Moment d'Inertie

### Nom
Moment d'Inertie

### Formule (Point Matériel)
$$I = mr^2$$

### Formule (Corps Solide)
$$I = \int r^2 dm$$

### Définition
Le moment d'inertie mesure la résistance d'un corps à la rotation autour d'un axe.

### Démonstration
Intégrale de la masse multipliée par le carré de la distance à l'axe de rotation.

### Unités SI
kg·m²

### Variables
- $m$ : Masse (kg)
- $r$ : Distance à l'axe de rotation (m)
- $I$ : Moment d'inertie (kg·m²)

### Origine Scientifique
Leonhard Euler

### Date
1765

### Publication
Theoria Motus Corporum Solidorum seu Rigidorum

### DOI
N/A

### Utilisation dans le Projet
Estimation du moment d'inertie du corps humain. Analyse de la résistance à la rotation.

### Implémentation Python
`formulas/dynamics.py` - fonction `moment_of_inertia()`

---

## Force de Frottement

### Nom
Force de Frottement Cinétique

### Formule
$$F_f = \mu_k N$$

### Définition
La force de frottement cinétique est proportionnelle à la force normale et au coefficient de frottement.

### Démonstration
Loi empirique d'Amontons-Coulomb.

### Unités SI
Newton (N)

### Variables
- $\mu_k$ : Coefficient de frottement cinétique (sans dimension)
- $N$ : Force normale (N)
- $F_f$ : Force de frottement (N)

### Origine Scientifique
Guillaume Amontons / Charles-Augustin Coulomb

### Date
1699 (Amontons) / 1785 (Coulomb)

### Publication
De la résistance causée dans les machines (Amontons) / Théorie des machines simples (Coulomb)

### DOI
N/A

### Utilisation dans le Projet
Modélisation du freinage au sol lors de l'impact. Estimation de la décélération après impact.

### Implémentation Python
`formulas/dynamics.py` - fonction `friction_force()`

---

## Force d'Impact

### Nom
Force d'Impact

### Formule (Impulsion-Momentum)
$$F_{impact} = \frac{\Delta p}{\Delta t} = \frac{m\Delta v}{\Delta t}$$

### Définition
La force d'impact est la force moyenne exercée pendant la durée de l'impact.

### Démonstration
Dérivé du théorème de l'impulsion : $\Delta p = F\Delta t$

### Unités SI
Newton (N)

### Variables
- $\Delta p$ : Variation d'impulsion (kg·m/s)
- $m$ : Masse (kg)
- $\Delta v$ : Variation de vitesse (m/s)
- $\Delta t$ : Durée de l'impact (s)
- $F_{impact}$ : Force d'impact (N)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Calcul de la force d'impact au sol. Estimation de la violence de la chute.

### Implémentation Python
`formulas/dynamics.py` - fonction `impact_force()`

---

## Coefficient de Restitution

### Nom
Coefficient de Restitution

### Formule
$$e = \frac{v_{après}}{v_{avant}} = \sqrt{\frac{h_{rebond}}{h_{chute}}}$$

### Définition
Le coefficient de restitution mesure l'élasticité d'une collision, rapport des vitesses après et avant l'impact.

### Démonstration
Conservation de l'énergie cinétique et de l'énergie potentielle.

### Unités SI
Sans dimension (adimensionnel)

### Variables
- $v_{avant}$ : Vitesse avant impact (m/s)
- $v_{après}$ : Vitesse après impact (m/s)
- $h_{chute}$ : Hauteur de chute (m)
- $h_{rebond}$ : Hauteur de rebond (m)
- $e$ : Coefficient de restitution

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Analyse de l'élasticité de l'impact au sol. Détection des rebonds (chutes avec rebond vs sans rebond).

### Implémentation Python
`formulas/dynamics.py` - fonction `coefficient_of_restitution()`

---

## Force Centripète

### Nom
Force Centripète

### Formule
$$F_c = \frac{mv^2}{r} = m\omega^2r$$

### Définition
La force centripète est la force qui maintient un objet en mouvement circulaire.

### Démonstration
Dérivé de la deuxième loi de Newton appliquée au mouvement circulaire uniforme.

### Unités SI
Newton (N)

### Variables
- $m$ : Masse (kg)
- $v$ : Vitesse tangentielle (m/s)
- $r$ : Rayon de la trajectoire (m)
- $\omega$ : Vitesse angulaire (rad/s)
- $F_c$ : Force centripète (N)

### Origine Scientifique
Christiaan Huygens

### Date
1673

### Publication
Horologium Oscillatorium

### DOI
N/A

### Utilisation dans le Projet
Analyse des mouvements circulaires du corps. Détection des rotations du tronc.

### Implémentation Python
`formulas/dynamics.py` - fonction `centripetal_force()`

---

## Force de Réaction du Sol

### Nom
Force de Réaction du Sol (Ground Reaction Force)

### Formule
$$\mathbf{F}_{GRF} = m\mathbf{g} + m\mathbf{a}$$

### Définition
La force de réaction du sol est la force exercée par le sol sur le corps en réaction au poids et à l'accélération.

### Démonstration
Application de la deuxième loi de Newton au corps en contact avec le sol.

### Unités SI
Newton (N)

### Variables
- $m$ : Masse (kg)
- $\mathbf{g}$ : Accélération gravitationnelle (9.81 m/s²)
- $\mathbf{a}$ : Accélération du corps (m/s²)
- $\mathbf{F}_{GRF}$ : Force de réaction du sol (N)

### Origine Scientifique
Isaac Newton

### Date
1687

### Publication
Philosophiæ Naturalis Principia Mathematica

### DOI
N/A

### Utilisation dans le Projet
Estimation de la force subie par le corps lors de l'impact. Calcul du pic de force d'impact.

### Implémentation Python
`formulas/dynamics.py` - fonction `ground_reaction_force()`

---

## Pression d'Impact

### Nom
Pression d'Impact

### Formule
$$P = \frac{F}{A}$$

### Définition
La pression est la force exercée par unité de surface.

### Démonstration
Définition fondamentale de la pression.

### Unités SI
Pascal (Pa) = N/m²

### Variables
- $F$ : Force (N)
- $A$ : Surface de contact (m²)
- $P$ : Pression (Pa)

### Origine Scientifique
Blaise Pascal

### Date
1647

### Publication
Expériences nouvelles touchant le vide

### DOI
N/A

### Utilisation dans le Projet
Calcul de la pression d'impact au sol. Estimation du risque de blessure en fonction de la surface de contact.

### Implémentation Python
`formulas/dynamics.py` - fonction `impact_pressure()`

---

## Énergie d'Impact

### Nom
Énergie d'Impact

### Formule
$$E_{impact} = \frac{1}{2}mv_{impact}^2$$

### Définition
L'énergie d'impact est l'énergie cinétique au moment de l'impact.

### Démonstration
Application directe de la formule de l'énergie cinétique.

### Unités SI
Joule (J)

### Variables
- $m$ : Masse (kg)
- $v_{impact}$ : Vitesse d'impact (m/s)
- $E_{impact}$ : Énergie d'impact (J)

### Origine Scientifique
Gottfried Wilhelm Leibniz

### Date
1686

### Publication
Brevis demonstratio

### DOI
N/A

### Utilisation dans le Projet
Calcul de l'énergie dissipée lors de l'impact. Indicateur de la gravité potentielle de la chute.

### Implémentation Python
`formulas/dynamics.py` - fonction `impact_energy()`

---

## Puissance

### Nom
Puissance

### Formule
$$P = \frac{W}{\Delta t} = \frac{dE}{dt}$$

### Formule (Mécanique)
$$P = \mathbf{F} \cdot \mathbf{v}$$

### Définition
La puissance est le taux de transfert d'énergie ou le travail par unité de temps.

### Démonstration
Définition de la puissance comme dérivée de l'énergie par rapport au temps.

### Unités SI
Watt (W) = J/s

### Variables
- $W$ : Travail (J)
- $\Delta t$ : Intervalle de temps (s)
- $\mathbf{F}$ : Force (N)
- $\mathbf{v}$ : Vitesse (m/s)
- $P$ : Puissance (W)

### Origine Scientifique
James Watt

### Date
1782

### Publication
Improvements in the Steam Engine

### DOI
N/A

### Utilisation dans le Projet
Calcul de la puissance développée lors de l'impact. Analyse de l'intensité du choc.

### Implémentation Python
`formulas/dynamics.py` - fonction `power()`

---

## Références

1. Isaac Newton - Philosophiæ Naturalis Principia Mathematica (1687)
2. Gottfried Leibniz - Brevis demonstratio (1686)
3. William Rankine - On the Mechanical Action of Heat (1853)
4. Gaspard Coriolis - Du Calcul de l'Effet des Machines (1829)
5. Leonhard Euler - Theoria Motus Corporum Solidorum (1765)
6. Christiaan Huygens - Horologium Oscillatorium (1673)
7. Blaise Pascal - Expériences nouvelles touchant le vide (1647)
8. James Watt - Improvements in the Steam Engine (1782)

---

## Implémentations Python Associées

- `formulas/dynamics.py` : forces, énergies, impulsions, impacts
- `formulas/kinematics.py` : calculs de vitesses et accélérations pour la dynamique
- `formulas/vectors.py` : opérations vectorielles pour les forces
