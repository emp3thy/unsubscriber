"""IMAP Connection Manager

Handles IMAP connection and authentication, separated from business operations
for better testability and maintainability.
"""

import imaplib
import socket
import logging
from typing import Optional
from .auth.auth_strategy import IMAPAuthStrategy


class IMAPConnectionManager:
    """Manages IMAP connections and authentication.
    
    This class encapsulates the connection logic, making it easier to mock
    and test IMAP client operations independently of connection management.
    """
    
    # Server configurations
    SERVERS = {
        'gmail': 'imap.gmail.com',
        'outlook': 'outlook.office365.com'
    }
    
    def __init__(self, email: str, auth_strategy: IMAPAuthStrategy, provider: str = None):
        """Initialize IMAP connection manager.
        
        Args:
            email: Email address for authentication
            auth_strategy: Authentication strategy to use
            provider: Email provider ('gmail' or 'outlook'), auto-detected if None
            
        Raises:
            ValueError: If provider cannot be detected from email
        """
        self.email = email
        self.auth_strategy = auth_strategy
        self.provider = provider or self._detect_provider(email)
        self.connection: Optional[imaplib.IMAP4_SSL] = None
        self.logger = logging.getLogger(__name__)
    
    def _detect_provider(self, email: str) -> str:
        """Auto-detect email provider from address.
        
        Args:
            email: Email address to analyze
            
        Returns:
            Provider name ('gmail' or 'outlook')
            
        Raises:
            ValueError: If provider cannot be detected
        """
        email_lower = email.lower()
        
        if email_lower.endswith(('@gmail.com', '@googlemail.com')):
            return 'gmail'
        elif email_lower.endswith(('@outlook.com', '@hotmail.com', '@live.com')):
            return 'outlook'
        else:
            raise ValueError(f"Unsupported email provider: {email}")
    
    def connect(self) -> bool:
        """Connect to IMAP server and authenticate.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Get server settings
            if self.provider not in self.SERVERS:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            server = self.SERVERS[self.provider]
            
            # Connect with SSL
            self.logger.info(f"Connecting to {server}:993...")
            self.connection = imaplib.IMAP4_SSL(server, 993)
            
            # Authenticate using the strategy
            success = self.auth_strategy.authenticate(self.connection, self.email)
            
            if success:
                self.logger.info(f"Successfully connected to {self.provider}")
            else:
                self.connection = None
            
            return success
            
        except socket.error as e:
            self.logger.error(f"Network error: {e}")
            self.connection = None
            return False
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            self.connection = None
            return False
    
    def disconnect(self):
        """Close IMAP connection."""
        if self.connection:
            try:
                self.connection.logout()
                self.logger.info("Disconnected from IMAP server")
            except:
                pass
            finally:
                self.connection = None
    
    def is_connected(self) -> bool:
        """Check if connected to IMAP server.
        
        Returns:
            True if connected, False otherwise
        """
        return self.connection is not None
    
    def get_connection(self) -> Optional[imaplib.IMAP4_SSL]:
        """Get the active IMAP connection.
        
        Returns:
            Active IMAP connection or None if not connected
        """
        return self.connection
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to IMAP server.
        
        Returns:
            True if reconnection successful, False otherwise
        """
        self.logger.info("Attempting to reconnect...")
        self.disconnect()
        return self.connect()
    
    def get_error_message(self) -> str:
        """Get the last error message from authentication attempt.
        
        Returns:
            Error message string, empty if no error
        """
        return self.auth_strategy.get_error_message()

