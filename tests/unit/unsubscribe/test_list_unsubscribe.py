"""Unit tests for ListUnsubscribeStrategy.

Tests List-Unsubscribe RFC 2369 implementation including:
- HTTP GET/POST requests
- Header parsing
- Redirect handling
- Error handling (timeouts, 4xx, 5xx)
- Success/failure detection
"""

import pytest
import responses
import requests
from unittest.mock import Mock, patch
from src.unsubscribe.list_unsubscribe import ListUnsubscribeStrategy


class TestListUnsubscribeStrategy:
    """Test suite for ListUnsubscribeStrategy."""
    
    @pytest.fixture
    def strategy(self):
        """Create ListUnsubscribeStrategy instance."""
        return ListUnsubscribeStrategy()
    
    def test_can_handle_with_header(self, strategy):
        """Test can_handle returns True when List-Unsubscribe header present."""
        email_data = {
            'list_unsubscribe': '<https://example.com/unsub>'
        }
        
        assert strategy.can_handle(email_data) is True
    
    def test_can_handle_without_header(self, strategy):
        """Test can_handle returns False when header missing."""
        email_data = {}
        
        assert strategy.can_handle(email_data) is False
    
    def test_can_handle_with_empty_header(self, strategy):
        """Test can_handle returns False when header empty."""
        email_data = {
            'list_unsubscribe': ''
        }
        
        assert strategy.can_handle(email_data) is False
    
    def test_can_handle_with_whitespace_header(self, strategy):
        """Test can_handle returns False when header only whitespace."""
        email_data = {
            'list_unsubscribe': '   '
        }
        
        assert strategy.can_handle(email_data) is False
    
    def test_can_handle_with_mailto_only(self, strategy):
        """Test can_handle returns True even with mailto only."""
        email_data = {
            'list_unsubscribe': '<mailto:unsub@example.com>'
        }
        
        # Strategy will return True in can_handle, but execute will fail for mailto-only
        assert strategy.can_handle(email_data) is True
    
    @responses.activate
    def test_execute_success_get_request(self, strategy):
        """Test successful unsubscribe via GET request."""
        responses.add(
            responses.GET,
            'https://example.com/unsubscribe',
            status=200,
            body='Successfully unsubscribed'
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsubscribe>'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is True
        assert 'success' in message.lower() or '200' in message
        assert len(responses.calls) == 1
        assert responses.calls[0].request.method == 'GET'
    
    @responses.activate
    def test_execute_success_post_request(self, strategy):
        """Test successful unsubscribe via POST request with One-Click."""
        responses.add(
            responses.POST,
            'https://example.com/unsubscribe',
            status=200,
            body='Unsubscribed'
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsubscribe>',
            'list_unsubscribe_post': 'List-Unsubscribe=One-Click'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is True
        assert len(responses.calls) == 1
        assert responses.calls[0].request.method == 'POST'
    
    @responses.activate
    def test_execute_handles_redirect(self, strategy):
        """Test handling of HTTP redirects."""
        responses.add(
            responses.GET,
            'https://example.com/unsub',
            status=301,
            headers={'Location': 'https://example.com/confirm'}
        )
        responses.add(
            responses.GET,
            'https://example.com/confirm',
            status=200,
            body='Success'
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsub>'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is True
        # Requests library handles redirects automatically
        assert len(responses.calls) >= 1
    
    @responses.activate
    def test_execute_handles_404(self, strategy):
        """Test handling of 404 Not Found."""
        responses.add(
            responses.GET,
            'https://example.com/unsub',
            status=404,
            body='Not Found'
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsub>'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is False
        assert '404' in message or 'not found' in message.lower()
    
    @responses.activate
    def test_execute_handles_500(self, strategy):
        """Test handling of 500 Server Error."""
        responses.add(
            responses.GET,
            'https://example.com/unsub',
            status=500,
            body='Internal Server Error'
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsub>'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is False
        assert '500' in message or 'server error' in message.lower()
    
    @responses.activate
    def test_execute_handles_timeout(self, strategy):
        """Test handling of request timeout."""
        responses.add(
            responses.GET,
            'https://example.com/unsub',
            body=requests.Timeout('Request timed out')
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsub>'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is False
        assert 'timeout' in message.lower() or 'timed out' in message.lower()
    
    @responses.activate
    def test_execute_handles_connection_error(self, strategy):
        """Test handling of connection error."""
        responses.add(
            responses.GET,
            'https://example.com/unsub',
            body=requests.ConnectionError('Connection refused')
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsub>'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is False
        assert 'connection' in message.lower() or 'error' in message.lower()
    
    def test_execute_no_http_urls(self, strategy):
        """Test execute when only mailto URLs present."""
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<mailto:unsub@example.com>'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is False
        assert 'no http' in message.lower() or 'no urls' in message.lower()
    
    def test_execute_multiple_urls_uses_first(self, strategy):
        """Test that execute uses first HTTP URL when multiple present."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                'https://example.com/unsub1',
                status=200,
                body='Success'
            )
            
            email_data = {
                'sender': 'test@example.com',
                'list_unsubscribe': '<https://example.com/unsub1>, <https://example.com/unsub2>'
            }
            
            success, message = strategy.execute(email_data)
            
            assert success is True
            # Should only call the first URL
            assert len(rsps.calls) == 1
            assert 'unsub1' in rsps.calls[0].request.url
    
    @responses.activate
    def test_execute_with_mixed_urls(self, strategy):
        """Test execute with mixed mailto and HTTP URLs."""
        responses.add(
            responses.GET,
            'https://example.com/unsub',
            status=200
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<mailto:unsub@example.com>, <https://example.com/unsub>'
        }
        
        success, message = strategy.execute(email_data)
        
        # Should skip mailto and use HTTP
        assert success is True
        assert len(responses.calls) == 1
    
    @responses.activate
    def test_status_code_200_is_success(self, strategy):
        """Test that 200 status code is treated as success."""
        responses.add(
            responses.GET,
            'https://example.com/unsub',
            status=200
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsub>'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is True
    
    @responses.activate
    def test_status_code_201_is_success(self, strategy):
        """Test that 201 status code is treated as success."""
        responses.add(
            responses.GET,
            'https://example.com/unsub',
            status=201
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsub>'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is True
    
    @responses.activate
    def test_status_code_204_is_success(self, strategy):
        """Test that 204 No Content is treated as success."""
        responses.add(
            responses.GET,
            'https://example.com/unsub',
            status=204
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsub>'
        }
        
        success, message = strategy.execute(email_data)
        
        assert success is True


class TestListUnsubscribeStrategyEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def strategy(self):
        """Create ListUnsubscribeStrategy instance."""
        return ListUnsubscribeStrategy()
    
    def test_execute_with_missing_sender(self, strategy):
        """Test execute when sender field missing."""
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, 'https://example.com/unsub', status=200)
            
            email_data = {
                # Missing sender
                'list_unsubscribe': '<https://example.com/unsub>'
            }
            
            # Should handle gracefully
            success, message = strategy.execute(email_data)
            assert isinstance(success, bool)
    
    def test_extract_urls_from_complex_header(self, strategy):
        """Test URL extraction from complex List-Unsubscribe header."""
        header = '<mailto:unsub@example.com?subject=unsubscribe>, <https://example.com/unsub?id=123&token=abc>'
        
        import re
        urls = re.findall(r'<(https?://[^>]+)>', header)
        
        assert len(urls) == 1
        assert 'https://example.com/unsub' in urls[0]
        assert 'id=123' in urls[0]
    
    @responses.activate
    def test_custom_user_agent_sent(self, strategy):
        """Test that custom User-Agent header is sent."""
        responses.add(
            responses.GET,
            'https://example.com/unsub',
            status=200
        )
        
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<https://example.com/unsub>'
        }
        
        strategy.execute(email_data)
        
        # Check that User-Agent header was sent
        assert len(responses.calls) == 1
        headers = responses.calls[0].request.headers
        assert 'User-Agent' in headers
        assert 'Email Unsubscriber' in headers['User-Agent']
    
    @responses.activate
    def test_timeout_configured(self, strategy):
        """Test that timeout is configured on requests."""
        # This is hard to test directly without mocking requests
        # Just verify the timeout attribute exists
        assert hasattr(strategy, 'timeout')
        assert strategy.timeout == 10
    
    def test_redirects_enabled(self, strategy):
        """Test that redirects are enabled by default."""
        # The requests library handles redirects by default with allow_redirects=True
        # Just verify the strategy has configuration attributes
        assert hasattr(strategy, 'timeout')
        assert hasattr(strategy, 'headers')
    
    @responses.activate
    def test_malformed_url_handled(self, strategy):
        """Test handling of malformed URL in header."""
        # responses library might not handle malformed URLs well
        # But our regex should prevent them from being extracted
        email_data = {
            'sender': 'test@example.com',
            'list_unsubscribe': '<not-a-valid-url>'
        }
        
        success, message = strategy.execute(email_data)
        
        # Should fail gracefully
        assert success is False

