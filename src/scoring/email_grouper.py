"""Email grouping system for Email Unsubscriber

Groups and aggregates emails by sender, calculating summary statistics
and scores for each sender.
"""

from collections import defaultdict
from typing import List, Dict
from src.scoring.scorer import EmailScorer


class EmailGrouper:
    """Group and aggregate emails by sender.
    
    Transforms individual emails into sender-level statistics with scores,
    sorted by priority for user action.
    """
    
    def __init__(self, scorer: EmailScorer):
        """Initialize email grouper.
        
        Args:
            scorer: EmailScorer instance for calculating scores
        """
        self.scorer = scorer
    
    def group_by_sender(self, emails: List[Dict]) -> List[Dict]:
        """Group emails by sender and calculate aggregate stats.
        
        Args:
            emails: List of email dictionaries with sender, is_unread, etc.
            
        Returns:
            List of sender dictionaries sorted by total_score (descending)
        """
        if not emails:
            return []
        
        # Group emails by sender
        groups = defaultdict(list)
        for email in emails:
            sender = email.get('sender', 'unknown@example.com')
            groups[sender].append(email)
        
        # Aggregate stats for each sender
        senders = []
        for sender, sender_emails in groups.items():
            sender_data = self._aggregate_sender_data(sender, sender_emails)
            senders.append(sender_data)
        
        # Sort by total score descending
        return sorted(senders, key=lambda x: x['total_score'], reverse=True)
    
    def _aggregate_sender_data(self, sender: str, emails: List[Dict]) -> Dict:
        """Calculate aggregate statistics for a sender.
        
        Args:
            sender: Sender email address
            emails: List of emails from this sender
            
        Returns:
            Dictionary with sender statistics
        """
        frequency = len(emails)
        unread_count = sum(1 for e in emails if e.get('is_unread', False))
        
        # Calculate scores for all emails
        scores = []
        score_breakdowns = []
        for email in emails:
            score, breakdown = self.scorer.calculate_score(
                email,
                frequency=frequency,
                sender=sender
            )
            scores.append(score)
            score_breakdowns.append(breakdown)
        
        # Collect unsubscribe links
        all_links = []
        for email in emails:
            links = email.get('unsubscribe_links', [])
            all_links.extend(links)
        sample_links = list(set(all_links))[:3]  # Unique, up to 3
        
        # Aggregate score breakdowns for the sender
        aggregated_breakdown = self._aggregate_score_breakdowns(score_breakdowns)

        return {
            'sender': sender,
            'total_count': frequency,
            'unread_count': unread_count,
            'average_score': sum(scores) / len(scores) if scores else 0,
            'total_score': sum(scores),
            'score_breakdown': aggregated_breakdown,
            'has_unsubscribe': len(all_links) > 0,
            'sample_links': sample_links,
            'last_email_date': emails[-1].get('date', '') if emails else ''
        }

    def _aggregate_score_breakdowns(self, breakdowns: List[Dict]) -> Dict:
        """Aggregate score breakdowns from multiple emails into a single breakdown.

        Args:
            breakdowns: List of score breakdown dictionaries from individual emails

        Returns:
            Aggregated breakdown dictionary for the sender
        """
        if not breakdowns:
            return {'total': 0}

        # Initialize aggregated breakdown
        aggregated = {
            'total': 0,
            'unread': 0,
            'frequency': 0,
            'has_unsubscribe': 0,
            'historical_unwanted': 0
        }

        # Sum up all components
        for breakdown in breakdowns:
            if 'total' in breakdown:
                aggregated['total'] += breakdown['total']
            if 'unread' in breakdown:
                aggregated['unread'] += breakdown['unread']
            if 'frequency' in breakdown:
                aggregated['frequency'] += breakdown['frequency']
            if 'has_unsubscribe' in breakdown:
                aggregated['has_unsubscribe'] += breakdown['has_unsubscribe']
            if 'historical_unwanted' in breakdown:
                aggregated['historical_unwanted'] += breakdown['historical_unwanted']

        return aggregated

