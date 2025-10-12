"""Database Manager for Email Unsubscriber

This module provides a clean API for all database operations with the SQLite database.
Handles connection management, query execution, and error handling using context managers
and parameterized queries to prevent SQL injection.
"""

import sqlite3
from contextlib import contextmanager
from typing import Any, Optional, List, Dict
import logging


class DBManager:
    """Manages all database operations for the Email Unsubscriber application."""
    
    def __init__(self, db_path: str):
        """Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def initialize_db(self, schema_path: str):
        """Initialize database from schema file.
        
        Args:
            schema_path: Path to the SQL schema file
            
        Raises:
            Exception: If database initialization fails
        """
        try:
            with open(schema_path, 'r') as f:
                schema = f.read()
            with self.get_connection() as conn:
                conn.executescript(schema)
            self.logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections.
        
        Automatically handles commit/rollback and connection closing.
        
        Yields:
            sqlite3.Connection: Database connection
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def add_to_whitelist(self, entry: str, is_domain: bool = False, 
                        notes: str = "") -> bool:
        """Add an email or domain to the whitelist.
        
        Args:
            entry: Email address or domain pattern to whitelist
            is_domain: True if entry is a domain pattern (e.g., "@company.com")
            notes: Optional notes about this whitelist entry
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if is_domain:
                    # Check for duplicates
                    cursor.execute("SELECT 1 FROM whitelist WHERE domain = ?", (entry,))
                    if cursor.fetchone():
                        self.logger.info(f"Domain already in whitelist: {entry}")
                        return False
                    cursor.execute("""
                        INSERT INTO whitelist (domain, notes)
                        VALUES (?, ?)
                    """, (entry, notes))
                else:
                    # Check for duplicates
                    cursor.execute("SELECT 1 FROM whitelist WHERE email = ?", (entry,))
                    if cursor.fetchone():
                        self.logger.info(f"Email already in whitelist: {entry}")
                        return False
                    cursor.execute("""
                        INSERT INTO whitelist (email, notes)
                        VALUES (?, ?)
                    """, (entry, notes))
            self.logger.info(f"Added to whitelist: entry={entry}, is_domain={is_domain}")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Failed to add to whitelist: {e}")
            return False
    
    def check_whitelist(self, email: str) -> bool:
        """Check if email or its domain is whitelisted.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email or its domain is whitelisted, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Check exact email match or domain match
                cursor.execute("""
                    SELECT 1 FROM whitelist 
                    WHERE email = ? 
                    OR (domain IS NOT NULL AND ? LIKE '%' || domain)
                    LIMIT 1
                """, (email, email))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            self.logger.error(f"Error checking whitelist: {e}")
            return False
    
    def remove_from_whitelist(self, entry: str) -> bool:
        """Remove an entry from the whitelist.
        
        Args:
            entry: Email address or domain to remove
            
        Returns:
            True if removed, False if not found or error
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Try to delete as email first, then as domain
                cursor.execute("""
                    DELETE FROM whitelist WHERE email = ? OR domain = ?
                """, (entry, entry))
                removed = cursor.rowcount > 0
                if removed:
                    self.logger.info(f"Removed from whitelist: {entry}")
                else:
                    self.logger.warning(f"Entry not found in whitelist: {entry}")
                return removed
        except sqlite3.Error as e:
            self.logger.error(f"Error removing from whitelist: {e}")
            return False
    
    def get_whitelist(self) -> List[Dict]:
        """Get all whitelist entries.
        
        Returns:
            List of dictionaries with keys: entry, type, notes, added_date
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, email, domain, notes, added_date
                    FROM whitelist
                    ORDER BY added_date DESC
                """)
                rows = cursor.fetchall()
                
                result = []
                for row in rows:
                    entry_type = 'domain' if row[2] else 'email'
                    entry_value = row[2] if row[2] else row[1]
                    result.append({
                        'id': row[0],
                        'entry': entry_value,
                        'type': entry_type,
                        'notes': row[3] or '',
                        'added_date': row[4]
                    })
                return result
        except sqlite3.Error as e:
            self.logger.error(f"Error getting whitelist: {e}")
            return []
    
    def add_unwanted_sender(self, email: str, reason: str, 
                           failed_unsubscribe: bool = False):
        """Add an email to the unwanted senders list.
        
        Args:
            email: Email address of unwanted sender
            reason: Reason for marking as unwanted
            failed_unsubscribe: Whether unsubscribe attempt failed
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO unwanted_senders 
                    (email, reason, failed_unsubscribe)
                    VALUES (?, ?, ?)
                """, (email, reason, 1 if failed_unsubscribe else 0))
            self.logger.debug(f"Added unwanted sender: {email}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to add unwanted sender: {e}")
            raise
    
    def check_unwanted(self, email: str) -> bool:
        """Check if email is in the unwanted senders list.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email is in unwanted list, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 1 FROM unwanted_senders 
                    WHERE email = ?
                    LIMIT 1
                """, (email,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            self.logger.error(f"Error checking unwanted senders: {e}")
            return False
    
    def log_action(self, sender_email: str, action_type: str, 
                  success: bool, details: str):
        """Log an action to the action history.
        
        Args:
            sender_email: Email address the action was performed on
            action_type: Type of action performed
            success: Whether the action succeeded
            details: Additional details about the action
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO action_history 
                    (sender_email, action_type, success, details)
                    VALUES (?, ?, ?, ?)
                """, (sender_email, action_type, 1 if success else 0, details))
            self.logger.debug(f"Logged action: {action_type} for {sender_email}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to log action: {e}")
            raise
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value FROM config
                    WHERE key = ?
                """, (key,))
                result = cursor.fetchone()
                return result[0] if result else default
        except sqlite3.Error as e:
            self.logger.error(f"Error getting config '{key}': {e}")
            return default
    
    def set_config(self, key: str, value: Any):
        """Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO config (key, value)
                    VALUES (?, ?)
                """, (key, str(value)))
            self.logger.debug(f"Set config: {key}={value}")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to set config '{key}': {e}")
            raise
    
    def add_account(self, email: str, encrypted_password: str, provider: str) -> bool:
        """Add or update email account in database.
        
        Args:
            email: Email address
            encrypted_password: Encrypted password (from CredentialManager)
            provider: Email provider ('gmail' or 'outlook')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO accounts 
                    (email, encrypted_password, provider, added_date)
                    VALUES (?, ?, ?, datetime('now'))
                """, (email, encrypted_password, provider))
                self.logger.info(f"Account added/updated: {email}")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error adding account: {e}")
            return False
    
    def get_account(self, email: str) -> Optional[Dict]:
        """Retrieve account by email address.
        
        Args:
            email: Email address to retrieve
            
        Returns:
            Dictionary with account data or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT email, encrypted_password, provider, added_date
                    FROM accounts WHERE email = ?
                """, (email,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'email': row[0],
                        'encrypted_password': row[1],
                        'provider': row[2],
                        'added_date': row[3]
                    }
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving account: {e}")
            return None
    
    def list_accounts(self) -> List[Dict]:
        """List all accounts.
        
        Returns:
            List of account dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT email, encrypted_password, provider, added_date
                    FROM accounts ORDER BY added_date DESC
                """)
                rows = cursor.fetchall()
                
                return [{
                    'email': row[0],
                    'encrypted_password': row[1],
                    'provider': row[2],
                    'added_date': row[3]
                } for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error listing accounts: {e}")
            return []
    
    def delete_account(self, email: str) -> bool:
        """Delete account from database.
        
        Args:
            email: Email address to delete
            
        Returns:
            True if deleted, False if not found or error
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM accounts WHERE email = ?", (email,))
                deleted = cursor.rowcount > 0
                if deleted:
                    self.logger.info(f"Account deleted: {email}")
                return deleted
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting account: {e}")
            return False
    
    def get_primary_account(self) -> Optional[Dict]:
        """Get primary (first) account.
        
        Returns:
            First account dictionary or None if no accounts
        """
        accounts = self.list_accounts()
        return accounts[0] if accounts else None
    
    def log_unsubscribe_attempt(self, sender: str, strategy: str, success: bool, message: str) -> bool:
        """
        Log an unsubscribe attempt to action_history.
        
        Args:
            sender: Email address of sender
            strategy: Strategy name used (e.g., 'ListUnsubscribeStrategy')
            success: Whether the attempt was successful
            message: Result message
            
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            details = f"Strategy: {strategy} - {message}"
            return self.log_action(sender, 'unsubscribe', success, details)
        except Exception as e:
            self.logger.error(f"Error logging unsubscribe attempt: {e}")
            return False
    
    def add_to_must_delete(self, sender: str, reason: str):
        """Add sender to must-delete list (failed unsubscribe).
        
        This method marks a sender whose unsubscribe attempt failed, so they
        appear in the "Must Delete" list for manual email deletion.
        
        Args:
            sender: Email address of sender
            reason: Reason for unsubscribe failure
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO unwanted_senders (email, reason, failed_unsubscribe, added_date)
                    VALUES (?, ?, 1, datetime('now'))
                    ON CONFLICT(email) DO UPDATE SET
                        failed_unsubscribe = 1,
                        reason = excluded.reason,
                        added_date = datetime('now')
                """, (sender, reason))
                self.logger.info(f"Added {sender} to must-delete list: {reason}")
        except sqlite3.Error as e:
            self.logger.error(f"Error adding to must-delete: {e}")
    
    def get_must_delete_senders(self) -> List[Dict]:
        """Get all senders that need manual deletion (failed unsubscribe).
        
        Returns:
            List of dictionaries with keys: email, reason, added_date
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT email, reason, added_date
                    FROM unwanted_senders
                    WHERE failed_unsubscribe = 1
                    ORDER BY added_date DESC
                """)
                return [{
                    'email': row[0],
                    'reason': row[1] or 'Unknown',
                    'added_date': row[2]
                } for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"Error getting must-delete senders: {e}")
            return []
    
    def remove_from_must_delete(self, sender: str) -> bool:
        """Remove sender from must-delete list.
        
        Args:
            sender: Email address to remove
            
        Returns:
            True if removed, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM unwanted_senders
                    WHERE email = ? AND failed_unsubscribe = 1
                """, (sender,))
                removed = cursor.rowcount > 0
                if removed:
                    self.logger.info(f"Removed {sender} from must-delete list")
                return removed
        except sqlite3.Error as e:
            self.logger.error(f"Error removing from must-delete: {e}")
            return False
    
    def get_must_delete_count(self) -> int:
        """Get count of senders in must-delete list.
        
        Returns:
            Count of must-delete senders
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM unwanted_senders
                    WHERE failed_unsubscribe = 1
                """)
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            self.logger.error(f"Error getting must-delete count: {e}")
            return 0
    
    def get_strategy_stats(self) -> Dict:
        """
        Get statistics on unsubscribe strategies.
        
        Returns:
            Dictionary with:
                - total: Total unsubscribe attempts
                - successful: Successful attempts
                - failed: Failed attempts
                - by_strategy: Per-strategy breakdown
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get overall stats
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
                    FROM action_history
                    WHERE action_type = 'unsubscribe'
                """)
                row = cursor.fetchone()
                total = row[0] if row else 0
                successful = row[1] if row and row[1] else 0
                failed = row[2] if row and row[2] else 0
                
                # Get per-strategy stats
                cursor.execute("""
                    SELECT 
                        details,
                        COUNT(*) as total,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                        SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
                    FROM action_history
                    WHERE action_type = 'unsubscribe'
                    GROUP BY details
                """)
                
                by_strategy = {}
                for row in cursor.fetchall():
                    details = row[0] or 'Unknown'
                    # Extract strategy name from details (format: "Strategy: StrategyName - message")
                    strategy_name = 'Unknown'
                    if 'Strategy:' in details:
                        parts = details.split('Strategy:')[1].split('-')
                        if parts:
                            strategy_name = parts[0].strip()
                    
                    if strategy_name not in by_strategy:
                        by_strategy[strategy_name] = {
                            'total': 0,
                            'successful': 0,
                            'failed': 0
                        }
                    
                    by_strategy[strategy_name]['total'] += row[1]
                    by_strategy[strategy_name]['successful'] += row[2] if row[2] else 0
                    by_strategy[strategy_name]['failed'] += row[3] if row[3] else 0
                
                return {
                    'total': total,
                    'successful': successful,
                    'failed': failed,
                    'by_strategy': by_strategy
                }
        
        except sqlite3.Error as e:
            self.logger.error(f"Error getting strategy stats: {e}")
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'by_strategy': {}
            }
    
    def get_failure_reasons(self) -> List[Dict]:
        """
        Get common failure reasons from action history.
        
        Returns:
            List of dictionaries with:
                - reason: Failure reason
                - count: Number of occurrences
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT details, COUNT(*) as count
                    FROM action_history
                    WHERE action_type = 'unsubscribe' AND success = 0
                    GROUP BY details
                    ORDER BY count DESC
                    LIMIT 10
                """)
                
                results = []
                for row in cursor.fetchall():
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
        
        except sqlite3.Error as e:
            self.logger.error(f"Error getting failure reasons: {e}")
            return []
    
    def get_action_history(self, limit: int = 1000) -> List[Dict]:
        """
        Get action history records.
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of action history dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT sender_email, action_type, timestamp, success, details
                    FROM action_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                return [{
                    'sender_email': row[0],
                    'action_type': row[1],
                    'timestamp': row[2],
                    'success': bool(row[3]),
                    'details': row[4]
                } for row in cursor.fetchall()]
        
        except sqlite3.Error as e:
            self.logger.error(f"Error getting action history: {e}")
            return []

