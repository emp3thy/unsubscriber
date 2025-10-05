"""
Strategy Chain Coordinator for managing unsubscribe strategies.

This module implements the Chain of Responsibility pattern to coordinate
multiple unsubscribe strategies, trying each in order until one succeeds.
"""
from typing import Dict, Tuple, List
import logging
from src.unsubscribe.strategy_base import UnsubscribeStrategy
from src.database.db_manager import DBManager


class StrategyChain:
    """
    Coordinates multiple unsubscribe strategies.
    
    This class manages a chain of unsubscribe strategies and executes them
    in priority order, stopping at the first successful strategy.
    All attempts are logged to the database for audit purposes.
    
    Example:
        >>> from src.unsubscribe.list_unsubscribe import ListUnsubscribeStrategy
        >>> from src.unsubscribe.http_strategy import HTTPStrategy
        >>> 
        >>> chain = StrategyChain(db_manager)
        >>> chain.add_strategy(ListUnsubscribeStrategy())
        >>> chain.add_strategy(HTTPStrategy())
        >>> 
        >>> success, message, strategy = chain.execute(email_data)
        >>> print(f"Success: {success}, Strategy: {strategy}")
    """
    
    def __init__(self, db_manager: DBManager):
        """
        Initialize strategy chain.
        
        Args:
            db_manager: Database manager for logging attempts
        """
        self.db = db_manager
        self.strategies: List[UnsubscribeStrategy] = []
        self.logger = logging.getLogger(__name__)
    
    def add_strategy(self, strategy: UnsubscribeStrategy):
        """
        Add a strategy to the chain.
        
        Strategies are tried in the order they are added.
        
        Args:
            strategy: Unsubscribe strategy instance to add
        """
        self.strategies.append(strategy)
        strategy_name = strategy.__class__.__name__
        self.logger.info(f"Added strategy: {strategy_name}")
    
    def execute(self, email_data: Dict) -> Tuple[bool, str, str]:
        """
        Execute strategies in order until one succeeds.
        
        Tries each strategy that can handle the email, stopping at the
        first success. All attempts are logged to the database.
        
        Args:
            email_data: Email data dictionary with sender, headers, links, etc.
        
        Returns:
            Tuple of (success, message, strategy_name):
                - success: True if any strategy succeeded
                - message: Result message from the successful/last strategy
                - strategy_name: Name of successful strategy or "None" if all failed
        """
        sender = email_data.get('sender', 'unknown')
        self.logger.info(f"Starting unsubscribe chain for {sender}")
        
        if not self.strategies:
            message = "No strategies configured"
            self.logger.error(message)
            return (False, message, "None")
        
        # Try each strategy
        last_message = ""
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            
            try:
                # Check if strategy can handle this email
                if not strategy.can_handle(email_data):
                    self.logger.debug(f"{strategy_name} cannot handle this email")
                    continue
                
                # Execute strategy
                self.logger.info(f"Trying {strategy_name} for {sender}")
                success, message = strategy.execute(email_data)
                last_message = message
                
                # Log attempt to database
                self._log_attempt(sender, strategy_name, success, message)
                
                # If successful, return immediately
                if success:
                    self.logger.info(f"{strategy_name} succeeded for {sender}")
                    return (True, message, strategy_name)
                else:
                    self.logger.warning(f"{strategy_name} failed for {sender}: {message}")
            
            except Exception as e:
                # Strategy raised an exception
                error_msg = f"Strategy error: {str(e)[:100]}"
                self.logger.error(f"{strategy_name} raised exception for {sender}: {e}")
                self._log_attempt(sender, strategy_name, False, error_msg)
                last_message = error_msg
        
        # All strategies failed - add to must-delete list
        final_message = last_message if last_message else "All unsubscribe strategies failed"
        self.logger.warning(f"All strategies failed for {sender}")
        
        # Add to must-delete list for manual intervention
        try:
            self.db.add_to_must_delete(sender, final_message)
        except Exception as e:
            self.logger.error(f"Failed to add {sender} to must-delete list: {e}")
        
        return (False, final_message, "None")
    
    def _log_attempt(self, sender: str, strategy: str, success: bool, message: str):
        """
        Log unsubscribe attempt to database.
        
        Args:
            sender: Email address of sender
            strategy: Strategy name
            success: Whether attempt was successful
            message: Result message
        """
        try:
            self.db.log_unsubscribe_attempt(sender, strategy, success, message)
        except Exception as e:
            # Don't let logging errors interrupt the unsubscribe process
            self.logger.error(f"Failed to log attempt to database: {e}")
    
    def get_strategies(self) -> List[str]:
        """
        Get list of registered strategy names.
        
        Returns:
            List of strategy class names
        """
        return [strategy.__class__.__name__ for strategy in self.strategies]

