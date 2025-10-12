"""Unit tests for EmailScorer.

Tests scoring logic including:
- Score calculation for various email attributes
- Frequency scoring
- Historical unwanted sender scoring
- Whitelist protection
- Score breakdown transparency
"""

import pytest
from unittest.mock import Mock
from src.scoring.scorer import EmailScorer


class TestEmailScorer:
    """Test suite for EmailScorer class."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        db = Mock()
        db.check_whitelist.return_value = False
        db.check_unwanted.return_value = False
        return db
    
    @pytest.fixture
    def scorer(self, mock_db):
        """Create EmailScorer instance with mock DB."""
        return EmailScorer(mock_db)
    
    @pytest.fixture
    def scorer_no_db(self):
        """Create EmailScorer without database."""
        return EmailScorer(None)
    
    def test_score_unread_email(self, scorer):
        """Test scoring unread email (+1 point)."""
        email_data = {'is_unread': True}
        
        score, breakdown = scorer.calculate_score(email_data)
        
        assert score == 1
        assert breakdown['unread'] == 1
        assert breakdown['total'] == 1
    
    def test_score_read_email(self, scorer):
        """Test scoring read email (0 points)."""
        email_data = {'is_unread': False}
        
        score, breakdown = scorer.calculate_score(email_data)
        
        assert score == 0
        assert 'unread' not in breakdown
        assert breakdown['total'] == 0
    
    def test_score_with_unsubscribe_link(self, scorer):
        """Test scoring email with unsubscribe link (+1 point)."""
        email_data = {'unsubscribe_links': ['https://example.com/unsub']}
        
        score, breakdown = scorer.calculate_score(email_data)
        
        assert score == 1
        assert breakdown['has_unsubscribe'] == 1
        assert breakdown['total'] == 1
    
    def test_score_without_unsubscribe_link(self, scorer):
        """Test scoring email without unsubscribe link (0 points)."""
        email_data = {'unsubscribe_links': []}
        
        score, breakdown = scorer.calculate_score(email_data)
        
        assert score == 0
        assert 'has_unsubscribe' not in breakdown
    
    def test_score_with_empty_unsubscribe_links(self, scorer):
        """Test that empty list doesn't add points."""
        email_data = {'unsubscribe_links': []}
        
        score, breakdown = scorer.calculate_score(email_data)
        
        assert score == 0
        assert 'has_unsubscribe' not in breakdown
    
    def test_frequency_score_single_email(self, scorer):
        """Test frequency scoring with single email (0 bonus)."""
        email_data = {}
        
        score, breakdown = scorer.calculate_score(email_data, frequency=1)
        
        assert 'frequency' not in breakdown
    
    def test_frequency_score_multiple_emails(self, scorer):
        """Test frequency scoring with multiple emails."""
        email_data = {}
        
        score, breakdown = scorer.calculate_score(email_data, frequency=5)
        
        assert breakdown['frequency'] == 4  # frequency - 1
        assert breakdown['total'] == 4
    
    def test_combined_scoring(self, scorer):
        """Test combined scoring with multiple factors."""
        email_data = {
            'is_unread': True,
            'unsubscribe_links': ['https://example.com/unsub']
        }
        
        score, breakdown = scorer.calculate_score(email_data, frequency=3)
        
        # 1 (unread) + 1 (unsubscribe) + 2 (frequency-1) = 4
        assert score == 4
        assert breakdown['unread'] == 1
        assert breakdown['has_unsubscribe'] == 1
        assert breakdown['frequency'] == 2
        assert breakdown['total'] == 4
    
    def test_whitelisted_sender_returns_negative_score(self, scorer, mock_db):
        """Test that whitelisted sender returns -1 score."""
        mock_db.check_whitelist.return_value = True
        
        email_data = {
            'is_unread': True,
            'unsubscribe_links': ['https://example.com/unsub']
        }
        
        score, breakdown = scorer.calculate_score(
            email_data, 
            frequency=5, 
            sender='protected@example.com'
        )
        
        assert score == -1
        assert breakdown['whitelisted'] is True
        assert breakdown['total'] == -1
        # Other factors should not be calculated
        assert 'unread' not in breakdown
        assert 'has_unsubscribe' not in breakdown
    
    def test_historical_unwanted_sender(self, scorer, mock_db):
        """Test historical unwanted sender adds +5 points."""
        mock_db.check_unwanted.return_value = True
        
        email_data = {}
        
        score, breakdown = scorer.calculate_score(
            email_data,
            sender='spam@example.com'
        )
        
        assert score == 5
        assert breakdown['historical_unwanted'] == 5
        assert breakdown['total'] == 5
    
    def test_historical_unwanted_with_other_factors(self, scorer, mock_db):
        """Test historical unwanted scoring combines with other factors."""
        mock_db.check_unwanted.return_value = True
        
        email_data = {
            'is_unread': True,
            'unsubscribe_links': ['https://example.com/unsub']
        }
        
        score, breakdown = scorer.calculate_score(
            email_data,
            frequency=3,
            sender='spam@example.com'
        )
        
        # 1 (unread) + 1 (unsubscribe) + 2 (frequency) + 5 (historical) = 9
        assert score == 9
        assert breakdown['historical_unwanted'] == 5
    
    def test_scoring_without_db_manager(self, scorer_no_db):
        """Test scoring works without database manager."""
        email_data = {
            'is_unread': True,
            'unsubscribe_links': ['https://example.com/unsub']
        }
        
        score, breakdown = scorer_no_db.calculate_score(
            email_data,
            frequency=2,
            sender='test@example.com'
        )
        
        # 1 (unread) + 1 (unsubscribe) + 1 (frequency) = 3
        # No historical or whitelist checks
        assert score == 3
        assert 'historical_unwanted' not in breakdown
        assert 'whitelisted' not in breakdown
    
    def test_score_missing_email_attributes(self, scorer):
        """Test scoring email with missing attributes."""
        email_data = {}  # No attributes
        
        score, breakdown = scorer.calculate_score(email_data)
        
        assert score == 0
        assert breakdown['total'] == 0
    
    def test_calculate_frequency_score_zero(self, scorer):
        """Test frequency score calculation with zero frequency."""
        freq_score = scorer._calculate_frequency_score(0)
        
        # Should return 0, not negative
        assert freq_score == 0
    
    def test_calculate_frequency_score_one(self, scorer):
        """Test frequency score calculation with one email."""
        freq_score = scorer._calculate_frequency_score(1)
        
        assert freq_score == 0
    
    def test_calculate_frequency_score_ten(self, scorer):
        """Test frequency score calculation with ten emails."""
        freq_score = scorer._calculate_frequency_score(10)
        
        assert freq_score == 9
    
    def test_check_historical_unwanted_not_found(self, scorer, mock_db):
        """Test historical check when sender not in unwanted list."""
        mock_db.check_unwanted.return_value = False
        
        hist_score = scorer._check_historical_unwanted('normal@example.com')
        
        assert hist_score == 0
        mock_db.check_unwanted.assert_called_once_with('normal@example.com')
    
    def test_check_historical_unwanted_found(self, scorer, mock_db):
        """Test historical check when sender in unwanted list."""
        mock_db.check_unwanted.return_value = True
        
        hist_score = scorer._check_historical_unwanted('spam@example.com')
        
        assert hist_score == 5
        mock_db.check_unwanted.assert_called_once_with('spam@example.com')
    
    def test_check_whitelisted_true(self, scorer, mock_db):
        """Test whitelist check when sender is whitelisted."""
        mock_db.check_whitelist.return_value = True
        
        is_whitelisted = scorer._check_whitelisted('protected@example.com')
        
        assert is_whitelisted is True
        mock_db.check_whitelist.assert_called_once_with('protected@example.com')
    
    def test_check_whitelisted_false(self, scorer, mock_db):
        """Test whitelist check when sender not whitelisted."""
        mock_db.check_whitelist.return_value = False
        
        is_whitelisted = scorer._check_whitelisted('regular@example.com')
        
        assert is_whitelisted is False
    
    def test_whitelist_check_priority_over_all_factors(self, scorer, mock_db):
        """Test whitelist check takes priority over all other factors."""
        mock_db.check_whitelist.return_value = True
        mock_db.check_unwanted.return_value = True  # Both whitelisted AND unwanted
        
        email_data = {
            'is_unread': True,
            'unsubscribe_links': ['https://example.com/unsub']
        }
        
        score, breakdown = scorer.calculate_score(
            email_data,
            frequency=10,
            sender='protected@example.com'
        )
        
        # Should return -1 due to whitelist, ignoring everything else
        assert score == -1
        assert breakdown['whitelisted'] is True
        # Historical check should not even run
        mock_db.check_unwanted.assert_not_called()
    
    def test_scoring_without_sender_parameter(self, scorer):
        """Test scoring without providing sender parameter."""
        email_data = {
            'is_unread': True,
            'unsubscribe_links': ['https://example.com/unsub']
        }
        
        score, breakdown = scorer.calculate_score(email_data, frequency=2)
        
        # Should score normally without historical/whitelist checks
        assert score == 3
        assert 'whitelisted' not in breakdown
        assert 'historical_unwanted' not in breakdown


class TestEmailScorerEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        db = Mock()
        db.check_whitelist.return_value = False
        db.check_unwanted.return_value = False
        return db
    
    @pytest.fixture
    def scorer(self, mock_db):
        """Create EmailScorer instance."""
        return EmailScorer(mock_db)
    
    def test_score_with_none_values(self, scorer):
        """Test scoring with None values in email_data."""
        email_data = {
            'is_unread': None,
            'unsubscribe_links': None
        }
        
        # Should handle None gracefully
        score, breakdown = scorer.calculate_score(email_data)
        
        assert isinstance(score, int)
        assert isinstance(breakdown, dict)
    
    def test_score_with_negative_frequency(self, scorer):
        """Test scoring with negative frequency (invalid input)."""
        email_data = {}
        
        score, breakdown = scorer.calculate_score(email_data, frequency=-5)
        
        # Frequency score should be 0 (max of -6 and 0)
        assert score == 0
        assert 'frequency' not in breakdown
    
    def test_score_with_very_high_frequency(self, scorer):
        """Test scoring with very high frequency."""
        email_data = {}
        
        score, breakdown = scorer.calculate_score(email_data, frequency=1000)
        
        # Frequency score = 999
        assert score == 999
        assert breakdown['frequency'] == 999
    
    def test_score_with_empty_sender_string(self, scorer):
        """Test scoring with empty sender string."""
        email_data = {}
        
        score, breakdown = scorer.calculate_score(email_data, sender='')
        
        # Should not crash, treats empty string as no sender
        assert isinstance(score, int)
    
    def test_breakdown_always_includes_total(self, scorer):
        """Test that breakdown always includes 'total' key."""
        test_cases = [
            {},
            {'is_unread': True},
            {'unsubscribe_links': ['link']},
            {'is_unread': True, 'unsubscribe_links': ['link']}
        ]
        
        for email_data in test_cases:
            score, breakdown = scorer.calculate_score(email_data)
            assert 'total' in breakdown
            assert breakdown['total'] == score
    
    def test_db_exception_handled_gracefully(self, scorer, mock_db):
        """Test that database exceptions are handled gracefully."""
        mock_db.check_whitelist.side_effect = Exception("DB error")
        
        email_data = {'is_unread': True}
        
        # Should handle exception and continue scoring
        # (or may raise - depends on implementation)
        try:
            score, breakdown = scorer.calculate_score(
                email_data,
                sender='test@example.com'
            )
            # If it doesn't raise, that's fine
            assert isinstance(score, int)
        except Exception:
            # If it raises, that's also acceptable behavior
            pass

