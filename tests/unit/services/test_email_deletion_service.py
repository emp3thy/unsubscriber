"""
Unit tests for EmailDeletionService.

Tests the email deletion service with mocked dependencies to verify
deletion orchestration, whitelist protection, progress reporting, and error handling.
"""

import pytest
from unittest.mock import Mock
from src.services.email_deletion_service import EmailDeletionService


class TestEmailDeletionService:
    """Test suite for EmailDeletionService."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock email client."""
        client = Mock()
        client.delete_emails_from_sender.return_value = (10, "Deleted 10 emails")
        return client
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        db = Mock()
        db.check_whitelist.return_value = False
        db.log_action.return_value = None
        db.remove_from_must_delete.return_value = None
        db.get_must_delete_senders.return_value = []
        return db
    
    @pytest.fixture
    def service(self, mock_client, mock_db):
        """Create EmailDeletionService with mocked dependencies."""
        return EmailDeletionService(mock_client, mock_db)
    
    def test_service_initialization(self, service, mock_client, mock_db):
        """Test that service initializes with all dependencies."""
        assert service.email_client is mock_client
        assert service.db is mock_db
        assert service.cancel_event is not None
    
    def test_delete_from_senders_success(self, service, mock_client):
        """Test successful deletion from multiple senders."""
        senders = [
            {'sender': 'spam1@example.com'},
            {'sender': 'spam2@example.com'},
        ]
        
        results = service.delete_from_senders(senders)
        
        assert results['deleted_senders'] == 2
        assert results['total_emails_deleted'] == 20  # 10 per sender
        assert results['failed_senders'] == 0
        assert results['skipped_senders'] == 0
        assert mock_client.delete_emails_from_sender.call_count == 2
    
    def test_delete_skips_whitelisted(self, service, mock_db, mock_client):
        """Test that whitelisted senders are protected from deletion."""
        mock_db.check_whitelist.side_effect = lambda email: email == 'safe@example.com'
        
        senders = [
            {'sender': 'safe@example.com'},
            {'sender': 'spam@example.com'},
        ]
        
        results = service.delete_from_senders(senders)
        
        assert results['skipped_senders'] == 1
        assert results['deleted_senders'] == 1
        # Client should only be called once (not for whitelisted)
        assert mock_client.delete_emails_from_sender.call_count == 1
        # Verify it was called with the spam sender, not the safe one
        call_args = mock_client.delete_emails_from_sender.call_args[0]
        assert call_args[0] == 'spam@example.com'
    
    def test_delete_no_emails_found(self, service, mock_client):
        """Test handling when sender has no emails."""
        mock_client.delete_emails_from_sender.return_value = (0, "No emails found")
        
        senders = [
            {'sender': 'noemails@example.com'},
        ]
        
        results = service.delete_from_senders(senders)
        
        assert results['deleted_senders'] == 0
        assert results['skipped_senders'] == 1
        assert results['total_emails_deleted'] == 0
    
    def test_delete_error_handling(self, service, mock_client, mock_db):
        """Test handling of deletion errors."""
        mock_client.delete_emails_from_sender.side_effect = Exception("Network error")
        
        senders = [
            {'sender': 'error@example.com'},
        ]
        
        results = service.delete_from_senders(senders)
        
        assert results['failed_senders'] == 1
        assert results['deleted_senders'] == 0
        # Should log the failure
        mock_db.log_action.assert_called()
    
    def test_delete_with_progress_callback(self, service):
        """Test that progress callback is invoked."""
        calls = []
        def progress(current, total, message):
            calls.append((current, total, message))
        
        senders = [
            {'sender': 'spam1@example.com'},
            {'sender': 'spam2@example.com'},
        ]
        
        service.delete_from_senders(senders, progress)
        
        # Should be called for each sender plus final
        assert len(calls) >= 2
        # Final call should show completion
        assert calls[-1] == (2, 2, "Complete")
    
    def test_delete_empty_list(self, service):
        """Test deleting from empty sender list."""
        results = service.delete_from_senders([])
        
        assert results['deleted_senders'] == 0
        assert results['failed_senders'] == 0
        assert results['skipped_senders'] == 0
        assert results['total_emails_deleted'] == 0
    
    def test_delete_cancellation(self, service):
        """Test that deletion can be cancelled."""
        senders = [{'sender': f'spam{i}@example.com'} for i in range(10)]
        
        # Cancel after first sender
        call_count = [0]
        def progress(current, total, message):
            call_count[0] += 1
            if call_count[0] == 1:
                service.cancel()
        
        results = service.delete_from_senders(senders, progress)
        
        # Should stop early
        assert results['deleted_senders'] < 10
        assert service.is_cancelled()
    
    def test_cancel_method(self, service):
        """Test cancel() method sets the cancel flag."""
        assert not service.is_cancelled()
        
        service.cancel()
        
        assert service.is_cancelled()
    
    def test_delete_removes_from_must_delete_list(self, service, mock_client, mock_db):
        """Test that successful deletion removes sender from must-delete list."""
        mock_client.delete_emails_from_sender.return_value = (5, "Deleted 5")
        
        senders = [
            {'sender': 'spam@example.com'},
        ]
        
        service.delete_from_senders(senders)
        
        # Should remove from must-delete list
        mock_db.remove_from_must_delete.assert_called_once_with('spam@example.com')
    
    def test_delete_logs_successful_deletion(self, service, mock_db):
        """Test that successful deletions are logged."""
        senders = [
            {'sender': 'spam@example.com'},
        ]
        
        service.delete_from_senders(senders)
        
        # Should log the action
        mock_db.log_action.assert_called()
        call_args = mock_db.log_action.call_args[0]
        assert call_args[0] == 'spam@example.com'
        assert call_args[1] == 'delete'
        assert call_args[2] is True  # success
    
    def test_delete_from_must_delete_list_success(self, service, mock_db, mock_client):
        """Test deleting from must-delete list."""
        mock_db.get_must_delete_senders.return_value = [
            {'sender': 'mustdelete1@example.com'},
            {'sender': 'mustdelete2@example.com'},
        ]
        mock_client.delete_emails_from_sender.return_value = (10, "Deleted 10")
        
        results = service.delete_from_must_delete_list()
        
        assert results['deleted_senders'] == 2
        assert results['total_emails_deleted'] == 20
        assert mock_client.delete_emails_from_sender.call_count == 2
    
    def test_delete_from_must_delete_list_empty(self, service, mock_db):
        """Test handling empty must-delete list."""
        mock_db.get_must_delete_senders.return_value = []
        
        results = service.delete_from_must_delete_list()
        
        assert results['deleted_senders'] == 0
        assert results['total_emails_deleted'] == 0
    
    def test_delete_from_must_delete_list_with_progress(self, service, mock_db):
        """Test that progress callback works with must-delete list."""
        mock_db.get_must_delete_senders.return_value = [
            {'sender': 'mustdelete@example.com'},
        ]
        
        calls = []
        def progress(current, total, message):
            calls.append((current, total, message))
        
        service.delete_from_must_delete_list(progress)
        
        assert len(calls) >= 1
    
    def test_delete_from_must_delete_list_error(self, service, mock_db):
        """Test error handling in must-delete list retrieval."""
        mock_db.get_must_delete_senders.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            service.delete_from_must_delete_list()
        
        assert "Database error" in str(exc_info.value)
    
    def test_delete_mixed_results(self, service, mock_client):
        """Test handling of mixed success and failure."""
        # First succeeds with 10, second succeeds with 5, third succeeds with 0 (skipped)
        mock_client.delete_emails_from_sender.side_effect = [
            (10, "Deleted 10"),
            (5, "Deleted 5"),
            (0, "No emails"),
        ]
        
        senders = [
            {'sender': 'spam1@example.com'},
            {'sender': 'spam2@example.com'},
            {'sender': 'spam3@example.com'},
        ]
        
        results = service.delete_from_senders(senders)
        
        assert results['deleted_senders'] == 2
        assert results['skipped_senders'] == 1
        assert results['total_emails_deleted'] == 15
    
    def test_delete_results_structure(self, service):
        """Test that results have all expected keys."""
        senders = [
            {'sender': 'spam@example.com'},
        ]
        
        results = service.delete_from_senders(senders)
        
        # Check all expected keys present
        assert 'deleted_senders' in results
        assert 'total_emails_deleted' in results
        assert 'failed_senders' in results
        assert 'skipped_senders' in results
        assert isinstance(results['deleted_senders'], int)
        assert isinstance(results['total_emails_deleted'], int)
    
    def test_multiple_deletion_operations(self, service):
        """Test that service can handle multiple operations."""
        senders1 = [{'sender': 'spam1@example.com'}]
        senders2 = [{'sender': 'spam2@example.com'}]
        
        results1 = service.delete_from_senders(senders1)
        results2 = service.delete_from_senders(senders2)
        
        assert results1['deleted_senders'] == 1
        assert results2['deleted_senders'] == 1
    
    def test_delete_with_must_delete_removal_error(self, service, mock_db, mock_client):
        """Test that must-delete removal errors are logged but don't stop processing."""
        mock_db.remove_from_must_delete.side_effect = Exception("Remove failed")
        mock_client.delete_emails_from_sender.return_value = (5, "Deleted 5")
        
        senders = [
            {'sender': 'spam@example.com'},
        ]
        
        # Should not raise, just log the error
        results = service.delete_from_senders(senders)
        
        assert results['deleted_senders'] == 1
        assert results['failed_senders'] == 0

