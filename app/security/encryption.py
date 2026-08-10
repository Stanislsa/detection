"""
Chiffrement AES-256-GCM des vidéos de preuve.
"""

import os
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

from app.config import settings


class EncryptionManager:
    """
    Gestion du chiffrement des données sensibles.
    
    Algorithme : AES-256-GCM (Galois/Counter Mode)
    - Confidentialité : AES en mode compteur
    - Authenticité : GHASH pour l'authentification
    - Non-répudiation : IV unique par chiffrement
    """
    
    def __init__(self, master_password: str):
        self.master_password = master_password.encode()
        self._key_cache = {}
    
    def _derive_key(self, salt: bytes) -> bytes:
        """
        Dérivation de clé via PBKDF2-HMAC-SHA256.
        NIST recommande ≥ 10 000 itérations.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=settings.PBKDF2_ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(self.master_password)
    
    def encrypt(self, data: bytes) -> bytes:
        """
        Chiffre les données avec AES-256-GCM.
        
        Format du résultat : salt (16) + nonce (12) + ciphertext + tag (16)
        """
        salt = secrets.token_bytes(16)
        key = self._derive_key(salt)
        
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)  # IV unique
        
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        # Format : salt + nonce + ciphertext
        return salt + nonce + ciphertext
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Déchiffre les données.
        """
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:28]
        ciphertext = encrypted_data[28:]
        
        key = self._derive_key(salt)
        aesgcm = AESGCM(key)
        
        return aesgcm.decrypt(nonce, ciphertext, None)
