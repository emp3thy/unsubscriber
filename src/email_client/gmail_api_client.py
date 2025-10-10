"""
Gmail API client for accessing Gmail accounts.

This client uses Google's official Gmail API instead of IMAP, providing
better reliability and avoiding OAuth2 IMAP authentication issues.
"""

import logging
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
from email.utils import parsedate_to_datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


class GmailAPIClient:
    """Gmail API client that mimics IMAP client interface."""

    def __init__(self, email: str, oauth_manager):
        """Initialize Gmail API client.

        Args:
            email: Gmail address
            oauth_manager: OAuthCredentialManager instance for token handling
        """
        self.email = email
        self.oauth_manager = oauth_manager
        self.service = None
        self.provider = 'gmail'
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
        """Check if connected to Gmail API."""
        return self.service is not None

    def get_error_message(self) -> str:
        """Get error message from last operation."""
        return self.error_message or ""

    def get_email_count(self) -> int:
        """Get total number of emails in mailbox."""
        if not self.service:
            return 0

        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('messagesTotal', 0)
        except Exception as e:
            self.logger.error(f"Failed to get email count: {e}")
            return 0

    def fetch_email_ids(self, limit: int = 250) -> List[str]:
        """Fetch recent email IDs.

        Args:
            limit: Maximum number of IDs to fetch

        Returns:
            List of Gmail message IDs
        """
        if not self.service:
            return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=limit
            ).execute()

            messages = results.get('messages', [])
            return [msg['id'] for msg in messages]

        except Exception as e:
            self.logger.error(f"Failed to fetch email IDs: {e}")
            return []

    def fetch_headers(self, message_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch email headers for given message IDs.

        Args:
            message_ids: List of Gmail message IDs

        Returns:
            List of email dictionaries with header information
        """
        if not self.service:
            return []

        emails = []
        for msg_id in message_ids:
            try:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date', 'List-Unsubscribe']
                ).execute()

                email_data = self._parse_message_headers(message)
                if email_data:
                    emails.append(email_data)

            except Exception as e:
                self.logger.warning(f"Failed to fetch message {msg_id}: {e}")
                continue

        return emails

    def _parse_message_headers(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Gmail API message into email dictionary.

        Args:
            message: Gmail API message object

        Returns:
            Email dictionary or None if parsing failed
        """
        try:
            headers = message.get('payload', {}).get('headers', [])
            email_data = {'message_id': message['id']}

            # Extract headers
            for header in headers:
                name = header['name'].lower()
                value = header['value']

                if name == 'from':
                    # Parse sender email from "Name <email@domain.com>" format
                    if '<' in value and '>' in value:
                        email_data['sender'] = value.split('<')[1].split('>')[0]
                        email_data['sender_name'] = value.split('<')[0].strip().strip('"')
                    else:
                        email_data['sender'] = value
                        email_data['sender_name'] = value
                elif name == 'subject':
                    email_data['subject'] = value
                elif name == 'date':
                    email_data['date'] = value
                    try:
                        email_data['date_obj'] = parsedate_to_datetime(value)
                    except:
                        email_data['date_obj'] = datetime.now()
                elif name == 'list-unsubscribe':
                    email_data['list_unsubscribe'] = value

            # Get snippet
            email_data['snippet'] = message.get('snippet', '')

            # Check labels for unread status
            labels = message.get('labelIds', [])
            email_data['is_unread'] = 'UNREAD' in labels

            return email_data

        except Exception as e:
            self.logger.warning(f"Failed to parse message: {e}")
            return None

    def get_email_body(self, message_id: str) -> Optional[Dict[str, str]]:
        """Get email body content.

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with 'text' and/or 'html' keys, or None if failed
        """
        if not self.service:
            return None

        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            return self._extract_body(message['payload'])

        except Exception as e:
            self.logger.error(f"Failed to get email body: {e}")
            return None

    def _extract_body(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """Extract text and HTML body from message payload."""
        body = {}

        if 'body' in payload and payload['body'].get('data'):
            # Simple message with body data
            content_type = payload.get('mimeType', '')
            decoded = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            
            if 'text/html' in content_type:
                body['html'] = decoded
            else:
                body['text'] = decoded

        elif 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                
                if mime_type == 'text/plain' and part.get('body', {}).get('data'):
                    body['text'] = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                elif mime_type == 'text/html' and part.get('body', {}).get('data'):
                    body['html'] = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                elif 'parts' in part:
                    # Nested parts
                    nested_body = self._extract_body(part)
                    body.update(nested_body)

        return body

    def mark_as_read(self, message_ids: List[str]) -> bool:
        """Mark emails as read.

        Args:
            message_ids: List of Gmail message IDs

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False

        try:
            for msg_id in message_ids:
                self.service.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()

            self.logger.info(f"Marked {len(message_ids)} emails as read")
            return True

        except Exception as e:
            self.error_message = f"Failed to mark emails as read: {str(e)}"
            self.logger.error(self.error_message)
            return False

    def delete_emails(self, message_ids: List[str]) -> bool:
        """Delete emails (move to trash).

        Args:
            message_ids: List of Gmail message IDs

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False

        try:
            for msg_id in message_ids:
                self.service.users().messages().trash(
                    userId='me',
                    id=msg_id
                ).execute()

            self.logger.info(f"Deleted {len(message_ids)} emails")
            return True

        except Exception as e:
            self.error_message = f"Failed to delete emails: {str(e)}"
            self.logger.error(self.error_message)
            return False

    def search_emails(self, query: str, limit: int = 250) -> List[str]:
        """Search for emails using Gmail query syntax.

        Args:
            query: Gmail search query (e.g., "from:example@email.com")
            limit: Maximum number of results

        Returns:
            List of message IDs matching the query
        """
        if not self.service:
            return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()

            messages = results.get('messages', [])
            return [msg['id'] for msg in messages]

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []

    def delete_emails_from_sender(self, sender_email: str, db_manager=None) -> tuple:
        """Delete all emails from a specific sender.
        
        This method searches for all emails from the specified sender,
        and moves them to trash.
        
        Args:
            sender_email: Email address of sender whose emails to delete
            db_manager: Optional DBManager for whitelist check (safety)
        
        Returns:
            Tuple of (count_deleted, message):
                - count_deleted: Number of emails deleted (0 if failed)
                - message: Descriptive result message
        """
        # Safety check: whitelist
        if db_manager and db_manager.check_whitelist(sender_email):
            message = f"Cannot delete: {sender_email} is whitelisted"
            self.logger.warning(message)
            return (0, message)
        
        try:
            # Search for all emails from this sender
            self.logger.info(f"Searching for emails from {sender_email}")
            query = f"from:{sender_email}"
            message_ids = self.search_emails(query, limit=1000)  # Get up to 1000 emails
            
            count = len(message_ids)
            
            if count == 0:
                message = f"No emails found from {sender_email}"
                self.logger.info(message)
                return (0, message)
            
            self.logger.info(f"Found {count} emails from {sender_email}, moving to trash")
            
            # Delete (trash) all emails
            success = self.delete_emails(message_ids)
            
            if success:
                message = f"Deleted {count} emails from {sender_email}"
                self.logger.info(message)
                return (count, message)
            else:
                message = f"Failed to delete emails from {sender_email}"
                self.logger.error(message)
                return (0, message)
            
        except Exception as e:
            message = f"Error deleting emails from {sender_email}: {str(e)}"
            self.logger.error(message)
            return (0, message)

