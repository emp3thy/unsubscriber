"""Database Manager for Email Unsubscriber - Refactored with Repository Pattern

This module provides a facade over specialized repository classes while maintaining
backward compatibility with existing code. All database operations are delegated to
appropriate repository classes.
"""

import sqlite3
from contextlib import contextmanager
from typing import Any, Optional, List, Dict
import logging

from .whitelist_repository import WhitelistRepository
from .account_repository import AccountRepository
from .action_history_repository import ActionHistoryRepository
from .unwanted_senders_repository import UnwantedSendersRepository
from .config_repository import ConfigRepository


class DBManager:
    """Facade over repository classes for database operations.
    
    Maintains backward compatibility while delegating operations to specialized repositories.
    Direct repository access available via properties: whitelist, accounts, history, unwanted, config
    """
    
    def __init__(self, db_path: str):
        """Initialize the database manager with all repositories.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize all repositories
        self._whitelist_repo = WhitelistRepository(db_path)
        self._account_repo = AccountRepository(db_path)
        self._history_repo = ActionHistoryRepository(db_path)
        self._unwanted_repo = UnwantedSendersRepository(db_path)
        self._config_repo = ConfigRepository(db_path)
    
    # Property access to repositories for direct use
    @property
    def whitelist(self) -> WhitelistRepository:
        """Direct access to WhitelistRepository."""
        return self._whitelist_repo
    
    @property
    def accounts(self) -> AccountRepository:
        """Direct access to AccountRepository."""
        return self._account_repo
    
    @property
    def history(self) -> ActionHistoryRepository:
        """Direct access to ActionHistoryRepository."""
        return self._history_repo
    
    @property
    def unwanted(self) -> UnwantedSendersRepository:
        """Direct access to UnwantedSendersRepository."""
        return self._unwanted_repo
    
    @property
    def config(self) -> ConfigRepository:
        """Direct access to ConfigRepository."""
        return self._config_repo
    
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
        
        Maintained for backward compatibility and schema initialization.
        
        Yields:
            sqlite3.Connection: Database connection
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
    
    # Whitelist methods - delegate to WhitelistRepository
    def add_to_whitelist(self, entry: str, is_domain: bool = False, notes: str = "") -> bool:
        """Add entry to whitelist. Delegates to WhitelistRepository."""
        return self._whitelist_repo.add_to_whitelist(entry, is_domain, notes)
    
    def check_whitelist(self, email: str) -> bool:
        """Check if email is whitelisted. Delegates to WhitelistRepository."""
        return self._whitelist_repo.check_whitelist(email)
    
    def remove_from_whitelist(self, entry: str) -> bool:
        """Remove entry from whitelist. Delegates to WhitelistRepository."""
        return self._whitelist_repo.remove_from_whitelist(entry)
    
    def get_whitelist(self) -> List[Dict]:
        """Get all whitelist entries. Delegates to WhitelistRepository."""
        return self._whitelist_repo.get_whitelist()
    
    # Account methods - delegate to AccountRepository
    def add_account(self, email: str, encrypted_password: str, provider: str) -> bool:
        """Add or update account. Delegates to AccountRepository."""
        return self._account_repo.add_account(email, encrypted_password, provider)
    
    def get_account(self, email: str) -> Optional[Dict]:
        """Get account by email. Delegates to AccountRepository."""
        return self._account_repo.get_account(email)
    
    def list_accounts(self) -> List[Dict]:
        """List all accounts. Delegates to AccountRepository."""
        return self._account_repo.list_accounts()
    
    def delete_account(self, email: str) -> bool:
        """Delete account. Delegates to AccountRepository."""
        return self._account_repo.delete_account(email)
    
    def get_primary_account(self) -> Optional[Dict]:
        """Get primary account. Delegates to AccountRepository."""
        return self._account_repo.get_primary_account()
    
    # Action History methods - delegate to ActionHistoryRepository
    def log_action(self, sender_email: str, action_type: str, success: bool, details: str):
        """Log action. Delegates to ActionHistoryRepository."""
        self._history_repo.log_action(sender_email, action_type, success, details)
    
    def log_unsubscribe_attempt(self, sender: str, strategy: str, success: bool, message: str) -> bool:
        """Log unsubscribe attempt. Delegates to ActionHistoryRepository."""
        return self._history_repo.log_unsubscribe_attempt(sender, strategy, success, message)
    
    def get_action_history(self, limit: int = 1000) -> List[Dict]:
        """Get action history. Delegates to ActionHistoryRepository."""
        return self._history_repo.get_action_history(limit)
    
    def get_strategy_stats(self) -> Dict:
        """Get unsubscribe strategy stats. Delegates to ActionHistoryRepository."""
        return self._history_repo.get_strategy_stats()
    
    def get_failure_reasons(self) -> List[Dict]:
        """Get failure reasons. Delegates to ActionHistoryRepository."""
        return self._history_repo.get_failure_reasons()
    
    # Unwanted Senders methods - delegate to UnwantedSendersRepository
    def add_unwanted_sender(self, email: str, reason: str, failed_unsubscribe: bool = False):
        """Add unwanted sender. Delegates to UnwantedSendersRepository."""
        self._unwanted_repo.add_unwanted_sender(email, reason, failed_unsubscribe)
    
    def check_unwanted(self, email: str) -> bool:
        """Check if sender is unwanted. Delegates to UnwantedSendersRepository."""
        return self._unwanted_repo.check_unwanted(email)
    
    def add_to_must_delete(self, sender: str, reason: str):
        """Add to must-delete list. Delegates to UnwantedSendersRepository."""
        self._unwanted_repo.add_to_must_delete(sender, reason)
    
    def get_must_delete_senders(self) -> List[Dict]:
        """Get must-delete senders. Delegates to UnwantedSendersRepository."""
        return self._unwanted_repo.get_must_delete_senders()
    
    def remove_from_must_delete(self, sender: str) -> bool:
        """Remove from must-delete list. Delegates to UnwantedSendersRepository."""
        return self._unwanted_repo.remove_from_must_delete(sender)
    
    def get_must_delete_count(self) -> int:
        """Get must-delete count. Delegates to UnwantedSendersRepository."""
        return self._unwanted_repo.get_must_delete_count()
    
    # Config methods - delegate to ConfigRepository
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get config value. Delegates to ConfigRepository."""
        return self._config_repo.get_config(key, default)
    
    def set_config(self, key: str, value: Any):
        """Set config value. Delegates to ConfigRepository."""
        self._config_repo.set_config(key, value)

