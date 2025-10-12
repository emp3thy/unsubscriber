"""
Email Scan Service for Email Unsubscriber.

This service orchestrates the process of scanning an inbox, parsing emails,
scoring them, and grouping by sender. It handles progress reporting,
cancellation, and error handling.
"""

import logging
from typing import List, Dict, Callable, Optional
from threading import Event


class EmailScanService:
    """
    Service for scanning and analyzing inbox emails.
    
    This service coordinates email fetching, parsing, scoring, and grouping
    operations with proper error handling and progress reporting.
    
    Example:
        >>> service = EmailScanService(email_client, db, parser, scorer, grouper)
        >>> def progress(current, total, msg):
        ...     print(f"{current}/{total}: {msg}")
        >>> senders = service.scan_inbox(progress_callback=progress)
        >>> print(f"Found {len(senders)} unique senders")
    """
    
    def __init__(self, email_client, db_manager, parser, scorer, grouper):
        """
        Initialize EmailScanService with injected dependencies.
        
        Args:
            email_client: Email client instance (IMAP or Gmail API)
            db_manager: Database manager for persistent operations
            parser: EmailParser instance for parsing raw emails
            scorer: EmailScorer instance for scoring emails
            grouper: EmailGrouper instance for grouping by sender
        """
        self.email_client = email_client
        self.db = db_manager
        self.parser = parser
        self.scorer = scorer
        self.grouper = grouper
        self.logger = logging.getLogger(__name__)
        self.cancel_event = Event()
    
    def scan_inbox(self, progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[Dict]:
        """
        Scan inbox and return grouped sender data.
        
        Orchestrates the complete scan process:
        1. Fetch email IDs from client
        2. Fetch and parse email headers
        3. Group emails by sender
        4. Calculate scores for each sender
        
        Args:
            progress_callback: Optional callback function(current, total, message)
                               Called periodically to report progress
        
        Returns:
            List of sender dictionaries with aggregated stats and scores.
            Each dict contains: sender, email_count, unread_count, total_score, etc.
            Returns empty list if no emails found or scan is cancelled.
        
        Raises:
            Exception: Re-raises any critical errors after logging
        """
        try:
            # Reset cancel event for new scan
            self.cancel_event.clear()
            
            # Fetch email IDs
            if progress_callback:
                progress_callback(0, 100, "Fetching email list...")
            
            self.logger.info("Starting inbox scan")
            email_ids = self.email_client.fetch_email_ids()
            total = len(email_ids)
            
            if total == 0:
                self.logger.info("No emails found in inbox")
                return []
            
            self.logger.info(f"Found {total} emails to process")
            
            # Parse emails
            emails = []
            parse_errors = 0
            
            for i, email_id in enumerate(email_ids):
                # Check for cancellation
                if self.cancel_event.is_set():
                    self.logger.info(f"Scan cancelled at email {i+1}/{total}")
                    break
                
                try:
                    # Fetch headers for this email
                    headers = self.email_client.fetch_headers([email_id])
                    if headers:
                        # Parse email data
                        email_data = self.parser.parse_email(headers[0])
                        emails.append(email_data)
                except Exception as e:
                    # Log parse errors but continue processing
                    parse_errors += 1
                    self.logger.warning(f"Error parsing email {email_id}: {e}")
                    continue
                
                # Update progress periodically (every 50 emails)
                if progress_callback and i % 50 == 0:
                    progress_callback(i + 1, total, f"Processing {i+1:,} of {total:,}")
            
            # Log any parse errors
            if parse_errors > 0:
                self.logger.warning(f"Failed to parse {parse_errors} emails")
            
            # Check if cancelled before grouping
            if self.cancel_event.is_set():
                self.logger.info(f"Scan cancelled. Processed {len(emails)} emails before cancellation")
                # Return partial results
                if emails:
                    senders = self.grouper.group_by_sender(emails)
                    return senders
                return []
            
            # Score and group by sender
            if progress_callback:
                progress_callback(total, total, "Analyzing senders...")
            
            self.logger.info(f"Grouping {len(emails)} emails by sender")
            senders = self.grouper.group_by_sender(emails)
            
            self.logger.info(f"Scan complete: {len(senders)} unique senders found")
            return senders
        
        except Exception as e:
            # Log critical errors and re-raise
            self.logger.error(f"Scan failed with critical error: {e}", exc_info=True)
            raise
    
    def cancel(self):
        """
        Cancel ongoing scan operation.
        
        Sets the cancellation flag. The scan will stop at the next
        checkpoint (after current email is processed) and return
        partial results.
        """
        self.logger.info("Scan cancellation requested")
        self.cancel_event.set()
    
    def is_cancelled(self) -> bool:
        """
        Check if scan has been cancelled.
        
        Returns:
            True if cancel() has been called, False otherwise
        """
        return self.cancel_event.is_set()

