"""
Utilitaires de validation.
Validation des entrées utilisateur.
"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Valide une adresse email.
    
    Args:
        email: Adresse email à valider
    
    Returns:
        True si valide
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """
    Valide une URL.
    
    Args:
        url: URL à valider
    
    Returns:
        True si valide
    """
    pattern = r'^(http|https|rtsp)://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


def validate_rtsp_url(url: str) -> bool:
    """
    Valide une URL RTSP.
    
    Args:
        url: URL RTSP à valider
    
    Returns:
        True si valide
    """
    pattern = r'^rtsp://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


def validate_ip_address(ip: str) -> bool:
    """
    Valide une adresse IP.
    
    Args:
        ip: Adresse IP à valider
    
    Returns:
        True si valide
    """
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    # Vérifier que chaque octet est entre 0 et 255
    octets = ip.split('.')
    for octet in octets:
        if not 0 <= int(octet) <= 255:
            return False
    
    return True


def validate_port(port: int) -> bool:
    """
    Valide un numéro de port.
    
    Args:
        port: Numéro de port à valider
    
    Returns:
        True si valide (1-65535)
    """
    return 1 <= port <= 65535


def validate_username(username: str) -> bool:
    """
    Valide un nom d'utilisateur.
    
    Args:
        username: Nom d'utilisateur à valider
    
    Returns:
        True si valide
    """
    # 3-30 caractères, alphanumériques et underscores
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    return re.match(pattern, username) is not None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valide la force d'un mot de passe.
    
    Args:
        password: Mot de passe à valider
    
    Returns:
        (est_valide, message)
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not re.search(r'[0-9]', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial"
    
    return True, "Mot de passe valide"


def validate_totp_code(code: str) -> bool:
    """
    Valide un code TOTP.
    
    Args:
        code: Code TOTP à valider
    
    Returns:
        True si valide (6 chiffres)
    """
    pattern = r'^\d{6}$'
    return re.match(pattern, code) is not None


def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier.
    
    Args:
        filename: Nom de fichier à nettoyer
    
    Returns:
        Nom de fichier nettoyé
    """
    # Supprimer les caractères invalides
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limiter la longueur
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename
