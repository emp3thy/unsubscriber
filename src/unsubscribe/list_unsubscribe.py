"""
List-Unsubscribe header strategy for unsubscribing from emails.

This module implements RFC 2369 List-Unsubscribe header processing,
which is the most reliable and standardized unsubscribe method.
"""
from src.unsubscribe.strategy_base import UnsubscribeStrategy
from typing import Dict, Tuple
import requests
import re
import logging


class ListUnsubscribeStrategy(UnsubscribeStrategy):
    """
    Strategy using RFC 2369 List-Unsubscribe header.
    
    This strategy looks for the List-Unsubscribe header in email headers
    and uses it to perform one-click unsubscribe via HTTP GET or POST.
    
    Supports:
    - HTTP/HTTPS URLs in List-Unsubscribe header
    - List-Unsubscribe-Post for one-click POST requests
    - Fallback to GET when Post header not present
    """
    
    def __init__(self):
        """Initialize List-Unsubscribe strategy."""
        super().__init__()
        self.timeout = 10
        self.headers = {'User-Agent': 'Mozilla/5.0 (Email Unsubscriber)'}
        self.max_redirects = 5
    
    def can_handle(self, email_data: Dict) -> bool:
        """
        Check if email has List-Unsubscribe header.
        
        Args:
            email_data: Email data dictionary
        
        Returns:
            True if List-Unsubscribe header present and not empty
        """
        header = email_data.get('list_unsubscribe', '')
        return bool(header and header.strip())
    
    def execute(self, email_data: Dict) -> Tuple[bool, str]:
        """
        Execute unsubscribe using List-Unsubscribe header.
        
        Args:
            email_data: Email data dictionary
        
        Returns:
            Tuple of (success, message)
        """
        header = email_data.get('list_unsubscribe', '')
        sender = email_data.get('sender', 'unknown')
        
        self._log_attempt(sender, 'List-Unsubscribe header')
        
        # Extract HTTP/HTTPS URLs from header
        # Format: <http://url1>, <http://url2> or <mailto:...>
        urls = re.findall(r'<(https?://[^>]+)>', header)
        
        if not urls:
            message = "No HTTP URLs found in List-Unsubscribe header"
            self._log_result(sender, False, message)
            return (False, message)
        
        # Use first HTTP URL
        url = urls[0]
        self.logger.info(f"Using List-Unsubscribe URL: {url}")
        
        try:
            # Check if List-Unsubscribe-Post header exists (RFC 8058)
            has_post = 'list_unsubscribe_post' in email_data
            
            if has_post:
                # Use POST with One-Click as per RFC 8058
                self.logger.info("List-Unsubscribe-Post header present, using POST")
                response = requests.post(
                    url,
                    data={'List-Unsubscribe': 'One-Click'},
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
            else:
                # Use GET (traditional method)
                self.logger.info("Using GET request for List-Unsubscribe")
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
            
            # Check response status
            if 200 <= response.status_code < 300:
                method = "POST" if has_post else "GET"
                message = f"Unsubscribed successfully via {method} (HTTP {response.status_code})"
                self._log_result(sender, True, message)
                return (True, message)
            else:
                message = f"Unsubscribe failed (HTTP {response.status_code})"
                self._log_result(sender, False, message)
                return (False, message)
        
        except requests.Timeout:
            message = "Unsubscribe request timed out"
            self._log_result(sender, False, message)
            return (False, message)
        
        except requests.TooManyRedirects:
            message = "Too many redirects during unsubscribe"
            self._log_result(sender, False, message)
            return (False, message)
        
        except requests.RequestException as e:
            error_msg = str(e)[:100]  # Limit error message length
            message = f"Network error: {error_msg}"
            self._log_result(sender, False, message)
            return (False, message)
        
        except Exception as e:
            error_msg = str(e)[:100]
            message = f"Unexpected error: {error_msg}"
            self.logger.error(f"Unexpected error in ListUnsubscribeStrategy: {e}")
            self._log_result(sender, False, message)
            return (False, message)

