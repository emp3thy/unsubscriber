"""Unit tests for EmailClientInterface."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.email_client.email_client_interface import EmailClientInterface
from src.email_client.imap_client import IMAPClient
from src.email_client.gmail_api_client import GmailAPIClient


class TestEmailClientInterface:
    """Test cases for EmailClientInterface."""
    
    def test_interface_is_abstract(self):
        """Test that interface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EmailClientInterface()
    
    def test_imap_client_implements_interface(self):
        """Test that IMAPClient implements EmailClientInterface."""
        assert issubclass(IMAPClient, EmailClientInterface)
    
    def test_gmail_client_implements_interface(self):
        """Test that GmailAPIClient implements EmailClientInterface."""
        assert issubclass(GmailAPIClient, EmailClientInterface)
    
    def test_interface_has_required_methods(self):
        """Test that interface defines all required methods."""
        required_methods = [
            'connect',
            'disconnect',
            'is_connected',
            'fetch_email_ids',
            'fetch_headers',
            'delete_emails_from_sender',
            'get_error_message',
            'get_email_count'
        ]
        
        for method in required_methods:
            assert hasattr(EmailClientInterface, method)
            assert callable(getattr(EmailClientInterface, method))
    
    @patch('imaplib.IMAP4_SSL')
    def test_imap_client_satisfies_interface(self, mock_imap):
        """Test that IMAPClient can be used through interface."""
        # Create IMAP client
        mock_auth = Mock()
        mock_auth.authenticate.return_value = True
        mock_auth.get_error_message.return_value = ""
        
        client: EmailClientInterface = IMAPClient(
            email='test@gmail.com',
            auth_strategy=mock_auth
        )
        
        # Verify all interface methods exist and are callable
        assert hasattr(client, 'connect')
        assert hasattr(client, 'disconnect')
        assert hasattr(client, 'is_connected')
        assert hasattr(client, 'fetch_email_ids')
        assert hasattr(client, 'fetch_headers')
        assert hasattr(client, 'delete_emails_from_sender')
        assert hasattr(client, 'get_error_message')
        assert hasattr(client, 'get_email_count')
    
    def test_gmail_client_satisfies_interface(self):
        """Test that GmailAPIClient can be used through interface."""
        mock_oauth = Mock()
        mock_oauth.get_oauth_tokens.return_value = None
        
        client: EmailClientInterface = GmailAPIClient(
            email='test@gmail.com',
            oauth_manager=mock_oauth
        )
        
        # Verify all interface methods exist and are callable
        assert hasattr(client, 'connect')
        assert hasattr(client, 'disconnect')
        assert hasattr(client, 'is_connected')
        assert hasattr(client, 'fetch_email_ids')
        assert hasattr(client, 'fetch_headers')
        assert hasattr(client, 'delete_emails_from_sender')
        assert hasattr(client, 'get_error_message')
        assert hasattr(client, 'get_email_count')


class MockEmailClient(EmailClientInterface):
    """Mock implementation of EmailClientInterface for testing."""
    
    def __init__(self):
        self.connected = False
        self.error_msg = ""
    
    def connect(self) -> bool:
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.connected = False
    
    def is_connected(self) -> bool:
        return self.connected
    
    def fetch_email_ids(self, limit: int = 500):
        return ['id1', 'id2', 'id3']
    
    def fetch_headers(self, message_ids):
        return [
            {'from': 'test@example.com', 'subject': 'Test'}
        ]
    
    def delete_emails_from_sender(self, sender_email: str, db_manager=None):
        return (5, f"Deleted 5 emails from {sender_email}")
    
    def get_error_message(self) -> str:
        return self.error_msg
    
    def get_email_count(self) -> int:
        return 100


class TestMockEmailClient:
    """Test that mock client correctly implements interface."""
    
    def test_mock_client_implements_interface(self):
        """Test that MockEmailClient implements EmailClientInterface."""
        assert issubclass(MockEmailClient, EmailClientInterface)
    
    def test_mock_client_can_be_instantiated(self):
        """Test that mock client can be instantiated."""
        client = MockEmailClient()
        assert isinstance(client, EmailClientInterface)
    
    def test_mock_client_connect(self):
        """Test mock client connect."""
        client = MockEmailClient()
        result = client.connect()
        assert result is True
        assert client.is_connected()
    
    def test_mock_client_disconnect(self):
        """Test mock client disconnect."""
        client = MockEmailClient()
        client.connect()
        client.disconnect()
        assert not client.is_connected()
    
    def test_mock_client_fetch_email_ids(self):
        """Test mock client fetch_email_ids."""
        client = MockEmailClient()
        ids = client.fetch_email_ids()
        assert ids == ['id1', 'id2', 'id3']
    
    def test_mock_client_fetch_headers(self):
        """Test mock client fetch_headers."""
        client = MockEmailClient()
        headers = client.fetch_headers(['id1'])
        assert len(headers) == 1
        assert headers[0]['from'] == 'test@example.com'
    
    def test_mock_client_delete_emails_from_sender(self):
        """Test mock client delete_emails_from_sender."""
        client = MockEmailClient()
        count, message = client.delete_emails_from_sender('test@example.com')
        assert count == 5
        assert 'Deleted' in message
    
    def test_mock_client_get_error_message(self):
        """Test mock client get_error_message."""
        client = MockEmailClient()
        assert client.get_error_message() == ""
    
    def test_mock_client_get_email_count(self):
        """Test mock client get_email_count."""
        client = MockEmailClient()
        assert client.get_email_count() == 100


class TestPolymorphicUsage:
    """Test polymorphic usage of email clients through interface."""
    
    def test_can_use_clients_through_interface_reference(self):
        """Test that clients can be used polymorphically through interface."""
        clients = []
        
        # Add mock client
        clients.append(MockEmailClient())
        
        # Test all clients through interface
        for client in clients:
            assert isinstance(client, EmailClientInterface)
            
            # Call interface methods
            result = client.connect()
            assert isinstance(result, bool)
            
            assert isinstance(client.is_connected(), bool)
            
            ids = client.fetch_email_ids(limit=10)
            assert isinstance(ids, list)
            
            headers = client.fetch_headers(ids[:1] if ids else [])
            assert isinstance(headers, list)
            
            count, msg = client.delete_emails_from_sender('test@example.com')
            assert isinstance(count, int)
            assert isinstance(msg, str)
            
            error = client.get_error_message()
            assert isinstance(error, str)
            
            email_count = client.get_email_count()
            assert isinstance(email_count, int)
            
            client.disconnect()
    
    def test_function_accepting_interface(self):
        """Test function that accepts EmailClientInterface."""
        def scan_emails(client: EmailClientInterface):
            """Function that works with any client implementing the interface."""
            if not client.is_connected():
                client.connect()
            
            ids = client.fetch_email_ids(limit=5)
            headers = client.fetch_headers(ids)
            return len(headers)
        
        # Test with mock client
        mock_client = MockEmailClient()
        result = scan_emails(mock_client)
        assert result == 1
        assert mock_client.is_connected()
    
    def test_service_with_injected_client(self):
        """Test service that uses injected client through interface."""
        class EmailService:
            def __init__(self, client: EmailClientInterface):
                self.client = client
            
            def get_sender_list(self):
                if not self.client.is_connected():
                    self.client.connect()
                ids = self.client.fetch_email_ids(limit=10)
                headers = self.client.fetch_headers(ids)
                return [h.get('from', '') for h in headers]
        
        # Test with mock client
        mock_client = MockEmailClient()
        service = EmailService(mock_client)
        senders = service.get_sender_list()
        
        assert len(senders) == 1
        assert senders[0] == 'test@example.com'


class TestInterfaceMethodSignatures:
    """Test that interface methods have correct signatures."""
    
    def test_connect_signature(self):
        """Test connect method signature."""
        client = MockEmailClient()
        result = client.connect()
        assert isinstance(result, bool)
    
    def test_disconnect_signature(self):
        """Test disconnect method signature (returns None)."""
        client = MockEmailClient()
        result = client.disconnect()
        assert result is None
    
    def test_is_connected_signature(self):
        """Test is_connected method signature."""
        client = MockEmailClient()
        result = client.is_connected()
        assert isinstance(result, bool)
    
    def test_fetch_email_ids_signature(self):
        """Test fetch_email_ids method signature."""
        client = MockEmailClient()
        # Test with default limit
        result1 = client.fetch_email_ids()
        assert isinstance(result1, list)
        
        # Test with explicit limit
        result2 = client.fetch_email_ids(limit=100)
        assert isinstance(result2, list)
    
    def test_fetch_headers_signature(self):
        """Test fetch_headers method signature."""
        client = MockEmailClient()
        result = client.fetch_headers(['id1', 'id2'])
        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], dict)
    
    def test_delete_emails_from_sender_signature(self):
        """Test delete_emails_from_sender method signature."""
        client = MockEmailClient()
        # Test with sender only
        count1, msg1 = client.delete_emails_from_sender('test@example.com')
        assert isinstance(count1, int)
        assert isinstance(msg1, str)
        
        # Test with db_manager
        count2, msg2 = client.delete_emails_from_sender('test@example.com', db_manager=None)
        assert isinstance(count2, int)
        assert isinstance(msg2, str)
    
    def test_get_error_message_signature(self):
        """Test get_error_message method signature."""
        client = MockEmailClient()
        result = client.get_error_message()
        assert isinstance(result, str)
    
    def test_get_email_count_signature(self):
        """Test get_email_count method signature."""
        client = MockEmailClient()
        result = client.get_email_count()
        assert isinstance(result, int)

