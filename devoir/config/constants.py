"""
Constantes physiques et paramètres du système de détection de chutes.
Basé sur les travaux de Bourke et al., Wu et al., et Dempster.
"""

# Constantes physiques
GRAVITY = 9.81  # m/s² (Galilée)
G_FORCE = 9.81  # m/s²

# Seuils de détection (Bourke et al. 2007, Wu et al. 2017)
THRESHOLD_ACCEL_RESULTANT = 3.0 * G_FORCE  # 3g
THRESHOLD_ANGULAR_VELOCITY = 200  # deg/s
THRESHOLD_VERTICAL_VELOCITY = -2.5  # m/s
THRESHOLD_TRUNK_ANGLE = 60  # degrés
THRESHOLD_TRUNK_ANGLE_STRONG = 75  # degrés
THRESHOLD_IMPACT_VELOCITY_LOW = 1.5  # m/s
THRESHOLD_IMPACT_VELOCITY_MED = 3.0  # m/s
THRESHOLD_IMPACT_VELOCITY_HIGH = 5.0  # m/s

# Seuils d'immobilité
THRESHOLD_IMMOBILITY_VARIANCE = 0.01  # m²
THRESHOLD_IMMOBILITY_TIME = 3.0  # secondes

# Délai d'observation par profil (secondes)
DELAY_PROFILE = {
    "senior_fragile": 8,
    "senior_autonome": 12,
    "adulte": 15,
    "handicape": 6,
}

# Poids du score de confiance chute
WEIGHTS_FALL_CONFIDENCE = {
    "vertical_velocity": 0.35,
    "acceleration": 0.25,
    "trunk_angle": 0.25,
    "inertia": 0.10,
    "distance_to_ground": 0.05,
}

# Poids du score de gravité
WEIGHTS_GRAVITY = {
    "intensity": 0.30,
    "time_on_ground": 0.35,
    "injury_probability": 0.20,
    "post_fall_reactivity": 0.15,
}

# Niveaux de gravité
GRAVITY_LEVELS = {
    "faible": (0, 25),
    "moyenne": (26, 50),
    "elevee": (51, 75),
    "critique": (76, 100),
}

# Modèle anthropométrique Dempster (1955)
BODY_SEGMENT_MASS = {
    0: 0.081,   # Tête
    11: 0.254,  # Épaule gauche
    12: 0.254,  # Épaule droite
    23: 0.254,  # Hanche gauche
    24: 0.254,  # Hanche droite
    13: 0.054,  # Coude gauche
    14: 0.054,  # Coude droit
    15: 0.032,  # Poignet gauche
    16: 0.032,  # Poignet droit
    25: 0.101,  # Genou gauche
    26: 0.101,  # Genou droit
    27: 0.044,  # Cheville gauche
    28: 0.044,  # Cheville droite
}

# Paramètres caméra
DEFAULT_FPS = 30
FRAME_INTERVAL = 1.0 / DEFAULT_FPS

# Sécurité
AES_KEY_SIZE = 256  # bits
PBKDF2_ITERATIONS = 100000
SESSION_DURATION_HOURS = 4
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
