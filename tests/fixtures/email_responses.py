"""Recorded email response fixtures for testing.

These fixtures contain realistic email data structures from IMAP and Gmail API
to ensure tests accurately reflect real-world scenarios.
"""

# Sample IMAP raw email with various headers
SAMPLE_IMAP_HEADER = b"""From: "Test Newsletter" <newsletter@example.com>
Subject: =?UTF-8?B?V2Vla2x5IE5ld3NsZXR0ZXI=?=
Date: Mon, 1 Jan 2024 12:00:00 +0000
List-Unsubscribe: <https://example.com/unsubscribe?id=123>, <mailto:unsub@example.com>
Message-ID: <abc123@example.com>
Content-Type: text/plain; charset=UTF-8

This is the email body.
"""

# Sample IMAP email with multipart content
SAMPLE_IMAP_MULTIPART = b"""From: marketing@company.com
Subject: Special Offer
Date: Tue, 2 Jan 2024 10:00:00 +0000
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset=UTF-8

Plain text version.
Unsubscribe here: https://company.com/optout

--boundary123
Content-Type: text/html; charset=UTF-8

<html><body>
<p>HTML version.</p>
<a href="https://company.com/optout">Unsubscribe</a>
</body></html>
--boundary123--
"""

# Sample IMAP email without unsubscribe link
SAMPLE_IMAP_NO_UNSUB = b"""From: friend@personal.com
Subject: Hey there
Date: Wed, 3 Jan 2024 15:00:00 +0000
Content-Type: text/plain; charset=UTF-8

Just a personal email from a friend.
"""

# Sample Gmail API message format
SAMPLE_GMAIL_MESSAGE = {
    'id': 'msg_12345',
    'threadId': 'thread_456',
    'labelIds': ['INBOX', 'UNREAD'],
    'snippet': 'This is a test email with unsubscribe link...',
    'internalDate': '1704110400000',
    'payload': {
        'partId': '',
        'mimeType': 'text/html',
        'filename': '',
        'headers': [
            {'name': 'From', 'value': 'Test Sender <test@example.com>'},
            {'name': 'To', 'value': 'user@gmail.com'},
            {'name': 'Subject', 'value': 'Test Email'},
            {'name': 'Date', 'value': 'Mon, 1 Jan 2024 12:00:00 +0000'},
            {'name': 'Message-ID', 'value': '<msg123@example.com>'},
            {'name': 'List-Unsubscribe', 'value': '<https://example.com/unsub>'}
        ],
        'body': {
            'size': 1234,
            'data': 'VGVzdCBlbWFpbCBib2R5'  # Base64 encoded "Test email body"
        }
    },
    'sizeEstimate': 1500
}

# Sample Gmail API message list response
SAMPLE_GMAIL_LIST_RESPONSE = {
    'messages': [
        {'id': 'msg_1', 'threadId': 'thread_1'},
        {'id': 'msg_2', 'threadId': 'thread_2'},
        {'id': 'msg_3', 'threadId': 'thread_3'}
    ],
    'nextPageToken': 'token123',
    'resultSizeEstimate': 100
}

# Sample Gmail API message without List-Unsubscribe
SAMPLE_GMAIL_PERSONAL = {
    'id': 'msg_personal',
    'threadId': 'thread_personal',
    'labelIds': ['INBOX'],
    'snippet': 'Personal message from friend...',
    'payload': {
        'headers': [
            {'name': 'From', 'value': 'Friend <friend@personal.com>'},
            {'name': 'Subject', 'value': 'Personal Email'},
            {'name': 'Date', 'value': 'Wed, 3 Jan 2024 15:00:00 +0000'}
        ],
        'body': {'size': 500}
    }
}

# Sample malformed email for error handling tests
SAMPLE_MALFORMED_EMAIL = b"""From: incomplete
Subject:
"""

# Sample encoded subject headers
SAMPLE_ENCODED_SUBJECTS = {
    'utf8': '=?UTF-8?B?VGVzdCBTdWJqZWN0?=',  # "Test Subject"
    'iso': '=?ISO-8859-1?Q?Test_Subject?=',
    'mixed': '=?UTF-8?B?VGVzdA==?= Plain =?UTF-8?B?U3ViamVjdA==?='  # "Test Plain Subject"
}

# Sample unsubscribe link patterns
SAMPLE_UNSUBSCRIBE_PATTERNS = {
    'http_only': '<https://example.com/unsubscribe>',
    'mailto_only': '<mailto:unsub@example.com>',
    'both': '<https://example.com/unsub>, <mailto:unsub@example.com>',
    'multiple_http': '<https://example.com/unsub1>, <https://example.com/unsub2>'
}

