"""
Password-based authentication strategy for IMAP clients.

Handles traditional username/password authentication for email providers
that support this method (Outlook, Yahoo, etc.).
"""

import imaplib
import logging
from .auth_strategy import IMAPAuthStrategy


class PasswordAuthStrategy(IMAPAuthStrategy):
    """Password-based IMAP authentication strategy.
    
    Uses traditional username/password authentication via IMAP LOGIN command.
    """
    
    def __init__(self, password: str):
        """Initialize password authentication strategy.
        
        Args:
            password: Password or app password for authentication
        """
        super().__init__()
        self.password = password
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self, imap_connection: imaplib.IMAP4_SSL, email: str) -> bool:
        """Authenticate using username and password.
        
        Args:
            imap_connection: Established IMAP SSL connection
            email: Email address to authenticate
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            imap_connection.login(email, self.password)
            self.logger.info(f"Successfully authenticated {email} using password")
            return True
            
        except imaplib.IMAP4.error as e:
            error_msg = str(e).lower()
            
            if 'application-specific password required' in error_msg or 'less secure' in error_msg:
                self.logger.error(f"Gmail app password required: {e}")
                self._set_error_message(
                    "Gmail no longer supports password authentication. "
                    "Please use OAuth 2.0 or generate an App Password."
                )
            elif 'authentication failed' in error_msg or 'login failed' in error_msg:
                self.logger.error(f"Authentication failed: {e}")
                self._set_error_message(
                    "Invalid email address or password. Please check your credentials."
                )
            elif 'connection refused' in error_msg or 'network is unreachable' in error_msg:
                self.logger.error(f"Network error: {e}")
                self._set_error_message(
                    "Cannot connect to email server. Please check your internet connection."
                )
            else:
                self.logger.error(f"Password authentication error: {e}")
                self._set_error_message(
                    "Failed to authenticate with email server. Please try again."
                )
            
            return False
        
        except Exception as e:
            self.logger.error(f"Unexpected password authentication error: {e}")
            self._set_error_message("Unexpected authentication error.")
            return False
