"""Tests for data builder classes and assertion helpers."""

import pytest
from tests.fixtures.builders import (
    EmailDataBuilder,
    SenderDataBuilder,
    AccountDataBuilder
)
from tests.fixtures.assertions import (
    assert_email_structure,
    assert_sender_structure,
    assert_account_structure
)


class TestEmailDataBuilder:
    """Tests for EmailDataBuilder."""
    
    def test_build_default_email(self):
        """Test building email with default values."""
        email = EmailDataBuilder().build()
        
        assert email['sender'] == 'test@example.com'
        assert email['subject'] == 'Test Email'
        assert email['is_unread'] == False
        assert email['unsubscribe_links'] == []
        assert_email_structure(email)
    
    def test_with_sender(self):
        """Test customizing sender."""
        email = EmailDataBuilder().with_sender('custom@test.com').build()
        
        assert email['sender'] == 'custom@test.com'
        assert_email_structure(email)
    
    def test_with_subject(self):
        """Test customizing subject."""
        email = EmailDataBuilder().with_subject('Custom Subject').build()
        
        assert email['subject'] == 'Custom Subject'
        assert_email_structure(email)
    
    def test_with_unread(self):
        """Test setting unread status."""
        email = EmailDataBuilder().with_unread(True).build()
        
        assert email['is_unread'] == True
        assert_email_structure(email)
    
    def test_with_unsubscribe_link(self):
        """Test adding unsubscribe link."""
        email = EmailDataBuilder().with_unsubscribe_link('https://example.com/unsub').build()
        
        assert 'https://example.com/unsub' in email['unsubscribe_links']
        assert email['list_unsubscribe'] == '<https://example.com/unsub>'
        assert_email_structure(email)
    
    def test_with_mailto_unsubscribe(self):
        """Test adding mailto unsubscribe."""
        email = EmailDataBuilder().with_mailto_unsubscribe('unsub@test.com', 'Remove Me').build()
        
        assert email['list_unsubscribe'] == '<mailto:unsub@test.com?subject=Remove Me>'
        assert_email_structure(email)
    
    def test_fluent_api(self):
        """Test chaining multiple builder methods."""
        email = (EmailDataBuilder()
                 .with_sender('newsletter@example.com')
                 .with_subject('Weekly Newsletter')
                 .with_unread(True)
                 .with_unsubscribe_link('https://example.com/unsub')
                 .with_body_text('Newsletter content')
                 .build())
        
        assert email['sender'] == 'newsletter@example.com'
        assert email['subject'] == 'Weekly Newsletter'
        assert email['is_unread'] == True
        assert 'https://example.com/unsub' in email['unsubscribe_links']
        assert email['body_text'] == 'Newsletter content'
        assert_email_structure(email)
    
    def test_build_returns_copy(self):
        """Test that build() returns a copy for reusability."""
        builder = EmailDataBuilder().with_sender('test@example.com')
        
        email1 = builder.build()
        email2 = builder.build()
        
        # Modify email1
        email1['sender'] = 'modified@example.com'
        
        # email2 should not be affected
        assert email2['sender'] == 'test@example.com'


class TestSenderDataBuilder:
    """Tests for SenderDataBuilder."""
    
    def test_build_default_sender(self):
        """Test building sender with default values."""
        sender = SenderDataBuilder().build()
        
        assert sender['sender'] == 'test@example.com'
        assert sender['email_count'] == 1
        assert sender['unread_count'] == 0
        assert sender['has_unsubscribe'] == False
        assert_sender_structure(sender)
    
    def test_with_email_count(self):
        """Test setting email count."""
        sender = SenderDataBuilder().with_email_count(10).build()
        
        assert sender['email_count'] == 10
        assert_sender_structure(sender)
    
    def test_with_unread_count(self):
        """Test setting unread count."""
        sender = SenderDataBuilder().with_email_count(10).with_unread_count(5).build()
        
        assert sender['unread_count'] == 5
        assert_sender_structure(sender)
    
    def test_with_unsubscribe_link(self):
        """Test adding unsubscribe link."""
        sender = SenderDataBuilder().with_unsubscribe_link('https://example.com/unsub').build()
        
        assert sender['has_unsubscribe'] == True
        assert 'https://example.com/unsub' in sender['unsubscribe_links']
        assert sender['list_unsubscribe'] == '<https://example.com/unsub>'
        assert_sender_structure(sender)
    
    def test_with_score(self):
        """Test setting score."""
        sender = SenderDataBuilder().with_score(85).build()
        
        assert sender['score'] == 85
        assert_sender_structure(sender)
    
    def test_with_sample_subjects(self):
        """Test setting sample subjects."""
        subjects = ['Subject 1', 'Subject 2', 'Subject 3']
        sender = SenderDataBuilder().with_sample_subjects(subjects).build()
        
        assert sender['sample_subjects'] == subjects
        assert_sender_structure(sender)
    
    def test_fluent_api(self):
        """Test chaining multiple builder methods."""
        sender = (SenderDataBuilder()
                  .with_sender('newsletter@example.com')
                  .with_email_count(45)
                  .with_unread_count(12)
                  .with_unsubscribe_link('https://example.com/unsub')
                  .with_score(85)
                  .build())
        
        assert sender['sender'] == 'newsletter@example.com'
        assert sender['email_count'] == 45
        assert sender['unread_count'] == 12
        assert sender['has_unsubscribe'] == True
        assert sender['score'] == 85
        assert_sender_structure(sender)


class TestAccountDataBuilder:
    """Tests for AccountDataBuilder."""
    
    def test_build_default_account(self):
        """Test building account with default values."""
        account = AccountDataBuilder().build()
        
        assert account['email'] == 'test@example.com'
        assert account['provider'] == 'gmail'
        assert 'encrypted_password' in account
        assert_account_structure(account)
    
    def test_with_email(self):
        """Test setting email."""
        account = AccountDataBuilder().with_email('user@gmail.com').build()
        
        assert account['email'] == 'user@gmail.com'
        assert_account_structure(account)
    
    def test_with_provider(self):
        """Test setting provider."""
        account = AccountDataBuilder().with_provider('outlook').build()
        
        assert account['provider'] == 'outlook'
        assert_account_structure(account)
    
    def test_fluent_api(self):
        """Test chaining multiple builder methods."""
        account = (AccountDataBuilder()
                   .with_email('user@gmail.com')
                   .with_provider('gmail')
                   .with_password('encrypted_pass_123')
                   .with_added_date('2024-01-15')
                   .build())
        
        assert account['email'] == 'user@gmail.com'
        assert account['provider'] == 'gmail'
        assert account['encrypted_password'] == 'encrypted_pass_123'
        assert account['added_date'] == '2024-01-15'
        assert_account_structure(account)


class TestAssertionHelpers:
    """Tests for assertion helper functions."""
    
    def test_assert_email_structure_valid(self):
        """Test that valid email passes assertion."""
        email = EmailDataBuilder().build()
        
        # Should not raise
        assert_email_structure(email)
    
    def test_assert_email_structure_missing_field(self):
        """Test that email missing field raises AssertionError."""
        email = EmailDataBuilder().build()
        del email['sender']
        
        with pytest.raises(AssertionError, match='missing required fields'):
            assert_email_structure(email)
    
    def test_assert_email_structure_wrong_type(self):
        """Test that email with wrong field type raises AssertionError."""
        email = EmailDataBuilder().build()
        email['is_unread'] = 'yes'  # Should be bool
        
        with pytest.raises(AssertionError, match='is_unread must be bool'):
            assert_email_structure(email)
    
    def test_assert_email_structure_not_dict(self):
        """Test that non-dict raises AssertionError."""
        with pytest.raises(AssertionError, match='must be a dictionary'):
            assert_email_structure('not a dict')
    
    def test_assert_sender_structure_valid(self):
        """Test that valid sender passes assertion."""
        sender = SenderDataBuilder().build()
        
        # Should not raise
        assert_sender_structure(sender)
    
    def test_assert_sender_structure_invalid_counts(self):
        """Test that invalid counts raise AssertionError."""
        sender = SenderDataBuilder().with_email_count(10).with_unread_count(15).build()
        
        with pytest.raises(AssertionError, match='unread_count .* cannot exceed email_count'):
            assert_sender_structure(sender)
    
    def test_assert_sender_structure_invalid_score(self):
        """Test that score outside 0-100 raises AssertionError."""
        sender = SenderDataBuilder().with_score(150).build()
        
        with pytest.raises(AssertionError, match='score must be between 0 and 100'):
            assert_sender_structure(sender)
    
    def test_assert_account_structure_valid(self):
        """Test that valid account passes assertion."""
        account = AccountDataBuilder().build()
        
        # Should not raise
        assert_account_structure(account)
    
    def test_assert_account_structure_invalid_email(self):
        """Test that email without @ raises AssertionError."""
        account = AccountDataBuilder().with_email('notanemail').build()
        
        with pytest.raises(AssertionError, match="email must contain '@'"):
            assert_account_structure(account)

