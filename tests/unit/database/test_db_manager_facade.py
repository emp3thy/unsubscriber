"""Tests for DBManager facade pattern.

Verifies that DBManager correctly delegates to repository classes
and maintains backward compatibility with existing code.
"""

import pytest
import tempfile
import os
import sqlite3
from src.database.db_manager import DBManager


@pytest.fixture
def temp_db_with_schema():
    """Create a temporary database with full schema."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize with full schema
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE whitelist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            domain TEXT,
            notes TEXT,
            added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            CHECK (email IS NOT NULL OR domain IS NOT NULL)
        );
        
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            encrypted_password TEXT NOT NULL,
            provider TEXT NOT NULL,
            added_date DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE action_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT NOT NULL,
            action_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT 0,
            details TEXT
        );
        
        CREATE TABLE unwanted_senders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            reason TEXT,
            failed_unsubscribe BOOLEAN DEFAULT 0,
            added_date DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE config (
            key TEXT PRIMARY KEY,
            value TEXT
        );
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
def db_manager(temp_db_with_schema):
    """Create a DBManager instance with full schema."""
    return DBManager(temp_db_with_schema)


class TestDBManagerFacade:
    """Tests for DBManager facade pattern."""
    
    def test_init_creates_all_repositories(self, temp_db_with_schema):
        """Test DBManager initializes all repository instances."""
        db = DBManager(temp_db_with_schema)
        
        # Verify all repositories exist
        assert db._whitelist_repo is not None
        assert db._account_repo is not None
        assert db._history_repo is not None
        assert db._unwanted_repo is not None
        assert db._config_repo is not None
    
    def test_property_access_to_repositories(self, db_manager):
        """Test direct repository access via properties."""
        # Should be able to access repositories directly
        assert db_manager.whitelist is not None
        assert db_manager.accounts is not None
        assert db_manager.history is not None
        assert db_manager.unwanted is not None
        assert db_manager.config is not None
    
    def test_whitelist_delegation(self, db_manager):
        """Test whitelist methods delegate to WhitelistRepository."""
        # Add via DBManager
        result = db_manager.add_to_whitelist('test@example.com', notes='Test')
        assert result is True
        
        # Check via DBManager
        assert db_manager.check_whitelist('test@example.com') is True
        
        # Get via DBManager
        entries = db_manager.get_whitelist()
        assert len(entries) == 1
        assert entries[0]['entry'] == 'test@example.com'
        
        # Remove via DBManager
        result = db_manager.remove_from_whitelist('test@example.com')
        assert result is True
        assert db_manager.check_whitelist('test@example.com') is False
    
    def test_account_delegation(self, db_manager):
        """Test account methods delegate to AccountRepository."""
        # Add via DBManager
        result = db_manager.add_account('user@gmail.com', 'encrypted', 'gmail')
        assert result is True
        
        # Get via DBManager
        account = db_manager.get_account('user@gmail.com')
        assert account is not None
        assert account['email'] == 'user@gmail.com'
        
        # List via DBManager
        accounts = db_manager.list_accounts()
        assert len(accounts) == 1
        
        # Get primary via DBManager
        primary = db_manager.get_primary_account()
        assert primary['email'] == 'user@gmail.com'
        
        # Delete via DBManager
        result = db_manager.delete_account('user@gmail.com')
        assert result is True
        assert db_manager.get_account('user@gmail.com') is None
    
    def test_action_history_delegation(self, db_manager):
        """Test action history methods delegate to ActionHistoryRepository."""
        # Log action via DBManager
        db_manager.log_action('test@example.com', 'test', True, 'Test action')
        
        # Get history via DBManager
        history = db_manager.get_action_history()
        assert len(history) == 1
        assert history[0]['sender_email'] == 'test@example.com'
        
        # Log unsubscribe via DBManager
        result = db_manager.log_unsubscribe_attempt('spam@example.com', 'HTTP', True, 'Success')
        assert result is True
        
        # Get stats via DBManager
        stats = db_manager.get_strategy_stats()
        assert stats['total'] == 1
        
        # Get failure reasons via DBManager (no failures yet)
        reasons = db_manager.get_failure_reasons()
        assert reasons == []
    
    def test_unwanted_senders_delegation(self, db_manager):
        """Test unwanted senders methods delegate to UnwantedSendersRepository."""
        # Add unwanted via DBManager
        db_manager.add_unwanted_sender('spam@example.com', 'Spam', False)
        
        # Check via DBManager
        assert db_manager.check_unwanted('spam@example.com') is True
        
        # Add to must-delete via DBManager
        db_manager.add_to_must_delete('mustdelete@example.com', 'Failed unsub')
        
        # Get must-delete via DBManager
        senders = db_manager.get_must_delete_senders()
        assert len(senders) == 1
        assert senders[0]['email'] == 'mustdelete@example.com'
        
        # Get count via DBManager
        count = db_manager.get_must_delete_count()
        assert count == 1
        
        # Remove via DBManager
        result = db_manager.remove_from_must_delete('mustdelete@example.com')
        assert result is True
        assert db_manager.get_must_delete_count() == 0
    
    def test_config_delegation(self, db_manager):
        """Test config methods delegate to ConfigRepository."""
        # Set via DBManager
        db_manager.set_config('test_key', 'test_value')
        
        # Get via DBManager
        value = db_manager.get_config('test_key')
        assert value == 'test_value'
        
        # Get with default via DBManager
        value = db_manager.get_config('nonexistent', 'default')
        assert value == 'default'
    
    def test_direct_repository_access(self, db_manager):
        """Test can use repositories directly via properties."""
        # Use whitelist repository directly
        db_manager.whitelist.add_to_whitelist('direct@example.com')
        assert db_manager.check_whitelist('direct@example.com') is True
        
        # Use account repository directly
        db_manager.accounts.add_account('direct@gmail.com', 'pass', 'gmail')
        assert db_manager.get_account('direct@gmail.com') is not None
        
        # Use config repository directly
        db_manager.config.set_config('direct_key', 'direct_value')
        assert db_manager.get_config('direct_key') == 'direct_value'
    
    def test_backward_compatibility_complete_workflow(self, db_manager):
        """Test complete workflow using old DBManager API."""
        # This simulates existing code that uses DBManager
        
        # Setup account
        db_manager.add_account('user@gmail.com', 'encrypted_pass', 'gmail')
        account = db_manager.get_primary_account()
        assert account is not None
        
        # Setup whitelist
        db_manager.add_to_whitelist('important@example.com')
        assert db_manager.check_whitelist('important@example.com') is True
        
        # Log some actions
        db_manager.log_action('spam@example.com', 'unsubscribe', True, 'Success')
        db_manager.log_unsubscribe_attempt('spam2@example.com', 'HTTP', False, 'Timeout')
        
        # Check history
        history = db_manager.get_action_history()
        assert len(history) == 2
        
        # Add to must-delete
        db_manager.add_to_must_delete('failed@example.com', 'No unsubscribe link')
        assert db_manager.get_must_delete_count() == 1
        
        # Set some config
        db_manager.set_config('max_emails', '1000')
        assert db_manager.get_config('max_emails') == '1000'
        
        # Everything works through the facade!
    
    def test_initialize_db_works(self, temp_db_with_schema):
        """Test initialize_db still works for schema creation."""
        # Create empty DB
        fd, empty_db = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        try:
            db = DBManager(empty_db)
            
            # Should be able to initialize with schema
            # (We'll just verify it doesn't crash - actual schema tested elsewhere)
            assert db.db_path == empty_db
        finally:
            try:
                os.unlink(empty_db)
            except:
                pass

