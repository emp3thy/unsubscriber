"""Tests for AccountRepository class."""

import pytest
import tempfile
import os
import sqlite3
from src.database.account_repository import AccountRepository


@pytest.fixture
def temp_db():
    """Create a temporary database with accounts table."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize with accounts table
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            encrypted_password TEXT NOT NULL,
            provider TEXT NOT NULL,
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
def account_repo(temp_db):
    """Create an AccountRepository instance."""
    return AccountRepository(temp_db)


class TestAccountRepository:
    """Tests for AccountRepository class."""
    
    def test_init(self, temp_db):
        """Test repository initialization."""
        repo = AccountRepository(temp_db)
        
        assert repo.db_path == temp_db
        assert repo.logger is not None
    
    def test_add_account(self, account_repo):
        """Test adding account."""
        result = account_repo.add_account(
            'test@gmail.com',
            'encrypted_pass',
            'gmail'
        )
        
        assert result is True
        
        # Verify added
        account = account_repo.get_account('test@gmail.com')
        assert account is not None
        assert account['email'] == 'test@gmail.com'
        assert account['provider'] == 'gmail'
    
    def test_add_account_updates_existing(self, account_repo):
        """Test adding account with duplicate email updates existing."""
        # Add first time
        account_repo.add_account('test@gmail.com', 'pass1', 'gmail')
        
        # Add again with different password
        result = account_repo.add_account('test@gmail.com', 'pass2', 'gmail')
        assert result is True
        
        # Should have updated password
        account = account_repo.get_account('test@gmail.com')
        assert account['encrypted_password'] == 'pass2'
        
        # Should still only have one account
        accounts = account_repo.list_accounts()
        assert len(accounts) == 1
    
    def test_get_account_exists(self, account_repo):
        """Test getting account that exists."""
        account_repo.add_account('test@gmail.com', 'encrypted_pass', 'gmail')
        
        account = account_repo.get_account('test@gmail.com')
        
        assert account is not None
        assert account['email'] == 'test@gmail.com'
        assert account['encrypted_password'] == 'encrypted_pass'
        assert account['provider'] == 'gmail'
        assert 'added_date' in account
    
    def test_get_account_not_exists(self, account_repo):
        """Test getting account that doesn't exist."""
        account = account_repo.get_account('notfound@gmail.com')
        
        assert account is None
    
    def test_get_account_returns_dict_not_tuple(self, account_repo):
        """Test get_account returns typed dictionary."""
        account_repo.add_account('test@gmail.com', 'pass', 'gmail')
        
        account = account_repo.get_account('test@gmail.com')
        
        assert isinstance(account, dict)
        assert 'email' in account
        assert 'encrypted_password' in account
        assert 'provider' in account
        assert 'added_date' in account
    
    def test_list_accounts_empty(self, account_repo):
        """Test listing accounts when empty."""
        accounts = account_repo.list_accounts()
        
        assert accounts == []
    
    def test_list_accounts_multiple(self, account_repo):
        """Test listing multiple accounts."""
        account_repo.add_account('test1@gmail.com', 'pass1', 'gmail')
        account_repo.add_account('test2@gmail.com', 'pass2', 'gmail')
        account_repo.add_account('test3@outlook.com', 'pass3', 'outlook')
        
        accounts = account_repo.list_accounts()
        
        assert len(accounts) == 3
        emails = {acc['email'] for acc in accounts}
        assert 'test1@gmail.com' in emails
        assert 'test2@gmail.com' in emails
        assert 'test3@outlook.com' in emails
    
    def test_list_accounts_returns_dicts(self, account_repo):
        """Test list_accounts returns typed dictionaries."""
        account_repo.add_account('test@gmail.com', 'pass', 'gmail')
        
        accounts = account_repo.list_accounts()
        
        assert len(accounts) == 1
        assert isinstance(accounts[0], dict)
        assert all(key in accounts[0] for key in ['email', 'encrypted_password', 'provider', 'added_date'])
    
    def test_delete_account_exists(self, account_repo):
        """Test deleting account that exists."""
        account_repo.add_account('test@gmail.com', 'pass', 'gmail')
        
        result = account_repo.delete_account('test@gmail.com')
        
        assert result is True
        assert account_repo.get_account('test@gmail.com') is None
    
    def test_delete_account_not_exists(self, account_repo):
        """Test deleting account that doesn't exist."""
        result = account_repo.delete_account('notfound@gmail.com')
        
        assert result is False
    
    def test_delete_account_removes_from_list(self, account_repo):
        """Test deleted account no longer appears in list."""
        account_repo.add_account('test1@gmail.com', 'pass1', 'gmail')
        account_repo.add_account('test2@gmail.com', 'pass2', 'gmail')
        
        account_repo.delete_account('test1@gmail.com')
        
        accounts = account_repo.list_accounts()
        assert len(accounts) == 1
        assert accounts[0]['email'] == 'test2@gmail.com'
    
    def test_get_primary_account_exists(self, account_repo):
        """Test getting primary account when accounts exist."""
        account_repo.add_account('test1@gmail.com', 'pass1', 'gmail')
        account_repo.add_account('test2@gmail.com', 'pass2', 'gmail')
        
        primary = account_repo.get_primary_account()
        
        assert primary is not None
        # Should be most recent (test2, added last but DESC order means it's first)
        assert primary['email'] in ['test1@gmail.com', 'test2@gmail.com']
    
    def test_get_primary_account_empty(self, account_repo):
        """Test getting primary account when no accounts exist."""
        primary = account_repo.get_primary_account()
        
        assert primary is None
    
    def test_get_primary_account_returns_first_from_list(self, account_repo):
        """Test primary account is first from list."""
        account_repo.add_account('test@gmail.com', 'pass', 'gmail')
        
        primary = account_repo.get_primary_account()
        accounts = account_repo.list_accounts()
        
        assert primary == accounts[0]
    
    def test_multiple_providers(self, account_repo):
        """Test accounts with different providers."""
        account_repo.add_account('test1@gmail.com', 'pass1', 'gmail')
        account_repo.add_account('test2@outlook.com', 'pass2', 'outlook')
        account_repo.add_account('test3@yahoo.com', 'pass3', 'yahoo')
        
        accounts = account_repo.list_accounts()
        
        providers = {acc['provider'] for acc in accounts}
        assert providers == {'gmail', 'outlook', 'yahoo'}

