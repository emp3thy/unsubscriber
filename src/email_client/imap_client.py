"""IMAP client for Email Unsubscriber

Provides IMAP connectivity for Gmail and Outlook with automatic provider
detection and secure SSL/TLS connections. Uses pluggable authentication
strategies for different providers and authentication methods.
"""

import imaplib
import socket
import logging
import email
from email.header import decode_header
from typing import Optional, List, Dict, Tuple
from .auth.auth_strategy import IMAPAuthStrategy
from .imap_connection import IMAPConnectionManager
from .email_client_interface import EmailClientInterface


class IMAPClient(EmailClientInterface):
    """IMAP client for Gmail and Outlook.
    
    Handles email operations using a pluggable connection manager.
    The connection manager handles authentication and connection lifecycle.
    Implements EmailClientInterface for polymorphic usage.
    """
    
    def __init__(self, email: str, auth_strategy: IMAPAuthStrategy = None, 
                 provider: str = None, connection_manager: IMAPConnectionManager = None):
        """Initialize IMAP client.
        
        Args:
            email: Email address for authentication
            auth_strategy: Authentication strategy (required if connection_manager not provided)
            provider: Email provider ('gmail' or 'outlook'), auto-detected if None
            connection_manager: Optional pre-configured connection manager
            
        Raises:
            ValueError: If neither auth_strategy nor connection_manager is provided
        """
        self.email = email
        self.logger = logging.getLogger(__name__)
        
        # Use provided connection manager or create one
        if connection_manager:
            self.connection_manager = connection_manager
        elif auth_strategy:
            self.connection_manager = IMAPConnectionManager(email, auth_strategy, provider)
        else:
            raise ValueError("Either auth_strategy or connection_manager must be provided")
        
        # Maintain backward compatibility
        self.auth_strategy = auth_strategy or (
            connection_manager.auth_strategy if connection_manager else None
        )
        self.provider = self.connection_manager.provider
        self.imap = None
    
    def connect(self) -> bool:
        """Connect to IMAP server and authenticate using the connection manager.
        
        Returns:
            True if connection successful, False otherwise
        """
        success = self.connection_manager.connect()
        if success:
            self.imap = self.connection_manager.get_connection()
        return success
    
    def disconnect(self):
        """Close IMAP connection."""
        self.connection_manager.disconnect()
        self.imap = None
    
    def is_connected(self) -> bool:
        """Check if connected to IMAP server.

        Returns:
            True if connected, False otherwise
        """
        return self.connection_manager.is_connected()

    def get_error_message(self) -> str:
        """Get the last error message from authentication attempt.

        Returns:
            Error message string, empty if no error
        """
        return self.connection_manager.get_error_message()
    
    def get_email_count(self) -> int:
        """Get total number of emails in INBOX.
        
        Returns:
            Email count, 0 on error
        """
        try:
            status, messages = self.imap.select('INBOX', readonly=True)
            if status == 'OK':
                count = int(messages[0].decode('utf-8'))
                self.logger.info(f"Found {count} emails in INBOX")
                return count
            return 0
        except Exception as e:
            self.logger.error(f"Error getting email count: {e}")
            return 0
    
    def fetch_email_ids(self, batch_size: int = 500) -> List[bytes]:
        """Fetch all message IDs, limited by batch size.
        
        Args:
            batch_size: Maximum number of IDs to fetch (default: 500)
            
        Returns:
            List of message IDs as bytes
        """
        try:
            status, messages = self.imap.search(None, 'ALL')
            if status == 'OK':
                ids = messages[0].split()
                # Return up to batch_size IDs
                result = ids[:batch_size] if batch_size else ids
                self.logger.info(f"Fetched {len(result)} email IDs")
                return result
            return []
        except Exception as e:
            self.logger.error(f"Error fetching email IDs: {e}")
            return []
    
    def fetch_headers(self, message_ids: List[bytes]) -> List[Dict]:
        """Fetch headers for a batch of message IDs.
        
        Args:
            message_ids: List of message IDs to fetch
            
        Returns:
            List of header dictionaries with keys: id, from, subject, date, is_read
        """
        headers = []
        for msg_id in message_ids:
            try:
                status, data = self.imap.fetch(msg_id, '(RFC822.HEADER FLAGS)')
                if status != 'OK':
                    continue
                
                # Parse headers
                header_data = data[0][1]
                flags_data = data[1] if len(data) > 1 else b''
                flags = flags_data.decode('utf-8', errors='ignore') if flags_data else ''
                msg = email.message_from_bytes(header_data)
                
                # Extract and decode headers
                from_header = self._decode_header_value(msg.get('From', ''))
                subject = self._decode_header_value(msg.get('Subject', ''))
                date = msg.get('Date', '')
                is_read = '\\Seen' in flags
                
                headers.append({
                    'id': msg_id.decode('utf-8'),
                    'from': from_header,
                    'subject': subject,
                    'date': date,
                    'is_read': is_read
                })
            except Exception as e:
                self.logger.warning(f"Error parsing email {msg_id}: {e}")
                continue
        
        self.logger.info(f"Fetched {len(headers)} email headers")
        return headers
    
    def fetch_body(self, message_id: bytes) -> Dict:
        """Fetch email body.
        
        Args:
            message_id: Message ID to fetch
            
        Returns:
            Dictionary with keys: id, body_text, body_html
        """
        try:
            # Use BODY.PEEK to avoid marking as read
            status, data = self.imap.fetch(message_id, '(BODY.PEEK[TEXT])')
            if status != 'OK':
                return {'id': message_id.decode('utf-8'), 'body_text': '', 'body_html': ''}
            
            # Extract body content
            body_data = data[0][1] if data and data[0] and len(data[0]) > 1 else b''
            
            # Decode body (try common encodings)
            body_text = ''
            for encoding in ['utf-8', 'iso-8859-1', 'windows-1252']:
                try:
                    body_text = body_data.decode(encoding, errors='ignore')
                    break
                except:
                    continue
            
            return {
                'id': message_id.decode('utf-8'),
                'body_text': body_text,
                'body_html': ''  # HTML parsing done in email_parser
            }
        except Exception as e:
            self.logger.error(f"Error fetching body for {message_id}: {e}")
            return {'id': message_id.decode('utf-8'), 'body_text': '', 'body_html': ''}
    
    def _decode_header_value(self, header: str) -> str:
        """Decode email header handling various encodings.
        
        Args:
            header: Header string to decode
            
        Returns:
            Decoded header string
        """
        try:
            decoded_parts = decode_header(header)
            result = []
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    result.append(part.decode(encoding or 'utf-8', errors='ignore'))
                else:
                    result.append(part)
            return ''.join(result)
        except Exception:
            return header
    
    def delete_emails_from_sender(self, sender_email: str, db_manager=None) -> Tuple[int, str]:
        """Delete all emails from a specific sender.
        
        This method searches for all emails from the specified sender,
        marks them with the \\Deleted flag, and then expunges them
        to permanently remove them from the mailbox.
        
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
            # Select inbox (read-write mode)
            status, data = self.imap.select('INBOX')
            if status != 'OK':
                message = "Failed to select INBOX"
                self.logger.error(message)
                return (0, message)
            
            # Search for emails from sender
            self.logger.info(f"Searching for emails from {sender_email}")
            message_ids = self._search_by_sender(sender_email)
            
            count = len(message_ids)
            
            if count == 0:
                message = f"No emails found from {sender_email}"
                self.logger.info(message)
                return (0, message)
            
            self.logger.info(f"Found {count} emails from {sender_email}, marking for deletion")
            
            # Mark all for deletion
            self._mark_deleted(message_ids)
            
            # Permanently delete
            self._expunge()
            
            message = f"Deleted {count} emails from {sender_email}"
            self.logger.info(message)
            return (count, message)
        
        except imaplib.IMAP4.error as e:
            message = f"IMAP error during deletion: {str(e)}"
            self.logger.error(message)
            return (0, message)
        except Exception as e:
            message = f"Unexpected error during deletion: {str(e)}"
            self.logger.error(message)
            return (0, message)
    
    def _search_by_sender(self, sender: str) -> List[bytes]:
        """Find all email IDs from a specific sender.
        
        Args:
            sender: Email address to search for
            
        Returns:
            List of message IDs as bytes
            
        Raises:
            imaplib.IMAP4.error: If IMAP search fails
        """
        status, data = self.imap.search(None, f'FROM "{sender}"')
        
        if status != 'OK':
            self.logger.error(f"Search failed for sender: {sender}")
            return []
        
        message_ids = data[0].split()
        return message_ids
    
    def _mark_deleted(self, message_ids: List[bytes]):
        """Mark emails with \\Deleted flag.
        
        Args:
            message_ids: List of message IDs to mark
            
        Raises:
            imaplib.IMAP4.error: If IMAP store operation fails
        """
        for msg_id in message_ids:
            self.imap.store(msg_id, '+FLAGS', '\\Deleted')
        
        self.logger.debug(f"Marked {len(message_ids)} emails for deletion")
    
    def _expunge(self):
        """Permanently delete all emails marked with \\Deleted flag.
        
        This operation cannot be undone.
        
        Raises:
            imaplib.IMAP4.error: If IMAP expunge operation fails
        """
        self.imap.expunge()
        self.logger.debug("Expunged deleted emails")

