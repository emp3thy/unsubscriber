"""Shared pytest fixtures and configuration."""

import pytest
from unittest.mock import Mock, MagicMock
from tests.fixtures.email_samples import (
    SAMPLE_EMAIL_FULL,
    SAMPLE_EMAIL_NO_UNSUB,
    SAMPLE_SENDER,
    SAMPLE_ACCOUNT
)


@pytest.fixture
def mock_db_manager():
    """Mock DBManager for testing.
    
    Returns a Mock object with common DBManager methods pre-configured.
    Tests can override specific return values as needed.
    """
    db = Mock()
    
    # Whitelist methods
    db.check_whitelist.return_value = False
    db.add_to_whitelist.return_value = True
    db.remove_from_whitelist.return_value = True
    db.get_whitelist.return_value = []
    
    # Account methods
    db.get_primary_account.return_value = SAMPLE_ACCOUNT.copy()
    db.add_account.return_value = True
    db.list_accounts.return_value = [SAMPLE_ACCOUNT.copy()]
    
    # Unwanted senders methods
    db.check_unwanted.return_value = False
    db.add_unwanted_sender.return_value = True
    db.get_must_delete_senders.return_value = []
    
    # Action history methods
    db.log_action.return_value = None
    db.log_unsubscribe_attempt.return_value = None
    db.get_action_history.return_value = []
    
    # Config methods
    db.get_config.return_value = None
    db.set_config.return_value = True
    
    return db


@pytest.fixture
def sample_email_data():
    """Sample email data for testing.
    
    Returns a complete email dictionary with all standard fields.
    Use .copy() when modifying to avoid affecting other tests.
    """
    return SAMPLE_EMAIL_FULL.copy()


@pytest.fixture
def mock_imap_connection():
    """Mock IMAP connection for testing.
    
    Returns a MagicMock configured to simulate IMAP4_SSL connection.
    """
    connection = MagicMock()
    
    # Common IMAP responses
    connection.select.return_value = ('OK', [b'100'])  # 100 emails in INBOX
    connection.search.return_value = ('OK', [b'1 2 3 4 5'])  # 5 email IDs
    connection.fetch.return_value = ('OK', [
        (b'1 (RFC822.HEADER {200}', b'From: test@example.com\r\nSubject: Test\r\n\r\n'),
        b')'
    ])
    connection.logout.return_value = ('BYE', [b'Logging out'])
    connection.close.return_value = ('OK', [b'CLOSE completed'])
    
    # Connection state
    connection.state = 'SELECTED'
    
    return connection


@pytest.fixture
def sample_sender_data():
    """Sample sender aggregate data for testing."""
    return SAMPLE_SENDER.copy()


@pytest.fixture
def sample_account_data():
    """Sample account data for testing."""
    return SAMPLE_ACCOUNT.copy()

