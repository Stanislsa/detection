"""
Fonctions utilitaires diverses.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import hashlib
import json

def ensure_dir(path: Path) -> Path:
    """
    S'assure qu'un répertoire existe, le crée si nécessaire.
    
    Args:
        path: Chemin du répertoire
    
    Returns:
        Chemin du répertoire
    """
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_timestamp() -> str:
    """
    Retourne un timestamp formaté pour les noms de fichiers.
    
    Returns:
        Timestamp au format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    Hache une chaîne de caractères.
    
    Args:
        text: Texte à hacher
        algorithm: Algorithme de hachage (sha256, md5, etc.)
    
    Returns:
        Hash hexadécimal
    """
    hash_func = hashlib.new(algorithm)
    hash_func.update(text.encode())
    return hash_func.hexdigest()

def save_json(data: dict, path: Path) -> None:
    """
    Sauvegarde un dictionnaire en JSON.
    
    Args:
        data: Données à sauvegarder
        path: Chemin du fichier
    """
    ensure_dir(path.parent)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

def load_json(path: Path) -> Optional[dict]:
    """
    Charge un fichier JSON.
    
    Args:
        path: Chemin du fichier
    
    Returns:
        Dictionnaire ou None si erreur
    """
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def format_duration(seconds: float) -> str:
    """
    Formate une durée en secondes en format lisible.
    
    Args:
        seconds: Durée en secondes
    
    Returns:
        Durée formatée (ex: "1h 23m 45s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)

def get_file_size_mb(path: Path) -> float:
    """
    Retourne la taille d'un fichier en Mo.
    
    Args:
        path: Chemin du fichier
    
    Returns:
        Taille en Mo
    """
    if not path.exists():
        return 0.0
    return path.stat().st_size / (1024 * 1024)
