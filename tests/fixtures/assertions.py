"""Custom assertion helpers for validating test data structures."""

from typing import Dict, Any


def assert_email_structure(email: Dict[str, Any]) -> None:
    """Validate that email dictionary has correct structure.
    
    Args:
        email: Email dictionary to validate
        
    Raises:
        AssertionError: If email structure is invalid with descriptive message
    """
    required_fields = [
        'sender',
        'subject',
        'date',
        'is_unread',
        'unsubscribe_links',
        'list_unsubscribe',
        'body_text',
        'body_html'
    ]
    
    # Check email is a dictionary
    assert isinstance(email, dict), \
        f"Email must be a dictionary, got {type(email).__name__}"
    
    # Check all required fields are present
    missing_fields = [field for field in required_fields if field not in email]
    assert not missing_fields, \
        f"Email missing required fields: {', '.join(missing_fields)}"
    
    # Validate field types
    assert isinstance(email['sender'], str), \
        f"sender must be str, got {type(email['sender']).__name__}"
    
    assert isinstance(email['subject'], str), \
        f"subject must be str, got {type(email['subject']).__name__}"
    
    assert isinstance(email['date'], str), \
        f"date must be str, got {type(email['date']).__name__}"
    
    assert isinstance(email['is_unread'], bool), \
        f"is_unread must be bool, got {type(email['is_unread']).__name__}"
    
    assert isinstance(email['unsubscribe_links'], list), \
        f"unsubscribe_links must be list, got {type(email['unsubscribe_links']).__name__}"
    
    assert isinstance(email['list_unsubscribe'], str), \
        f"list_unsubscribe must be str, got {type(email['list_unsubscribe']).__name__}"
    
    assert isinstance(email['body_text'], str), \
        f"body_text must be str, got {type(email['body_text']).__name__}"
    
    assert isinstance(email['body_html'], str), \
        f"body_html must be str, got {type(email['body_html']).__name__}"


def assert_sender_structure(sender: Dict[str, Any]) -> None:
    """Validate that sender dictionary has correct structure.
    
    Args:
        sender: Sender dictionary to validate
        
    Raises:
        AssertionError: If sender structure is invalid with descriptive message
    """
    required_fields = [
        'sender',
        'email_count',
        'unread_count',
        'has_unsubscribe',
        'unsubscribe_links',
        'list_unsubscribe',
        'score',
        'latest_date',
        'sample_subjects'
    ]
    
    # Check sender is a dictionary
    assert isinstance(sender, dict), \
        f"Sender must be a dictionary, got {type(sender).__name__}"
    
    # Check all required fields are present
    missing_fields = [field for field in required_fields if field not in sender]
    assert not missing_fields, \
        f"Sender missing required fields: {', '.join(missing_fields)}"
    
    # Validate field types
    assert isinstance(sender['sender'], str), \
        f"sender must be str, got {type(sender['sender']).__name__}"
    
    assert isinstance(sender['email_count'], int), \
        f"email_count must be int, got {type(sender['email_count']).__name__}"
    
    assert isinstance(sender['unread_count'], int), \
        f"unread_count must be int, got {type(sender['unread_count']).__name__}"
    
    assert isinstance(sender['has_unsubscribe'], bool), \
        f"has_unsubscribe must be bool, got {type(sender['has_unsubscribe']).__name__}"
    
    assert isinstance(sender['unsubscribe_links'], list), \
        f"unsubscribe_links must be list, got {type(sender['unsubscribe_links']).__name__}"
    
    assert isinstance(sender['list_unsubscribe'], str), \
        f"list_unsubscribe must be str, got {type(sender['list_unsubscribe']).__name__}"
    
    assert isinstance(sender['score'], int), \
        f"score must be int, got {type(sender['score']).__name__}"
    
    assert isinstance(sender['latest_date'], str), \
        f"latest_date must be str, got {type(sender['latest_date']).__name__}"
    
    assert isinstance(sender['sample_subjects'], list), \
        f"sample_subjects must be list, got {type(sender['sample_subjects']).__name__}"
    
    # Validate business logic
    assert sender['email_count'] >= 0, \
        f"email_count must be >= 0, got {sender['email_count']}"
    
    assert sender['unread_count'] >= 0, \
        f"unread_count must be >= 0, got {sender['unread_count']}"
    
    assert sender['unread_count'] <= sender['email_count'], \
        f"unread_count ({sender['unread_count']}) cannot exceed email_count ({sender['email_count']})"
    
    assert 0 <= sender['score'] <= 100, \
        f"score must be between 0 and 100, got {sender['score']}"


def assert_account_structure(account: Dict[str, Any]) -> None:
    """Validate that account dictionary has correct structure.
    
    Args:
        account: Account dictionary to validate
        
    Raises:
        AssertionError: If account structure is invalid with descriptive message
    """
    required_fields = [
        'email',
        'provider',
        'encrypted_password',
        'added_date'
    ]
    
    # Check account is a dictionary
    assert isinstance(account, dict), \
        f"Account must be a dictionary, got {type(account).__name__}"
    
    # Check all required fields are present
    missing_fields = [field for field in required_fields if field not in account]
    assert not missing_fields, \
        f"Account missing required fields: {', '.join(missing_fields)}"
    
    # Validate field types
    assert isinstance(account['email'], str), \
        f"email must be str, got {type(account['email']).__name__}"
    
    assert isinstance(account['provider'], str), \
        f"provider must be str, got {type(account['provider']).__name__}"
    
    assert isinstance(account['encrypted_password'], str), \
        f"encrypted_password must be str, got {type(account['encrypted_password']).__name__}"
    
    assert isinstance(account['added_date'], str), \
        f"added_date must be str, got {type(account['added_date']).__name__}"
    
    # Validate email format (basic check)
    assert '@' in account['email'], \
        f"email must contain '@', got {account['email']}"

