"""
Rate Limiter for Email Unsubscriber.

This module implements rate limiting and concurrency control to prevent
abuse, respect server limits, and avoid being flagged as a bot.
"""
import threading
import time
import random
from contextlib import contextmanager
import logging


class RateLimiter:
    """
    Rate limiter with concurrency control and exponential backoff.
    
    Features:
    - Limits concurrent operations using semaphore
    - Adds random delays between requests
    - Handles 429 Too Many Requests responses
    - Implements exponential backoff
    - Thread-safe implementation
    """
    
    def __init__(self, max_concurrent: int = 3, min_delay: float = 2.0, 
                 max_delay: float = 5.0):
        """
        Initialize rate limiter.
        
        Args:
            max_concurrent: Maximum number of concurrent operations
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
        """
        self.semaphore = threading.Semaphore(max_concurrent)
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.logger = logging.getLogger(__name__)
        self.last_request_time = 0
        self.lock = threading.Lock()
        self.max_concurrent = max_concurrent
        
        self.logger.info(f"RateLimiter initialized: max_concurrent={max_concurrent}, "
                        f"delay={min_delay}-{max_delay}s")
    
    @contextmanager
    def acquire(self):
        """
        Acquire rate limiter, add delay, then release.
        
        This context manager ensures:
        - Only max_concurrent operations run simultaneously
        - Minimum delay between consecutive requests
        - Thread-safe operation
        
        Usage:
            with rate_limiter.acquire():
                # Perform rate-limited operation
                make_request()
        
        Yields:
            None
        """
        # Acquire semaphore (blocks if max_concurrent reached)
        acquired = self.semaphore.acquire(blocking=True)
        if not acquired:
            self.logger.warning("Failed to acquire semaphore")
            return
        
        try:
            # Add delay since last request (thread-safe)
            with self.lock:
                now = time.time()
                elapsed = now - self.last_request_time
                
                # Calculate required delay with random jitter
                delay = random.uniform(self.min_delay, self.max_delay)
                
                # If not enough time has passed, sleep for remaining time
                if elapsed < delay:
                    sleep_time = delay - elapsed
                    self.logger.debug(f"Rate limiting: sleeping {sleep_time:.1f}s")
                    time.sleep(sleep_time)
                
                # Update last request time
                self.last_request_time = time.time()
            
            yield
        
        finally:
            # Always release semaphore
            self.semaphore.release()
    
    def handle_429(self, retry_after: str = None) -> float:
        """
        Handle 429 Too Many Requests response.
        
        Args:
            retry_after: Optional Retry-After header value (seconds)
        
        Returns:
            Wait time in seconds
        """
        # Parse Retry-After header if provided
        if retry_after:
            try:
                wait_time = int(retry_after)
                self.logger.warning(f"Rate limited (429). Retry-After: {wait_time}s")
            except ValueError:
                # If not an integer, default to 30 seconds
                wait_time = 30
                self.logger.warning(f"Rate limited (429). Invalid Retry-After header, using {wait_time}s")
        else:
            # No Retry-After header, use default
            wait_time = 30
            self.logger.warning(f"Rate limited (429). No Retry-After header, using {wait_time}s")
        
        return wait_time
    
    def exponential_backoff(self, attempt: int, base_delay: float = 30.0, 
                           max_delay: float = 240.0) -> float:
        """
        Calculate exponential backoff delay.
        
        Args:
            attempt: Attempt number (0-indexed)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
        
        Returns:
            Delay in seconds with jitter
        """
        # Calculate exponential delay: base * (2 ^ attempt)
        delay = min(base_delay * (2 ** attempt), max_delay)
        
        # Add random jitter (±10%)
        jitter = delay * random.uniform(-0.1, 0.1)
        delay_with_jitter = delay + jitter
        
        self.logger.debug(f"Exponential backoff (attempt {attempt}): {delay_with_jitter:.1f}s")
        return delay_with_jitter
    
    def wait(self, delay: float):
        """
        Wait for specified delay.
        
        Args:
            delay: Delay in seconds
        """
        self.logger.info(f"Waiting {delay:.1f}s due to rate limiting")
        time.sleep(delay)
    
    def update_settings(self, max_concurrent: int = None, min_delay: float = None, 
                       max_delay: float = None):
        """
        Update rate limiter settings.
        
        Args:
            max_concurrent: New maximum concurrent operations (optional)
            min_delay: New minimum delay in seconds (optional)
            max_delay: New maximum delay in seconds (optional)
        """
        with self.lock:
            if max_concurrent is not None and max_concurrent != self.max_concurrent:
                # Semaphore value cannot be changed, log warning
                self.logger.warning(f"Cannot change max_concurrent after initialization. "
                                   f"Restart required to change from {self.max_concurrent} to {max_concurrent}")
            
            if min_delay is not None:
                self.min_delay = min_delay
                self.logger.info(f"Updated min_delay to {min_delay}s")
            
            if max_delay is not None:
                self.max_delay = max_delay
                self.logger.info(f"Updated max_delay to {max_delay}s")
    
    def get_settings(self) -> dict:
        """
        Get current rate limiter settings.
        
        Returns:
            Dictionary with current settings
        """
        with self.lock:
            return {
                'max_concurrent': self.max_concurrent,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            }

