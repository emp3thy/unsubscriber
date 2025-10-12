"""Tests for WhitelistRepository class."""

import pytest
import tempfile
import os
import sqlite3
from src.database.whitelist_repository import WhitelistRepository


@pytest.fixture
def temp_db():
    """Create a temporary database with whitelist table."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize with whitelist table
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE whitelist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            domain TEXT,
            notes TEXT,
            added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            CHECK (email IS NOT NULL OR domain IS NOT NULL)
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
def whitelist_repo(temp_db):
    """Create a WhitelistRepository instance."""
    return WhitelistRepository(temp_db)


class TestWhitelistRepository:
    """Tests for WhitelistRepository class."""
    
    def test_init(self, temp_db):
        """Test repository initialization."""
        repo = WhitelistRepository(temp_db)
        
        assert repo.db_path == temp_db
        assert repo.logger is not None
    
    def test_add_email_to_whitelist(self, whitelist_repo):
        """Test adding email to whitelist."""
        result = whitelist_repo.add_to_whitelist('test@example.com', is_domain=False, notes='Test email')
        
        assert result is True
        
        # Verify added
        assert whitelist_repo.check_whitelist('test@example.com') is True
    
    def test_add_domain_to_whitelist(self, whitelist_repo):
        """Test adding domain to whitelist."""
        result = whitelist_repo.add_to_whitelist('@company.com', is_domain=True, notes='Work domain')
        
        assert result is True
        
        # Verify domain pattern works
        assert whitelist_repo.check_whitelist('user@company.com') is True
        assert whitelist_repo.check_whitelist('admin@company.com') is True
    
    def test_add_duplicate_email_returns_false(self, whitelist_repo):
        """Test adding duplicate email returns False."""
        # Add first time
        result1 = whitelist_repo.add_to_whitelist('test@example.com')
        assert result1 is True
        
        # Add again
        result2 = whitelist_repo.add_to_whitelist('test@example.com')
        assert result2 is False
        
        # Should still only have one entry
        entries = whitelist_repo.get_whitelist()
        assert len(entries) == 1
    
    def test_add_duplicate_domain_returns_false(self, whitelist_repo):
        """Test adding duplicate domain returns False."""
        # Add first time
        result1 = whitelist_repo.add_to_whitelist('@company.com', is_domain=True)
        assert result1 is True
        
        # Add again
        result2 = whitelist_repo.add_to_whitelist('@company.com', is_domain=True)
        assert result2 is False
        
        # Should still only have one entry
        entries = whitelist_repo.get_whitelist()
        assert len(entries) == 1
    
    def test_check_whitelist_exact_email_match(self, whitelist_repo):
        """Test checking whitelist with exact email match."""
        whitelist_repo.add_to_whitelist('test@example.com')
        
        assert whitelist_repo.check_whitelist('test@example.com') is True
        assert whitelist_repo.check_whitelist('other@example.com') is False
    
    def test_check_whitelist_domain_pattern_match(self, whitelist_repo):
        """Test checking whitelist with domain pattern match."""
        whitelist_repo.add_to_whitelist('@company.com', is_domain=True)
        
        # All emails from @company.com should match
        assert whitelist_repo.check_whitelist('user@company.com') is True
        assert whitelist_repo.check_whitelist('admin@company.com') is True
        assert whitelist_repo.check_whitelist('test.user@company.com') is True
        
        # Other domains should not match
        assert whitelist_repo.check_whitelist('user@other.com') is False
    
    def test_check_whitelist_not_found(self, whitelist_repo):
        """Test checking whitelist returns False when not found."""
        result = whitelist_repo.check_whitelist('notfound@example.com')
        
        assert result is False
    
    def test_remove_from_whitelist_email(self, whitelist_repo):
        """Test removing email from whitelist."""
        # Add first
        whitelist_repo.add_to_whitelist('test@example.com')
        assert whitelist_repo.check_whitelist('test@example.com') is True
        
        # Remove
        result = whitelist_repo.remove_from_whitelist('test@example.com')
        assert result is True
        
        # Verify removed
        assert whitelist_repo.check_whitelist('test@example.com') is False
    
    def test_remove_from_whitelist_domain(self, whitelist_repo):
        """Test removing domain from whitelist."""
        # Add first
        whitelist_repo.add_to_whitelist('@company.com', is_domain=True)
        assert whitelist_repo.check_whitelist('user@company.com') is True
        
        # Remove
        result = whitelist_repo.remove_from_whitelist('@company.com')
        assert result is True
        
        # Verify removed
        assert whitelist_repo.check_whitelist('user@company.com') is False
    
    def test_remove_from_whitelist_not_found(self, whitelist_repo):
        """Test removing non-existent entry returns False."""
        result = whitelist_repo.remove_from_whitelist('notfound@example.com')
        
        assert result is False
    
    def test_get_whitelist_empty(self, whitelist_repo):
        """Test getting whitelist when empty."""
        entries = whitelist_repo.get_whitelist()
        
        assert entries == []
    
    def test_get_whitelist_multiple_entries(self, whitelist_repo):
        """Test getting whitelist with multiple entries."""
        # Add entries
        whitelist_repo.add_to_whitelist('test1@example.com', notes='First')
        whitelist_repo.add_to_whitelist('test2@example.com', notes='Second')
        whitelist_repo.add_to_whitelist('@company.com', is_domain=True, notes='Domain')
        
        entries = whitelist_repo.get_whitelist()
        
        assert len(entries) == 3
        # Check structure
        assert all('id' in e for e in entries)
        assert all('entry' in e for e in entries)
        assert all('type' in e for e in entries)
        assert all('notes' in e for e in entries)
        assert all('added_date' in e for e in entries)
        
        # Check types
        email_entries = [e for e in entries if e['type'] == 'email']
        domain_entries = [e for e in entries if e['type'] == 'domain']
        assert len(email_entries) == 2
        assert len(domain_entries) == 1
    
    def test_get_whitelist_entry_structure_email(self, whitelist_repo):
        """Test whitelist entry structure for email."""
        whitelist_repo.add_to_whitelist('test@example.com', notes='Test note')
        
        entries = whitelist_repo.get_whitelist()
        entry = entries[0]
        
        assert entry['entry'] == 'test@example.com'
        assert entry['type'] == 'email'
        assert entry['notes'] == 'Test note'
        assert 'id' in entry
        assert 'added_date' in entry
    
    def test_get_whitelist_entry_structure_domain(self, whitelist_repo):
        """Test whitelist entry structure for domain."""
        whitelist_repo.add_to_whitelist('@company.com', is_domain=True, notes='Work domain')
        
        entries = whitelist_repo.get_whitelist()
        entry = entries[0]
        
        assert entry['entry'] == '@company.com'
        assert entry['type'] == 'domain'
        assert entry['notes'] == 'Work domain'
        assert 'id' in entry
        assert 'added_date' in entry
    
    def test_get_whitelist_returns_all_entries(self, whitelist_repo):
        """Test whitelist returns all entries."""
        # Add multiple entries
        whitelist_repo.add_to_whitelist('first@example.com')
        whitelist_repo.add_to_whitelist('second@example.com')
        whitelist_repo.add_to_whitelist('third@example.com')
        
        entries = whitelist_repo.get_whitelist()
        
        # Should have all 3 entries
        assert len(entries) == 3
        emails = {e['entry'] for e in entries}
        assert 'first@example.com' in emails
        assert 'second@example.com' in emails
        assert 'third@example.com' in emails
    
    def test_add_without_notes(self, whitelist_repo):
        """Test adding entry without notes."""
        whitelist_repo.add_to_whitelist('test@example.com')
        
        entries = whitelist_repo.get_whitelist()
        assert entries[0]['notes'] == ''
    
    def test_check_whitelist_empty_email(self, whitelist_repo):
        """Test checking whitelist with empty email."""
        result = whitelist_repo.check_whitelist('')
        
        assert result is False

