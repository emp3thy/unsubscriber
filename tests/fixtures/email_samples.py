"""Sample email data for testing."""

# Sample email with all standard fields
SAMPLE_EMAIL_FULL = {
    'sender': 'newsletter@example.com',
    'subject': 'Weekly Newsletter',
    'date': '2024-01-01',
    'is_unread': True,
    'list_unsubscribe': '<https://example.com/unsub>',
    'unsubscribe_links': ['https://example.com/unsub'],
    'body_text': 'This is a newsletter email.',
    'body_html': '<html><body>This is a newsletter email.</body></html>'
}

# Sample email without unsubscribe link
SAMPLE_EMAIL_NO_UNSUB = {
    'sender': 'personal@example.com',
    'subject': 'Personal Email',
    'date': '2024-01-02',
    'is_unread': False,
    'list_unsubscribe': '',
    'unsubscribe_links': [],
    'body_text': 'Personal message',
    'body_html': ''
}

# Sample email with mailto unsubscribe
SAMPLE_EMAIL_MAILTO = {
    'sender': 'marketing@company.com',
    'subject': 'Marketing Update',
    'date': '2024-01-03',
    'is_unread': True,
    'list_unsubscribe': '<mailto:unsubscribe@company.com?subject=Unsubscribe>',
    'unsubscribe_links': [],
    'body_text': 'Marketing content',
    'body_html': ''
}

# Sample sender aggregate data
SAMPLE_SENDER = {
    'sender': 'newsletter@example.com',
    'email_count': 45,
    'unread_count': 12,
    'has_unsubscribe': True,
    'unsubscribe_links': ['https://example.com/unsub'],
    'list_unsubscribe': '<https://example.com/unsub>',
    'score': 85,
    'latest_date': '2024-01-01',
    'sample_subjects': ['Newsletter #1', 'Newsletter #2', 'Newsletter #3']
}

# Sample account data
SAMPLE_ACCOUNT = {
    'email': 'test@example.com',
    'provider': 'gmail',
    'encrypted_password': 'encrypted_password_here',
    'added_date': '2024-01-01'
}

