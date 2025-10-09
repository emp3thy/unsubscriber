"""Email parser for Email Unsubscriber

Transforms raw email data from IMAP into consistent, structured format.
Handles character encoding, multipart messages, and malformed emails gracefully.
"""

import email
from email.message import Message
from email.header import decode_header
from email.utils import parseaddr
from typing import Dict, List, Union
import logging
import re
from bs4 import BeautifulSoup


class EmailParser:
    """Parse raw email data into structured format.
    
    Extracts sender, subject, date, and body content while handling
    various character encodings and malformed emails.
    """
    
    def __init__(self):
        """Initialize email parser."""
        self.logger = logging.getLogger(__name__)
    
    def parse_email(self, raw_email: Union[bytes, Dict]) -> Dict:
        """Parse raw email data into structured format.
        
        Args:
            raw_email: Raw email data as bytes (IMAP) or dict (Gmail API)
            
        Returns:
            Dictionary with keys: sender, subject, date, body_text, body_html
        """
        try:
            # Handle Gmail API dict format
            if isinstance(raw_email, dict):
                # Parse List-Unsubscribe header into unsubscribe_links list
                list_unsub_header = raw_email.get('list_unsubscribe', '')
                unsubscribe_links = self._parse_list_unsubscribe_header(list_unsub_header)
                
                return {
                    'sender': raw_email.get('sender', ''),
                    'sender_name': raw_email.get('sender_name', ''),
                    'subject': raw_email.get('subject', ''),
                    'date': raw_email.get('date', ''),
                    'body_text': '',  # Gmail API uses snippet initially
                    'body_html': '',
                    'snippet': raw_email.get('snippet', ''),
                    'message_id': raw_email.get('message_id', ''),
                    'unsubscribe_links': unsubscribe_links,
                    'is_unread': raw_email.get('is_unread', False)
                }
            
            # Handle IMAP bytes format
            msg = email.message_from_bytes(raw_email)
            
            return {
                'sender': self._extract_sender(msg),
                'subject': self._extract_subject(msg),
                'date': self._extract_date(msg),
                'body_text': self._extract_body(msg).get('text', ''),
                'body_html': self._extract_body(msg).get('html', '')
            }
        except Exception as e:
            self.logger.error(f"Error parsing email: {e}")
            return {
                'sender': '',
                'subject': '',
                'date': '',
                'body_text': '',
                'body_html': ''
            }
    
    def _extract_sender(self, msg: Message) -> str:
        """Extract sender email address from From header.
        
        Args:
            msg: Email message object
            
        Returns:
            Sender email address
        """
        from_header = msg.get('From', '')
        name, email_addr = parseaddr(from_header)
        return email_addr
    
    def _extract_subject(self, msg: Message) -> str:
        """Extract and decode subject line.
        
        Args:
            msg: Email message object
            
        Returns:
            Decoded subject string
        """
        subject = msg.get('Subject', '')
        return self._decode_header_value(subject)
    
    def _extract_date(self, msg: Message) -> str:
        """Extract date header.
        
        Args:
            msg: Email message object
            
        Returns:
            Date string
        """
        return msg.get('Date', '')
    
    def _extract_body(self, msg: Message) -> Dict[str, str]:
        """Extract text and HTML body parts.
        
        Args:
            msg: Email message object
            
        Returns:
            Dictionary with 'text' and 'html' keys
        """
        body_text = ''
        body_html = ''
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' and not body_text:
                    body_text = self._decode_payload(part)
                elif content_type == 'text/html' and not body_html:
                    body_html = self._decode_payload(part)
        else:
            content_type = msg.get_content_type()
            if content_type == 'text/plain':
                body_text = self._decode_payload(msg)
            elif content_type == 'text/html':
                body_html = self._decode_payload(msg)
        
        return {'text': body_text, 'html': body_html}
    
    def _decode_payload(self, part: Message) -> str:
        """Decode email part payload.
        
        Args:
            part: Email message part
            
        Returns:
            Decoded payload string
        """
        try:
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or 'utf-8'
                return payload.decode(charset, errors='ignore')
        except Exception as e:
            self.logger.warning(f"Error decoding payload: {e}")
        return ''
    
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
        except Exception as e:
            self.logger.warning(f"Error decoding header: {e}")
            return header
    
    def detect_unsubscribe_links(self, email_data: Dict) -> List[str]:
        """Detect unsubscribe links using multiple strategies.
        
        Uses three detection strategies:
        1. List-Unsubscribe header (RFC 2369)
        2. HTML body parsing with BeautifulSoup
        3. Plain text regex matching
        
        Args:
            email_data: Dictionary with email data (headers and body)
            
        Returns:
            List of unique unsubscribe URLs (up to 5)
        """
        links = []
        
        # Strategy 1: List-Unsubscribe header
        links.extend(self._extract_from_header(email_data))
        
        # Strategy 2: HTML body
        if email_data.get('body_html'):
            links.extend(self._extract_from_html(email_data['body_html']))
        
        # Strategy 3: Plain text regex
        if email_data.get('body_text'):
            links.extend(self._extract_from_text(email_data['body_text']))
        
        # Remove duplicates and return up to 5
        unique_links = list(set(links))
        self.logger.info(f"Found {len(unique_links)} unsubscribe links")
        return unique_links[:5]
    
    def _extract_from_header(self, email_data: Dict) -> List[str]:
        """Extract links from List-Unsubscribe header.
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            List of URLs from header
        """
        links = []
        header = email_data.get('list_unsubscribe', '')
        if header:
            # Extract URLs from <url> format
            found = re.findall(r'<(.*?)>', header)
            links.extend(found)
        return links
    
    def _extract_from_html(self, html: str) -> List[str]:
        """Extract unsubscribe links from HTML body.
        
        Args:
            html: HTML body content
            
        Returns:
            List of unsubscribe URLs found in HTML
        """
        links = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            keywords = ['unsubscribe', 'opt-out', 'opt out', 'remove', 
                       'stop receiving', 'cancel subscription']
            
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                text = link.get_text().lower()
                
                # Check if keyword in URL or text
                if any(kw in href or kw in text for kw in keywords):
                    links.append(link['href'])
        except Exception as e:
            self.logger.warning(f"Error parsing HTML: {e}")
        return links
    
    def _extract_from_text(self, text: str) -> List[str]:
        """Extract unsubscribe links from plain text using regex.
        
        Args:
            text: Plain text body content
            
        Returns:
            List of unsubscribe URLs found in text
        """
        links = []
        
        # HTTP/HTTPS URLs with unsubscribe keywords
        url_pattern = r'https?://[^\s<>"]+(?:unsubscribe|opt-out|optout|remove|stop)[^\s<>"]*'
        links.extend(re.findall(url_pattern, text, re.IGNORECASE))
        
        # mailto: links with unsubscribe keywords
        mailto_pattern = r'mailto:[^\s<>"]+(?:unsubscribe|opt-out|remove)[^\s<>"]*'
        links.extend(re.findall(mailto_pattern, text, re.IGNORECASE))
        
        return links
    
    def _parse_list_unsubscribe_header(self, header_value: str) -> List[str]:
        """Parse List-Unsubscribe header into list of URLs.
        
        The List-Unsubscribe header format is: <url1>, <url2>
        Example: <mailto:unsub@example.com>, <https://example.com/unsub>
        
        Args:
            header_value: Raw List-Unsubscribe header value
            
        Returns:
            List of unsubscribe URLs (http/https/mailto)
        """
        if not header_value:
            return []
        
        links = []
        # Extract URLs from angle brackets: <url>
        url_pattern = r'<([^>]+)>'
        matches = re.findall(url_pattern, header_value)
        
        for url in matches:
            url = url.strip()
            # Only include http/https/mailto URLs
            if url.startswith(('http://', 'https://', 'mailto:')):
                links.append(url)
        
        return links

