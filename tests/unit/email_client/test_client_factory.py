"""Unit tests for email client factory.

Tests client creation logic including:
- Provider detection from email domain
- Gmail API vs IMAP client selection
- OAuth token availability checking
- Error handling for invalid accounts
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.email_client.client_factory import create_email_client
from src.email_client.gmail_api_client import GmailAPIClient
from src.email_client.imap_client import IMAPClient


class TestClientFactory:
    """Test suite for create_email_client factory function."""
    
    @pytest.fixture
    def mock_auth_factory(self):
        """Create mock authentication factory."""
        factory = Mock()
        mock_strategy = Mock()
        factory.create_strategy.return_value = mock_strategy
        return factory
    
    @pytest.fixture
    def mock_oauth_manager(self):
        """Create mock OAuth manager."""
        manager = Mock()
        manager.get_oauth_tokens.return_value = None  # Default: no tokens
        return manager
    
    def test_create_gmail_client_with_oauth(self, mock_auth_factory, mock_oauth_manager):
        """Test creating Gmail API client when OAuth tokens available."""
        account = {
            'email': 'user@gmail.com',
            'provider': 'gmail',
            'encrypted_password': 'encrypted123'
        }
        
        # Setup OAuth manager to return tokens
        mock_oauth_manager.get_oauth_tokens.return_value = {
            'access_token': 'token123',
            'refresh_token': 'refresh123'
        }
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        # Should create Gmail API client
        assert isinstance(client, GmailAPIClient)
        assert client.email == 'user@gmail.com'
        # Should not call auth_factory for OAuth
        mock_auth_factory.create_strategy.assert_not_called()
    
    def test_create_imap_client_for_gmail_without_oauth(self, mock_auth_factory, mock_oauth_manager):
        """Test creating IMAP client for Gmail when no OAuth tokens."""
        account = {
            'email': 'user@gmail.com',
            'provider': 'gmail',
            'encrypted_password': 'encrypted123'
        }
        
        # No OAuth tokens available
        mock_oauth_manager.get_oauth_tokens.return_value = None
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        # Should fall back to IMAP client
        assert isinstance(client, IMAPClient)
        assert client.email == 'user@gmail.com'
        # Should call auth_factory to create strategy
        mock_auth_factory.create_strategy.assert_called_once_with(
            'user@gmail.com', 'gmail', 'encrypted123'
        )
    
    def test_create_imap_client_for_outlook(self, mock_auth_factory, mock_oauth_manager):
        """Test creating IMAP client for Outlook account."""
        account = {
            'email': 'user@outlook.com',
            'provider': 'outlook',
            'encrypted_password': 'encrypted123'
        }
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        # Should create IMAP client
        assert isinstance(client, IMAPClient)
        assert client.email == 'user@outlook.com'
        assert client.provider == 'outlook'
        mock_auth_factory.create_strategy.assert_called_once_with(
            'user@outlook.com', 'outlook', 'encrypted123'
        )
    
    def test_detect_gmail_provider_from_email(self, mock_auth_factory, mock_oauth_manager):
        """Test automatic Gmail provider detection from email domain."""
        account = {
            'email': 'user@gmail.com',
            'encrypted_password': 'encrypted123'
            # No provider specified
        }
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        # Should detect gmail provider and create IMAP client (no OAuth)
        assert isinstance(client, IMAPClient)
        assert client.provider == 'gmail'
    
    def test_detect_googlemail_provider(self, mock_auth_factory, mock_oauth_manager):
        """Test automatic provider detection for @googlemail.com."""
        account = {
            'email': 'user@googlemail.com',
            'encrypted_password': 'encrypted123'
        }
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        # Should detect gmail provider
        assert isinstance(client, IMAPClient)
        assert client.provider == 'gmail'
    
    def test_detect_outlook_provider_from_email(self, mock_auth_factory, mock_oauth_manager):
        """Test automatic Outlook provider detection from email domain."""
        test_domains = ['@outlook.com', '@hotmail.com', '@live.com']
        
        for domain in test_domains:
            account = {
                'email': f'user{domain}',
                'encrypted_password': 'encrypted123'
            }
            
            client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
            
            assert isinstance(client, IMAPClient)
            assert client.provider == 'outlook'
    
    def test_detect_yahoo_provider_from_email(self, mock_auth_factory, mock_oauth_manager):
        """Test automatic Yahoo provider detection from email domain."""
        account = {
            'email': 'user@yahoo.com',
            'encrypted_password': 'encrypted123'
        }
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        assert isinstance(client, IMAPClient)
        assert client.provider == 'yahoo'
    
    def test_generic_provider_for_unknown_domain(self, mock_auth_factory, mock_oauth_manager):
        """Test generic provider used for unknown email domains."""
        account = {
            'email': 'user@company.com',
            'encrypted_password': 'encrypted123'
        }
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        assert isinstance(client, IMAPClient)
        assert client.provider == 'generic'
    
    def test_provider_override(self, mock_auth_factory, mock_oauth_manager):
        """Test that explicit provider overrides auto-detection."""
        account = {
            'email': 'user@gmail.com',
            'provider': 'generic',  # Override auto-detection
            'encrypted_password': 'encrypted123'
        }
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        # Should use explicit provider, not auto-detect
        assert client.provider == 'generic'
    
    def test_raise_error_for_missing_email(self, mock_auth_factory, mock_oauth_manager):
        """Test that missing email raises ValueError."""
        account = {
            'provider': 'gmail',
            'encrypted_password': 'encrypted123'
            # Missing email
        }
        
        with pytest.raises(ValueError, match="Account email is required"):
            create_email_client(account, mock_auth_factory, mock_oauth_manager)
    
    def test_raise_error_for_empty_email(self, mock_auth_factory, mock_oauth_manager):
        """Test that empty email raises ValueError."""
        account = {
            'email': '',
            'provider': 'gmail',
            'encrypted_password': 'encrypted123'
        }
        
        with pytest.raises(ValueError, match="Account email is required"):
            create_email_client(account, mock_auth_factory, mock_oauth_manager)
    
    def test_case_insensitive_provider(self, mock_auth_factory, mock_oauth_manager):
        """Test that provider comparison is case-insensitive."""
        account = {
            'email': 'user@gmail.com',
            'provider': 'GMAIL',  # Uppercase
            'encrypted_password': 'encrypted123'
        }
        
        # Should still work with uppercase provider
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        assert isinstance(client, IMAPClient)
    
    def test_case_insensitive_email_domain(self, mock_auth_factory, mock_oauth_manager):
        """Test that email domain detection is case-insensitive."""
        account = {
            'email': 'USER@GMAIL.COM',  # Uppercase
            'encrypted_password': 'encrypted123'
        }
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        # Should detect gmail provider despite uppercase
        assert client.provider == 'gmail'
    
    def test_handle_account_without_password(self, mock_auth_factory, mock_oauth_manager):
        """Test handling account without encrypted_password field."""
        account = {
            'email': 'user@outlook.com',
            'provider': 'outlook'
            # No encrypted_password
        }
        
        # Should still create client, passing None for password
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        assert isinstance(client, IMAPClient)
        mock_auth_factory.create_strategy.assert_called_once_with(
            'user@outlook.com', 'outlook', None
        )
    
    def test_gmail_with_explicit_provider_and_oauth(self, mock_auth_factory, mock_oauth_manager):
        """Test Gmail client with explicit provider set and OAuth available."""
        account = {
            'email': 'user@gmail.com',
            'provider': 'gmail',
            'encrypted_password': 'encrypted123'
        }
        
        mock_oauth_manager.get_oauth_tokens.return_value = {'access_token': 'token'}
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        # Should use Gmail API
        assert isinstance(client, GmailAPIClient)
    
    def test_multiple_client_creation(self, mock_auth_factory, mock_oauth_manager):
        """Test creating multiple clients with same factory."""
        accounts = [
            {'email': 'user1@gmail.com', 'provider': 'gmail', 'encrypted_password': 'pwd1'},
            {'email': 'user2@outlook.com', 'provider': 'outlook', 'encrypted_password': 'pwd2'},
            {'email': 'user3@yahoo.com', 'provider': 'yahoo', 'encrypted_password': 'pwd3'}
        ]
        
        clients = [
            create_email_client(account, mock_auth_factory, mock_oauth_manager)
            for account in accounts
        ]
        
        # All should be IMAP clients (no OAuth)
        assert all(isinstance(client, IMAPClient) for client in clients)
        assert clients[0].provider == 'gmail'
        assert clients[1].provider == 'outlook'
        assert clients[2].provider == 'yahoo'


class TestClientFactoryEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def mock_auth_factory(self):
        """Create mock authentication factory."""
        factory = Mock()
        mock_strategy = Mock()
        factory.create_strategy.return_value = mock_strategy
        return factory
    
    @pytest.fixture
    def mock_oauth_manager(self):
        """Create mock OAuth manager."""
        manager = Mock()
        manager.get_oauth_tokens.return_value = None
        return manager
    
    def test_account_with_extra_fields(self, mock_auth_factory, mock_oauth_manager):
        """Test that extra account fields don't break client creation."""
        account = {
            'email': 'user@gmail.com',
            'provider': 'gmail',
            'encrypted_password': 'encrypted123',
            'extra_field1': 'value1',
            'extra_field2': 'value2'
        }
        
        # Should ignore extra fields
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        assert isinstance(client, IMAPClient)
    
    def test_email_with_plus_addressing(self, mock_auth_factory, mock_oauth_manager):
        """Test email with plus addressing (e.g., user+tag@gmail.com)."""
        account = {
            'email': 'user+tag@gmail.com',
            'encrypted_password': 'encrypted123'
        }
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        # Should still detect gmail provider
        assert client.provider == 'gmail'
        assert client.email == 'user+tag@gmail.com'
    
    def test_email_with_subdomain(self, mock_auth_factory, mock_oauth_manager):
        """Test email with subdomain (e.g., user@mail.company.com)."""
        account = {
            'email': 'user@mail.company.com',
            'encrypted_password': 'encrypted123'
        }
        
        client = create_email_client(account, mock_auth_factory, mock_oauth_manager)
        
        # Should use generic provider
        assert client.provider == 'generic'

