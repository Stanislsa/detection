"""
Utilitaires de formatage.
Formatage de dates, nombres, etc.
"""

from datetime import datetime
from typing import Optional


def format_datetime(dt: Optional[datetime], format: str = "%d/%m/%Y %H:%M") -> str:
    """
    Formate une date/heure.
    
    Args:
        dt: Date/heure à formater
        format: Format de sortie
    
    Returns:
        Chaîne formatée ou chaîne vide
    """
    if dt is None:
        return ""
    return dt.strftime(format)


def format_date(dt: Optional[datetime]) -> str:
    """
    Formate une date.
    
    Args:
        dt: Date à formater
    
    Returns:
        Chaîne formatée ou chaîne vide
    """
    return format_datetime(dt, "%d/%m/%Y")


def format_time(dt: Optional[datetime]) -> str:
    """
    Formate une heure.
    
    Args:
        dt: Date/heure à formater
    
    Returns:
        Chaîne formatée ou chaîne vide
    """
    return format_datetime(dt, "%H:%M:%S")


def format_number(value: float, decimals: int = 2) -> str:
    """
    Formate un nombre.
    
    Args:
        value: Nombre à formater
        decimals: Nombre de décimales
    
    Returns:
        Chaîne formatée
    """
    return f"{value:.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formate un pourcentage.
    
    Args:
        value: Valeur entre 0 et 1
        decimals: Nombre de décimales
    
    Returns:
        Chaîne formatée avec %
    """
    return f"{value * 100:.{decimals}f}%"


def format_bytes(bytes_value: int) -> str:
    """
    Formate une taille en octets.
    
    Args:
        bytes_value: Taille en octets
    
    Returns:
        Chaîne formatée (ex: "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Formate une durée en secondes.
    
    Args:
        seconds: Durée en secondes
    
    Returns:
        Chaîne formatée (ex: "1h 30m 45s")
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


def format_french_date(dt: Optional[datetime]) -> str:
    """
    Formate une date en français.
    
    Args:
        dt: Date à formater
    
    Returns:
        Chaîne formatée (ex: "30 juillet 2026")
    """
    if dt is None:
        return ""
    
    months = [
        "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre"
    ]
    
    return f"{dt.day} {months[dt.month - 1]} {dt.year}"
