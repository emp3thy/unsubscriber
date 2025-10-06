"""
Authentication strategies for IMAP clients.

This module provides a pluggable authentication system using the Strategy pattern.
Each authentication method (password, OAuth, etc.) is implemented as a separate
strategy class, making it easy to add new authentication methods without
modifying existing code.
"""

from .auth_strategy import IMAPAuthStrategy
from .password_auth import PasswordAuthStrategy
from .gmail_oauth_auth import GmailOAuthStrategy
from .auth_factory import AuthStrategyFactory

__all__ = [
    'IMAPAuthStrategy',
    'PasswordAuthStrategy', 
    'GmailOAuthStrategy',
    'AuthStrategyFactory'
]
