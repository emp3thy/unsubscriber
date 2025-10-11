"""Data builder classes for constructing test data with sensible defaults."""

from typing import List, Dict, Any


class EmailDataBuilder:
    """Builder for email data dictionaries.
    
    Provides fluent API for creating email dictionaries with sensible defaults
    and easy customization.
    
    Example:
        email = EmailDataBuilder()\\
            .with_sender('test@example.com')\\
            .with_unread()\\
            .with_unsubscribe_link('https://example.com/unsub')\\
            .build()
    """
    
    def __init__(self):
        """Initialize builder with default email data."""
        self._data = {
            'sender': 'test@example.com',
            'subject': 'Test Email',
            'date': '2024-01-01',
            'is_unread': False,
            'unsubscribe_links': [],
            'list_unsubscribe': '',
            'body_text': '',
            'body_html': ''
        }
    
    def with_sender(self, sender: str) -> 'EmailDataBuilder':
        """Set sender email address."""
        self._data['sender'] = sender
        return self
    
    def with_subject(self, subject: str) -> 'EmailDataBuilder':
        """Set email subject."""
        self._data['subject'] = subject
        return self
    
    def with_date(self, date: str) -> 'EmailDataBuilder':
        """Set email date."""
        self._data['date'] = date
        return self
    
    def with_unread(self, is_unread: bool = True) -> 'EmailDataBuilder':
        """Set unread status."""
        self._data['is_unread'] = is_unread
        return self
    
    def with_unsubscribe_link(self, link: str) -> 'EmailDataBuilder':
        """Add unsubscribe link (HTTP/HTTPS).
        
        Args:
            link: Unsubscribe URL (e.g., 'https://example.com/unsub')
        """
        self._data['unsubscribe_links'].append(link)
        self._data['list_unsubscribe'] = f'<{link}>'
        return self
    
    def with_mailto_unsubscribe(self, email: str, subject: str = '') -> 'EmailDataBuilder':
        """Add mailto unsubscribe.
        
        Args:
            email: Unsubscribe email address
            subject: Optional subject for unsubscribe email
        """
        if subject:
            mailto = f'mailto:{email}?subject={subject}'
        else:
            mailto = f'mailto:{email}'
        self._data['list_unsubscribe'] = f'<{mailto}>'
        return self
    
    def with_body_text(self, text: str) -> 'EmailDataBuilder':
        """Set plain text body."""
        self._data['body_text'] = text
        return self
    
    def with_body_html(self, html: str) -> 'EmailDataBuilder':
        """Set HTML body."""
        self._data['body_html'] = html
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the email dictionary.
        
        Returns a copy so the builder can be reused.
        """
        return self._data.copy()


class SenderDataBuilder:
    """Builder for sender aggregate data dictionaries.
    
    Provides fluent API for creating sender aggregates with statistics.
    
    Example:
        sender = SenderDataBuilder()\\
            .with_sender('newsletter@example.com')\\
            .with_email_count(45)\\
            .with_unread_count(12)\\
            .with_unsubscribe_link('https://example.com/unsub')\\
            .with_score(85)\\
            .build()
    """
    
    def __init__(self):
        """Initialize builder with default sender data."""
        self._data = {
            'sender': 'test@example.com',
            'email_count': 1,
            'unread_count': 0,
            'has_unsubscribe': False,
            'unsubscribe_links': [],
            'list_unsubscribe': '',
            'score': 0,
            'latest_date': '2024-01-01',
            'sample_subjects': ['Test Email']
        }
    
    def with_sender(self, sender: str) -> 'SenderDataBuilder':
        """Set sender email address."""
        self._data['sender'] = sender
        return self
    
    def with_email_count(self, count: int) -> 'SenderDataBuilder':
        """Set total email count from this sender."""
        self._data['email_count'] = count
        return self
    
    def with_unread_count(self, count: int) -> 'SenderDataBuilder':
        """Set unread email count from this sender."""
        self._data['unread_count'] = count
        return self
    
    def with_unsubscribe_link(self, link: str) -> 'SenderDataBuilder':
        """Add unsubscribe link.
        
        Args:
            link: Unsubscribe URL
        """
        self._data['has_unsubscribe'] = True
        self._data['unsubscribe_links'] = [link]
        self._data['list_unsubscribe'] = f'<{link}>'
        return self
    
    def with_score(self, score: int) -> 'SenderDataBuilder':
        """Set sender score (0-100)."""
        self._data['score'] = score
        return self
    
    def with_latest_date(self, date: str) -> 'SenderDataBuilder':
        """Set date of most recent email."""
        self._data['latest_date'] = date
        return self
    
    def with_sample_subjects(self, subjects: List[str]) -> 'SenderDataBuilder':
        """Set sample subject lines from this sender."""
        self._data['sample_subjects'] = subjects
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the sender dictionary.
        
        Returns a copy so the builder can be reused.
        """
        return self._data.copy()


class AccountDataBuilder:
    """Builder for account data dictionaries.
    
    Provides fluent API for creating account objects.
    
    Example:
        account = AccountDataBuilder()\\
            .with_email('user@gmail.com')\\
            .with_provider('gmail')\\
            .with_password('encrypted_pass')\\
            .build()
    """
    
    def __init__(self):
        """Initialize builder with default account data."""
        self._data = {
            'email': 'test@example.com',
            'provider': 'gmail',
            'encrypted_password': 'encrypted_password_here',
            'added_date': '2024-01-01'
        }
    
    def with_email(self, email: str) -> 'AccountDataBuilder':
        """Set account email address."""
        self._data['email'] = email
        return self
    
    def with_provider(self, provider: str) -> 'AccountDataBuilder':
        """Set email provider (e.g., 'gmail', 'outlook')."""
        self._data['provider'] = provider
        return self
    
    def with_password(self, encrypted_password: str) -> 'AccountDataBuilder':
        """Set encrypted password."""
        self._data['encrypted_password'] = encrypted_password
        return self
    
    def with_added_date(self, date: str) -> 'AccountDataBuilder':
        """Set date account was added."""
        self._data['added_date'] = date
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the account dictionary.
        
        Returns a copy so the builder can be reused.
        """
        return self._data.copy()

