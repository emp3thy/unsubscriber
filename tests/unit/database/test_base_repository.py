"""Tests for BaseRepository class."""

import pytest
import sqlite3
import tempfile
import os
from src.database.base_repository import BaseRepository


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize with a simple table
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value INTEGER
        )
    """)
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def base_repo(temp_db):
    """Create a BaseRepository instance with temp database."""
    return BaseRepository(temp_db)


class TestBaseRepository:
    """Tests for BaseRepository class."""
    
    def test_init(self, temp_db):
        """Test repository initialization."""
        repo = BaseRepository(temp_db)
        
        assert repo.db_path == temp_db
        assert repo.logger is not None
    
    def test_execute_query_insert(self, base_repo):
        """Test _execute_query can insert data."""
        sql = "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)"
        params = (1, 'test', 100)
        
        # Should not raise
        base_repo._execute_query(sql, params)
        
        # Verify data inserted
        result = base_repo._fetch_one("SELECT * FROM test_table WHERE id = ?", (1,))
        assert result == (1, 'test', 100)
    
    def test_execute_query_update(self, base_repo):
        """Test _execute_query can update data."""
        # Insert first
        base_repo._execute_query(
            "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)",
            (1, 'test', 100)
        )
        
        # Update
        base_repo._execute_query(
            "UPDATE test_table SET value = ? WHERE id = ?",
            (200, 1)
        )
        
        # Verify updated
        result = base_repo._fetch_one("SELECT value FROM test_table WHERE id = ?", (1,))
        assert result == (200,)
    
    def test_execute_query_delete(self, base_repo):
        """Test _execute_query can delete data."""
        # Insert first
        base_repo._execute_query(
            "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)",
            (1, 'test', 100)
        )
        
        # Delete
        base_repo._execute_query("DELETE FROM test_table WHERE id = ?", (1,))
        
        # Verify deleted
        result = base_repo._fetch_one("SELECT * FROM test_table WHERE id = ?", (1,))
        assert result is None
    
    def test_execute_many(self, base_repo):
        """Test _execute_many can batch insert."""
        sql = "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)"
        params_list = [
            (1, 'test1', 100),
            (2, 'test2', 200),
            (3, 'test3', 300)
        ]
        
        base_repo._execute_many(sql, params_list)
        
        # Verify all inserted
        results = base_repo._fetch_all("SELECT * FROM test_table ORDER BY id")
        assert len(results) == 3
        assert results[0] == (1, 'test1', 100)
        assert results[1] == (2, 'test2', 200)
        assert results[2] == (3, 'test3', 300)
    
    def test_fetch_one_exists(self, base_repo):
        """Test _fetch_one returns row when exists."""
        # Insert data
        base_repo._execute_query(
            "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)",
            (1, 'test', 100)
        )
        
        # Fetch
        result = base_repo._fetch_one("SELECT * FROM test_table WHERE id = ?", (1,))
        
        assert result is not None
        assert result == (1, 'test', 100)
    
    def test_fetch_one_not_exists(self, base_repo):
        """Test _fetch_one returns None when no results."""
        result = base_repo._fetch_one("SELECT * FROM test_table WHERE id = ?", (999,))
        
        assert result is None
    
    def test_fetch_all_multiple_rows(self, base_repo):
        """Test _fetch_all returns all rows."""
        # Insert multiple rows
        params_list = [
            (1, 'test1', 100),
            (2, 'test2', 200),
            (3, 'test3', 300)
        ]
        base_repo._execute_many(
            "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)",
            params_list
        )
        
        # Fetch all
        results = base_repo._fetch_all("SELECT * FROM test_table ORDER BY id")
        
        assert len(results) == 3
        assert results[0] == (1, 'test1', 100)
        assert results[1] == (2, 'test2', 200)
        assert results[2] == (3, 'test3', 300)
    
    def test_fetch_all_empty(self, base_repo):
        """Test _fetch_all returns empty list when no results."""
        results = base_repo._fetch_all("SELECT * FROM test_table")
        
        assert results == []
    
    def test_parameterized_queries_prevent_injection(self, base_repo):
        """Test that parameterized queries prevent SQL injection."""
        # Insert test data
        base_repo._execute_query(
            "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)",
            (1, 'test', 100)
        )
        
        # Try SQL injection via parameter (should be treated as string)
        malicious_input = "1 OR 1=1"
        result = base_repo._fetch_one(
            "SELECT * FROM test_table WHERE id = ?",
            (malicious_input,)
        )
        
        # Should not find anything (injection prevented)
        assert result is None
    
    def test_transaction_rollback_on_error(self, base_repo):
        """Test that transactions rollback on error."""
        # Insert first record successfully
        base_repo._execute_query(
            "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)",
            (1, 'test1', 100)
        )
        
        # Try to insert duplicate id (should fail due to PRIMARY KEY)
        with pytest.raises(sqlite3.IntegrityError):
            base_repo._execute_query(
                "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)",
                (1, 'test2', 200)
            )
        
        # Verify only first record exists (second was rolled back)
        results = base_repo._fetch_all("SELECT * FROM test_table")
        assert len(results) == 1
        assert results[0] == (1, 'test1', 100)
    
    def test_connection_closed_after_operation(self, base_repo):
        """Test that connections are properly closed."""
        # Execute a query
        base_repo._execute_query(
            "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)",
            (1, 'test', 100)
        )
        
        # Should be able to execute another query (proves connection was closed properly)
        base_repo._execute_query(
            "INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)",
            (2, 'test2', 200)
        )
        
        # Verify both inserted
        results = base_repo._fetch_all("SELECT * FROM test_table ORDER BY id")
        assert len(results) == 2
    
    def test_get_connection_context_manager(self, base_repo):
        """Test _get_connection context manager directly."""
        with base_repo._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO test_table (id, name, value) VALUES (?, ?, ?)", (1, 'test', 100))
        
        # Verify data committed
        result = base_repo._fetch_one("SELECT * FROM test_table WHERE id = ?", (1,))
        assert result == (1, 'test', 100)

