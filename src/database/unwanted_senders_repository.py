"""Repository for unwanted senders operations.

Handles tracking of unwanted senders and must-delete list for failed unsubscribes.
"""

from typing import List, Dict
from .base_repository import BaseRepository


class UnwantedSendersRepository(BaseRepository):
    """Repository for managing unwanted senders and must-delete lists.
    
    Tracks senders that failed unsubscribe attempts and need manual deletion.
    """
    
    def add_to_must_delete(self, sender: str, reason: str) -> None:
        """Add sender to must-delete list (failed unsubscribe).
        
        Uses UPSERT pattern to update timestamp if already exists.
        
        Args:
            sender: Email address of sender
            reason: Reason for unsubscribe failure
            
        Example:
            >>> repo.add_to_must_delete('spam@example.com', 'No unsubscribe link')
        """
        sql = """
            INSERT INTO unwanted_senders (email, reason, failed_unsubscribe, added_date)
            VALUES (?, ?, 1, datetime('now'))
            ON CONFLICT(email) DO UPDATE SET
                failed_unsubscribe = 1,
                reason = excluded.reason,
                added_date = datetime('now')
        """
        self._execute_query(sql, (sender, reason))
        self.logger.info(f"Added {sender} to must-delete list: {reason}")
    
    def get_must_delete_senders(self) -> List[Dict]:
        """Get all senders that need manual deletion.
        
        Returns:
            List of dictionaries with keys: email, reason, added_date
            Ordered by most recent first
            
        Example:
            >>> senders = repo.get_must_delete_senders()
            >>> senders[0]
            {'email': 'spam@example.com', 'reason': 'No unsubscribe link', 'added_date': '2024-01-01'}
        """
        sql = """
            SELECT email, reason, added_date
            FROM unwanted_senders
            WHERE failed_unsubscribe = 1
            ORDER BY added_date DESC
        """
        rows = self._fetch_all(sql)
        
        return [{
            'email': row[0],
            'reason': row[1] or 'Unknown',
            'added_date': row[2]
        } for row in rows]
    
    def remove_from_must_delete(self, sender: str) -> bool:
        """Remove sender from must-delete list.
        
        Args:
            sender: Email address to remove
            
        Returns:
            True if removed, False if not found
            
        Example:
            >>> repo.remove_from_must_delete('spam@example.com')
            True
        """
        # Check if exists first
        check_sql = """
            SELECT 1 FROM unwanted_senders
            WHERE email = ? AND failed_unsubscribe = 1
        """
        if not self._fetch_one(check_sql, (sender,)):
            self.logger.info(f"Sender not in must-delete list: {sender}")
            return False
        
        sql = """
            DELETE FROM unwanted_senders
            WHERE email = ? AND failed_unsubscribe = 1
        """
        self._execute_query(sql, (sender,))
        self.logger.info(f"Removed {sender} from must-delete list")
        return True
    
    def get_must_delete_count(self) -> int:
        """Get count of senders in must-delete list.
        
        Returns:
            Count of must-delete senders
            
        Example:
            >>> repo.get_must_delete_count()
            15
        """
        sql = """
            SELECT COUNT(*) FROM unwanted_senders
            WHERE failed_unsubscribe = 1
        """
        result = self._fetch_one(sql)
        return result[0] if result else 0
    
    def add_unwanted_sender(self, email: str, reason: str, 
                           failed_unsubscribe: bool = False) -> None:
        """Add an email to the unwanted senders list.
        
        Args:
            email: Email address of unwanted sender
            reason: Reason for marking as unwanted
            failed_unsubscribe: Whether unsubscribe attempt failed
            
        Example:
            >>> repo.add_unwanted_sender('spam@example.com', 'Suspicious content', False)
        """
        sql = """
            INSERT OR IGNORE INTO unwanted_senders 
            (email, reason, failed_unsubscribe)
            VALUES (?, ?, ?)
        """
        self._execute_query(sql, (email, reason, 1 if failed_unsubscribe else 0))
        self.logger.debug(f"Added unwanted sender: {email}")
    
    def check_unwanted(self, email: str) -> bool:
        """Check if email is in the unwanted senders list.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email is in unwanted list, False otherwise
            
        Example:
            >>> repo.check_unwanted('spam@example.com')
            True
        """
        sql = """
            SELECT 1 FROM unwanted_senders 
            WHERE email = ?
            LIMIT 1
        """
        result = self._fetch_one(sql, (email,))
        return result is not None

