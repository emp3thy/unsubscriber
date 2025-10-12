"""Unit tests for GmailConnectionManager."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from src.email_client.gmail_connection import GmailConnectionManager


class TestGmailConnectionManager:
    """Test cases for GmailConnectionManager."""
    
    @pytest.fixture
    def mock_oauth_manager(self):
        """Create mock OAuth manager."""
        manager = Mock()
        manager.get_oauth_tokens.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'token_expiry': None
        }
        
        # Mock gmail_oauth
        gmail_oauth = Mock()
        gmail_oauth._get_client_id.return_value = 'test_client_id'
        gmail_oauth._get_client_secret.return_value = 'test_client_secret'
        gmail_oauth.is_token_expired.return_value = False
        manager.gmail_oauth = gmail_oauth
        
        return manager
    
    @pytest.fixture
    def connection_manager(self, mock_oauth_manager):
        """Create connection manager with mock OAuth manager."""
        return GmailConnectionManager(
            email='test@gmail.com',
            oauth_manager=mock_oauth_manager
        )
    
    def test_init(self, mock_oauth_manager):
        """Test initialization."""
        manager = GmailConnectionManager(
            email='test@gmail.com',
            oauth_manager=mock_oauth_manager
        )
        
        assert manager.email == 'test@gmail.com'
        assert manager.oauth_manager == mock_oauth_manager
        assert manager.service is None
        assert manager.error_message is None
    
    @patch('src.email_client.gmail_connection.build')
    @patch('src.email_client.gmail_connection.Credentials')
    def test_connect_success(self, mock_credentials_class, mock_build, 
                            connection_manager, mock_oauth_manager):
        """Test successful connection."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_credentials = MagicMock()
        mock_credentials_class.return_value = mock_credentials
        
        result = connection_manager.connect()
        
        assert result is True
        assert connection_manager.is_connected()
        assert connection_manager.get_service() == mock_service
        mock_oauth_manager.get_oauth_tokens.assert_called_once_with('test@gmail.com')
    
    @patch('src.email_client.gmail_connection.build')
    @patch('src.email_client.gmail_connection.Credentials')
    @patch('src.email_client.gmail_connection.Request')
    def test_connect_with_token_refresh(self, mock_request_class, mock_credentials_class, 
                                       mock_build, connection_manager, mock_oauth_manager):
        """Test connection with expired token refresh."""
        # Setup expired token
        mock_oauth_manager.gmail_oauth.is_token_expired.return_value = True
        
        mock_credentials = MagicMock()
        mock_credentials.token = 'new_access_token'
        mock_credentials.refresh_token = 'new_refresh_token'
        mock_credentials.expiry = datetime.now() + timedelta(hours=1)
        mock_credentials_class.return_value = mock_credentials
        
        mock_request = MagicMock()
        mock_request_class.return_value = mock_request
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        result = connection_manager.connect()
        
        assert result is True
        mock_credentials.refresh.assert_called_once_with(mock_request)
        mock_oauth_manager.store_oauth_tokens.assert_called_once()
    
    def test_connect_no_tokens(self, connection_manager, mock_oauth_manager):
        """Test connection when no OAuth tokens available."""
        mock_oauth_manager.get_oauth_tokens.return_value = None
        
        result = connection_manager.connect()
        
        assert result is False
        assert not connection_manager.is_connected()
        assert "No OAuth tokens found" in connection_manager.get_error_message()
    
    @patch('src.email_client.gmail_connection.build')
    def test_connect_exception(self, mock_build, connection_manager):
        """Test connection with exception."""
        mock_build.side_effect = Exception("Connection error")
        
        result = connection_manager.connect()
        
        assert result is False
        assert not connection_manager.is_connected()
        assert "Failed to connect" in connection_manager.get_error_message()
    
    def test_disconnect(self, connection_manager):
        """Test disconnect."""
        mock_service = MagicMock()
        connection_manager.service = mock_service
        
        connection_manager.disconnect()
        
        assert connection_manager.service is None
        assert not connection_manager.is_connected()
    
    def test_disconnect_when_not_connected(self, connection_manager):
        """Test disconnect when not connected."""
        connection_manager.disconnect()  # Should not raise
        assert connection_manager.service is None
    
    def test_is_connected_true(self, connection_manager):
        """Test is_connected when connected."""
        connection_manager.service = MagicMock()
        assert connection_manager.is_connected() is True
    
    def test_is_connected_false(self, connection_manager):
        """Test is_connected when not connected."""
        connection_manager.service = None
        assert connection_manager.is_connected() is False
    
    def test_get_service(self, connection_manager):
        """Test get_service."""
        mock_service = MagicMock()
        connection_manager.service = mock_service
        
        assert connection_manager.get_service() == mock_service
    
    def test_get_service_when_not_connected(self, connection_manager):
        """Test get_service when not connected."""
        assert connection_manager.get_service() is None
    
    @patch('src.email_client.gmail_connection.build')
    @patch('src.email_client.gmail_connection.Credentials')
    def test_reconnect_success(self, mock_credentials_class, mock_build, 
                              connection_manager, mock_oauth_manager):
        """Test successful reconnection."""
        mock_service1 = MagicMock()
        mock_service2 = MagicMock()
        mock_build.side_effect = [mock_service1, mock_service2]
        mock_credentials_class.return_value = MagicMock()
        
        connection_manager.connect()
        result = connection_manager.reconnect()
        
        assert result is True
        assert connection_manager.get_service() == mock_service2
    
    @patch('src.email_client.gmail_connection.build')
    def test_reconnect_failure(self, mock_build, connection_manager):
        """Test reconnection failure."""
        mock_build.side_effect = Exception("Connection failed")
        
        result = connection_manager.reconnect()
        
        assert result is False
        assert not connection_manager.is_connected()
    
    def test_get_error_message_none(self, connection_manager):
        """Test getting error message when none set."""
        assert connection_manager.get_error_message() == ""
    
    def test_get_error_message_with_error(self, connection_manager):
        """Test getting error message when error set."""
        connection_manager.error_message = "Test error"
        assert connection_manager.get_error_message() == "Test error"
    
    @patch('src.email_client.gmail_connection.build')
    @patch('src.email_client.gmail_connection.Credentials')
    def test_credentials_created_correctly(self, mock_credentials_class, mock_build,
                                          connection_manager, mock_oauth_manager):
        """Test that Credentials object is created with correct parameters."""
        mock_credentials = MagicMock()
        mock_credentials_class.return_value = mock_credentials
        mock_build.return_value = MagicMock()
        
        connection_manager.connect()
        
        # Verify Credentials was called with correct arguments
        mock_credentials_class.assert_called_once()
        call_kwargs = mock_credentials_class.call_args[1]
        assert call_kwargs['token'] == 'test_access_token'
        assert call_kwargs['refresh_token'] == 'test_refresh_token'
        assert call_kwargs['token_uri'] == 'https://oauth2.googleapis.com/token'
        assert call_kwargs['client_id'] == 'test_client_id'
        assert call_kwargs['client_secret'] == 'test_client_secret'
        assert 'gmail.modify' in call_kwargs['scopes'][0]
    
    @patch('src.email_client.gmail_connection.build')
    @patch('src.email_client.gmail_connection.Credentials')
    def test_build_called_correctly(self, mock_credentials_class, mock_build,
                                   connection_manager):
        """Test that build is called with correct parameters."""
        mock_credentials = MagicMock()
        mock_credentials_class.return_value = mock_credentials
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        connection_manager.connect()
        
        # Verify build was called correctly
        mock_build.assert_called_once_with(
            'gmail', 'v1', 
            credentials=mock_credentials, 
            cache_discovery=False
        )

