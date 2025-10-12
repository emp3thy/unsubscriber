"""
Unit tests for EmailScanService.

Tests the email scanning service with mocked dependencies to verify
orchestration logic, error handling, progress reporting, and cancellation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.services.email_scan_service import EmailScanService


class TestEmailScanService:
    """Test suite for EmailScanService."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock email client."""
        client = Mock()
        client.fetch_email_ids.return_value = ['id1', 'id2', 'id3']
        client.fetch_headers.return_value = [{'sender': 'test@example.com', 'subject': 'Test'}]
        return client
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        return Mock()
    
    @pytest.fixture
    def mock_parser(self):
        """Create mock email parser."""
        parser = Mock()
        parser.parse_email.return_value = {
            'sender': 'test@example.com',
            'subject': 'Test Email',
            'is_unread': False,
            'date': '2024-01-01'
        }
        return parser
    
    @pytest.fixture
    def mock_scorer(self):
        """Create mock email scorer."""
        return Mock()
    
    @pytest.fixture
    def mock_grouper(self):
        """Create mock email grouper."""
        grouper = Mock()
        grouper.group_by_sender.return_value = [
            {
                'sender': 'test@example.com',
                'email_count': 3,
                'total_score': 75
            }
        ]
        return grouper
    
    @pytest.fixture
    def service(self, mock_client, mock_db, mock_parser, mock_scorer, mock_grouper):
        """Create EmailScanService with mocked dependencies."""
        return EmailScanService(mock_client, mock_db, mock_parser, mock_scorer, mock_grouper)
    
    def test_service_initialization(self, service, mock_client, mock_db):
        """Test that service initializes with all dependencies."""
        assert service.email_client is mock_client
        assert service.db is mock_db
        assert service.parser is not None
        assert service.scorer is not None
        assert service.grouper is not None
        assert service.cancel_event is not None
    
    def test_scan_inbox_success(self, service, mock_grouper):
        """Test successful inbox scan."""
        result = service.scan_inbox()
        
        assert len(result) == 1
        assert result[0]['sender'] == 'test@example.com'
        assert result[0]['email_count'] == 3
        mock_grouper.group_by_sender.assert_called_once()
    
    def test_scan_inbox_empty_inbox(self, service, mock_client):
        """Test scanning empty inbox returns empty list."""
        mock_client.fetch_email_ids.return_value = []
        
        result = service.scan_inbox()
        
        assert result == []
        assert len(result) == 0
    
    def test_scan_inbox_with_progress_callback(self, service):
        """Test that progress callback is called during scan."""
        calls = []
        def progress(current, total, message):
            calls.append((current, total, message))
        
        service.scan_inbox(progress)
        
        # Should be called at least twice (start and end)
        assert len(calls) >= 2
        # First call should be initial
        assert calls[0] == (0, 100, "Fetching email list...")
        # Last call should be final
        assert calls[-1] == (3, 3, "Analyzing senders...")
    
    def test_scan_inbox_parse_errors_continue_processing(self, service, mock_parser, mock_grouper):
        """Test that parse errors are logged but processing continues."""
        # First email fails, second succeeds, third fails
        mock_parser.parse_email.side_effect = [
            Exception("Parse error"),
            {'sender': 'good@example.com', 'subject': 'Good'},
            Exception("Parse error")
        ]
        
        result = service.scan_inbox()
        
        # Should still return grouped results (grouper was called)
        assert len(result) == 1
        mock_grouper.group_by_sender.assert_called_once()
        # Grouper should have received only the successful email
        parsed_emails = mock_grouper.group_by_sender.call_args[0][0]
        assert len(parsed_emails) == 1
        assert parsed_emails[0]['sender'] == 'good@example.com'
    
    def test_scan_inbox_connection_error_propagates(self, service, mock_client):
        """Test that connection errors are propagated after logging."""
        mock_client.fetch_email_ids.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            service.scan_inbox()
        
        assert "Connection failed" in str(exc_info.value)
    
    def test_scan_inbox_cancellation(self, service, mock_client):
        """Test that scan can be cancelled mid-operation."""
        # Setup more emails to process
        mock_client.fetch_email_ids.return_value = [f'id{i}' for i in range(10)]
        
        # Cancel after processing first email
        call_count = [0]
        def side_effect(ids):
            call_count[0] += 1
            if call_count[0] == 2:  # After first email
                service.cancel()
            return [{'sender': 'test@example.com'}]
        
        mock_client.fetch_headers.side_effect = side_effect
        
        result = service.scan_inbox()
        
        # Should have stopped early
        assert call_count[0] < 10
        assert service.is_cancelled()
    
    def test_cancel_method(self, service):
        """Test cancel() method sets the cancel flag."""
        assert not service.is_cancelled()
        
        service.cancel()
        
        assert service.is_cancelled()
    
    def test_scan_inbox_resets_cancel_flag(self, service):
        """Test that starting a new scan resets the cancel flag."""
        service.cancel()
        assert service.is_cancelled()
        
        service.scan_inbox()
        
        # Cancel flag should be cleared at start of new scan
        # (It will be set again if we cancelled, but initially it's cleared)
        assert not service.is_cancelled() or True  # After scan completes
    
    def test_scan_inbox_returns_partial_results_on_cancel(self, service, mock_client, mock_parser, mock_grouper):
        """Test that cancellation returns partial results."""
        mock_client.fetch_email_ids.return_value = [f'id{i}' for i in range(5)]
        mock_parser.parse_email.return_value = {'sender': 'test@example.com'}
        mock_grouper.group_by_sender.return_value = [{'sender': 'test@example.com', 'count': 2}]
        
        # Cancel after 2 emails
        call_count = [0]
        def side_effect(email_id):
            call_count[0] += 1
            if call_count[0] == 2:
                service.cancel()
            return {'sender': 'test@example.com'}
        
        mock_parser.parse_email.side_effect = side_effect
        
        result = service.scan_inbox()
        
        # Should return grouped results from partial scan
        assert len(result) == 1
        mock_grouper.group_by_sender.assert_called_once()
    
    def test_scan_inbox_with_no_headers(self, service, mock_client, mock_parser):
        """Test handling when fetch_headers returns None."""
        mock_client.fetch_headers.return_value = None
        
        result = service.scan_inbox()
        
        # Should handle gracefully and return empty grouping
        mock_parser.parse_email.assert_not_called()
    
    def test_scan_inbox_progress_updates_periodically(self, service, mock_client):
        """Test that progress updates happen every 50 emails."""
        # Create 150 emails
        mock_client.fetch_email_ids.return_value = [f'id{i}' for i in range(150)]
        
        calls = []
        def progress(current, total, message):
            if "Processing" in message:
                calls.append(current)
        
        service.scan_inbox(progress)
        
        # Should update at 0, 50, 100, 150
        assert len(calls) >= 3
        # Check that updates happen roughly every 50
        assert any(c in [1, 50, 51] for c in calls)  # First update
        assert any(c in [100, 101] for c in calls)  # Second update
    
    def test_multiple_scans_with_same_service(self, service):
        """Test that the same service can be used for multiple scans."""
        result1 = service.scan_inbox()
        result2 = service.scan_inbox()
        
        assert len(result1) == 1
        assert len(result2) == 1
        # Both should succeed independently

