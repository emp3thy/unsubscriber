"""
mailto: Link Strategy for Email Unsubscriber.

This module implements RFC 2369 mailto: unsubscribe handling by sending
unsubscribe emails via SMTP using the user's email account credentials.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse, parse_qs, unquote
from typing import Dict, Tuple, Optional
import re
import logging

from src.unsubscribe.strategy_base import UnsubscribeStrategy
from src.email_client.credentials import CredentialManager
from src.database.db_manager import DBManager


class MailtoStrategy(UnsubscribeStrategy):
    """
    Strategy using mailto: links in List-Unsubscribe headers.
    
    This strategy sends unsubscribe emails via SMTP when the email
    provider supports RFC 2369 mailto: unsubscribe links.
    
    Features:
    - Parses mailto: URLs from sample_links
    - Sends email via SMTP using user's account
    - Supports Gmail and Outlook SMTP servers
    - Handles subject and body parameters from mailto: URL
    """
    
    def __init__(self, db_manager: DBManager, cred_manager: CredentialManager = None):
        """Initialize mailto strategy.
        
        Args:
            db_manager: DBManager instance for account retrieval
            cred_manager: Optional CredentialManager (created if not provided)
        """
        super().__init__()
        self.db = db_manager
        self.cred = cred_manager or CredentialManager()
        self.timeout = 30  # SMTP timeout in seconds
        
        # SMTP server configurations
        self.smtp_servers = {
            'gmail': ('smtp.gmail.com', 587),
            'outlook': ('smtp.office365.com', 587)
        }
    
    def can_handle(self, email_data: Dict) -> bool:
        """
        Check if email has mailto: unsubscribe link.
        
        Args:
            email_data: Sender data dictionary
        
        Returns:
            True if mailto: link found in sample_links
        """
        # Check sample_links for mailto: URLs
        links = email_data.get('sample_links', [])
        for link in links:
            if link.lower().startswith('mailto:'):
                return True
        return False
    
    def execute(self, email_data: Dict) -> Tuple[bool, str]:
        """
        Execute unsubscribe by sending email via SMTP.
        
        Args:
            email_data: Sender data dictionary
        
        Returns:
            Tuple of (success, message)
        """
        sender = email_data.get('sender', 'unknown')
        self._log_attempt(sender, 'mailto Strategy')
        
        # Find mailto: link
        mailto_link = None
        links = email_data.get('sample_links', [])
        for link in links:
            if link.lower().startswith('mailto:'):
                mailto_link = link
                break
        
        if not mailto_link:
            message = "No mailto: link found"
            self._log_result(sender, False, message)
            return (False, message)
        
        self.logger.info(f"Found mailto: link: {mailto_link[:80]}")
        
        try:
            # Parse mailto: URL
            recipient, subject, body = self._parse_mailto(mailto_link)
            if not recipient:
                message = "Failed to parse mailto: link - no recipient"
                self._log_result(sender, False, message)
                return (False, message)
            
            self.logger.info(f"Mailto recipient: {recipient}")
            self.logger.debug(f"Subject: {subject}, Body length: {len(body)}")
            
            # Get user's email account
            account = self._get_primary_account()
            if not account:
                message = "No email account configured"
                self._log_result(sender, False, message)
                return (False, message)
            
            # Send unsubscribe email
            success, send_message = self._send_unsubscribe_email(
                account,
                recipient,
                subject,
                body
            )
            
            if success:
                message = f"Unsubscribe email sent to {recipient}"
                self._log_result(sender, True, message)
                return (True, message)
            else:
                self._log_result(sender, False, send_message)
                return (False, send_message)
        
        except Exception as e:
            error_msg = str(e)[:100]
            message = f"Error sending unsubscribe email: {error_msg}"
            self.logger.error(f"Unexpected error in MailtoStrategy: {e}")
            self._log_result(sender, False, message)
            return (False, message)
    
    def _parse_mailto(self, mailto_url: str) -> Tuple[Optional[str], str, str]:
        """
        Parse mailto: URL to extract recipient, subject, and body.
        
        Args:
            mailto_url: mailto: URL string
        
        Returns:
            Tuple of (recipient, subject, body)
        """
        try:
            # Remove 'mailto:' prefix
            if mailto_url.lower().startswith('mailto:'):
                mailto_url = mailto_url[7:]
            
            # Split recipient from parameters
            if '?' in mailto_url:
                recipient, params_str = mailto_url.split('?', 1)
            else:
                recipient = mailto_url
                params_str = ''
            
            recipient = unquote(recipient.strip())
            
            # Parse parameters
            subject = ''
            body = ''
            
            if params_str:
                # Parse key=value pairs
                params = parse_qs(params_str)
                
                # Extract subject (can be 'subject' or 'Subject')
                for key in ['subject', 'Subject', 'SUBJECT']:
                    if key in params and params[key]:
                        subject = unquote(params[key][0])
                        break
                
                # Extract body (can be 'body' or 'Body')
                for key in ['body', 'Body', 'BODY']:
                    if key in params and params[key]:
                        body = unquote(params[key][0])
                        break
            
            # Default subject if not provided
            if not subject:
                subject = 'Unsubscribe'
            
            # Default body if not provided
            if not body:
                body = 'Please unsubscribe me from this mailing list.'
            
            return (recipient, subject, body)
        
        except Exception as e:
            self.logger.error(f"Error parsing mailto URL: {e}")
            return (None, '', '')
    
    def _get_primary_account(self) -> Optional[Dict]:
        """
        Get the primary email account from database.
        
        Returns:
            Account dictionary or None if no accounts
        """
        try:
            accounts = self.db.list_accounts()
            if accounts:
                return accounts[0]  # Return first account as primary
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving account: {e}")
            return None
    
    def _send_unsubscribe_email(self, account: Dict, recipient: str, 
                                 subject: str, body: str) -> Tuple[bool, str]:
        """
        Send unsubscribe email via SMTP.
        
        Args:
            account: Account dictionary with email, encrypted_password, provider
            recipient: Unsubscribe email recipient
            subject: Email subject
            body: Email body
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Decrypt password
            password = self.cred.decrypt_password(account['encrypted_password'])
            email_address = account['email']
            provider = account['provider'].lower()
            
            # Get SMTP server
            if provider not in self.smtp_servers:
                return (False, f"Unsupported provider: {provider}")
            
            smtp_host, smtp_port = self.smtp_servers[provider]
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = email_address
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email via SMTP
            self.logger.info(f"Connecting to SMTP: {smtp_host}:{smtp_port}")
            with smtplib.SMTP(smtp_host, smtp_port, timeout=self.timeout) as server:
                server.starttls()
                self.logger.debug(f"Logging in as {email_address}")
                server.login(email_address, password)
                self.logger.debug(f"Sending email to {recipient}")
                server.send_message(msg)
            
            self.logger.info(f"Successfully sent unsubscribe email to {recipient}")
            return (True, f"Email sent to {recipient}")
        
        except smtplib.SMTPAuthenticationError as e:
            message = f"SMTP authentication failed: {str(e)[:50]}"
            self.logger.error(message)
            return (False, message)
        
        except smtplib.SMTPException as e:
            message = f"SMTP error: {str(e)[:50]}"
            self.logger.error(message)
            return (False, message)
        
        except Exception as e:
            message = f"Error sending email: {str(e)[:50]}"
            self.logger.error(f"Unexpected error in _send_unsubscribe_email: {e}")
            return (False, message)

