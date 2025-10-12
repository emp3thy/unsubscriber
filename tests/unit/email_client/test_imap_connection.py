"""Unit tests for IMAPConnectionManager."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import imaplib
from src.email_client.imap_connection import IMAPConnectionManager
from src.email_client.auth.auth_strategy import IMAPAuthStrategy


class TestIMAPConnectionManager:
    """Test cases for IMAPConnectionManager."""
    
    @pytest.fixture
    def mock_auth_strategy(self):
        """Create mock authentication strategy."""
        strategy = Mock(spec=IMAPAuthStrategy)
        strategy.authenticate.return_value = True
        strategy.get_error_message.return_value = ""
        return strategy
    
    @pytest.fixture
    def connection_manager(self, mock_auth_strategy):
        """Create connection manager with mock strategy."""
        return IMAPConnectionManager(
            email='test@gmail.com',
            auth_strategy=mock_auth_strategy
        )
    
    def test_init_with_gmail(self, mock_auth_strategy):
        """Test initialization with Gmail address."""
        manager = IMAPConnectionManager(
            email='test@gmail.com',
            auth_strategy=mock_auth_strategy
        )
        
        assert manager.email == 'test@gmail.com'
        assert manager.auth_strategy == mock_auth_strategy
        assert manager.provider == 'gmail'
        assert manager.connection is None
    
    def test_init_with_outlook(self, mock_auth_strategy):
        """Test initialization with Outlook address."""
        manager = IMAPConnectionManager(
            email='test@outlook.com',
            auth_strategy=mock_auth_strategy
        )
        
        assert manager.provider == 'outlook'
    
    def test_init_with_explicit_provider(self, mock_auth_strategy):
        """Test initialization with explicit provider."""
        manager = IMAPConnectionManager(
            email='test@custom.com',
            auth_strategy=mock_auth_strategy,
            provider='gmail'
        )
        
        assert manager.provider == 'gmail'
    
    def test_detect_provider_gmail(self, connection_manager):
        """Test Gmail provider detection."""
        assert connection_manager._detect_provider('test@gmail.com') == 'gmail'
        assert connection_manager._detect_provider('test@googlemail.com') == 'gmail'
    
    def test_detect_provider_outlook(self, connection_manager):
        """Test Outlook provider detection."""
        assert connection_manager._detect_provider('test@outlook.com') == 'outlook'
        assert connection_manager._detect_provider('test@hotmail.com') == 'outlook'
        assert connection_manager._detect_provider('test@live.com') == 'outlook'
    
    def test_detect_provider_unsupported(self, connection_manager):
        """Test detection of unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported email provider"):
            connection_manager._detect_provider('test@unknown.com')
    
    @patch('imaplib.IMAP4_SSL')
    def test_connect_success(self, mock_imap_class, connection_manager, mock_auth_strategy):
        """Test successful connection."""
        mock_connection = MagicMock()
        mock_imap_class.return_value = mock_connection
        
        result = connection_manager.connect()
        
        assert result is True
        assert connection_manager.is_connected()
        assert connection_manager.get_connection() == mock_connection
        mock_auth_strategy.authenticate.assert_called_once_with(mock_connection, 'test@gmail.com')
    
    @patch('imaplib.IMAP4_SSL')
    def test_connect_auth_failure(self, mock_imap_class, connection_manager, mock_auth_strategy):
        """Test connection with authentication failure."""
        mock_connection = MagicMock()
        mock_imap_class.return_value = mock_connection
        mock_auth_strategy.authenticate.return_value = False
        
        result = connection_manager.connect()
        
        assert result is False
        assert not connection_manager.is_connected()
        assert connection_manager.get_connection() is None
    
    @patch('imaplib.IMAP4_SSL')
    def test_connect_network_error(self, mock_imap_class, connection_manager):
        """Test connection with network error."""
        mock_imap_class.side_effect = Exception("Network error")
        
        result = connection_manager.connect()
        
        assert result is False
        assert not connection_manager.is_connected()
    
    def test_disconnect(self, connection_manager):
        """Test disconnect."""
        # Setup connected state
        mock_connection = MagicMock()
        connection_manager.connection = mock_connection
        
        connection_manager.disconnect()
        
        assert connection_manager.connection is None
        mock_connection.logout.assert_called_once()
    
    def test_disconnect_when_not_connected(self, connection_manager):
        """Test disconnect when not connected."""
        connection_manager.disconnect()  # Should not raise
        assert connection_manager.connection is None
    
    def test_disconnect_with_logout_error(self, connection_manager):
        """Test disconnect when logout fails."""
        mock_connection = MagicMock()
        mock_connection.logout.side_effect = Exception("Logout error")
        connection_manager.connection = mock_connection
        
        connection_manager.disconnect()  # Should not raise
        assert connection_manager.connection is None
    
    def test_is_connected_true(self, connection_manager):
        """Test is_connected when connected."""
        connection_manager.connection = MagicMock()
        assert connection_manager.is_connected() is True
    
    def test_is_connected_false(self, connection_manager):
        """Test is_connected when not connected."""
        connection_manager.connection = None
        assert connection_manager.is_connected() is False
    
    def test_get_connection(self, connection_manager):
        """Test get_connection."""
        mock_connection = MagicMock()
        connection_manager.connection = mock_connection
        
        assert connection_manager.get_connection() == mock_connection
    
    def test_get_connection_when_not_connected(self, connection_manager):
        """Test get_connection when not connected."""
        assert connection_manager.get_connection() is None
    
    @patch('imaplib.IMAP4_SSL')
    def test_reconnect_success(self, mock_imap_class, connection_manager, mock_auth_strategy):
        """Test successful reconnection."""
        # Setup initial connection
        mock_connection1 = MagicMock()
        mock_connection2 = MagicMock()
        mock_imap_class.side_effect = [mock_connection1, mock_connection2]
        
        connection_manager.connect()
        result = connection_manager.reconnect()
        
        assert result is True
        assert connection_manager.get_connection() == mock_connection2
        mock_connection1.logout.assert_called_once()
    
    @patch('imaplib.IMAP4_SSL')
    def test_reconnect_failure(self, mock_imap_class, connection_manager):
        """Test reconnection failure."""
        mock_imap_class.side_effect = Exception("Connection failed")
        
        result = connection_manager.reconnect()
        
        assert result is False
        assert not connection_manager.is_connected()
    
    def test_get_error_message(self, connection_manager, mock_auth_strategy):
        """Test getting error message from auth strategy."""
        mock_auth_strategy.get_error_message.return_value = "Auth failed"
        
        message = connection_manager.get_error_message()
        
        assert message == "Auth failed"
        mock_auth_strategy.get_error_message.assert_called_once()
    
    def test_init_with_unsupported_provider_raises(self, mock_auth_strategy):
        """Test initialization with unsupported email raises ValueError."""
        with pytest.raises(ValueError):
            IMAPConnectionManager(
                email='test@unknown.com',
                auth_strategy=mock_auth_strategy
            )
    
    @patch('imaplib.IMAP4_SSL')
    def test_connect_with_unknown_provider_raises(self, mock_imap_class, mock_auth_strategy):
        """Test connection with unknown provider fails."""
        manager = IMAPConnectionManager(
            email='test@gmail.com',
            auth_strategy=mock_auth_strategy
        )
        # Manually set invalid provider
        manager.provider = 'unknown'
        
        result = manager.connect()
        
        assert result is False

