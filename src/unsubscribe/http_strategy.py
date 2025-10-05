"""
Direct HTTP GET/POST strategy for unsubscribing from emails.

This module implements unsubscribe functionality for links found in email
bodies, trying GET first and then POST if needed.
"""
from src.unsubscribe.strategy_base import UnsubscribeStrategy
from typing import Dict, Tuple
import requests
import logging
import time
import random
import re


class HTTPStrategy(UnsubscribeStrategy):
    """
    Strategy using direct HTTP GET/POST to unsubscribe links.
    
    This strategy handles unsubscribe links found in email bodies (HTML or text).
    It tries GET first (most common), then POST if GET returns 405 Method Not Allowed.
    
    Features:
    - Tries up to 3 links from the email
    - GET-then-POST fallback for each link
    - Session support for cookie requirements
    - Stops on first successful link
    - Retry logic with exponential backoff
    - Email address parameter injection
    - User-agent rotation
    - Enhanced success detection
    """
    
    def __init__(self):
        """Initialize HTTP strategy."""
        super().__init__()
        self.timeout = 15  # Longer timeout for page loading
        self.max_links = 3
        self.max_redirects = 5
        self.max_retries = 3
        
        # User-agent rotation to avoid bot detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0'
        ]
        
        # Success keywords in response
        self.success_keywords = [
            'success', 'unsubscribed', 'removed', 'opt-out', 'opted out',
            'no longer receive', 'preferences updated', 'subscription cancelled',
            'successfully removed', 'been removed', 'confirmation'
        ]
    
    def can_handle(self, email_data: Dict) -> bool:
        """
        Check if email has unsubscribe links.
        
        Args:
            email_data: Email data dictionary
        
        Returns:
            True if sample_links list present and not empty with HTTP URLs
        """
        # Check both sample_links (from EmailGrouper) and unsubscribe_links
        links = email_data.get('sample_links', []) or email_data.get('unsubscribe_links', [])
        # Filter for HTTP/HTTPS links only (not mailto:)
        http_links = [link for link in links if link.lower().startswith(('http://', 'https://'))]
        return len(http_links) > 0
    
    def execute(self, email_data: Dict) -> Tuple[bool, str]:
        """
        Execute unsubscribe using HTTP requests to unsubscribe links.
        
        Tries each link in order until one succeeds, up to max_links.
        For each link, tries GET first, then POST if GET returns 405.
        Includes retry logic with exponential backoff and email injection.
        
        Args:
            email_data: Email data dictionary
        
        Returns:
            Tuple of (success, message)
        """
        # Get links from sample_links or unsubscribe_links
        links = email_data.get('sample_links', []) or email_data.get('unsubscribe_links', [])
        # Filter for HTTP/HTTPS links only
        links = [link for link in links if link.lower().startswith(('http://', 'https://'))]
        sender = email_data.get('sender', 'unknown')
        
        self._log_attempt(sender, 'HTTP Strategy')
        
        if not links:
            message = "No HTTP unsubscribe links found"
            self._log_result(sender, False, message)
            return (False, message)
        
        # Inject email address into URLs if needed
        injected_links = [self._inject_email(link, sender) for link in links]
        
        # Try up to max_links
        links_to_try = injected_links[:self.max_links]
        self.logger.info(f"Found {len(links)} link(s), trying first {len(links_to_try)}")
        
        for i, url in enumerate(links_to_try):
            self.logger.info(f"Trying link {i+1}/{len(links_to_try)}: {url[:80]}...")
            
            success, message = self._try_url_with_retry(url, sender)
            if success:
                self._log_result(sender, True, message)
                return (True, message)
            else:
                self.logger.debug(f"Link {i+1} failed: {message}")
        
        # All links failed
        message = f"All {len(links_to_try)} unsubscribe link(s) failed"
        self._log_result(sender, False, message)
        return (False, message)
    
    def _inject_email(self, url: str, email: str) -> str:
        """
        Inject email address into URL parameters if placeholders found.
        
        Args:
            url: Original URL
            email: Email address to inject
        
        Returns:
            URL with email injected
        """
        # Check for common email placeholders
        placeholders = ['{EMAIL_ADDRESS}', '{EMAIL}', '{EMAILADDRESS}', 
                       '%7BEMAIL_ADDRESS%7D', '%7BEMAIL%7D']
        
        for placeholder in placeholders:
            if placeholder in url.upper():
                # Replace placeholder (case-insensitive)
                pattern = re.compile(re.escape(placeholder), re.IGNORECASE)
                url = pattern.sub(email, url)
                self.logger.debug(f"Injected email into URL placeholder")
                return url
        
        # If no placeholder but URL has email parameter without value, add it
        if '?email=' in url.lower() or '&email=' in url.lower():
            if '=&' in url or url.endswith('='):
                url = url.replace('=&', f'={email}&').replace('email=', f'email={email}')
                self.logger.debug(f"Added email to empty parameter")
                return url
        
        # If no email parameter at all, try adding it
        if 'unsubscribe' in url.lower():
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}email={email}"
            self.logger.debug(f"Appended email parameter to URL")
        
        return url
    
    def _try_url_with_retry(self, url: str, sender: str) -> Tuple[bool, str]:
        """
        Try URL with retry logic and exponential backoff.
        
        Args:
            url: URL to try
            sender: Sender email for POST data
        
        Returns:
            Tuple of (success, message)
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                success, message = self._try_url(url, sender)
                
                # If successful, return immediately
                if success:
                    return (True, message)
                
                # Check if we should retry (5xx errors, timeouts)
                should_retry = (
                    'HTTP 5' in message or
                    'timed out' in message.lower() or
                    'connection' in message.lower()
                )
                
                if not should_retry or attempt == self.max_retries - 1:
                    return (False, message)
                
                # Exponential backoff with jitter: 2s, 4s, 8s
                delay = (2 ** attempt) + random.uniform(0, 1)
                self.logger.info(f"Retrying in {delay:.1f}s (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(delay)
                
                last_error = message
            
            except Exception as e:
                last_error = str(e)[:50]
                if attempt < self.max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    self.logger.warning(f"Error on attempt {attempt + 1}, retrying in {delay:.1f}s: {last_error}")
                    time.sleep(delay)
                else:
                    return (False, f"Failed after {self.max_retries} attempts: {last_error}")
        
        return (False, f"Failed after {self.max_retries} attempts: {last_error}")
    
    def _try_url(self, url: str, sender: str = None) -> Tuple[bool, str]:
        """
        Try a single URL with GET, then POST if needed.
        
        Args:
            url: URL to try
            sender: Optional sender email for POST data
        
        Returns:
            Tuple of (success, message)
        """
        session = requests.Session()
        
        # Rotate user agent
        headers = {
            'User-Agent': random.choice(self.user_agents)
        }
        
        try:
            # Try GET first (most common method)
            self.logger.debug(f"Attempting GET request to {url[:80]}")
            response = session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
                max_redirects=self.max_redirects
            )
            
            # Check if successful (by status code or content)
            if self._is_success_response(response):
                return (True, f"Unsubscribed via GET (HTTP {response.status_code})")
            
            # If Method Not Allowed, try POST
            if response.status_code == 405:
                self.logger.info(f"GET returned 405, trying POST")
                
                # Try POST with form data first
                if sender:
                    response = session.post(
                        url,
                        data={'email': sender},
                        headers=headers,
                        timeout=self.timeout,
                        allow_redirects=True,
                        max_redirects=self.max_redirects
                    )
                    
                    if self._is_success_response(response):
                        return (True, f"Unsubscribed via POST with form data (HTTP {response.status_code})")
                    
                    # Try POST with JSON
                    headers['Content-Type'] = 'application/json'
                    response = session.post(
                        url,
                        json={'email': sender},
                        headers=headers,
                        timeout=self.timeout,
                        allow_redirects=True,
                        max_redirects=self.max_redirects
                    )
                    
                    if self._is_success_response(response):
                        return (True, f"Unsubscribed via POST with JSON (HTTP {response.status_code})")
                else:
                    # Try POST without data
                    response = session.post(
                        url,
                        headers=headers,
                        timeout=self.timeout,
                        allow_redirects=True,
                        max_redirects=self.max_redirects
                    )
                    
                    if self._is_success_response(response):
                        return (True, f"Unsubscribed via POST (HTTP {response.status_code})")
                
                return (False, f"POST returned HTTP {response.status_code}")
            
            # Other non-success status
            return (False, f"HTTP {response.status_code}")
        
        except requests.Timeout:
            return (False, "Request timed out")
        
        except requests.TooManyRedirects:
            return (False, "Too many redirects")
        
        except requests.RequestException as e:
            error_msg = str(e)[:50]  # Limit error message length
            return (False, f"Network error: {error_msg}")
        
        except Exception as e:
            error_msg = str(e)[:50]
            self.logger.error(f"Unexpected error in HTTPStrategy._try_url: {e}")
            return (False, f"Unexpected error: {error_msg}")
        
        finally:
            session.close()
    
    def _is_success_response(self, response: requests.Response) -> bool:
        """
        Determine if response indicates successful unsubscribe.
        
        Args:
            response: HTTP response object
        
        Returns:
            True if response indicates success
        """
        # Check status code
        if 200 <= response.status_code < 300:
            # Additional check: look for success keywords in response
            try:
                response_text = response.text.lower()
                if any(keyword in response_text for keyword in self.success_keywords):
                    self.logger.debug(f"Success keyword found in response")
                    return True
                # If no keywords, assume 2xx is success
                return True
            except:
                # If can't read response text, trust the status code
                return True
        
        return False

