"""Repository for account operations.

Handles CRUD operations for email account credentials.
"""

from typing import List, Dict, Optional
from .base_repository import BaseRepository


class AccountRepository(BaseRepository):
    """Repository for managing email account credentials.
    
    Stores encrypted passwords and provider information for email accounts.
    """
    
    def add_account(self, email: str, encrypted_password: str, provider: str) -> bool:
        """Add or update email account.
        
        Uses INSERT OR REPLACE to update existing accounts.
        
        Args:
            email: Email address
            encrypted_password: Encrypted password from CredentialManager
            provider: Email provider ('gmail', 'outlook', etc.)
            
        Returns:
            True if successful
            
        Example:
            >>> repo.add_account('user@gmail.com', 'encrypted_pass', 'gmail')
            True
        """
        sql = """
            INSERT OR REPLACE INTO accounts 
            (email, encrypted_password, provider, added_date)
            VALUES (?, ?, ?, datetime('now'))
        """
        self._execute_query(sql, (email, encrypted_password, provider))
        self.logger.info(f"Account added/updated: {email}")
        return True
    
    def get_account(self, email: str) -> Optional[Dict]:
        """Retrieve account by email address.
        
        Args:
            email: Email address to retrieve
            
        Returns:
            Dictionary with account data or None if not found
            Keys: email, encrypted_password, provider, added_date
            
        Example:
            >>> account = repo.get_account('user@gmail.com')
            >>> account['provider']
            'gmail'
        """
        sql = """
            SELECT email, encrypted_password, provider, added_date
            FROM accounts WHERE email = ?
        """
        row = self._fetch_one(sql, (email,))
        
        if row:
            return {
                'email': row[0],
                'encrypted_password': row[1],
                'provider': row[2],
                'added_date': row[3]
            }
        return None
    
    def list_accounts(self) -> List[Dict]:
        """List all accounts.
        
        Returns:
            List of account dictionaries, ordered by most recent first
            
        Example:
            >>> accounts = repo.list_accounts()
            >>> len(accounts)
            2
        """
        sql = """
            SELECT email, encrypted_password, provider, added_date
            FROM accounts ORDER BY added_date DESC
        """
        rows = self._fetch_all(sql)
        
        return [{
            'email': row[0],
            'encrypted_password': row[1],
            'provider': row[2],
            'added_date': row[3]
        } for row in rows]
    
    def delete_account(self, email: str) -> bool:
        """Delete account from database.
        
        Args:
            email: Email address to delete
            
        Returns:
            True if deleted, False if not found
            
        Example:
            >>> repo.delete_account('old@gmail.com')
            True
        """
        # Check if exists
        if not self.get_account(email):
            self.logger.info(f"Account not found: {email}")
            return False
        
        sql = "DELETE FROM accounts WHERE email = ?"
        self._execute_query(sql, (email,))
        self.logger.info(f"Account deleted: {email}")
        return True
    
    def get_primary_account(self) -> Optional[Dict]:
        """Get primary (first) account.
        
        Returns the most recently added account (first in list).
        
        Returns:
            First account dictionary or None if no accounts exist
            
        Example:
            >>> account = repo.get_primary_account()
            >>> account['email']
            'primary@gmail.com'
        """
        accounts = self.list_accounts()
        return accounts[0] if accounts else None

