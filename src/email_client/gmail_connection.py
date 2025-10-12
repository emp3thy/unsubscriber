"""Gmail API Connection Manager

Handles Gmail API connection and OAuth authentication, separated from business
operations for better testability and maintainability.
"""

import logging
from typing import Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


class GmailConnectionManager:
    """Manages Gmail API connections and OAuth authentication.
    
    This class encapsulates the OAuth token management and service building,
    making it easier to mock and test Gmail API client operations.
    """
    
    def __init__(self, email: str, oauth_manager):
        """Initialize Gmail connection manager.
        
        Args:
            email: Gmail address
            oauth_manager: OAuthCredentialManager instance for token handling
        """
        self.email = email
        self.oauth_manager = oauth_manager
        self.service = None
        self.logger = logging.getLogger(__name__)
        self.error_message = None
    
    def connect(self) -> bool:
        """Connect to Gmail API using OAuth2 credentials.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Get OAuth tokens
            tokens = self.oauth_manager.get_oauth_tokens(self.email)
            if not tokens:
                self.error_message = "No OAuth tokens found. Please re-authorize."
                self.logger.error(self.error_message)
                return False
            
            # Get client credentials from gmail_oauth manager
            gmail_oauth = self.oauth_manager.gmail_oauth
            
            # Create credentials object
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_uri='https://oauth2.googleapis.com/token',
                client_id=gmail_oauth._get_client_id(),
                client_secret=gmail_oauth._get_client_secret(),
                scopes=['https://www.googleapis.com/auth/gmail.modify']
            )
            
            # Check if token needs refresh
            if gmail_oauth.is_token_expired(tokens.get('token_expiry')):
                self.logger.info("Refreshing expired token...")
                request = Request()
                credentials.refresh(request)
                
                # Update stored tokens
                self.oauth_manager.store_oauth_tokens(
                    self.email,
                    credentials.token,
                    credentials.refresh_token,
                    credentials.expiry.isoformat() if credentials.expiry else None
                )
            
            # Build Gmail API service
            self.service = build('gmail', 'v1', credentials=credentials, cache_discovery=False)
            self.logger.info(f"Successfully connected to Gmail API for {self.email}")
            return True
            
        except Exception as e:
            self.error_message = f"Failed to connect to Gmail API: {str(e)}"
            self.logger.error(self.error_message)
            return False
    
    def disconnect(self):
        """Close connection (no-op for Gmail API)."""
        self.service = None
        self.logger.info("Disconnected from Gmail API")
    
    def is_connected(self) -> bool:
        """Check if connected to Gmail API.
        
        Returns:
            True if connected, False otherwise
        """
        return self.service is not None
    
    def get_service(self):
        """Get the Gmail API service object.
        
        Returns:
            Gmail API service or None if not connected
        """
        return self.service
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to Gmail API.
        
        Returns:
            True if reconnection successful, False otherwise
        """
        self.logger.info("Attempting to reconnect...")
        self.disconnect()
        return self.connect()
    
    def get_error_message(self) -> str:
        """Get error message from last operation.
        
        Returns:
            Error message string, empty if no error
        """
        return self.error_message or ""

