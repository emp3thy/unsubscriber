"""
Authentication strategy factory for IMAP clients.

Provides a factory method to create appropriate authentication strategies
based on email provider and available credentials.
"""

import logging
from typing import Optional
from .auth_strategy import IMAPAuthStrategy
from .password_auth import PasswordAuthStrategy
from .gmail_oauth_auth import GmailOAuthStrategy


class AuthStrategyFactory:
    """Factory for creating IMAP authentication strategies.
    
    Given an email address and available credentials, this factory determines
    the best authentication strategy to use and returns an instance of it.
    """
    
    def __init__(self, cred_manager, oauth_manager):
        """Initialize the authentication strategy factory.
        
        Args:
            cred_manager: CredentialManager instance for password encryption
            oauth_manager: OAuthCredentialManager instance for OAuth tokens
        """
        self.cred_manager = cred_manager
        self.oauth_manager = oauth_manager
        self.logger = logging.getLogger(__name__)
    
    def create_strategy(self, email: str, provider: str, 
                       encrypted_password: Optional[str] = None) -> IMAPAuthStrategy:
        """Create appropriate authentication strategy for the given email.
        
        Args:
            email: Email address to authenticate
            provider: Email provider ('gmail', 'outlook', etc.)
            encrypted_password: Encrypted password from database (optional)
            
        Returns:
            Appropriate authentication strategy instance
            
        Raises:
            ValueError: If no suitable authentication method is available
        """
        self.logger.debug(f"Creating auth strategy for {email} (provider: {provider})")
        
        # For Gmail, prefer OAuth if tokens are available
        if provider == 'gmail':
            oauth_tokens = self.oauth_manager.get_oauth_tokens(email)
            if oauth_tokens:
                self.logger.info(f"Using OAuth authentication for {email}")
                return GmailOAuthStrategy(self.oauth_manager)
        
        # Fall back to password authentication if available
        if encrypted_password:
            try:
                password = self.cred_manager.decrypt_password(encrypted_password)
                self.logger.info(f"Using password authentication for {email}")
                return PasswordAuthStrategy(password)
            except Exception as e:
                self.logger.error(f"Failed to decrypt password for {email}: {e}")
                raise ValueError(f"Failed to decrypt password: {e}")
        
        # No authentication method available
        error_msg = f"No authentication method available for {email}"
        self.logger.error(error_msg)
        raise ValueError(error_msg)
    
    def get_available_auth_methods(self, email: str, provider: str, 
                                  encrypted_password: Optional[str] = None) -> list:
        """Get list of available authentication methods for an email.
        
        Args:
            email: Email address to check
            provider: Email provider
            encrypted_password: Encrypted password from database (optional)
            
        Returns:
            List of available authentication method names
        """
        methods = []
        
        # Check OAuth availability
        if provider == 'gmail':
            oauth_tokens = self.oauth_manager.get_oauth_tokens(email)
            if oauth_tokens:
                methods.append('oauth')
        
        # Check password availability
        if encrypted_password:
            methods.append('password')
        
        return methods
