"""Unit tests for StrategyChain.

Tests Chain of Responsibility pattern including:
- Strategy ordering and execution
- Fallback behavior
- Success on first match
- Logging to database
- Handling of no strategies
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.unsubscribe.strategy_chain import StrategyChain


class TestStrategyChain:
    """Test suite for StrategyChain class."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        db = Mock()
        db.log_unsubscribe_attempt = Mock()
        return db
    
    @pytest.fixture
    def chain(self, mock_db):
        """Create StrategyChain instance."""
        return StrategyChain(mock_db)
    
    @pytest.fixture
    def mock_strategy(self):
        """Create a mock strategy."""
        strategy = Mock()
        strategy.__class__.__name__ = 'MockStrategy'
        strategy.can_handle.return_value = True
        strategy.execute.return_value = (True, 'Success')
        return strategy
    
    def test_add_strategy(self, chain, mock_strategy):
        """Test adding strategy to chain."""
        chain.add_strategy(mock_strategy)
        
        assert len(chain.strategies) == 1
        assert chain.strategies[0] == mock_strategy
    
    def test_add_multiple_strategies(self, chain):
        """Test adding multiple strategies."""
        strategy1 = Mock()
        strategy1.__class__.__name__ = 'Strategy1'
        strategy2 = Mock()
        strategy2.__class__.__name__ = 'Strategy2'
        
        chain.add_strategy(strategy1)
        chain.add_strategy(strategy2)
        
        assert len(chain.strategies) == 2
        assert chain.strategies[0] == strategy1
        assert chain.strategies[1] == strategy2
    
    def test_execute_with_no_strategies(self, chain):
        """Test execute when no strategies configured."""
        email_data = {'sender': 'test@example.com'}
        
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is False
        assert 'no strategies' in message.lower()
        assert strategy_name == 'None'
    
    def test_execute_single_strategy_success(self, chain, mock_strategy):
        """Test execute with single successful strategy."""
        mock_strategy.execute.return_value = (True, 'Unsubscribed successfully')
        chain.add_strategy(mock_strategy)
        
        email_data = {'sender': 'test@example.com'}
        
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is True
        assert 'success' in message.lower()
        assert strategy_name == 'MockStrategy'
        mock_strategy.can_handle.assert_called_once_with(email_data)
        mock_strategy.execute.assert_called_once_with(email_data)
    
    def test_execute_single_strategy_failure(self, chain, mock_strategy):
        """Test execute with single failing strategy."""
        mock_strategy.execute.return_value = (False, 'Failed to unsubscribe')
        chain.add_strategy(mock_strategy)
        
        email_data = {'sender': 'test@example.com'}
        
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is False
        assert strategy_name == 'None'
    
    def test_execute_fallback_to_second_strategy(self, chain):
        """Test that chain tries second strategy when first fails."""
        # First strategy fails
        strategy1 = Mock()
        strategy1.__class__.__name__ = 'Strategy1'
        strategy1.can_handle.return_value = True
        strategy1.execute.return_value = (False, 'Strategy 1 failed')
        
        # Second strategy succeeds
        strategy2 = Mock()
        strategy2.__class__.__name__ = 'Strategy2'
        strategy2.can_handle.return_value = True
        strategy2.execute.return_value = (True, 'Strategy 2 succeeded')
        
        chain.add_strategy(strategy1)
        chain.add_strategy(strategy2)
        
        email_data = {'sender': 'test@example.com'}
        
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is True
        assert 'Strategy 2' in message
        assert strategy_name == 'Strategy2'
        # Both should be attempted
        strategy1.execute.assert_called_once()
        strategy2.execute.assert_called_once()
    
    def test_execute_stops_after_success(self, chain):
        """Test that chain stops after first successful strategy."""
        # First strategy succeeds
        strategy1 = Mock()
        strategy1.__class__.__name__ = 'Strategy1'
        strategy1.can_handle.return_value = True
        strategy1.execute.return_value = (True, 'Strategy 1 succeeded')
        
        # Second strategy should not be tried
        strategy2 = Mock()
        strategy2.__class__.__name__ = 'Strategy2'
        strategy2.can_handle.return_value = True
        
        chain.add_strategy(strategy1)
        chain.add_strategy(strategy2)
        
        email_data = {'sender': 'test@example.com'}
        
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is True
        assert strategy_name == 'Strategy1'
        strategy1.execute.assert_called_once()
        # Second strategy should not be attempted
        strategy2.execute.assert_not_called()
    
    def test_execute_skips_strategy_that_cannot_handle(self, chain):
        """Test that chain skips strategies that can't handle the email."""
        # First strategy cannot handle
        strategy1 = Mock()
        strategy1.__class__.__name__ = 'Strategy1'
        strategy1.can_handle.return_value = False
        
        # Second strategy can handle and succeeds
        strategy2 = Mock()
        strategy2.__class__.__name__ = 'Strategy2'
        strategy2.can_handle.return_value = True
        strategy2.execute.return_value = (True, 'Strategy 2 succeeded')
        
        chain.add_strategy(strategy1)
        chain.add_strategy(strategy2)
        
        email_data = {'sender': 'test@example.com'}
        
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is True
        assert strategy_name == 'Strategy2'
        # First strategy should not execute
        strategy1.execute.assert_not_called()
        strategy2.execute.assert_called_once()
    
    def test_execute_all_strategies_fail(self, chain):
        """Test when all strategies fail."""
        strategy1 = Mock()
        strategy1.__class__.__name__ = 'Strategy1'
        strategy1.can_handle.return_value = True
        strategy1.execute.return_value = (False, 'Failed 1')
        
        strategy2 = Mock()
        strategy2.__class__.__name__ = 'Strategy2'
        strategy2.can_handle.return_value = True
        strategy2.execute.return_value = (False, 'Failed 2')
        
        chain.add_strategy(strategy1)
        chain.add_strategy(strategy2)
        
        email_data = {'sender': 'test@example.com'}
        
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is False
        assert strategy_name == 'None'
        # Both should be attempted
        strategy1.execute.assert_called_once()
        strategy2.execute.assert_called_once()
    
    def test_execute_no_strategies_can_handle(self, chain):
        """Test when no strategies can handle the email."""
        strategy1 = Mock()
        strategy1.__class__.__name__ = 'Strategy1'
        strategy1.can_handle.return_value = False
        
        strategy2 = Mock()
        strategy2.__class__.__name__ = 'Strategy2'
        strategy2.can_handle.return_value = False
        
        chain.add_strategy(strategy1)
        chain.add_strategy(strategy2)
        
        email_data = {'sender': 'test@example.com'}
        
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is False
        # Message should indicate all failed (actual implementation says "All...strategies failed")
        assert 'failed' in message.lower()
        assert strategy_name == 'None'
        # Neither should execute
        strategy1.execute.assert_not_called()
        strategy2.execute.assert_not_called()
    
    def test_execute_logs_attempts(self, chain, mock_db, mock_strategy):
        """Test that strategy attempts are logged to database."""
        mock_strategy.execute.return_value = (True, 'Success')
        chain.add_strategy(mock_strategy)
        
        email_data = {'sender': 'test@example.com'}
        
        chain.execute(email_data)
        
        # Should log the attempt
        mock_db.log_unsubscribe_attempt.assert_called()
    
    def test_execute_with_missing_sender(self, chain, mock_strategy):
        """Test execute when sender field missing."""
        mock_strategy.execute.return_value = (True, 'Success')
        chain.add_strategy(mock_strategy)
        
        email_data = {}  # Missing sender
        
        success, message, strategy_name = chain.execute(email_data)
        
        # Should handle gracefully
        assert isinstance(success, bool)
        assert isinstance(message, str)
        assert isinstance(strategy_name, str)
    
    def test_strategy_execution_order_preserved(self, chain):
        """Test that strategies are executed in order they were added."""
        execution_order = []
        
        def make_strategy(name):
            strategy = Mock()
            strategy.__class__.__name__ = name
            strategy.can_handle.return_value = True
            strategy.execute.side_effect = lambda ed: (
                execution_order.append(name) or (False, f'{name} executed')
            )
            return strategy
        
        strategy1 = make_strategy('First')
        strategy2 = make_strategy('Second')
        strategy3 = make_strategy('Third')
        
        chain.add_strategy(strategy1)
        chain.add_strategy(strategy2)
        chain.add_strategy(strategy3)
        
        email_data = {'sender': 'test@example.com'}
        
        chain.execute(email_data)
        
        # Should execute in order
        assert execution_order == ['First', 'Second', 'Third']


class TestStrategyChainEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        db = Mock()
        db.log_unsubscribe_attempt = Mock()
        return db
    
    @pytest.fixture
    def chain(self, mock_db):
        """Create StrategyChain instance."""
        return StrategyChain(mock_db)
    
    def test_execute_with_strategy_exception(self, chain):
        """Test handling of strategy execution exception."""
        strategy = Mock()
        strategy.__class__.__name__ = 'FaultyStrategy'
        strategy.can_handle.return_value = True
        strategy.execute.side_effect = Exception('Strategy crashed')
        
        chain.add_strategy(strategy)
        
        email_data = {'sender': 'test@example.com'}
        
        # Should handle exception gracefully
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is False
        assert 'error' in message.lower() or 'exception' in message.lower()
    
    def test_execute_with_can_handle_exception(self, chain):
        """Test handling of can_handle exception."""
        strategy = Mock()
        strategy.__class__.__name__ = 'FaultyStrategy'
        strategy.can_handle.side_effect = Exception('can_handle crashed')
        
        chain.add_strategy(strategy)
        
        email_data = {'sender': 'test@example.com'}
        
        # Should handle exception gracefully
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is False
    
    def test_add_same_strategy_multiple_times(self, chain):
        """Test adding same strategy instance multiple times."""
        strategy = Mock()
        strategy.__class__.__name__ = 'Strategy1'
        
        chain.add_strategy(strategy)
        chain.add_strategy(strategy)
        
        # Should allow (though not recommended)
        assert len(chain.strategies) == 2
    
    def test_execute_with_none_email_data(self, chain):
        """Test execute with None email data."""
        mock_strategy = Mock()
        mock_strategy.__class__.__name__ = 'MockStrategy'
        mock_strategy.can_handle.return_value = True
        mock_strategy.execute.return_value = (True, 'Success')
        
        chain.add_strategy(mock_strategy)
        
        # Should handle None gracefully or raise appropriate error
        try:
            success, message, strategy_name = chain.execute(None)
            # If it doesn't raise, verify return types
            assert isinstance(success, bool)
        except (TypeError, AttributeError):
            # It's acceptable to raise on None input
            pass
    
    def test_chain_with_different_strategy_types(self, chain):
        """Test chain with different types of strategies."""
        from unittest.mock import Mock
        
        # Create strategies mimicking real ones
        list_unsub = Mock()
        list_unsub.__class__.__name__ = 'ListUnsubscribeStrategy'
        list_unsub.can_handle.return_value = True
        list_unsub.execute.return_value = (True, 'Success via List-Unsubscribe')
        
        http_strategy = Mock()
        http_strategy.__class__.__name__ = 'HTTPStrategy'
        http_strategy.can_handle.return_value = True
        http_strategy.execute.return_value = (False, 'No links found')
        
        chain.add_strategy(list_unsub)
        chain.add_strategy(http_strategy)
        
        email_data = {'sender': 'test@example.com'}
        
        success, message, strategy_name = chain.execute(email_data)
        
        assert success is True
        assert strategy_name == 'ListUnsubscribeStrategy'

