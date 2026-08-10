"""
Chiffrement et déchiffrement AES-256-GCM.

Assure la confidentialité des données (chiffrement des vidéos).
"""

import os
import base64
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from config.constants import AES_KEY_SIZE, PBKDF2_ITERATIONS


class EncryptionManager:
    """
    Gestionnaire de chiffrement AES-256-GCM.
    
    Fonctionnalités:
    - Chiffrement/déchiffrement AES-256-GCM
    - Dérivation de clé PBKDF2-HMAC-SHA256
    - Rotation de clés
    """
    
    def __init__(self, password: str = None):
        """
        Initialise le gestionnaire de chiffrement.
        
        Args:
            password: Mot de passe pour dériver la clé (optionnel)
        """
        self.backend = default_backend()
        self.key_size = AES_KEY_SIZE // 8  # Convertir bits en octets
        self.iterations = PBKDF2_ITERATIONS
        
        if password:
            self.key = self._derive_key(password)
        else:
            self.key = os.urandom(self.key_size)
    
    def _derive_key(self, password: str, salt: bytes = None) -> bytes:
        """
        Dérive une clé cryptographique à partir d'un mot de passe.
        
        Formule: clé = PBKDF2(mot_de_passe, sel, iterations=100000, longueur=32)
        
        Args:
            password: Mot de passe
            salt: Sel pour la dérivation (généré si None)
        
        Returns:
            Clé dérivée (32 octets pour AES-256)
        """
        if salt is None:
            salt = os.urandom(16)  # Sel de 16 octets
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_size,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )
        
        key = kdf.derive(password.encode())
        
        return key
    
    def encrypt(self, plaintext: bytes, associated_data: bytes = None) -> Tuple[bytes, bytes, bytes]:
        """
        Chiffre des données avec AES-256-GCM.
        
        Formule: C = E_K(P) ⊕ GHASH(H, A, C)
        
        Où:
        - E_K = AES en mode compteur
        - GHASH = authentification Galois
        - H = header, A = additional data, C = ciphertext
        
        Args:
            plaintext: Données à chiffrer
            associated_data: Données additionnelles authentifiées (optionnel)
        
        Returns:
            (nonce, ciphertext, tag) - Nonce, texte chiffré, tag d'authentification
        """
        # Générer un nonce unique (12 octets pour GCM)
        nonce = os.urandom(12)
        
        # Créer l'instance AES-GCM
        aesgcm = AESGCM(self.key)
        
        # Chiffrer
        if associated_data:
            ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
        else:
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # Dans AES-GCM, le tag est inclus dans le ciphertext (16 derniers octets)
        # Séparer le tag et le ciphertext
        tag = ciphertext[-16:]
        actual_ciphertext = ciphertext[:-16]
        
        return nonce, actual_ciphertext, tag
    
    def decrypt(self, nonce: bytes, ciphertext: bytes, tag: bytes, associated_data: bytes = None) -> bytes:
        """
        Déchiffre des données avec AES-256-GCM.
        
        Args:
            nonce: Nonce utilisé lors du chiffrement
            ciphertext: Texte chiffré
            tag: Tag d'authentification
            associated_data: Données additionnelles authentifiées (optionnel)
        
        Returns:
            Texte déchiffré
        
        Raises:
            ValueError: Si le déchiffrement échoue (tag invalide)
        """
        # Recombiner ciphertext et tag
        full_ciphertext = ciphertext + tag
        
        # Créer l'instance AES-GCM
        aesgcm = AESGCM(self.key)
        
        # Déchiffrer
        try:
            if associated_data:
                plaintext = aesgcm.decrypt(nonce, full_ciphertext, associated_data)
            else:
                plaintext = aesgcm.decrypt(nonce, full_ciphertext, None)
            
            return plaintext
            
        except Exception as e:
            raise ValueError(f"Déchiffrement échoué: {str(e)}")
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> str:
        """
        Chiffre un fichier.
        
        Args:
            file_path: Chemin du fichier à chiffrer
            output_path: Chemin de sortie (si None, ajoute .enc)
        
        Returns:
            Chemin du fichier chiffré
        """
        with open(file_path, 'rb') as f:
            plaintext = f.read()
        
        nonce, ciphertext, tag = self.encrypt(plaintext)
        
        if output_path is None:
            output_path = file_path + '.enc'
        
        # Sauvegarder: nonce + tag + ciphertext
        with open(output_path, 'wb') as f:
            f.write(nonce)
            f.write(tag)
            f.write(ciphertext)
        
        return output_path
    
    def decrypt_file(self, file_path: str, output_path: str = None) -> str:
        """
        Déchiffre un fichier.
        
        Args:
            file_path: Chemin du fichier chiffré
            output_path: Chemin de sortie (si None, retire .enc)
        
        Returns:
            Chemin du fichier déchiffré
        
        Raises:
            ValueError: Si le déchiffrement échoue
        """
        with open(file_path, 'rb') as f:
            nonce = f.read(12)  # Nonce: 12 octets
            tag = f.read(16)    # Tag: 16 octets
            ciphertext = f.read()  # Reste: ciphertext
        
        plaintext = self.decrypt(nonce, ciphertext, tag)
        
        if output_path is None:
            if file_path.endswith('.enc'):
                output_path = file_path[:-4]
            else:
                output_path = file_path + '.dec'
        
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        
        return output_path
    
    def rotate_key(self, new_password: str = None) -> bytes:
        """
        Rotation de la clé de chiffrement.
        
        Args:
            new_password: Nouveau mot de passe (optionnel)
        
        Returns:
            Nouvelle clé
        """
        if new_password:
            self.key = self._derive_key(new_password)
        else:
            self.key = os.urandom(self.key_size)
        
        return self.key
    
    def encrypt_to_base64(self, plaintext: str) -> str:
        """
        Chiffre une chaîne et retourne le résultat en base64.
        
        Args:
            plaintext: Chaîne à chiffrer
        
        Returns:
            Chaîne base64 (nonce:tag:ciphertext)
        """
        plaintext_bytes = plaintext.encode()
        nonce, ciphertext, tag = self.encrypt(plaintext_bytes)
        
        # Combiner et encoder en base64
        combined = nonce + tag + ciphertext
        return base64.b64encode(combined).decode()
    
    def decrypt_from_base64(self, encrypted_b64: str) -> str:
        """
        Déchiffre une chaîne base64.
        
        Args:
            encrypted_b64: Chaîne base64 (nonce:tag:ciphertext)
        
        Returns:
            Chaîne déchiffrée
        """
        combined = base64.b64decode(encrypted_b64)
        
        nonce = combined[:12]
        tag = combined[12:28]
        ciphertext = combined[28:]
        
        plaintext_bytes = self.decrypt(nonce, ciphertext, tag)
        return plaintext_bytes.decode()


class KeyManager:
    """
    Gestionnaire de clés cryptographiques.
    
    Gère le stockage et la rotation des clés.
    """
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Génère une clé aléatoire.
        
        Returns:
            Clé de 32 octets (AES-256)
        """
        return os.urandom(32)
    
    @staticmethod
    def key_to_base64(key: bytes) -> str:
        """
        Convertit une clé en base64.
        
        Args:
            key: Clé en bytes
        
        Returns:
            Clé encodée en base64
        """
        return base64.b64encode(key).decode()
    
    @staticmethod
    def key_from_base64(key_b64: str) -> bytes:
        """
        Décode une clé depuis base64.
        
        Args:
            key_b64: Clé encodée en base64
        
        Returns:
            Clé en bytes
        """
        return base64.b64decode(key_b64)
