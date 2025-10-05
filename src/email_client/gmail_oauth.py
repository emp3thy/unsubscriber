"""Gmail OAuth 2.0 authentication manager.

This module handles OAuth 2.0 authentication for Gmail IMAP access,
including token storage, refresh, and IMAP authentication string generation.
"""

import os
import json
import logging
import base64
from typing import Optional, Dict
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GmailOAuthManager:
    """Manages OAuth 2.0 authentication for Gmail IMAP access."""
    
    # Gmail IMAP requires full mail access scope
    SCOPES = ['https://mail.google.com/']
    
    # OAuth 2.0 endpoints
    TOKEN_URI = 'https://oauth2.googleapis.com/token'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    
    def __init__(self, credentials_path: str = 'data/gmail_credentials.json'):
        """Initialize Gmail OAuth manager.
        
        Args:
            credentials_path: Path to OAuth client credentials file
        """
        self.credentials_path = credentials_path
        self.logger = logging.getLogger(__name__)
        self.credentials = None
        
    def has_credentials_file(self) -> bool:
        """Check if OAuth credentials file exists.
        
        Returns:
            True if credentials file exists, False otherwise
        """
        return os.path.exists(self.credentials_path)
    
    def authorize(self, email: str) -> Optional[Dict[str, str]]:
        """Start OAuth authorization flow for a Gmail account.
        
        Opens a browser window for user to grant permissions.
        
        Args:
            email: Gmail address to authorize
            
        Returns:
            Dictionary with 'access_token' and 'refresh_token', or None on failure
        """
        try:
            if not self.has_credentials_file():
                self.logger.error(f"Credentials file not found: {self.credentials_path}")
                return None
            
            # Load client configuration
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            
            # Set login hint to pre-fill email
            flow.oauth2session.redirect_uri = flow._OOB_REDIRECT_URI
            
            # Run local server flow
            self.logger.info(f"Starting OAuth flow for {email}")
            self.credentials = flow.run_local_server(
                port=0,
                authorization_prompt_message='Please visit this URL to authorize: {url}',
                success_message='Authorization successful! You can close this window.',
                open_browser=True
            )
            
            # Extract tokens
            tokens = {
                'access_token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_expiry': self.credentials.expiry.isoformat() if self.credentials.expiry else None
            }
            
            self.logger.info(f"OAuth authorization successful for {email}")
            return tokens
            
        except Exception as e:
            self.logger.error(f"OAuth authorization failed: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh an expired access token.
        
        Args:
            refresh_token: The refresh token from initial authorization
            
        Returns:
            Dictionary with new 'access_token' and expiry, or None on failure
        """
        try:
            # Load client configuration
            with open(self.credentials_path, 'r') as f:
                client_config = json.load(f)
            
            # Extract client info
            if 'installed' in client_config:
                client_info = client_config['installed']
            elif 'web' in client_config:
                client_info = client_config['web']
            else:
                self.logger.error("Invalid credentials file format")
                return None
            
            # Create credentials object with refresh token
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri=self.TOKEN_URI,
                client_id=client_info['client_id'],
                client_secret=client_info['client_secret'],
                scopes=self.SCOPES
            )
            
            # Refresh the token
            self.logger.info("Refreshing access token")
            credentials.refresh(Request())
            
            # Return new tokens
            tokens = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token or refresh_token,  # Keep old if no new one
                'token_expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            self.logger.info("Access token refreshed successfully")
            return tokens
            
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
            return None
    
    def generate_oauth2_string(self, email: str, access_token: str) -> str:
        """Generate OAuth2 authentication string for IMAP.
        
        Args:
            email: Gmail address
            access_token: Valid OAuth2 access token
            
        Returns:
            Base64-encoded OAuth2 authentication string
        """
        # Format: user={email}^Aauth=Bearer {token}^A^A
        # where ^A is ASCII 0x01 (SOH - Start of Header)
        auth_string = f"user={email}\x01auth=Bearer {access_token}\x01\x01"
        
        # Encode to base64
        return base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
    
    def is_token_expired(self, token_expiry: Optional[str]) -> bool:
        """Check if an access token is expired.
        
        Args:
            token_expiry: ISO format expiry timestamp, or None
            
        Returns:
            True if expired or expiry unknown, False if still valid
        """
        if not token_expiry:
            return True
        
        try:
            expiry = datetime.fromisoformat(token_expiry)
            # Consider expired if less than 5 minutes remaining
            return datetime.utcnow() >= expiry - timedelta(minutes=5)
        except Exception:
            return True
    
    def validate_token(self, access_token: str) -> bool:
        """Validate an access token by making a test request.
        
        Args:
            access_token: Access token to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Create a credentials object and check validity
            credentials = Credentials(token=access_token)
            return credentials.valid
        except Exception as e:
            self.logger.error(f"Token validation failed: {e}")
            return False


class OAuthCredentialManager:
    """Manages storage and retrieval of OAuth tokens in the database."""
    
    def __init__(self, db_manager, credential_manager):
        """Initialize OAuth credential manager.
        
        Args:
            db_manager: DBManager instance for database operations
            credential_manager: CredentialManager instance for encryption
        """
        self.db = db_manager
        self.cred = credential_manager
        self.logger = logging.getLogger(__name__)
    
    def store_oauth_tokens(self, email: str, access_token: str, 
                          refresh_token: str, token_expiry: Optional[str] = None) -> bool:
        """Store OAuth tokens in the database (encrypted).
        
        Args:
            email: Gmail address
            access_token: OAuth2 access token
            refresh_token: OAuth2 refresh token
            token_expiry: ISO format expiry timestamp
            
        Returns:
            True if stored successfully, False otherwise
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
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store OAuth tokens: {e}")
            return False
    
    def get_oauth_tokens(self, email: str) -> Optional[Dict[str, str]]:
        """Retrieve OAuth tokens from the database.
        
        Args:
            email: Gmail address
            
        Returns:
            Dictionary with 'access_token', 'refresh_token', and 'token_expiry', or None
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT access_token, refresh_token, token_expiry
                    FROM oauth_tokens
                    WHERE email = ?
                """, (email,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Decrypt tokens
                access_token = self.cred.decrypt_password(row[0])
                refresh_token = self.cred.decrypt_password(row[1])
                
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_expiry': row[2]
                }
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve OAuth tokens: {e}")
            return None
    
    def delete_oauth_tokens(self, email: str) -> bool:
        """Delete OAuth tokens from the database.
        
        Args:
            email: Gmail address
            
        Returns:
            True if deleted, False otherwise
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
            self.logger.error(f"Failed to delete OAuth tokens: {e}")
            return False
