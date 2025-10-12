"""Unit tests for EmailGrouper.

Tests email grouping and aggregation including:
- Grouping emails by sender
- Calculating aggregate statistics
- Score aggregation
- Sorting by priority
- Edge cases (empty lists, single email, etc.)
"""

import pytest
from unittest.mock import Mock
from src.scoring.email_grouper import EmailGrouper
from src.scoring.scorer import EmailScorer
from tests.fixtures.builders import EmailDataBuilder


class TestEmailGrouper:
    """Test suite for EmailGrouper class."""
    
    @pytest.fixture
    def mock_scorer(self):
        """Create mock scorer."""
        scorer = Mock(spec=EmailScorer)
        # Default: return score of 5 with basic breakdown
        scorer.calculate_score.return_value = (5, {'total': 5, 'unread': 1})
        return scorer
    
    @pytest.fixture
    def grouper(self, mock_scorer):
        """Create EmailGrouper instance."""
        return EmailGrouper(mock_scorer)
    
    def test_group_empty_list(self, grouper):
        """Test grouping empty email list."""
        result = grouper.group_by_sender([])
        
        assert result == []
    
    def test_group_single_email(self, grouper, mock_scorer):
        """Test grouping single email."""
        emails = [
            {'sender': 'test@example.com', 'is_unread': True}
        ]
        
        mock_scorer.calculate_score.return_value = (3, {'total': 3, 'unread': 1})
        
        result = grouper.group_by_sender(emails)
        
        assert len(result) == 1
        assert result[0]['sender'] == 'test@example.com'
        assert result[0]['total_count'] == 1
        assert result[0]['unread_count'] == 1
        assert result[0]['total_score'] == 3
    
    def test_group_multiple_senders(self, grouper, mock_scorer):
        """Test grouping emails from multiple senders."""
        emails = [
            {'sender': 'sender1@example.com', 'is_unread': True},
            {'sender': 'sender2@example.com', 'is_unread': False},
            {'sender': 'sender3@example.com', 'is_unread': True}
        ]
        
        mock_scorer.calculate_score.return_value = (2, {'total': 2})
        
        result = grouper.group_by_sender(emails)
        
        assert len(result) == 3
        senders = [r['sender'] for r in result]
        assert 'sender1@example.com' in senders
        assert 'sender2@example.com' in senders
        assert 'sender3@example.com' in senders
    
    def test_group_multiple_emails_same_sender(self, grouper, mock_scorer):
        """Test grouping multiple emails from same sender."""
        emails = [
            {'sender': 'repeat@example.com', 'is_unread': True},
            {'sender': 'repeat@example.com', 'is_unread': False},
            {'sender': 'repeat@example.com', 'is_unread': True}
        ]
        
        mock_scorer.calculate_score.return_value = (3, {'total': 3})
        
        result = grouper.group_by_sender(emails)
        
        assert len(result) == 1
        assert result[0]['sender'] == 'repeat@example.com'
        assert result[0]['total_count'] == 3
        assert result[0]['unread_count'] == 2
        assert result[0]['total_score'] == 9  # 3 emails * score 3
    
    def test_sorted_by_total_score_descending(self, grouper, mock_scorer):
        """Test that results are sorted by total score descending."""
        emails = [
            {'sender': 'low@example.com', 'is_unread': False},
            {'sender': 'high@example.com', 'is_unread': True},
            {'sender': 'medium@example.com', 'is_unread': True}
        ]
        
        # Configure scorer to return different scores per sender
        def score_side_effect(email_data, frequency, sender):
            if sender == 'high@example.com':
                return (10, {'total': 10})
            elif sender == 'medium@example.com':
                return (5, {'total': 5})
            else:
                return (1, {'total': 1})
        
        mock_scorer.calculate_score.side_effect = score_side_effect
        
        result = grouper.group_by_sender(emails)
        
        # Should be sorted by total_score descending
        assert result[0]['sender'] == 'high@example.com'
        assert result[1]['sender'] == 'medium@example.com'
        assert result[2]['sender'] == 'low@example.com'
    
    def test_aggregate_unread_count(self, grouper, mock_scorer):
        """Test that unread count is correctly aggregated."""
        emails = [
            {'sender': 'test@example.com', 'is_unread': True},
            {'sender': 'test@example.com', 'is_unread': True},
            {'sender': 'test@example.com', 'is_unread': False},
            {'sender': 'test@example.com', 'is_unread': True}
        ]
        
        mock_scorer.calculate_score.return_value = (1, {'total': 1})
        
        result = grouper.group_by_sender(emails)
        
        assert result[0]['unread_count'] == 3
        assert result[0]['total_count'] == 4
    
    def test_aggregate_unsubscribe_links(self, grouper, mock_scorer):
        """Test that unsubscribe links are collected and deduplicated."""
        emails = [
            {'sender': 'test@example.com', 'unsubscribe_links': ['https://example.com/unsub1']},
            {'sender': 'test@example.com', 'unsubscribe_links': ['https://example.com/unsub1', 'https://example.com/unsub2']},
            {'sender': 'test@example.com', 'unsubscribe_links': ['https://example.com/unsub3']}
        ]
        
        mock_scorer.calculate_score.return_value = (1, {'total': 1})
        
        result = grouper.group_by_sender(emails)
        
        assert result[0]['has_unsubscribe'] is True
        # Should have unique links, up to 3
        assert len(result[0]['sample_links']) <= 3
        assert 'https://example.com/unsub1' in result[0]['sample_links']
    
    def test_no_unsubscribe_links(self, grouper, mock_scorer):
        """Test sender with no unsubscribe links."""
        emails = [
            {'sender': 'test@example.com', 'unsubscribe_links': []},
            {'sender': 'test@example.com', 'unsubscribe_links': []}
        ]
        
        mock_scorer.calculate_score.return_value = (1, {'total': 1})
        
        result = grouper.group_by_sender(emails)
        
        assert result[0]['has_unsubscribe'] is False
        assert result[0]['sample_links'] == []
    
    def test_limits_sample_links_to_three(self, grouper, mock_scorer):
        """Test that sample links are limited to 3."""
        emails = [
            {'sender': 'test@example.com', 'unsubscribe_links': [
                'https://example.com/unsub1',
                'https://example.com/unsub2',
                'https://example.com/unsub3',
                'https://example.com/unsub4',
                'https://example.com/unsub5'
            ]}
        ]
        
        mock_scorer.calculate_score.return_value = (1, {'total': 1})
        
        result = grouper.group_by_sender(emails)
        
        # Should have maximum 3 links
        assert len(result[0]['sample_links']) <= 3
    
    def test_calculate_average_score(self, grouper, mock_scorer):
        """Test that average score is calculated correctly."""
        emails = [
            {'sender': 'test@example.com'},
            {'sender': 'test@example.com'},
            {'sender': 'test@example.com'}
        ]
        
        # Configure scorer to return different scores
        scores = [10, 5, 15]
        score_index = [0]
        
        def score_side_effect(*args, **kwargs):
            score = scores[score_index[0]]
            score_index[0] += 1
            return (score, {'total': score})
        
        mock_scorer.calculate_score.side_effect = score_side_effect
        
        result = grouper.group_by_sender(emails)
        
        # Average = (10 + 5 + 15) / 3 = 10
        assert result[0]['average_score'] == 10.0
        # Total = 10 + 5 + 15 = 30
        assert result[0]['total_score'] == 30
    
    def test_last_email_date(self, grouper, mock_scorer):
        """Test that last email date is captured."""
        emails = [
            {'sender': 'test@example.com', 'date': '2024-01-01'},
            {'sender': 'test@example.com', 'date': '2024-01-02'},
            {'sender': 'test@example.com', 'date': '2024-01-03'}
        ]
        
        mock_scorer.calculate_score.return_value = (1, {'total': 1})
        
        result = grouper.group_by_sender(emails)
        
        # Should capture last email's date
        assert result[0]['last_email_date'] == '2024-01-03'
    
    def test_scorer_receives_correct_parameters(self, grouper, mock_scorer):
        """Test that scorer receives correct frequency and sender."""
        emails = [
            {'sender': 'test@example.com', 'is_unread': True},
            {'sender': 'test@example.com', 'is_unread': False}
        ]
        
        mock_scorer.calculate_score.return_value = (5, {'total': 5})
        
        grouper.group_by_sender(emails)
        
        # Scorer should be called with frequency=2 for this sender
        calls = mock_scorer.calculate_score.call_args_list
        for call in calls:
            kwargs = call[1] if len(call) > 1 else call.kwargs
            assert kwargs.get('frequency') == 2
            assert kwargs.get('sender') == 'test@example.com'
    
    def test_missing_sender_field(self, grouper, mock_scorer):
        """Test handling email missing sender field."""
        emails = [
            {'is_unread': True},  # Missing sender
            {'sender': 'test@example.com', 'is_unread': False}
        ]
        
        mock_scorer.calculate_score.return_value = (1, {'total': 1})
        
        result = grouper.group_by_sender(emails)
        
        # Should use default sender for missing field
        assert len(result) == 2
        senders = [r['sender'] for r in result]
        assert 'unknown@example.com' in senders
        assert 'test@example.com' in senders
    
    def test_score_breakdown_aggregation(self, grouper, mock_scorer):
        """Test that score breakdowns are aggregated for sender."""
        emails = [
            {'sender': 'test@example.com'},
            {'sender': 'test@example.com'}
        ]
        
        # Return different breakdowns for each email
        breakdowns = [
            (5, {'total': 5, 'unread': 1, 'frequency': 2}),
            (7, {'total': 7, 'unread': 1, 'frequency': 2, 'has_unsubscribe': 1})
        ]
        mock_scorer.calculate_score.side_effect = breakdowns
        
        result = grouper.group_by_sender(emails)
        
        # Breakdown should be aggregated
        breakdown = result[0]['score_breakdown']
        assert breakdown['total'] == 12  # 5 + 7
        assert breakdown['unread'] == 2  # 1 + 1
        assert breakdown['frequency'] == 4  # 2 + 2


class TestEmailGrouperPerformance:
    """Test performance characteristics of grouper."""
    
    @pytest.fixture
    def mock_scorer(self):
        """Create mock scorer."""
        scorer = Mock(spec=EmailScorer)
        scorer.calculate_score.return_value = (5, {'total': 5})
        return scorer
    
    @pytest.fixture
    def grouper(self, mock_scorer):
        """Create EmailGrouper instance."""
        return EmailGrouper(mock_scorer)
    
    def test_group_large_email_list(self, grouper, mock_scorer):
        """Test grouping large number of emails (performance test)."""
        import time
        
        # Generate 1000 emails from 100 senders
        emails = []
        for i in range(100):
            sender = f'sender{i}@example.com'
            for j in range(10):
                emails.append({
                    'sender': sender,
                    'is_unread': j % 2 == 0,
                    'unsubscribe_links': [f'https://example.com/unsub{i}']
                })
        
        mock_scorer.calculate_score.return_value = (3, {'total': 3})
        
        start_time = time.time()
        result = grouper.group_by_sender(emails)
        elapsed_time = time.time() - start_time
        
        # Should complete in less than 1 second
        assert elapsed_time < 1.0
        assert len(result) == 100
        # Each sender should have 10 emails
        assert all(r['total_count'] == 10 for r in result)
    
    def test_group_many_unique_senders(self, grouper, mock_scorer):
        """Test grouping with many unique senders."""
        # 1000 unique senders, 1 email each
        emails = [
            {'sender': f'sender{i}@example.com', 'is_unread': False}
            for i in range(1000)
        ]
        
        mock_scorer.calculate_score.return_value = (2, {'total': 2})
        
        result = grouper.group_by_sender(emails)
        
        assert len(result) == 1000
        assert all(r['total_count'] == 1 for r in result)


class TestEmailGrouperEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def mock_scorer(self):
        """Create mock scorer."""
        scorer = Mock(spec=EmailScorer)
        scorer.calculate_score.return_value = (5, {'total': 5})
        return scorer
    
    @pytest.fixture
    def grouper(self, mock_scorer):
        """Create EmailGrouper instance."""
        return EmailGrouper(mock_scorer)
    
    def test_emails_with_missing_fields(self, grouper, mock_scorer):
        """Test handling emails with missing optional fields."""
        emails = [
            {},  # Completely empty
            {'sender': 'test@example.com'}  # No other fields
        ]
        
        mock_scorer.calculate_score.return_value = (1, {'total': 1})
        
        # Should handle gracefully
        result = grouper.group_by_sender(emails)
        
        assert len(result) == 2
    
    def test_email_with_none_values(self, grouper, mock_scorer):
        """Test handling emails with None values."""
        emails = [
            {'sender': 'test@example.com', 'is_unread': None}  # Don't include None unsubscribe_links
        ]
        
        mock_scorer.calculate_score.return_value = (1, {'total': 1})
        
        result = grouper.group_by_sender(emails)
        
        assert len(result) == 1
        # None should be treated as False for is_unread
        assert result[0]['unread_count'] == 0
    
    def test_empty_sender_string(self, grouper, mock_scorer):
        """Test handling email with empty sender string."""
        emails = [
            {'sender': '', 'is_unread': True}
        ]
        
        mock_scorer.calculate_score.return_value = (1, {'total': 1})
        
        result = grouper.group_by_sender(emails)
        
        # Should group by empty string
        assert len(result) == 1
        assert result[0]['sender'] == ''
    
    def test_aggregate_score_breakdowns_empty_list(self, grouper):
        """Test aggregating empty breakdown list."""
        result = grouper._aggregate_score_breakdowns([])
        
        assert result == {'total': 0}
    
    def test_aggregate_score_breakdowns_missing_keys(self, grouper):
        """Test aggregating breakdowns with missing keys."""
        breakdowns = [
            {'total': 5},  # Missing other keys
            {'total': 3, 'unread': 1}  # Has some keys
        ]
        
        result = grouper._aggregate_score_breakdowns(breakdowns)
        
        assert result['total'] == 8
        assert result['unread'] == 1
        assert result['frequency'] == 0

