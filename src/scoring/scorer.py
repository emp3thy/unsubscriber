"""Email scoring system for Email Unsubscriber

Calculates spam/unwanted email scores based on multiple criteria.
Provides transparent score breakdowns for user trust.
"""

from typing import Dict, Tuple, Optional
import logging


class EmailScorer:
    """Calculate spam/unwanted email scores.
    
    Evaluates emails based on multiple criteria:
    - Unread status
    - Presence of unsubscribe links
    - Email frequency from sender
    - Historical unwanted sender data
    """
    
    def __init__(self, db_manager=None):
        """Initialize email scorer.
        
        Args:
            db_manager: Optional DBManager for historical scoring
        """
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def calculate_score(self, email_data: Dict, frequency: int = 1, 
                       sender: Optional[str] = None) -> Tuple[int, Dict]:
        """Calculate score for an email.
        
        Args:
            email_data: Dictionary with email attributes
                - is_unread: bool (optional)
                - unsubscribe_links: list (optional)
            frequency: Number of emails from this sender
            sender: Sender email address for historical lookup
                
        Returns:
            Tuple of (total_score, breakdown_dict)
            breakdown_dict contains individual component scores
            Score of -1 indicates whitelisted sender (protected)
        """
        score = 0
        breakdown = {}
        
        # Check if whitelisted (highest priority - score = -1 to indicate protection)
        if sender and self.db:
            if self._check_whitelisted(sender):
                breakdown['whitelisted'] = True
                breakdown['total'] = -1
                return (-1, breakdown)
        
        # Check if unread (+1 point)
        if email_data.get('is_unread', False):
            score += 1
            breakdown['unread'] = 1
        
        # Check for unsubscribe link (+1 point)
        if email_data.get('unsubscribe_links'):
            score += 1
            breakdown['has_unsubscribe'] = 1
        
        # Frequency scoring (+1 per additional email)
        freq_score = self._calculate_frequency_score(frequency)
        if freq_score > 0:
            score += freq_score
            breakdown['frequency'] = freq_score
        
        # Historical scoring (+5 if previously marked unwanted)
        if sender and self.db:
            hist_score = self._check_historical_unwanted(sender)
            if hist_score > 0:
                score += hist_score
                breakdown['historical_unwanted'] = hist_score
        
        breakdown['total'] = score
        return (score, breakdown)
    
    def _calculate_frequency_score(self, frequency: int) -> int:
        """Calculate score based on email frequency.
        
        Args:
            frequency: Number of emails from sender
            
        Returns:
            Frequency bonus points (frequency - 1, minimum 0)
        """
        return max(0, frequency - 1)
    
    def _check_historical_unwanted(self, sender: str) -> int:
        """Check if sender was previously marked unwanted.
        
        Args:
            sender: Sender email address
            
        Returns:
            5 points if sender in unwanted list, 0 otherwise
        """
        try:
            if self.db.check_unwanted(sender):
                return 5
        except Exception as e:
            self.logger.error(f"Error checking historical data: {e}")
        return 0
    
    def _check_whitelisted(self, sender: str) -> bool:
        """Check if sender is whitelisted (protected).
        
        Args:
            sender: Sender email address
            
        Returns:
            True if sender is whitelisted, False otherwise
        """
        try:
            return self.db.check_whitelist(sender)
        except Exception as e:
            self.logger.error(f"Error checking whitelist: {e}")
            return False

