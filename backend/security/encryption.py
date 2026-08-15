"""
AES-256-GCM encryption for sensitive data.
"""

import os
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

from backend.core.config import settings
from backend.core.logger import get_logger

logger = get_logger(__name__)


class EncryptionManager:
    """
    Encryption manager using AES-256-GCM.
    
    Provides:
    - Confidentiality: AES in counter mode
    - Authenticity: GHASH for authentication
    - Non-repudiation: Unique IV per encryption
    """
    
    def __init__(self, master_password: str):
        """
        Initialize encryption manager.
        
        Args:
            master_password: Master password for key derivation
        """
        self.master_password = master_password.encode()
        self._key_cache = {}
    
    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key using PBKDF2-HMAC-SHA256.
        
        NIST recommends ≥ 10,000 iterations.
        
        Args:
            salt: Salt for key derivation
        
        Returns:
            Derived key (32 bytes for AES-256)
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
        Encrypt data with AES-256-GCM.
        
        Format: salt (16) + nonce (12) + ciphertext + tag (16)
        
        Args:
            data: Data to encrypt
        
        Returns:
            Encrypted data with salt and nonce
        """
        try:
            salt = secrets.token_bytes(16)
            key = self._derive_key(salt)
            
            aesgcm = AESGCM(key)
            nonce = secrets.token_bytes(12)  # Unique IV
            
            ciphertext = aesgcm.encrypt(nonce, data, None)
            
            # Format: salt + nonce + ciphertext
            return salt + nonce + ciphertext
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data with salt and nonce
        
        Returns:
            Decrypted data
        """
        try:
            salt = encrypted_data[:16]
            nonce = encrypted_data[16:28]
            ciphertext = encrypted_data[28:]
            
            key = self._derive_key(salt)
            aesgcm = AESGCM(key)
            
            return aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string and return base64 encoded result.
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            Base64 encoded encrypted data
        """
        encrypted = self.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_string(self, encrypted_b64: str) -> str:
        """
        Decrypt a base64 encoded encrypted string.
        
        Args:
            encrypted_b64: Base64 encoded encrypted data
        
        Returns:
            Decrypted string
        """
        encrypted = base64.b64decode(encrypted_b64.encode())
        decrypted = self.decrypt(encrypted)
        return decrypted.decode()
