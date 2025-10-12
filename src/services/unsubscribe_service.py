"""
Unsubscribe Service for Email Unsubscriber.

This service handles the process of unsubscribing from multiple senders
using the strategy chain pattern with proper error handling, progress
reporting, and cancellation support.
"""

import logging
from typing import List, Dict, Callable, Optional
from threading import Event


class UnsubscribeService:
    """
    Service for unsubscribing from multiple email senders.
    
    This service coordinates unsubscribe attempts across multiple senders,
    using a strategy chain to try different unsubscribe methods. It handles
    whitelist checking, progress reporting, cancellation, and comprehensive
    logging of all attempts.
    
    Example:
        >>> service = UnsubscribeService(strategy_chain, db_manager)
        >>> senders = [{'sender': 'spam@example.com', 'list_unsubscribe': '<https://...>'}]
        >>> def progress(current, total, msg):
        ...     print(f"{current}/{total}: {msg}")
        >>> results = service.unsubscribe_from_senders(senders, progress)
        >>> print(f"Success: {results['success_count']}, Failed: {results['failed_count']}")
    """
    
    def __init__(self, strategy_chain, db_manager):
        """
        Initialize UnsubscribeService with injected dependencies.
        
        Args:
            strategy_chain: StrategyChain instance for executing unsubscribe strategies
            db_manager: Database manager for whitelist checking and logging
        """
        self.strategy_chain = strategy_chain
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        self.cancel_event = Event()
    
    def unsubscribe_from_senders(
        self, 
        senders: List[Dict], 
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict:
        """
        Unsubscribe from multiple senders using strategy chain.
        
        Attempts to unsubscribe from each sender, checking whitelist first
        and trying available strategies. All attempts are logged to the
        action history.
        
        Args:
            senders: List of sender dictionaries with 'sender' email and
                    optional unsubscribe data (list_unsubscribe, etc.)
            progress_callback: Optional callback function(current, total, message)
                              Called after processing each sender
        
        Returns:
            Dictionary with results:
            {
                'success_count': int,      # Number of successful unsubscribes
                'failed_count': int,       # Number of failed attempts
                'skipped_count': int,      # Number skipped (whitelisted or no method)
                'details': List[str],      # List of result messages per sender
                'successful_senders': List[str]  # List of successfully unsubscribed emails
            }
        """
        # Reset cancel event
        self.cancel_event.clear()
        
        # Initialize results
        results = {
            'success_count': 0,
            'failed_count': 0,
            'skipped_count': 0,
            'details': [],
            'successful_senders': []
        }
        
        total = len(senders)
        self.logger.info(f"Starting unsubscribe process for {total} senders")
        
        if total == 0:
            return results
        
        # Process each sender
        for i, sender_data in enumerate(senders):
            # Check for cancellation
            if self.cancel_event.is_set():
                self.logger.info(f"Unsubscribe cancelled at sender {i+1}/{total}")
                results['details'].append("Operation cancelled by user")
                break
            
            sender_email = sender_data.get('sender', 'unknown')
            
            # Update progress
            if progress_callback:
                progress_callback(i, total, f"Processing {sender_email}...")
            
            try:
                # Check if whitelisted
                if self.db.check_whitelist(sender_email):
                    self.logger.info(f"Skipping whitelisted sender: {sender_email}")
                    results['skipped_count'] += 1
                    results['details'].append(f"{sender_email}: Skipped (whitelisted)")
                    continue
                
                # Check if sender has unsubscribe method
                has_unsubscribe = (
                    sender_data.get('list_unsubscribe') or 
                    sender_data.get('unsubscribe_links')
                )
                
                if not has_unsubscribe:
                    self.logger.info(f"No unsubscribe method for: {sender_email}")
                    results['skipped_count'] += 1
                    results['details'].append(f"{sender_email}: No unsubscribe method found")
                    # Log as failed attempt
                    self.db.log_action(
                        sender_email, 
                        'unsubscribe', 
                        False, 
                        'No unsubscribe method available'
                    )
                    continue
                
                # Attempt unsubscribe via strategy chain
                self.logger.info(f"Attempting unsubscribe for: {sender_email}")
                success, message, strategy = self.strategy_chain.execute(sender_data)
                
                if success:
                    results['success_count'] += 1
                    results['successful_senders'].append(sender_email)
                    results['details'].append(f"{sender_email}: Success ({strategy})")
                    self.logger.info(f"Successfully unsubscribed from {sender_email} using {strategy}")
                else:
                    results['failed_count'] += 1
                    results['details'].append(f"{sender_email}: Failed - {message}")
                    self.logger.warning(f"Failed to unsubscribe from {sender_email}: {message}")
            
            except Exception as e:
                # Handle unexpected errors
                error_msg = f"Unexpected error: {str(e)[:100]}"
                results['failed_count'] += 1
                results['details'].append(f"{sender_email}: Error - {error_msg}")
                self.logger.error(f"Error processing {sender_email}: {e}", exc_info=True)
                
                # Log to action history
                try:
                    self.db.log_action(sender_email, 'unsubscribe', False, error_msg)
                except Exception as log_error:
                    self.logger.error(f"Failed to log error for {sender_email}: {log_error}")
        
        # Final progress update
        if progress_callback:
            progress_callback(total, total, "Complete")
        
        # Log summary
        self.logger.info(
            f"Unsubscribe complete: {results['success_count']} success, "
            f"{results['failed_count']} failed, {results['skipped_count']} skipped"
        )
        
        return results
    
    def cancel(self):
        """
        Cancel ongoing unsubscribe operation.
        
        Sets the cancellation flag. The operation will stop after
        the current sender is processed and return partial results.
        """
        self.logger.info("Unsubscribe cancellation requested")
        self.cancel_event.set()
    
    def is_cancelled(self) -> bool:
        """
        Check if unsubscribe has been cancelled.
        
        Returns:
            True if cancel() has been called, False otherwise
        """
        return self.cancel_event.is_set()

