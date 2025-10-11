"""Sample test to verify pytest setup works correctly."""

import pytest


def test_pytest_works():
    """Verify basic pytest functionality."""
    assert True


def test_fixtures_available(mock_db_manager, sample_email_data, mock_imap_connection):
    """Verify that shared fixtures are available and work."""
    # Test mock_db_manager fixture
    assert mock_db_manager is not None
    assert mock_db_manager.check_whitelist('test@example.com') == False
    
    # Test sample_email_data fixture
    assert sample_email_data is not None
    assert 'sender' in sample_email_data
    assert sample_email_data['sender'] == 'newsletter@example.com'
    
    # Test mock_imap_connection fixture
    assert mock_imap_connection is not None
    status, data = mock_imap_connection.select('INBOX')
    assert status == 'OK'


def test_email_samples_importable():
    """Verify email samples can be imported."""
    from tests.fixtures.email_samples import (
        SAMPLE_EMAIL_FULL,
        SAMPLE_EMAIL_NO_UNSUB,
        SAMPLE_SENDER,
        SAMPLE_ACCOUNT
    )
    
    assert SAMPLE_EMAIL_FULL['sender'] == 'newsletter@example.com'
    assert SAMPLE_EMAIL_NO_UNSUB['unsubscribe_links'] == []
    assert SAMPLE_SENDER['email_count'] == 45
    assert SAMPLE_ACCOUNT['provider'] == 'gmail'


@pytest.mark.unit
def test_unit_marker():
    """Verify unit test marker works."""
    assert True


@pytest.mark.integration
def test_integration_marker():
    """Verify integration test marker works."""
    assert True

