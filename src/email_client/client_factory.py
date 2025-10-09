"""
Email client factory for creating appropriate clients based on provider.

Creates Gmail API clients for Gmail accounts and IMAP clients for others.
"""

import logging
from typing import Union
from .gmail_api_client import GmailAPIClient
from .imap_client import IMAPClient
from .auth import AuthStrategyFactory


def create_email_client(account: dict, auth_factory: AuthStrategyFactory, 
                       oauth_manager) -> Union[GmailAPIClient, IMAPClient]:
    """Create appropriate email client based on account provider.

    Args:
        account: Account dictionary with 'email', 'provider', 'encrypted_password', etc.
        auth_factory: Authentication strategy factory
        oauth_manager: OAuth credential manager

    Returns:
        GmailAPIClient for Gmail accounts, IMAPClient for others

    Raises:
        ValueError: If account data is invalid or no authentication available
    """
    logger = logging.getLogger(__name__)
    
    email = account.get('email')
    provider = account.get('provider', '').lower()
    encrypted_password = account.get('encrypted_password')
    
    if not email:
        raise ValueError("Account email is required")
    
    # Detect provider from email if not specified
    if not provider:
        email_lower = email.lower()
        if email_lower.endswith(('@gmail.com', '@googlemail.com')):
            provider = 'gmail'
        elif email_lower.endswith(('@outlook.com', '@hotmail.com', '@live.com')):
            provider = 'outlook'
        elif email_lower.endswith('@yahoo.com'):
            provider = 'yahoo'
        else:
            provider = 'generic'
    
    logger.debug(f"Creating email client for {email} (provider: {provider})")
    
    # Use Gmail API for Gmail accounts with OAuth tokens
    if provider == 'gmail':
        oauth_tokens = oauth_manager.get_oauth_tokens(email)
        if oauth_tokens:
            logger.info(f"Using Gmail API for {email}")
            return GmailAPIClient(email, oauth_manager)
        else:
            logger.info(f"No OAuth tokens found for Gmail account {email}, falling back to IMAP")
    
    # Use IMAP for all other cases
    logger.info(f"Using IMAP for {email}")
    auth_strategy = auth_factory.create_strategy(email, provider, encrypted_password)
    return IMAPClient(email, auth_strategy, provider)

