"""
Gmail OAuth 2.0 authentication strategy for IMAP clients.

Handles OAuth 2.0 authentication for Gmail accounts, including automatic
token refresh and XOAUTH2 SASL authentication.
"""

import imaplib
import logging
import base64
from typing import Optional, Dict, Any
from .auth_strategy import IMAPAuthStrategy
from ..gmail_oauth import GmailOAuthManager


class GmailOAuthStrategy(IMAPAuthStrategy):
    """Gmail OAuth 2.0 IMAP authentication strategy.
    
    Uses OAuth 2.0 tokens to authenticate with Gmail via XOAUTH2 SASL mechanism.
    Automatically refreshes expired tokens.
    """
    
    def __init__(self, oauth_manager):
        """Initialize Gmail OAuth authentication strategy.
        
        Args:
            oauth_manager: OAuthCredentialManager instance for token management
        """
        super().__init__()
        self.oauth_manager = oauth_manager
        self.gmail_oauth = GmailOAuthManager()
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self, imap_connection: imaplib.IMAP4_SSL, email: str) -> bool:
        """Authenticate using OAuth 2.0 tokens.
        
        Args:
            imap_connection: Established IMAP SSL connection
            email: Email address to authenticate
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Get stored tokens
            tokens = self.oauth_manager.get_oauth_tokens(email)
            if not tokens:
                self.logger.error(f"No OAuth tokens found for {email}")
                self._set_error_message(
                    "OAuth tokens not found. Please re-authorize the application."
                )
                return False
            
            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
            token_expiry = tokens.get('token_expiry')
            
            # Check if token needs refresh
            if self.gmail_oauth.is_token_expired(token_expiry):
                self.logger.info("Access token expired, refreshing...")
                new_tokens = self.gmail_oauth.refresh_token(refresh_token)
                
                if not new_tokens:
                    self.logger.error("Failed to refresh access token")
                    self._set_error_message(
                        "Failed to refresh OAuth token. Please re-authorize the application."
                    )
                    return False
                
                # Update stored tokens
                access_token = new_tokens['access_token']
                self.oauth_manager.store_oauth_tokens(
                    email,
                    new_tokens['access_token'],
                    new_tokens['refresh_token'],
                    new_tokens.get('token_expiry')
                )
                self.logger.info("OAuth tokens refreshed successfully")
            
            # Use Google's recommended XOAUTH2 authentication approach
            # Generate the auth string using the exact format Gmail expects
            auth_string = f'user={email}\001auth=Bearer {access_token}\001\001'
            auth_bytes = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
            
            self.logger.debug(f"Using direct XOAUTH2 with access token: {access_token[:20]}...")
            
            # Try direct XOAUTH2 authentication without callback
            try:
                # Method 1: Direct authenticate call with base64 string
                imap_connection.authenticate('XOAUTH2', lambda x: auth_bytes.encode('ascii'))
                self.logger.info(f"Successfully authenticated {email} using OAuth 2.0 (method 1)")
                return True
            except Exception as e1:
                self.logger.debug(f"Method 1 failed: {e1}")
                
                try:
                    # Method 2: Use simple callback returning bytes
                    def simple_auth(challenge):
                        return base64.b64encode(auth_string.encode('ascii'))
                    
                    imap_connection.authenticate('XOAUTH2', simple_auth)
                    self.logger.info(f"Successfully authenticated {email} using OAuth 2.0 (method 2)")
                    return True
                except Exception as e2:
                    self.logger.debug(f"Method 2 failed: {e2}")
                    raise e2  # Re-raise the last exception
            
        except imaplib.IMAP4.error as e:
            error_msg = str(e).lower()
            
            if 'invalid credentials' in error_msg or 'authentication failed' in error_msg:
                self.logger.error(f"OAuth authentication failed: {e}")
                
                # Try to refresh token one more time
                if self._retry_with_token_refresh(imap_connection, email, tokens):
                    return True
                
                self._set_error_message(
                    "OAuth authentication failed. Please re-authorize the application."
                )
            else:
                self.logger.error(f"OAuth connection error: {e}")
                self._set_error_message(
                    "Failed to connect to Gmail. Please try again."
                )
            
            return False
        
        except Exception as e:
            self.logger.error(f"Unexpected OAuth authentication error: {e}")
            self._set_error_message("Unexpected OAuth authentication error.")
            return False
    
    def _retry_with_token_refresh(self, imap_connection: imaplib.IMAP4_SSL, 
                                 email: str, tokens: Dict[str, Any]) -> bool:
        """Attempt to retry authentication after refreshing tokens.
        
        Args:
            imap_connection: IMAP connection to authenticate with
            email: Email address
            tokens: Current token dictionary
            
        Returns:
            True if retry successful, False otherwise
        """
        try:
            self.logger.info("Attempting token refresh and retry...")
            new_tokens = self.gmail_oauth.refresh_token(tokens['refresh_token'])
            
            if new_tokens:
                # Store refreshed tokens
                self.oauth_manager.store_oauth_tokens(
                    email,
                    new_tokens['access_token'],
                    new_tokens['refresh_token'],
                    new_tokens.get('token_expiry')
                )
                
                # Retry authentication with direct method
                access_token = new_tokens['access_token']
                auth_string = f'user={email}\001auth=Bearer {access_token}\001\001'
                auth_bytes = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
                
                try:
                    imap_connection.authenticate('XOAUTH2', lambda x: auth_bytes.encode('ascii'))
                    self.logger.info("Retry successful after token refresh (method 1)")
                    return True
                except Exception:
                    def simple_auth(challenge):
                        return base64.b64encode(auth_string.encode('ascii'))
                    
                    imap_connection.authenticate('XOAUTH2', simple_auth)
                    self.logger.info("Retry successful after token refresh (method 2)")
                    return True
                
        except Exception as retry_error:
            self.logger.error(f"Token refresh retry failed: {retry_error}")
        
        return False
