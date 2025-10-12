"""Base repository class for database operations.

Provides common database connection management, transaction handling,
and query execution methods for all repository classes.
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import Any, List, Tuple, Optional


class BaseRepository:
    """Base class for database repositories.
    
    Handles connection management, transaction management, and provides
    protected methods for query execution with automatic commit/rollback.
    All methods use parameterized queries to prevent SQL injection.
    """
    
    def __init__(self, db_path: str):
        """Initialize the repository with database path.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with automatic transaction management.
        
        Context manager that handles connection lifecycle:
        - Opens connection
        - Commits on success
        - Rolls back on error
        - Always closes connection
        
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
    
    def _execute_query(self, sql: str, params: Tuple = ()) -> None:
        """Execute a query that doesn't return results.
        
        Args:
            sql: SQL query string with ? placeholders
            params: Tuple of parameters to bind to query
            
        Raises:
            sqlite3.Error: If query execution fails
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            self.logger.debug(f"Executed query: {sql[:50]}...")
    
    def _execute_many(self, sql: str, params_list: List[Tuple]) -> None:
        """Execute a query multiple times with different parameters.
        
        Useful for batch inserts/updates.
        
        Args:
            sql: SQL query string with ? placeholders
            params_list: List of parameter tuples
            
        Raises:
            sqlite3.Error: If query execution fails
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(sql, params_list)
            self.logger.debug(f"Executed batch query ({len(params_list)} rows): {sql[:50]}...")
    
    def _fetch_one(self, sql: str, params: Tuple = ()) -> Optional[Tuple]:
        """Fetch a single row from database.
        
        Args:
            sql: SQL query string with ? placeholders
            params: Tuple of parameters to bind to query
            
        Returns:
            Single row as tuple, or None if no results
            
        Raises:
            sqlite3.Error: If query execution fails
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            result = cursor.fetchone()
            self.logger.debug(f"Fetched one: {sql[:50]}... -> {result is not None}")
            return result
    
    def _fetch_all(self, sql: str, params: Tuple = ()) -> List[Tuple]:
        """Fetch all rows from database.
        
        Args:
            sql: SQL query string with ? placeholders
            params: Tuple of parameters to bind to query
            
        Returns:
            List of rows, each row as tuple
            
        Raises:
            sqlite3.Error: If query execution fails
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            results = cursor.fetchall()
            self.logger.debug(f"Fetched all: {sql[:50]}... -> {len(results)} rows")
            return results

