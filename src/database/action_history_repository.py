"""Repository for action history operations.

Handles logging and querying of user actions and unsubscribe attempts.
"""

from typing import List, Dict
from .base_repository import BaseRepository


class ActionHistoryRepository(BaseRepository):
    """Repository for managing action history logs.
    
    Tracks all actions performed by the application including unsubscribes,
    deletions, and other operations for audit and troubleshooting.
    """
    
    def log_action(self, sender_email: str, action_type: str, 
                   success: bool, details: str) -> None:
        """Log an action to the action history.
        
        Args:
            sender_email: Email address the action was performed on
            action_type: Type of action ('unsubscribe', 'delete', etc.)
            success: Whether the action succeeded
            details: Additional details about the action
            
        Example:
            >>> repo.log_action('spam@example.com', 'unsubscribe', True, 'Successfully unsubscribed')
        """
        sql = """
            INSERT INTO action_history 
            (sender_email, action_type, success, details)
            VALUES (?, ?, ?, ?)
        """
        self._execute_query(sql, (sender_email, action_type, 1 if success else 0, details))
        self.logger.debug(f"Logged action: {action_type} for {sender_email}")
    
    def log_unsubscribe_attempt(self, sender: str, strategy: str, 
                               success: bool, message: str) -> bool:
        """Log an unsubscribe attempt with strategy information.
        
        Convenience method for logging unsubscribe-specific actions.
        
        Args:
            sender: Email address of sender
            strategy: Strategy name used (e.g., 'ListUnsubscribeStrategy')
            success: Whether the attempt was successful
            message: Result message
            
        Returns:
            True if logged successfully
            
        Example:
            >>> repo.log_unsubscribe_attempt('spam@example.com', 'ListUnsubscribe', True, 'Success')
            True
        """
        details = f"Strategy: {strategy} - {message}"
        self.log_action(sender, 'unsubscribe', success, details)
        return True
    
    def get_action_history(self, limit: int = 1000) -> List[Dict]:
        """Get action history records.
        
        Args:
            limit: Maximum number of records to return (default 1000)
            
        Returns:
            List of action dictionaries, ordered by most recent first
            Keys: sender_email, action_type, timestamp, success, details
            
        Example:
            >>> history = repo.get_action_history(limit=100)
            >>> history[0]['action_type']
            'unsubscribe'
        """
        sql = """
            SELECT sender_email, action_type, timestamp, success, details
            FROM action_history
            ORDER BY timestamp DESC
            LIMIT ?
        """
        rows = self._fetch_all(sql, (limit,))
        
        return [{
            'sender_email': row[0],
            'action_type': row[1],
            'timestamp': row[2],
            'success': bool(row[3]),
            'details': row[4]
        } for row in rows]
    
    def get_strategy_stats(self) -> Dict:
        """Get statistics on unsubscribe strategies.
        
        Returns:
            Dictionary with keys:
            - total: Total unsubscribe attempts
            - successful: Successful attempts  
            - failed: Failed attempts
            - by_strategy: Dict mapping strategy names to their stats
            
        Example:
            >>> stats = repo.get_strategy_stats()
            >>> stats['total']
            150
            >>> stats['by_strategy']['ListUnsubscribe']
            {'total': 100, 'successful': 95, 'failed': 5}
        """
        # Get overall stats
        sql_overall = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
            FROM action_history
            WHERE action_type = 'unsubscribe'
        """
        row = self._fetch_one(sql_overall)
        total = row[0] if row else 0
        successful = row[1] if row and row[1] else 0
        failed = row[2] if row and row[2] else 0
        
        # Get per-strategy stats
        sql_strategies = """
            SELECT 
                details,
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
            FROM action_history
            WHERE action_type = 'unsubscribe'
            GROUP BY details
        """
        rows = self._fetch_all(sql_strategies)
        
        by_strategy = {}
        for row in rows:
            details = row[0] or ''
            # Extract strategy name from details (format: "Strategy: StrategyName - message")
            strategy_name = 'Unknown'
            if details.startswith('Strategy: '):
                parts = details.split(' - ', 1)
                strategy_part = parts[0].replace('Strategy: ', '')
                if strategy_part:
                    strategy_name = strategy_part
            
            by_strategy[strategy_name] = {
                'total': row[1],
                'successful': row[2] if row[2] else 0,
                'failed': row[3] if row[3] else 0
            }
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'by_strategy': by_strategy
        }
    
    def get_failure_reasons(self) -> List[Dict]:
        """Get common failure reasons from action history.
        
        Returns:
            List of dictionaries with keys:
            - reason: Failure reason text
            - count: Number of occurrences
            Ordered by most common first, limited to top 10.
            
        Example:
            >>> reasons = repo.get_failure_reasons()
            >>> reasons[0]
            {'reason': 'Network timeout', 'count': 25}
        """
        sql = """
            SELECT details, COUNT(*) as count
            FROM action_history
            WHERE action_type = 'unsubscribe' AND success = 0
            GROUP BY details
            ORDER BY count DESC
            LIMIT 10
        """
        rows = self._fetch_all(sql)
        
        results = []
        for row in rows:
            details = row[0] or 'Unknown error'
            # Extract the message part after the strategy
            reason = details
            if ' - ' in details:
                parts = details.split(' - ', 1)
                if len(parts) > 1:
                    reason = parts[1]
            
            results.append({
                'reason': reason,
                'count': row[1]
            })
        
        return results
    
    def get_actions_for_sender(self, email: str) -> List[Dict]:
        """Get all actions for a specific sender.
        
        Args:
            email: Sender email address to query
            
        Returns:
            List of action dictionaries for this sender
            
        Example:
            >>> actions = repo.get_actions_for_sender('spam@example.com')
            >>> len(actions)
            3
        """
        sql = """
            SELECT sender_email, action_type, timestamp, success, details
            FROM action_history
            WHERE sender_email = ?
            ORDER BY timestamp DESC
        """
        rows = self._fetch_all(sql, (email,))
        
        return [{
            'sender_email': row[0],
            'action_type': row[1],
            'timestamp': row[2],
            'success': bool(row[3]),
            'details': row[4]
        } for row in rows]
    
    def get_successful_actions(self, action_type: str) -> List[Dict]:
        """Get all successful actions of a specific type.
        
        Args:
            action_type: Type of action to query ('unsubscribe', 'delete', etc.)
            
        Returns:
            List of successful action dictionaries
            
        Example:
            >>> successful = repo.get_successful_actions('unsubscribe')
            >>> all(a['success'] for a in successful)
            True
        """
        sql = """
            SELECT sender_email, action_type, timestamp, success, details
            FROM action_history
            WHERE action_type = ? AND success = 1
            ORDER BY timestamp DESC
        """
        rows = self._fetch_all(sql, (action_type,))
        
        return [{
            'sender_email': row[0],
            'action_type': row[1],
            'timestamp': row[2],
            'success': True,
            'details': row[4]
        } for row in rows]

