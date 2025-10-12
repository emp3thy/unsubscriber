"""Repository for whitelist operations.

Handles CRUD operations for whitelisted emails and domains.
"""

from typing import List, Dict
from .base_repository import BaseRepository


class WhitelistRepository(BaseRepository):
    """Repository for managing whitelist entries.
    
    Whitelisted emails and domains are protected from unsubscribe operations.
    Supports both exact email matches and domain pattern matches.
    """
    
    def add_to_whitelist(self, entry: str, is_domain: bool = False, notes: str = "") -> bool:
        """Add an email or domain to whitelist.
        
        Args:
            entry: Email address or domain pattern (e.g., '@company.com')
            is_domain: True if entry is a domain pattern
            notes: Optional notes about this entry
        
        Returns:
            True if added successfully, False if already exists
            
        Example:
            >>> repo.add_to_whitelist('important@example.com', notes='CEO')
            True
            >>> repo.add_to_whitelist('@company.com', is_domain=True, notes='Work domain')
            True
        """
        # Check for duplicates
        if is_domain:
            check_sql = "SELECT 1 FROM whitelist WHERE domain = ?"
        else:
            check_sql = "SELECT 1 FROM whitelist WHERE email = ?"
        
        if self._fetch_one(check_sql, (entry,)):
            self.logger.info(f"Entry already in whitelist: {entry}")
            return False
        
        # Insert
        if is_domain:
            sql = "INSERT INTO whitelist (domain, notes) VALUES (?, ?)"
        else:
            sql = "INSERT INTO whitelist (email, notes) VALUES (?, ?)"
        
        self._execute_query(sql, (entry, notes))
        self.logger.info(f"Added to whitelist: {entry} (domain={is_domain})")
        return True
    
    def check_whitelist(self, email: str) -> bool:
        """Check if email or its domain is whitelisted.
        
        Checks both exact email matches and domain pattern matches.
        For example, if '@company.com' is whitelisted, 'user@company.com' matches.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email or its domain is whitelisted, False otherwise
            
        Example:
            >>> repo.check_whitelist('important@example.com')
            True
            >>> repo.check_whitelist('user@company.com')  # If @company.com is whitelisted
            True
        """
        sql = """
            SELECT 1 FROM whitelist 
            WHERE email = ? 
            OR (domain IS NOT NULL AND ? LIKE '%' || domain)
            LIMIT 1
        """
        result = self._fetch_one(sql, (email, email))
        return result is not None
    
    def remove_from_whitelist(self, entry: str) -> bool:
        """Remove an entry from the whitelist.
        
        Removes by exact match on either email or domain field.
        
        Args:
            entry: Email address or domain to remove
            
        Returns:
            True if removed, False if not found
            
        Example:
            >>> repo.remove_from_whitelist('old@example.com')
            True
        """
        sql = "DELETE FROM whitelist WHERE email = ? OR domain = ?"
        
        # Check if exists before deleting
        check_sql = "SELECT 1 FROM whitelist WHERE email = ? OR domain = ?"
        if not self._fetch_one(check_sql, (entry, entry)):
            self.logger.info(f"Entry not found in whitelist: {entry}")
            return False
        
        self._execute_query(sql, (entry, entry))
        self.logger.info(f"Removed from whitelist: {entry}")
        return True
    
    def get_whitelist(self) -> List[Dict]:
        """Get all whitelist entries.
        
        Returns:
            List of dictionaries with keys: id, entry, type, notes, added_date
            - entry: The email address or domain
            - type: 'email' or 'domain'
            
        Example:
            >>> entries = repo.get_whitelist()
            >>> entries[0]
            {'id': 1, 'entry': 'ceo@company.com', 'type': 'email', 
             'notes': 'CEO', 'added_date': '2024-01-01 12:00:00'}
        """
        sql = """
            SELECT id, email, domain, notes, added_date
            FROM whitelist
            ORDER BY added_date DESC
        """
        rows = self._fetch_all(sql)
        
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

