"""
Base class for unsubscribe strategies.

This module defines the abstract base class that all unsubscribe strategies
must implement, ensuring a consistent interface across different strategies.
"""
from abc import ABC, abstractmethod
from typing import Dict, Tuple
import logging


class UnsubscribeStrategy(ABC):
    """
    Abstract base class for unsubscribe strategies.
    
    All unsubscribe strategy implementations must inherit from this class
    and implement the can_handle() and execute() methods.
    
    Example:
        class MyStrategy(UnsubscribeStrategy):
            def can_handle(self, email_data: Dict) -> bool:
                return 'my_field' in email_data
            
            def execute(self, email_data: Dict) -> Tuple[bool, str]:
                # Perform unsubscribe
                return (True, "Successfully unsubscribed")
    """
    
    def __init__(self):
        """Initialize strategy with a logger."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def can_handle(self, email_data: Dict) -> bool:
        """
        Check if this strategy can handle the given email.
        
        Args:
            email_data: Email data dictionary with sender, headers, links, etc.
        
        Returns:
            True if strategy can handle this email, False otherwise.
        
        Example:
            >>> strategy = MyStrategy()
            >>> email_data = {'sender': 'test@example.com', 'list_unsubscribe': '<...>'}
            >>> strategy.can_handle(email_data)
            True
        """
        pass
    
    @abstractmethod
    def execute(self, email_data: Dict) -> Tuple[bool, str]:
        """
        Execute unsubscribe for the given email.
        
        Args:
            email_data: Email data dictionary with sender, headers, links, etc.
        
        Returns:
            Tuple of (success, message):
                - success: True if unsubscribe successful, False otherwise
                - message: Human-readable result message for logging/display
        
        Raises:
            Exception: May raise exceptions which should be caught by caller
        
        Example:
            >>> strategy = MyStrategy()
            >>> email_data = {'sender': 'test@example.com'}
            >>> success, message = strategy.execute(email_data)
            >>> print(f"Success: {success}, Message: {message}")
            Success: True, Message: Unsubscribed successfully
        """
        pass
    
    def _log_attempt(self, email: str, method: str):
        """
        Log unsubscribe attempt.
        
        Args:
            email: Email address being unsubscribed from
            method: Method/strategy being used
        """
        self.logger.info(f"Attempting unsubscribe for {email} via {method}")
    
    def _log_result(self, email: str, success: bool, message: str):
        """
        Log unsubscribe result.
        
        Args:
            email: Email address
            success: Whether unsubscribe was successful
            message: Result message
        """
        level = logging.INFO if success else logging.WARNING
        status = "SUCCESS" if success else "FAILED"
        self.logger.log(level, f"Unsubscribe {status} for {email}: {message}")

