# Development Rules for Build Plan Execution

These are general rules for creating and executing build plans in a phased, step-by-step manner. These rules can be applied to any software project.

---

## Part A: Creating a Build Plan

### Rule 0: Build Plan Structure Requirements

**Mandatory structure:**
- ✅ Build plan MUST be divided into **Phases**
- ✅ Each phase MUST contain one or more **Steps**
- ✅ Each step MUST have clearly defined **Acceptance Criteria**
- ✅ Each step MUST specify **Files to Create/Modify**
- ✅ Each step MUST include a **Test** description

**Confidence scoring:**
- ✅ Each step MUST have a **Confidence Score** (0-100%)
- ✅ Each phase MUST have a **Composite Confidence Score** (average of all steps)
- ✅ Confidence represents likelihood of successful completion without blocking issues

**Execution rules based on confidence:**
- ⛔ Steps with confidence < 90% CANNOT be executed
- ⛔ Phases with composite confidence < 90% CANNOT be executed
- ✅ Steps/phases with confidence ≥ 90% CAN be executed
- ⚠️ If confidence < 90%, step/phase must be revised or broken down further

### Confidence Scoring Guidelines

**Confidence Levels:**

**95-100% (Very High Confidence)**
- All requirements are clear and unambiguous
- Technology/libraries are well-known and documented
- Similar implementations exist as reference
- No external dependencies or unknowns
- Standard, straightforward implementation

**90-94% (High Confidence)**
- Requirements are clear
- Technology is familiar but may have minor unknowns
- Good documentation available
- Minimal external dependencies
- May require some research but path is clear

**80-89% (Medium Confidence) ⚠️ CANNOT EXECUTE**
- Some requirements are unclear
- Technology is familiar but has edge cases to handle
- Documentation may be incomplete
- External dependencies with some unknowns
- May require trial and error
- **Action required:** Break into smaller steps or clarify requirements

**70-79% (Low Confidence) ⚠️ CANNOT EXECUTE**
- Requirements are vague or incomplete
- Technology is unfamiliar
- Limited documentation
- Significant external dependencies
- High chance of encountering blockers
- **Action required:** Research, prototype, or defer to later phase

**<70% (Very Low Confidence) ⚠️ CANNOT EXECUTE**
- Requirements are unclear or contradictory
- Technology is unknown
- No documentation or poor documentation
- Many unknowns and assumptions
- Very high risk of failure
- **Action required:** Spike, research, or remove from MVP

---

## Part B: Executing a Build Plan

These rules apply when executing a build plan that has been validated per Part A.

---

## Rule 1: Step Progression

**When you CAN proceed to next step:**
- ✅ Current step's acceptance criteria are fully met
- ✅ All files specified in "Files to Create/Modify" have been created/modified
- ✅ **Unit tests have been written for all code created/modified in this step**
- ✅ All unit tests pass
- ✅ Tests specified in the "Test" section have passed
- ✅ Code has been committed to git

**When you CANNOT proceed:**
- ❌ Acceptance criteria not met
- ❌ Unit tests not written for new/modified code
- ❌ Tests fail
- ❌ Code has errors or warnings
- ❌ Files not created as specified

**Skipping steps:**
- ❌ NEVER skip steps within a phase - must complete in order
- ✅ CAN proceed to next phase when all steps in current phase complete

---

## Rule 2: Step Execution Requirements

**Must do for every step:**
- ✅ Create or modify all specified files
- ✅ Implement the functionality described in acceptance criteria
- ✅ **CRITICAL: Write unit tests for any code created or altered in this step**
- ✅ Test that the step works before marking complete
- ✅ Commit to git after step completion with descriptive message
- ✅ Update CURRENT_PHASE.md to mark step as complete (add ✅)

**⛔ NEVER defer unit test creation to later steps or phases**
- Unit tests MUST be written in the same step as the code they test
- This is non-negotiable and critical to project success
- If you create or modify a class, write unit tests for that class immediately
- If you alter existing code, update or add unit tests in the same step

**Commit message format:**
```
Phase X, Step X.X: [Brief description]

- Acceptance criteria met:
  - [List what was achieved]
- Files modified: [List files]
- Unit tests: [Created/updated test file(s)]
- Test results: [Brief test outcome - unit tests + manual tests]
```

---

## Rule 5: Testing Requirements

**⛔ CRITICAL RULE: Unit Tests Must Be Written in the Same Step**
- **ALWAYS write unit tests for any code created or modified in a step**
- **NEVER defer unit testing to later steps or phases**
- This applies to ALL code: services, repositories, utilities, parsers, etc.
- Unit tests MUST be in the same commit as the code they test
- If you create a class in Step 3.2, write unit tests for that class in Step 3.2
- If you modify a method in Step 4.1, update/add unit tests for that method in Step 4.1
- No exceptions - this is a non-negotiable requirement

**Unit test requirements:**
- ✅ Write tests in `tests/unit/` directory matching the source structure
- ✅ Test file naming: `test_<module_name>.py`
- ✅ Use pytest framework (or project's standard framework)
- ✅ Achieve reasonable coverage (aim for >80% of new/modified code)
- ✅ Include both success and failure cases
- ✅ Mock external dependencies (databases, APIs, file systems)
- ✅ Tests must be fast (< 1 second per test preferred)

---

# PHASE 5: Add Comprehensive Unit Tests

**Goal:** Achieve 80%+ code coverage with unit tests  
**Duration Estimate:** 12-16 hours  
**Prerequisites:** Phases 1-4 complete  
**Phase Confidence:** 93% (Average of all step confidences)

**Progress:**
- ✅ Step 5.1: Test Repository Classes (COMPLETE - done in Phase 2)
- ✅ Step 5.2: Test Service Classes (COMPLETE - done in Phase 3)
- ✅ Step 5.3: Test Email Clients (COMPLETE)
- ✅ Step 5.4: Test Scoring and Grouping (COMPLETE)
- ✅ Step 5.5: Test Unsubscribe Strategies (COMPLETE)

---

## Step 5.3: Test Email Clients

**Confidence:** 92%

**Description:**
Create unit tests for IMAPClient and GmailAPIClient, mocking the underlying connection managers and network calls. Focus on testing client business logic, not actual IMAP/Gmail API.

**Implementation Details:**
- Create test files in `tests/unit/email_client/`
- Test files:
  - `test_imap_client.py`
  - `test_gmail_api_client.py`
  - `test_email_parser.py`
  - `test_client_factory.py`
- Mock connection managers
- Mock imaplib/googleapiclient responses
- Test scenarios:
  - Successful operations
  - Connection failures
  - Authentication failures
  - Parse errors
  - Empty results
- Use recorded fixtures for complex responses
- Aim for 85%+ coverage

**IMAP Mock Pattern (using MagicMock for imaplib):**
```python
@pytest.fixture
def mock_imap_connection():
    """Mock imaplib.IMAP4_SSL connection."""
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        connection = MagicMock()
        mock_imap.return_value = connection
        
        # Setup typical responses
        connection.select.return_value = ('OK', [b'150'])  # 150 emails
        connection.search.return_value = ('OK', [b'1 2 3 4 5'])
        connection.fetch.return_value = ('OK', [
            (b'1 (RFC822.HEADER {123}', b'From: test@example.com\r\n...'),
            b')'
        ])
        connection.logout.return_value = ('BYE', [b'Logging out'])
        
        yield connection

def test_imap_fetch_headers(mock_imap_connection):
    """Test IMAP header fetching."""
    client = IMAPClient('test@gmail.com', mock_auth_strategy)
    client.imap = mock_imap_connection  # Inject mock
    
    headers = client.fetch_headers([b'1', b'2'])
    
    assert len(headers) == 2
    assert mock_imap_connection.fetch.call_count == 2
```

**Gmail API Mock Pattern (using Mock for googleapiclient):**
```python
@pytest.fixture
def mock_gmail_service():
    """Mock Gmail API service."""
    service = MagicMock()
    
    # Mock messages().list() chain
    service.users().messages().list().execute.return_value = {
        'messages': [{'id': '123'}, {'id': '456'}]
    }
    
    # Mock messages().get() chain
    service.users().messages().get().execute.return_value = {
        'id': '123',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'test@example.com'},
                {'name': 'Subject', 'value': 'Test Email'}
            ]
        },
        'snippet': 'Email preview...'
    }
    
    return service

def test_gmail_fetch_email_ids(mock_gmail_service):
    """Test Gmail API email ID fetching."""
    client = GmailAPIClient('test@gmail.com', mock_oauth_manager)
    client.service = mock_gmail_service  # Inject mock
    
    ids = client.fetch_email_ids()
    
    assert ids == ['123', '456']
    mock_gmail_service.users().messages().list.assert_called_once()
```

**Recorded Fixtures for Complex Responses:**
```python
# tests/fixtures/email_responses.py
SAMPLE_IMAP_HEADER = b'''From: "Test Sender" <test@example.com>
Subject: =?UTF-8?B?VGVzdCBTdWJqZWN0?=
Date: Mon, 1 Jan 2024 12:00:00 +0000
List-Unsubscribe: <https://example.com/unsub>

'''

SAMPLE_GMAIL_MESSAGE = {
    'id': 'msg123',
    'threadId': 'thread456',
    'labelIds': ['INBOX', 'UNREAD'],
    'snippet': 'This is a test email...',
    'payload': {
        'headers': [
            {'name': 'From', 'value': 'Test <test@example.com>'},
            {'name': 'Subject', 'value': 'Test Subject'},
            {'name': 'Date', 'value': 'Mon, 1 Jan 2024 12:00:00 +0000'},
            {'name': 'List-Unsubscribe', 'value': '<https://example.com/unsub>'}
        ],
        'body': {'size': 1234}
    }
}
```

**Network Call Prevention:**
```python
# tests/unit/email_client/conftest.py
import pytest

@pytest.fixture(autouse=True)
def block_network_calls(monkeypatch):
    """Prevent any real network calls in email client tests."""
    def block_urlopen(*args, **kwargs):
        raise RuntimeError("Network call blocked in unit tests!")
    
    monkeypatch.setattr('urllib.request.urlopen', block_urlopen)
    monkeypatch.setattr('socket.socket.connect', block_urlopen)
```

**Acceptance Criteria:**
- ✅ Test files created for both clients
- ✅ Connection manager mocked using MagicMock patterns
- ✅ IMAP/API calls mocked with recorded fixtures
- ✅ All client methods tested
- ✅ Error handling tested (connection, auth, parse errors)
- ✅ Parser tested with various email formats (UTF-8, base64, multipart)
- ✅ No real network calls made (verified with auto-blocking fixture)
- ✅ Coverage 85%+ for client classes
- ✅ Tests use recorded fixtures for realistic responses

**Files to Create:**
- `tests/unit/email_client/test_imap_client.py`
- `tests/unit/email_client/test_gmail_api_client.py`
- `tests/unit/email_client/test_email_parser.py`
- `tests/unit/email_client/test_client_factory.py`
- `tests/fixtures/email_responses.py` - Recorded response fixtures

**Files to Modify:**
- `tests/unit/email_client/conftest.py` (create if doesn't exist) - Add network blocking fixture

**Dependencies:**
- pytest
- pytest-mock
- Email client classes

**Test:**
1. Run `pytest tests/unit/email_client/ -v`
2. Verify all tests pass
3. Verify no network calls (auto-blocked by fixture)
4. Run with coverage
5. Check coverage 85%+
6. Verify mocks accurately represent real API responses

**Confidence Rationale:**
92% confidence - Added specific mock patterns for both IMAP and Gmail API with recorded fixtures from actual responses. Network call prevention is automatic. Mock patterns match real library interfaces. Risk reduced to minor edge cases in response parsing.

---

## Step 5.4: Test Scoring and Grouping

**Confidence:** 94%

**Description:**
Create unit tests for EmailScorer and EmailGrouper classes. These are pure business logic with minimal dependencies, making them easier to test comprehensively.

**Implementation Details:**
- Create test files in `tests/unit/scoring/`
- Test files:
  - `test_scorer.py`
  - `test_email_grouper.py`
  - `test_analytics.py`
- Test scorer with various email attributes
- Test score breakdown calculation
- Test whitelist integration
- Test grouper with various email sets
- Test edge cases:
  - Empty email list
  - Single email
  - Large email list (performance)
  - Duplicate senders
- Aim for 95%+ coverage

**Acceptance Criteria:**
- ✅ Test files created for scorer and grouper
- ✅ All scoring logic tested
- ✅ Score breakdown verified
- ✅ Whitelist handling tested
- ✅ Grouping logic tested
- ✅ Edge cases covered
- ✅ Performance acceptable (< 1s for 1000 emails)
- ✅ Coverage 95%+ for scoring classes

**Files to Create:**
- `tests/unit/scoring/__init__.py`
- `tests/unit/scoring/test_scorer.py`
- `tests/unit/scoring/test_email_grouper.py`
- `tests/unit/scoring/test_analytics.py`

**Files to Modify:**
- None

**Dependencies:**
- pytest
- Scoring classes

**Test:**
1. Run `pytest tests/unit/scoring/ -v`
2. Verify all tests pass
3. Run with coverage
4. Check coverage 95%+
5. Run performance test with 1000 emails - verify < 1s

**Confidence Rationale:**
94% confidence - Pure business logic, easy to test. Minor risk around edge case coverage and ensuring all score components tested.

---

## Step 5.5: Test Unsubscribe Strategies

**Confidence:** 93%

**Description:**
Create unit tests for all unsubscribe strategy classes, mocking HTTP requests and email sends. Test strategy chain coordination and fallback behavior.

**Implementation Details:**
- Create test files in `tests/unit/unsubscribe/`
- Test files:
  - `test_list_unsubscribe.py`
  - `test_http_strategy.py`
  - `test_mailto_strategy.py`
  - `test_strategy_chain.py`
  - `test_rate_limiter.py`
- Use `responses` library for HTTP mocking (declarative, reliable)
- Mock smtplib for mailto strategy
- Test strategy can_handle() logic
- Test strategy execute() logic
- Test chain fallback behavior
- Test rate limiting
- Aim for 90%+ coverage

**HTTP Mocking with responses Library:**
```python
import responses

@responses.activate
def test_list_unsubscribe_success():
    """Test successful unsubscribe via List-Unsubscribe header."""
    # Setup mock HTTP response
    responses.add(
        responses.GET,
        'https://example.com/unsubscribe',
        status=200,
        body='Successfully unsubscribed'
    )
    
    strategy = ListUnsubscribeStrategy()
    email_data = {
        'sender': 'test@example.com',
        'list_unsubscribe': '<https://example.com/unsubscribe>'
    }
    
    success, message = strategy.execute(email_data)
    
    assert success is True
    assert 'Successfully' in message
    assert len(responses.calls) == 1

@responses.activate
def test_list_unsubscribe_redirect():
    """Test handling of redirects."""
    responses.add(
        responses.GET,
        'https://example.com/unsub',
        status=301,
        headers={'Location': 'https://example.com/confirm'}
    )
    responses.add(
        responses.GET,
        'https://example.com/confirm',
        status=200
    )
    
    strategy = ListUnsubscribeStrategy()
    email_data = {
        'sender': 'test@example.com',
        'list_unsubscribe': '<https://example.com/unsub>'
    }
    
    success, message = strategy.execute(email_data)
    
    assert success is True
    assert len(responses.calls) == 2  # Followed redirect

@responses.activate
def test_list_unsubscribe_timeout():
    """Test timeout handling."""
    responses.add(
        responses.GET,
        'https://example.com/unsub',
        body=requests.Timeout('Request timed out')
    )
    
    strategy = ListUnsubscribeStrategy()
    email_data = {
        'sender': 'test@example.com',
        'list_unsubscribe': '<https://example.com/unsub>'
    }
    
    success, message = strategy.execute(email_data)
    
    assert success is False
    assert 'timed out' in message.lower()
```

**Strategy Chain Fallback Testing:**
```python
def test_strategy_chain_fallback():
    """Test that chain tries next strategy when first fails."""
    chain = StrategyChain(mock_db)
    
    # First strategy fails
    strategy1 = Mock()
    strategy1.can_handle.return_value = True
    strategy1.execute.return_value = (False, 'Strategy 1 failed')
    strategy1.__class__.__name__ = 'Strategy1'
    
    # Second strategy succeeds
    strategy2 = Mock()
    strategy2.can_handle.return_value = True
    strategy2.execute.return_value = (True, 'Strategy 2 succeeded')
    strategy2.__class__.__name__ = 'Strategy2'
    
    chain.add_strategy(strategy1)
    chain.add_strategy(strategy2)
    
    email_data = {'sender': 'test@example.com'}
    success, message, strategy_name = chain.execute(email_data)
    
    assert success is True
    assert 'Strategy 2' in message
    assert strategy_name == 'Strategy2'
    # Verify both were tried
    strategy1.execute.assert_called_once()
    strategy2.execute.assert_called_once()
```

**can_handle() Logic Testing:**
```python
def test_list_unsubscribe_can_handle():
    """Test can_handle returns True only for emails with List-Unsubscribe."""
    strategy = ListUnsubscribeStrategy()
    
    # Has List-Unsubscribe
    assert strategy.can_handle({
        'list_unsubscribe': '<https://example.com/unsub>'
    }) is True
    
    # No List-Unsubscribe
    assert strategy.can_handle({
        'sender': 'test@example.com'
    }) is False
    
    # Empty List-Unsubscribe
    assert strategy.can_handle({
        'list_unsubscribe': ''
    }) is False
    
    # Only mailto (should still handle)
    assert strategy.can_handle({
        'list_unsubscribe': '<mailto:unsub@example.com>'
    }) is True
```

**Acceptance Criteria:**
- ✅ Test files created for all strategies
- ✅ HTTP requests mocked using responses library (declarative)
- ✅ Email sends mocked using unittest.mock
- ✅ can_handle() logic tested with various inputs
- ✅ execute() success and failure tested
- ✅ Strategy chain fallback tested with mock strategies
- ✅ Rate limiting tested with timing verification
- ✅ Coverage 90%+ for strategy classes
- ✅ All HTTP status codes tested (200, 3xx, 4xx, 5xx, timeout)
- ✅ Redirect handling tested

**Files to Create:**
- `tests/unit/unsubscribe/__init__.py`
- `tests/unit/unsubscribe/test_list_unsubscribe.py`
- `tests/unit/unsubscribe/test_http_strategy.py`
- `tests/unit/unsubscribe/test_mailto_strategy.py`
- `tests/unit/unsubscribe/test_strategy_chain.py`
- `tests/unit/unsubscribe/test_rate_limiter.py`

**Files to Modify:**
- `requirements.txt` - Add responses library

**Dependencies:**
- pytest
- pytest-mock
- responses (for mocking HTTP requests)
- Unsubscribe classes

**Test:**
1. Run `pytest tests/unit/unsubscribe/ -v`
2. Verify all tests pass
3. Verify no real HTTP requests (responses library blocks them)
4. Run with coverage
5. Check coverage 90%+
6. Verify rate limiter tests are deterministic (no flakiness)

**Confidence Rationale:**
93% confidence - responses library provides declarative, reliable HTTP mocking. Rate limiter testing uses standard timing patterns. Strategy chain testing uses simple mock objects. All patterns are well-established. Risk reduced to minor edge cases in error message formatting.

---

## Progress Tracking

Mark steps complete as you finish them:

- ✅ Step 5.1: Test Repository Classes (COMPLETE)
- ✅ Step 5.2: Test Service Classes (COMPLETE)
- ❌ Step 5.3: Test Email Clients
- ❌ Step 5.4: Test Scoring and Grouping
- ❌ Step 5.5: Test Unsubscribe Strategies

