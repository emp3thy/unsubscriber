"""
Gmail OAuth 2.0 authentication manager.

Handles OAuth 2.0 token management, authorization flow, and IMAP authentication
for Gmail accounts. Provides secure token storage and automatic refresh.
"""

import json
import base64
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from cryptography.fernet import Fernet


class GmailOAuthManager:
    """Manages Gmail OAuth 2.0 authentication and token operations."""
    
    # Gmail API scope - allows full mail access (read, send, delete)
    # Using googleapis.com scope for Gmail API (includes IMAP access)
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, credentials_file: str = 'data/gmail_credentials.json'):
        """Initialize Gmail OAuth manager.
        
        Args:
            credentials_file: Path to OAuth credentials JSON file
        """
        self.credentials_file = credentials_file
        self.logger = logging.getLogger(__name__)
    
    def authorize_user(self) -> Optional[Dict[str, Any]]:
        """Run OAuth authorization flow for a new user.
        
        Opens browser for user authorization and returns tokens.
        
        Returns:
            Dictionary with access_token, refresh_token, and token_expiry,
            or None if authorization failed
        """
        try:
            if not os.path.exists(self.credentials_file):
                self.logger.error(f"OAuth credentials file not found: {self.credentials_file}")
                raise FileNotFoundError(
                    f"OAuth credentials file not found: {self.credentials_file}\n"
                    f"Please follow the setup instructions to create this file."
                )
            
            # Create flow from credentials file
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.SCOPES
            )
            
            # Run local server flow (opens browser)
            self.logger.info("Starting OAuth authorization flow...")
            credentials = flow.run_local_server(port=0)
            
            # Extract token information
            tokens = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            self.logger.info("OAuth authorization completed successfully")
            return tokens
            
        except Exception as e:
            self.logger.error(f"OAuth authorization failed: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh an expired access token.
        
        Args:
            refresh_token: Refresh token to use
            
        Returns:
            Dictionary with new access_token, refresh_token, and token_expiry,
            or None if refresh failed
        """
        try:
            # Create credentials object with refresh token
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self._get_client_id(),
                client_secret=self._get_client_secret()
            )
            
            # Refresh the token
            request = Request()
            credentials.refresh(request)
            
            # Return new token information
            tokens = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token or refresh_token,
                'token_expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            self.logger.info("OAuth token refreshed successfully")
            return tokens
            
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
            return None
    
    def is_token_expired(self, token_expiry: Optional[str]) -> bool:
        """Check if an access token is expired or will expire soon.
        
        Args:
            token_expiry: Token expiry time in ISO format
            
        Returns:
            True if token is expired or will expire within 5 minutes
        """
        if not token_expiry:
            return True
        
        try:
            expiry_time = datetime.fromisoformat(token_expiry.replace('Z', '+00:00'))
            # Consider expired if expires within 5 minutes
            buffer_time = datetime.now(expiry_time.tzinfo) + timedelta(minutes=5)
            return expiry_time <= buffer_time
        except Exception:
            # If we can't parse the expiry time, assume expired
            return True
    
    def generate_oauth2_string(self, email: str, access_token: str) -> bytes:
        """Generate OAuth2 authentication string for IMAP XOAUTH2.
        
        Args:
            email: Email address
            access_token: OAuth access token
            
        Returns:
            Base64-encoded OAuth2 authentication string as bytes
        """
        # Format per RFC 7628: user=<email>\x01auth=Bearer <token>\x01\x01
        # Make sure Bearer is capitalized and format is exact
        auth_string = f'user={email}\x01auth=Bearer {access_token}\x01\x01'
        self.logger.debug(f"Raw OAuth2 string: {repr(auth_string)}")
        encoded = base64.b64encode(auth_string.encode('utf-8'))
        self.logger.debug(f"Encoded OAuth2 string: {encoded}")
        return encoded
    
    def _get_client_id(self) -> str:
        """Get OAuth client ID from credentials file.
        
        Returns:
            OAuth client ID
        """
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
                return credentials['installed']['client_id']
        except Exception as e:
            self.logger.error(f"Failed to read client ID: {e}")
            raise
    
    def _get_client_secret(self) -> str:
        """Get OAuth client secret from credentials file.
        
        Returns:
            OAuth client secret
        """
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
                return credentials['installed']['client_secret']
        except Exception as e:
            self.logger.error(f"Failed to read client secret: {e}")
            raise


class OAuthCredentialManager:
    """Manages encrypted storage of OAuth tokens in the database."""
    
    def __init__(self, db_manager, cred_manager):
        """Initialize OAuth credential manager.
        
        Args:
            db_manager: DBManager instance for database operations
            cred_manager: CredentialManager instance for encryption
        """
        self.db = db_manager
        self.cred = cred_manager
        self.gmail_oauth = GmailOAuthManager()
        self.logger = logging.getLogger(__name__)
    
    def store_oauth_tokens(self, email: str, access_token: str, 
                          refresh_token: str, token_expiry: Optional[str] = None):
        """Store OAuth tokens in encrypted form.
        
        Args:
            email: Email address the tokens belong to
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            token_expiry: Token expiry time in ISO format (optional)
        """
        try:
            # Encrypt tokens
            encrypted_access = self.cred.encrypt_password(access_token)
            encrypted_refresh = self.cred.encrypt_password(refresh_token)
            
            # Store in database
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO oauth_tokens 
                    (email, access_token, refresh_token, token_expiry, updated_date)
                    VALUES (?, ?, ?, ?, datetime('now'))
                """, (email, encrypted_access, encrypted_refresh, token_expiry))
            
            self.logger.info(f"OAuth tokens stored for {email}")
            
        except Exception as e:
            self.logger.error(f"Failed to store OAuth tokens for {email}: {e}")
            raise
    
    def get_oauth_tokens(self, email: str) -> Optional[Dict[str, str]]:
        """Retrieve and decrypt OAuth tokens for an email.
        
        Args:
            email: Email address to get tokens for
            
        Returns:
            Dictionary with access_token, refresh_token, and token_expiry,
            or None if no tokens found
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT access_token, refresh_token, token_expiry
                    FROM oauth_tokens WHERE email = ?
                """, (email,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Decrypt tokens
                access_token = self.cred.decrypt_password(row[0])
                refresh_token = self.cred.decrypt_password(row[1])
                token_expiry = row[2]
                
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_expiry': token_expiry
                }
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve OAuth tokens for {email}: {e}")
            return None
    
    def delete_oauth_tokens(self, email: str) -> bool:
        """Delete OAuth tokens for an email.
        
        Args:
            email: Email address to delete tokens for
            
        Returns:
            True if tokens were deleted, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM oauth_tokens WHERE email = ?", (email,))
                deleted = cursor.rowcount > 0
                
                if deleted:
                    self.logger.info(f"OAuth tokens deleted for {email}")
                
                return deleted
                
        except Exception as e:
            self.logger.error(f"Failed to delete OAuth tokens for {email}: {e}")
            return False