"""Credential encryption manager for Email Unsubscriber

Provides secure password encryption using Fernet symmetric encryption.
Ensures email passwords are never stored in plaintext.
"""

from cryptography.fernet import Fernet
import os
import logging


class CredentialManager:
    """Manages encryption and decryption of email passwords.
    
    Uses Fernet symmetric encryption from the cryptography library.
    The encryption key is stored in a file and reused for all operations.
    """
    
    def __init__(self, key_path: str = 'data/key.key'):
        """Initialize credential manager.
        
        Args:
            key_path: Path to the encryption key file
        """
        self.key_path = key_path
        self.logger = logging.getLogger(__name__)
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)
    
    def _load_or_create_key(self) -> bytes:
        """Load existing key or generate new one.
        
        Returns:
            Encryption key as bytes
            
        Raises:
            Exception: If key file operations fail
        """
        try:
            # Create data directory if needed
            key_dir = os.path.dirname(self.key_path)
            if key_dir:
                os.makedirs(key_dir, exist_ok=True)
            
            if os.path.exists(self.key_path):
                # Load existing key
                with open(self.key_path, 'rb') as key_file:
                    key = key_file.read()
                self.logger.info("Encryption key loaded")
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(self.key_path, 'wb') as key_file:
                    key_file.write(key)
                self.logger.info(f"New encryption key generated: {self.key_path}")
            
            return key
        except Exception as e:
            self.logger.error(f"Error with encryption key: {e}")
            raise
    
    def encrypt_password(self, password: str) -> str:
        """Encrypt password and return as base64 string.
        
        Args:
            password: Plain text password to encrypt
            
        Returns:
            Encrypted password as base64 string
            
        Raises:
            Exception: If encryption fails
        """
        try:
            encrypted_bytes = self.fernet.encrypt(password.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error encrypting password: {e}")
            raise
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt password from base64 string.
        
        Args:
            encrypted_password: Encrypted password as base64 string
            
        Returns:
            Decrypted password as plain text
            
        Raises:
            Exception: If decryption fails
        """
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_password.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error decrypting password: {e}")
            raise

