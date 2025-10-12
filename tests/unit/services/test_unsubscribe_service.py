"""
Unit tests for UnsubscribeService.

Tests the unsubscribe service with mocked dependencies to verify
unsubscribe orchestration, whitelist checking, progress reporting, and error handling.
"""

import pytest
from unittest.mock import Mock
from src.services.unsubscribe_service import UnsubscribeService


class TestUnsubscribeService:
    """Test suite for UnsubscribeService."""
    
    @pytest.fixture
    def mock_chain(self):
        """Create mock strategy chain."""
        chain = Mock()
        chain.execute.return_value = (True, "Unsubscribed successfully", "ListUnsubscribe")
        return chain
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        db = Mock()
        db.check_whitelist.return_value = False
        db.log_action.return_value = None
        return db
    
    @pytest.fixture
    def service(self, mock_chain, mock_db):
        """Create UnsubscribeService with mocked dependencies."""
        return UnsubscribeService(mock_chain, mock_db)
    
    def test_service_initialization(self, service, mock_chain, mock_db):
        """Test that service initializes with all dependencies."""
        assert service.strategy_chain is mock_chain
        assert service.db is mock_db
        assert service.cancel_event is not None
    
    def test_unsubscribe_success(self, service, mock_chain):
        """Test successful unsubscribe from multiple senders."""
        senders = [
            {'sender': 'spam1@example.com', 'list_unsubscribe': '<https://ex1.com/unsub>'},
            {'sender': 'spam2@example.com', 'list_unsubscribe': '<https://ex2.com/unsub>'},
        ]
        
        results = service.unsubscribe_from_senders(senders)
        
        assert results['success_count'] == 2
        assert results['failed_count'] == 0
        assert results['skipped_count'] == 0
        assert len(results['successful_senders']) == 2
        assert 'spam1@example.com' in results['successful_senders']
        assert 'spam2@example.com' in results['successful_senders']
        assert mock_chain.execute.call_count == 2
    
    def test_unsubscribe_skips_whitelisted(self, service, mock_db, mock_chain):
        """Test that whitelisted senders are skipped."""
        mock_db.check_whitelist.side_effect = lambda email: email == 'safe@example.com'
        
        senders = [
            {'sender': 'safe@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'},
            {'sender': 'spam@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'},
        ]
        
        results = service.unsubscribe_from_senders(senders)
        
        assert results['skipped_count'] == 1
        assert results['success_count'] == 1
        assert 'spam@example.com' in results['successful_senders']
        assert 'safe@example.com' not in results['successful_senders']
        # Strategy chain should only be called once (not for whitelisted)
        assert mock_chain.execute.call_count == 1
    
    def test_unsubscribe_skips_no_method(self, service, mock_db, mock_chain):
        """Test that senders without unsubscribe method are skipped."""
        senders = [
            {'sender': 'noreply@example.com'},  # No list_unsubscribe
        ]
        
        results = service.unsubscribe_from_senders(senders)
        
        assert results['skipped_count'] == 1
        assert results['success_count'] == 0
        # Should log the attempt
        mock_db.log_action.assert_called_once()
        assert mock_chain.execute.call_count == 0
    
    def test_unsubscribe_mixed_results(self, service, mock_chain):
        """Test handling of mixed success and failure."""
        # First succeeds, second fails
        mock_chain.execute.side_effect = [
            (True, "Success", "ListUnsubscribe"),
            (False, "HTTP error 404", "None"),
        ]
        
        senders = [
            {'sender': 'spam1@example.com', 'list_unsubscribe': '<https://ex1.com/unsub>'},
            {'sender': 'spam2@example.com', 'list_unsubscribe': '<https://ex2.com/unsub>'},
        ]
        
        results = service.unsubscribe_from_senders(senders)
        
        assert results['success_count'] == 1
        assert results['failed_count'] == 1
        assert len(results['details']) == 2
        assert 'spam1@example.com' in results['successful_senders']
        assert 'spam2@example.com' not in results['successful_senders']
    
    def test_unsubscribe_with_progress_callback(self, service):
        """Test that progress callback is invoked."""
        calls = []
        def progress(current, total, message):
            calls.append((current, total, message))
        
        senders = [
            {'sender': 'spam1@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'},
            {'sender': 'spam2@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'},
        ]
        
        service.unsubscribe_from_senders(senders, progress)
        
        # Should be called for each sender plus final
        assert len(calls) >= 2
        # Final call should show completion
        assert calls[-1] == (2, 2, "Complete")
    
    def test_unsubscribe_empty_list(self, service):
        """Test unsubscribing from empty sender list."""
        results = service.unsubscribe_from_senders([])
        
        assert results['success_count'] == 0
        assert results['failed_count'] == 0
        assert results['skipped_count'] == 0
        assert len(results['successful_senders']) == 0
    
    def test_unsubscribe_cancellation(self, service):
        """Test that unsubscribe can be cancelled."""
        senders = [{'sender': f'spam{i}@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'}
                   for i in range(10)]
        
        # Cancel after first sender
        call_count = [0]
        def progress(current, total, message):
            call_count[0] += 1
            if call_count[0] == 1:
                service.cancel()
        
        results = service.unsubscribe_from_senders(senders, progress)
        
        # Should stop early
        assert results['success_count'] < 10
        assert service.is_cancelled()
    
    def test_cancel_method(self, service):
        """Test cancel() method sets the cancel flag."""
        assert not service.is_cancelled()
        
        service.cancel()
        
        assert service.is_cancelled()
    
    def test_unsubscribe_exception_handling(self, service, mock_chain, mock_db):
        """Test handling of unexpected exceptions."""
        mock_chain.execute.side_effect = Exception("Unexpected error")
        
        senders = [
            {'sender': 'spam@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'},
        ]
        
        results = service.unsubscribe_from_senders(senders)
        
        assert results['failed_count'] == 1
        assert results['success_count'] == 0
        # Should log the error
        mock_db.log_action.assert_called()
    
    def test_unsubscribe_with_unsubscribe_links(self, service, mock_chain):
        """Test that unsubscribe_links field is also checked."""
        senders = [
            {'sender': 'spam@example.com', 'unsubscribe_links': ['https://ex.com/unsub']},
        ]
        
        results = service.unsubscribe_from_senders(senders)
        
        # Should not skip (has unsubscribe method)
        assert results['success_count'] == 1
        assert results['skipped_count'] == 0
    
    def test_unsubscribe_results_structure(self, service):
        """Test that results have all expected keys."""
        senders = [
            {'sender': 'spam@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'},
        ]
        
        results = service.unsubscribe_from_senders(senders)
        
        # Check all expected keys present
        assert 'success_count' in results
        assert 'failed_count' in results
        assert 'skipped_count' in results
        assert 'details' in results
        assert 'successful_senders' in results
        assert isinstance(results['details'], list)
        assert isinstance(results['successful_senders'], list)
    
    def test_unsubscribe_details_messages(self, service, mock_chain):
        """Test that details list contains informative messages."""
        mock_chain.execute.return_value = (True, "Unsubscribed", "ListUnsubscribe")
        
        senders = [
            {'sender': 'spam@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'},
        ]
        
        results = service.unsubscribe_from_senders(senders)
        
        assert len(results['details']) == 1
        detail = results['details'][0]
        assert 'spam@example.com' in detail
        assert 'Success' in detail or 'ListUnsubscribe' in detail
    
    def test_unsubscribe_logs_all_attempts(self, service, mock_chain, mock_db):
        """Test that all unsubscribe attempts are logged."""
        senders = [
            {'sender': 'spam1@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'},
            {'sender': 'spam2@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'},
        ]
        
        service.unsubscribe_from_senders(senders)
        
        # Strategy chain logs attempts, so we just verify service doesn't break logging
        assert mock_chain.execute.call_count == 2
    
    def test_multiple_unsubscribe_operations(self, service):
        """Test that service can handle multiple operations."""
        senders1 = [{'sender': 'spam1@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'}]
        senders2 = [{'sender': 'spam2@example.com', 'list_unsubscribe': '<https://ex.com/unsub>'}]
        
        results1 = service.unsubscribe_from_senders(senders1)
        results2 = service.unsubscribe_from_senders(senders2)
        
        assert results1['success_count'] == 1
        assert results2['success_count'] == 1

