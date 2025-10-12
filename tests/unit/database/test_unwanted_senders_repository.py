"""Tests for UnwantedSendersRepository class."""

import pytest
import tempfile
import os
import sqlite3
from src.database.unwanted_senders_repository import UnwantedSendersRepository


@pytest.fixture
def temp_db():
    """Create a temporary database with unwanted_senders table."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize with unwanted_senders table
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE unwanted_senders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            reason TEXT,
            failed_unsubscribe BOOLEAN DEFAULT 0,
            added_date DATETIME DEFAULT CURRENT_TIMESTAMP
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
def unwanted_repo(temp_db):
    """Create an UnwantedSendersRepository instance."""
    return UnwantedSendersRepository(temp_db)


class TestUnwantedSendersRepository:
    """Tests for UnwantedSendersRepository class."""
    
    def test_init(self, temp_db):
        """Test repository initialization."""
        repo = UnwantedSendersRepository(temp_db)
        
        assert repo.db_path == temp_db
        assert repo.logger is not None
    
    def test_add_to_must_delete(self, unwanted_repo):
        """Test adding sender to must-delete list."""
        unwanted_repo.add_to_must_delete('spam@example.com', 'No unsubscribe link')
        
        # Verify added
        senders = unwanted_repo.get_must_delete_senders()
        assert len(senders) == 1
        assert senders[0]['email'] == 'spam@example.com'
        assert senders[0]['reason'] == 'No unsubscribe link'
    
    def test_add_to_must_delete_updates_existing(self, unwanted_repo):
        """Test adding duplicate sender updates timestamp."""
        # Add first time
        unwanted_repo.add_to_must_delete('spam@example.com', 'First reason')
        
        # Add again with different reason (should update)
        unwanted_repo.add_to_must_delete('spam@example.com', 'Second reason')
        
        # Should still only have one entry with new reason
        senders = unwanted_repo.get_must_delete_senders()
        assert len(senders) == 1
        assert senders[0]['reason'] == 'Second reason'
    
    def test_get_must_delete_senders_empty(self, unwanted_repo):
        """Test getting must-delete senders when empty."""
        senders = unwanted_repo.get_must_delete_senders()
        
        assert senders == []
    
    def test_get_must_delete_senders_multiple(self, unwanted_repo):
        """Test getting multiple must-delete senders."""
        unwanted_repo.add_to_must_delete('spam1@example.com', 'Reason 1')
        unwanted_repo.add_to_must_delete('spam2@example.com', 'Reason 2')
        unwanted_repo.add_to_must_delete('spam3@example.com', 'Reason 3')
        
        senders = unwanted_repo.get_must_delete_senders()
        
        assert len(senders) == 3
        emails = {s['email'] for s in senders}
        assert 'spam1@example.com' in emails
        assert 'spam2@example.com' in emails
        assert 'spam3@example.com' in emails
    
    def test_get_must_delete_senders_returns_dicts(self, unwanted_repo):
        """Test must-delete senders returns typed dictionaries."""
        unwanted_repo.add_to_must_delete('spam@example.com', 'Test reason')
        
        senders = unwanted_repo.get_must_delete_senders()
        
        assert len(senders) == 1
        assert isinstance(senders[0], dict)
        assert 'email' in senders[0]
        assert 'reason' in senders[0]
        assert 'added_date' in senders[0]
    
    def test_get_must_delete_senders_default_reason(self, unwanted_repo):
        """Test must-delete senders shows 'Unknown' for null reasons."""
        # Add sender with no reason (None/null)
        sql = "INSERT INTO unwanted_senders (email, failed_unsubscribe) VALUES (?, 1)"
        unwanted_repo._execute_query(sql, ('spam@example.com',))
        
        senders = unwanted_repo.get_must_delete_senders()
        
        assert senders[0]['reason'] == 'Unknown'
    
    def test_remove_from_must_delete_exists(self, unwanted_repo):
        """Test removing sender from must-delete list."""
        # Add first
        unwanted_repo.add_to_must_delete('spam@example.com', 'Test')
        assert unwanted_repo.get_must_delete_count() == 1
        
        # Remove
        result = unwanted_repo.remove_from_must_delete('spam@example.com')
        
        assert result is True
        assert unwanted_repo.get_must_delete_count() == 0
    
    def test_remove_from_must_delete_not_exists(self, unwanted_repo):
        """Test removing non-existent sender returns False."""
        result = unwanted_repo.remove_from_must_delete('notfound@example.com')
        
        assert result is False
    
    def test_remove_from_must_delete_only_removes_must_delete(self, unwanted_repo):
        """Test remove only affects must-delete, not regular unwanted."""
        # Add regular unwanted sender (not must-delete)
        unwanted_repo.add_unwanted_sender('unwanted@example.com', 'Regular unwanted', False)
        
        # Try to remove from must-delete
        result = unwanted_repo.remove_from_must_delete('unwanted@example.com')
        
        # Should return False since not in must-delete list
        assert result is False
        # Should still be in unwanted list
        assert unwanted_repo.check_unwanted('unwanted@example.com') is True
    
    def test_get_must_delete_count_empty(self, unwanted_repo):
        """Test getting count when empty."""
        count = unwanted_repo.get_must_delete_count()
        
        assert count == 0
    
    def test_get_must_delete_count_with_data(self, unwanted_repo):
        """Test getting accurate count."""
        unwanted_repo.add_to_must_delete('spam1@example.com', 'Test 1')
        unwanted_repo.add_to_must_delete('spam2@example.com', 'Test 2')
        unwanted_repo.add_to_must_delete('spam3@example.com', 'Test 3')
        
        count = unwanted_repo.get_must_delete_count()
        
        assert count == 3
    
    def test_get_must_delete_count_excludes_regular_unwanted(self, unwanted_repo):
        """Test count only includes must-delete, not regular unwanted."""
        # Add must-delete
        unwanted_repo.add_to_must_delete('must@example.com', 'Must delete')
        # Add regular unwanted
        unwanted_repo.add_unwanted_sender('unwanted@example.com', 'Unwanted', False)
        
        count = unwanted_repo.get_must_delete_count()
        
        # Should only count the must-delete one
        assert count == 1
    
    def test_add_unwanted_sender_not_failed(self, unwanted_repo):
        """Test adding unwanted sender without failed unsubscribe."""
        unwanted_repo.add_unwanted_sender('unwanted@example.com', 'Suspicious', False)
        
        # Should be in unwanted list
        assert unwanted_repo.check_unwanted('unwanted@example.com') is True
        # Should NOT be in must-delete list
        assert unwanted_repo.get_must_delete_count() == 0
    
    def test_add_unwanted_sender_with_failed(self, unwanted_repo):
        """Test adding unwanted sender with failed unsubscribe."""
        unwanted_repo.add_unwanted_sender('spam@example.com', 'Failed unsub', True)
        
        # Should be in both unwanted and must-delete
        assert unwanted_repo.check_unwanted('spam@example.com') is True
        assert unwanted_repo.get_must_delete_count() == 1
    
    def test_add_unwanted_sender_duplicate_ignored(self, unwanted_repo):
        """Test adding duplicate unwanted sender is ignored."""
        # Add first time
        unwanted_repo.add_unwanted_sender('spam@example.com', 'First', False)
        
        # Add again (INSERT OR IGNORE should prevent duplicate)
        unwanted_repo.add_unwanted_sender('spam@example.com', 'Second', False)
        
        # Should still only have one
        assert unwanted_repo.check_unwanted('spam@example.com') is True
    
    def test_check_unwanted_exists(self, unwanted_repo):
        """Test checking unwanted sender that exists."""
        unwanted_repo.add_unwanted_sender('spam@example.com', 'Test', False)
        
        result = unwanted_repo.check_unwanted('spam@example.com')
        
        assert result is True
    
    def test_check_unwanted_not_exists(self, unwanted_repo):
        """Test checking unwanted sender that doesn't exist."""
        result = unwanted_repo.check_unwanted('notfound@example.com')
        
        assert result is False
    
    def test_check_unwanted_finds_must_delete(self, unwanted_repo):
        """Test check_unwanted finds must-delete senders too."""
        unwanted_repo.add_to_must_delete('spam@example.com', 'Test')
        
        # check_unwanted should find it
        assert unwanted_repo.check_unwanted('spam@example.com') is True
    
    def test_must_delete_workflow(self, unwanted_repo):
        """Test complete must-delete workflow."""
        # Add to must-delete
        unwanted_repo.add_to_must_delete('spam@example.com', 'No unsubscribe')
        
        # Verify in list
        senders = unwanted_repo.get_must_delete_senders()
        assert len(senders) == 1
        assert senders[0]['email'] == 'spam@example.com'
        
        # Verify count
        assert unwanted_repo.get_must_delete_count() == 1
        
        # Verify in unwanted check
        assert unwanted_repo.check_unwanted('spam@example.com') is True
        
        # Remove from must-delete
        assert unwanted_repo.remove_from_must_delete('spam@example.com') is True
        
        # Verify removed
        assert unwanted_repo.get_must_delete_count() == 0
        senders = unwanted_repo.get_must_delete_senders()
        assert len(senders) == 0

