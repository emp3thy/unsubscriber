"""
Email Deletion Service for Email Unsubscriber.

This service handles bulk deletion of emails from specified senders with
comprehensive safety checks, progress reporting, and database integration.
"""

import logging
from typing import List, Dict, Callable, Optional
from threading import Event


class EmailDeletionService:
    """
    Service for deleting emails from multiple senders.
    
    This service coordinates email deletion across multiple senders with
    whitelist safety checks, progress reporting, cancellation support,
    and integration with the must-delete list.
    
    Example:
        >>> service = EmailDeletionService(email_client, db_manager)
        >>> senders = [{'sender': 'spam@example.com', 'email_count': 50}]
        >>> def progress(current, total, msg):
        ...     print(f"{current}/{total}: {msg}")
        >>> results = service.delete_from_senders(senders, progress)
        >>> print(f"Deleted: {results['total_emails_deleted']}")
    """
    
    def __init__(self, email_client, db_manager):
        """
        Initialize EmailDeletionService with injected dependencies.
        
        Args:
            email_client: Email client instance for deletion operations
            db_manager: Database manager for whitelist checking and logging
        """
        self.email_client = email_client
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        self.cancel_event = Event()
    
    def delete_from_senders(
        self,
        senders: List[Dict],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict:
        """
        Delete emails from multiple senders.
        
        Deletes all emails from each specified sender, with whitelist
        safety checks. All deletions are logged to action history.
        
        Args:
            senders: List of sender dictionaries with 'sender' email address
            progress_callback: Optional callback function(current, total, message)
                              Called after processing each sender
        
        Returns:
            Dictionary with results:
            {
                'deleted_senders': int,     # Number of senders processed
                'total_emails_deleted': int, # Total emails deleted
                'failed_senders': int,       # Number of failures
                'skipped_senders': int       # Number skipped (whitelisted)
            }
        """
        # Reset cancel event
        self.cancel_event.clear()
        
        # Initialize results
        results = {
            'deleted_senders': 0,
            'total_emails_deleted': 0,
            'failed_senders': 0,
            'skipped_senders': 0
        }
        
        total = len(senders)
        self.logger.info(f"Starting deletion for {total} senders")
        
        if total == 0:
            return results
        
        # Process each sender
        for i, sender_data in enumerate(senders):
            # Check for cancellation
            if self.cancel_event.is_set():
                self.logger.info(f"Deletion cancelled at sender {i+1}/{total}")
                break
            
            sender_email = sender_data.get('sender', 'unknown')
            
            # Update progress
            if progress_callback:
                progress_callback(i, total, f"Deleting from {sender_email}...")
            
            try:
                # Safety check: whitelist
                if self.db.check_whitelist(sender_email):
                    self.logger.warning(
                        f"Skipping deletion from whitelisted sender: {sender_email}"
                    )
                    results['skipped_senders'] += 1
                    continue
                
                # Delete emails from this sender
                self.logger.info(f"Deleting emails from: {sender_email}")
                deleted_count, message = self.email_client.delete_emails_from_sender(
                    sender_email, self.db
                )
                
                if deleted_count > 0:
                    results['deleted_senders'] += 1
                    results['total_emails_deleted'] += deleted_count
                    self.logger.info(
                        f"Deleted {deleted_count} emails from {sender_email}"
                    )
                    
                    # Log successful deletion
                    self.db.log_action(
                        sender_email,
                        'delete',
                        True,
                        f'Deleted {deleted_count} emails'
                    )
                    
                    # Remove from must-delete list if present
                    try:
                        self.db.remove_from_must_delete(sender_email)
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to remove {sender_email} from must-delete list: {e}"
                        )
                else:
                    # No emails found or deletion failed
                    results['skipped_senders'] += 1
                    self.logger.info(f"No emails to delete from {sender_email}")
            
            except Exception as e:
                # Handle deletion errors
                error_msg = str(e)[:100]
                results['failed_senders'] += 1
                self.logger.error(
                    f"Error deleting from {sender_email}: {e}",
                    exc_info=True
                )
                
                # Log failed deletion
                try:
                    self.db.log_action(
                        sender_email,
                        'delete',
                        False,
                        f'Error: {error_msg}'
                    )
                except Exception as log_error:
                    self.logger.error(
                        f"Failed to log deletion error for {sender_email}: {log_error}"
                    )
        
        # Final progress update
        if progress_callback:
            progress_callback(total, total, "Complete")
        
        # Log summary
        self.logger.info(
            f"Deletion complete: {results['deleted_senders']} senders processed, "
            f"{results['total_emails_deleted']} emails deleted, "
            f"{results['failed_senders']} failed, "
            f"{results['skipped_senders']} skipped"
        )
        
        return results
    
    def delete_from_must_delete_list(
        self,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict:
        """
        Delete emails from all senders in the must-delete list.
        
        Retrieves the must-delete list from the database and deletes
        emails from each sender. Successfully processed senders are
        removed from the must-delete list.
        
        Args:
            progress_callback: Optional callback function(current, total, message)
        
        Returns:
            Dictionary with same structure as delete_from_senders()
        """
        self.logger.info("Starting deletion from must-delete list")
        
        try:
            # Get must-delete list
            must_delete_senders = self.db.get_must_delete_senders()
            
            if not must_delete_senders:
                self.logger.info("Must-delete list is empty")
                return {
                    'deleted_senders': 0,
                    'total_emails_deleted': 0,
                    'failed_senders': 0,
                    'skipped_senders': 0
                }
            
            self.logger.info(
                f"Found {len(must_delete_senders)} senders in must-delete list"
            )
            
            # Convert to format expected by delete_from_senders
            senders = [
                {'sender': sender_data['sender']}
                for sender_data in must_delete_senders
            ]
            
            # Delegate to delete_from_senders
            return self.delete_from_senders(senders, progress_callback)
        
        except Exception as e:
            self.logger.error(
                f"Error processing must-delete list: {e}",
                exc_info=True
            )
            raise
    
    def cancel(self):
        """
        Cancel ongoing deletion operation.
        
        Sets the cancellation flag. The operation will stop after
        the current sender is processed and return partial results.
        """
        self.logger.info("Deletion cancellation requested")
        self.cancel_event.set()
    
    def is_cancelled(self) -> bool:
        """
        Check if deletion has been cancelled.
        
        Returns:
            True if cancel() has been called, False otherwise
        """
        return self.cancel_event.is_set()

