"""
Base authentication strategy for IMAP clients.

Defines the interface that all authentication strategies must implement.
"""

from abc import ABC, abstractmethod
import imaplib
from typing import Optional


class IMAPAuthStrategy(ABC):
    """Base class for IMAP authentication strategies.
    
    Each authentication method (password, OAuth, etc.) should inherit from this
    class and implement the authenticate method.
    """
    
    def __init__(self):
        """Initialize the authentication strategy."""
        self.error_message = ""
    
    @abstractmethod
    def authenticate(self, imap_connection: imaplib.IMAP4_SSL, email: str) -> bool:
        """Authenticate with the IMAP server.
        
        Args:
            imap_connection: Established IMAP SSL connection
            email: Email address to authenticate
            
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    def get_error_message(self) -> str:
        """Get human-readable error message from last authentication attempt.
        
        Returns:
            Error message string, empty if no error
        """
        return self.error_message
    
    def _set_error_message(self, message: str):
        """Set the error message for this authentication attempt.
        
        Args:
            message: Error message to set
        """
        self.error_message = message
