"""Tests for ActionHistoryRepository class."""

import pytest
import tempfile
import os
import sqlite3
from src.database.action_history_repository import ActionHistoryRepository


@pytest.fixture
def temp_db():
    """Create a temporary database with action_history table."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize with action_history table
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE action_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT NOT NULL,
            action_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT 0,
            details TEXT
        )
    """)
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def history_repo(temp_db):
    """Create an ActionHistoryRepository instance."""
    return ActionHistoryRepository(temp_db)


class TestActionHistoryRepository:
    """Tests for ActionHistoryRepository class."""
    
    def test_init(self, temp_db):
        """Test repository initialization."""
        repo = ActionHistoryRepository(temp_db)
        
        assert repo.db_path == temp_db
        assert repo.logger is not None
    
    def test_log_action(self, history_repo):
        """Test logging an action."""
        history_repo.log_action(
            'test@example.com',
            'unsubscribe',
            True,
            'Successfully unsubscribed'
        )
        
        # Verify logged
        history = history_repo.get_action_history()
        assert len(history) == 1
        assert history[0]['sender_email'] == 'test@example.com'
        assert history[0]['action_type'] == 'unsubscribe'
        assert history[0]['success'] is True
        assert history[0]['details'] == 'Successfully unsubscribed'
    
    def test_log_unsubscribe_attempt_success(self, history_repo):
        """Test logging successful unsubscribe attempt."""
        result = history_repo.log_unsubscribe_attempt(
            'spam@example.com',
            'ListUnsubscribe',
            True,
            'Success'
        )
        
        assert result is True
        
        # Verify logged with strategy format
        history = history_repo.get_action_history()
        assert len(history) == 1
        assert 'Strategy: ListUnsubscribe' in history[0]['details']
    
    def test_log_unsubscribe_attempt_failure(self, history_repo):
        """Test logging failed unsubscribe attempt."""
        history_repo.log_unsubscribe_attempt(
            'spam@example.com',
            'HTTP',
            False,
            'Network timeout'
        )
        
        history = history_repo.get_action_history()
        assert history[0]['success'] is False
        assert 'Network timeout' in history[0]['details']
    
    def test_get_action_history_empty(self, history_repo):
        """Test getting history when empty."""
        history = history_repo.get_action_history()
        
        assert history == []
    
    def test_get_action_history_with_limit(self, history_repo):
        """Test getting history with limit."""
        # Add 10 actions
        for i in range(10):
            history_repo.log_action(f'test{i}@example.com', 'test', True, 'test')
        
        # Get with limit
        history = history_repo.get_action_history(limit=5)
        
        assert len(history) == 5
    
    def test_get_action_history_returns_all(self, history_repo):
        """Test history returns all logged actions."""
        history_repo.log_action('first@example.com', 'test', True, 'First')
        history_repo.log_action('second@example.com', 'test', True, 'Second')
        history_repo.log_action('third@example.com', 'test', True, 'Third')
        
        history = history_repo.get_action_history()
        
        # Should have all 3 entries
        assert len(history) == 3
        emails = {h['sender_email'] for h in history}
        assert 'first@example.com' in emails
        assert 'second@example.com' in emails
        assert 'third@example.com' in emails
    
    def test_get_strategy_stats_empty(self, history_repo):
        """Test getting strategy stats when no data."""
        stats = history_repo.get_strategy_stats()
        
        assert stats['total'] == 0
        assert stats['successful'] == 0
        assert stats['failed'] == 0
        assert stats['by_strategy'] == {}
    
    def test_get_strategy_stats_with_data(self, history_repo):
        """Test getting strategy stats with successful and failed attempts."""
        # Log various attempts
        history_repo.log_unsubscribe_attempt('test1@example.com', 'ListUnsubscribe', True, 'Success')
        history_repo.log_unsubscribe_attempt('test2@example.com', 'ListUnsubscribe', True, 'Success')
        history_repo.log_unsubscribe_attempt('test3@example.com', 'ListUnsubscribe', False, 'Failed')
        history_repo.log_unsubscribe_attempt('test4@example.com', 'HTTP', True, 'Success')
        history_repo.log_unsubscribe_attempt('test5@example.com', 'HTTP', False, 'Timeout')
        
        stats = history_repo.get_strategy_stats()
        
        assert stats['total'] == 5
        assert stats['successful'] == 3
        assert stats['failed'] == 2
        assert 'ListUnsubscribe' in stats['by_strategy']
        assert 'HTTP' in stats['by_strategy']
    
    def test_get_failure_reasons_empty(self, history_repo):
        """Test getting failure reasons when no failures."""
        reasons = history_repo.get_failure_reasons()
        
        assert reasons == []
    
    def test_get_failure_reasons_with_data(self, history_repo):
        """Test getting common failure reasons."""
        # Log failures with different reasons
        history_repo.log_unsubscribe_attempt('test1@example.com', 'HTTP', False, 'Network timeout')
        history_repo.log_unsubscribe_attempt('test2@example.com', 'HTTP', False, 'Network timeout')
        history_repo.log_unsubscribe_attempt('test3@example.com', 'HTTP', False, 'Network timeout')
        history_repo.log_unsubscribe_attempt('test4@example.com', 'HTTP', False, 'Invalid URL')
        history_repo.log_unsubscribe_attempt('test5@example.com', 'HTTP', False, 'Invalid URL')
        
        reasons = history_repo.get_failure_reasons()
        
        assert len(reasons) == 2
        # Most common should be first
        assert reasons[0]['reason'] == 'Network timeout'
        assert reasons[0]['count'] == 3
        assert reasons[1]['reason'] == 'Invalid URL'
        assert reasons[1]['count'] == 2
    
    def test_get_actions_for_sender(self, history_repo):
        """Test getting all actions for specific sender."""
        # Log actions for multiple senders
        history_repo.log_action('target@example.com', 'unsubscribe', True, 'First')
        history_repo.log_action('other@example.com', 'delete', True, 'Other')
        history_repo.log_action('target@example.com', 'delete', True, 'Second')
        history_repo.log_action('target@example.com', 'unsubscribe', False, 'Third')
        
        actions = history_repo.get_actions_for_sender('target@example.com')
        
        assert len(actions) == 3
        assert all(a['sender_email'] == 'target@example.com' for a in actions)
    
    def test_get_actions_for_sender_not_found(self, history_repo):
        """Test getting actions for sender with no history."""
        actions = history_repo.get_actions_for_sender('notfound@example.com')
        
        assert actions == []
    
    def test_get_successful_actions(self, history_repo):
        """Test getting only successful actions of type."""
        # Log mixed success/failure
        history_repo.log_action('test1@example.com', 'unsubscribe', True, 'Success')
        history_repo.log_action('test2@example.com', 'unsubscribe', False, 'Failed')
        history_repo.log_action('test3@example.com', 'unsubscribe', True, 'Success')
        history_repo.log_action('test4@example.com', 'delete', True, 'Deleted')
        
        successful = history_repo.get_successful_actions('unsubscribe')
        
        assert len(successful) == 2
        assert all(a['success'] for a in successful)
        assert all(a['action_type'] == 'unsubscribe' for a in successful)
    
    def test_get_successful_actions_none(self, history_repo):
        """Test getting successful actions when none exist."""
        history_repo.log_action('test@example.com', 'unsubscribe', False, 'Failed')
        
        successful = history_repo.get_successful_actions('unsubscribe')
        
        assert successful == []
    
    def test_action_includes_timestamp(self, history_repo):
        """Test that logged actions include timestamp."""
        history_repo.log_action('test@example.com', 'test', True, 'Test')
        
        history = history_repo.get_action_history()
        
        assert 'timestamp' in history[0]
        assert history[0]['timestamp'] is not None

