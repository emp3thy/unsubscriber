# Email Unsubscriber - Refactoring Plan

**Document Purpose:** Comprehensive refactoring plan to improve code maintainability and testability by favoring smaller classes, better separation of concerns, and composability.

**Date Created:** October 11, 2025

---

## Goals

1. **Decompose Large Classes**: Break down god classes (MainWindow: 1642 lines, DBManager: 683 lines) into smaller, focused components
2. **Introduce Service Layer**: Extract business logic from UI into testable service classes
3. **Improve Dependency Injection**: Remove tight coupling by injecting dependencies instead of direct instantiation
4. **Enable Unit Testing**: Make all components easily testable in isolation
5. **Maintain Backward Compatibility**: Ensure application continues to work throughout refactoring

---

## Overall Strategy

- **Incremental Refactoring**: Refactor one layer at a time, maintaining working application state
- **Test-Driven Approach**: Add tests before or during refactoring to prevent regressions
- **Strangler Fig Pattern**: Create new interfaces alongside old code, then migrate gradually
- **Progress Tracking**: Update this document with completion markers (✅) for each completed step and phase

---

## Progress Tracking Requirements

**After completing each step:**
1. Mark the step header with ✅ (e.g., `### Step 1.1: Setup pytest ✅`)
2. Mark all acceptance criteria as complete with ✅
3. Add completion notes if any deviations occurred
4. Commit changes to git with message referencing the step

**After completing each phase:**
1. Mark the phase header with ✅ (e.g., `## Phase 1: Testing Infrastructure Setup ✅`)
2. Verify all steps in the phase are marked complete
3. Add phase completion summary with any notes
4. Commit the updated refactoring.md

**Tracking Format:**
```markdown
## Phase X: Phase Name ✅

**Completion Date:** YYYY-MM-DD
**Actual Duration:** X hours
**Notes:** Any deviations or learnings

### Step X.1: Step Name ✅

**Completion Date:** YYYY-MM-DD
**Notes:** Brief notes about implementation

**Acceptance Criteria:**
- ✅ Criterion 1 - Completed
- ✅ Criterion 2 - Completed
```

This document serves as both the plan and the progress tracker. Keep it updated throughout execution.

---

## Phase 1: Testing Infrastructure Setup ✅

**Completion Date:** 2025-10-11
**Actual Duration:** ~1 hour
**Notes:** All acceptance criteria met. Test infrastructure is working perfectly with 33 passing tests.

**Goal:** Establish testing framework and utilities for unit testing  
**Duration Estimate:** 2-4 hours  
**Prerequisites:** None  
**Phase Confidence:** 96% (Average of all step confidences)

### Step 1.1: Setup pytest and Testing Structure ✅

**Completion Date:** 2025-10-11
**Notes:** pytest 8.4.2 installed, all fixtures working, 5 sample tests passing

**Confidence:** 98%

**Description:**
Set up pytest as the testing framework and create the basic test directory structure. This includes configuring pytest, adding necessary testing dependencies, and creating base test fixtures that can be reused across all test modules.

**Implementation Details:**
- Install pytest, pytest-mock, pytest-cov via requirements.txt
- Create `tests/` directory structure:
  - `tests/unit/` - Unit tests for individual components
  - `tests/integration/` - Integration tests
  - `tests/fixtures/` - Shared test fixtures
  - `tests/conftest.py` - Pytest configuration and shared fixtures
- Create `pytest.ini` for pytest configuration
- Add base fixtures:
  - `mock_db_manager` - Mock DBManager for testing
  - `sample_email_data` - Sample email dictionaries
  - `mock_imap_connection` - Mock IMAP connection

**Acceptance Criteria:**
- ✅ pytest installed and importable
- ✅ Test directory structure created with __init__.py files
- ✅ pytest.ini configured with test paths and markers
- ✅ Can run `pytest` command successfully (even with 0 tests)
- ✅ conftest.py contains at least 3 reusable fixtures
- ✅ Sample test file runs successfully
- ✅ **This refactoring.md document updated with ✅ markers**

**Files to Create:**
- `pytest.ini` - Pytest configuration
- `tests/__init__.py` - Test package initialization
- `tests/conftest.py` - Shared fixtures and configuration
- `tests/unit/__init__.py` - Unit test package
- `tests/integration/__init__.py` - Integration test package
- `tests/fixtures/__init__.py` - Fixtures package
- `tests/fixtures/email_samples.py` - Sample email data

**Files to Modify:**
- `requirements.txt` - Add pytest, pytest-mock, pytest-cov

**Dependencies:**
- pytest >= 7.0.0
- pytest-mock >= 3.10.0
- pytest-cov >= 4.0.0

**Test:**
1. Run `pip install -r requirements.txt`
2. Verify pytest installed: `pytest --version`
3. Run `pytest tests/` - should pass with 0 tests or sample test
4. Import fixtures in a test file to verify they work
5. Run `pytest --cov=src tests/` to verify coverage works
6. **Update this document: Mark step as complete with ✅**

**Confidence Rationale:**
98% confidence - pytest is well-documented, straightforward to set up. Minor risk around Windows path handling but standard patterns exist.

**Example Code:**
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_db_manager():
    """Mock DBManager for testing."""
    db = Mock()
    db.check_whitelist.return_value = False
    db.check_unwanted.return_value = False
    db.get_primary_account.return_value = {
        'email': 'test@example.com',
        'provider': 'gmail',
        'encrypted_password': 'encrypted'
    }
    return db

@pytest.fixture
def sample_email_data():
    """Sample email data for testing."""
    return {
        'sender': 'newsletter@example.com',
        'subject': 'Weekly Newsletter',
        'date': '2024-01-01',
        'is_unread': True,
        'list_unsubscribe': '<https://example.com/unsub>',
        'unsubscribe_links': ['https://example.com/unsub']
    }
```

### Step 1.2: Create Test Utilities and Builders ✅

**Completion Date:** 2025-10-11
**Notes:** All three builders (Email, Sender, Account) implemented with fluent API. Assertion helpers provide clear validation errors. 28 comprehensive tests all passing.

**Confidence:** 95%

**Description:**
Create utility classes and builder patterns for constructing test data. These utilities will make it easier to create complex test objects (emails, senders, accounts) with sensible defaults and easy customization.

**Implementation Details:**
- Create `TestDataBuilder` class using Builder pattern
- Create `EmailDataBuilder` for constructing email dictionaries
- Create `SenderDataBuilder` for constructing sender aggregates
- Create `AccountDataBuilder` for constructing account objects
- Each builder should have:
  - Sensible defaults for all fields
  - Fluent API for customization (`.with_sender()`, `.with_unread()`, etc.)
  - `.build()` method returning the dictionary
- Create assertion helpers:
  - `assert_email_structure()` - Validates email dictionary structure
  - `assert_sender_structure()` - Validates sender dictionary structure

**Acceptance Criteria:**
- ✅ Can create email data with `EmailDataBuilder().build()`
- ✅ Can customize fields: `EmailDataBuilder().with_sender('test@example.com').build()`
- ✅ Can create sender data with `SenderDataBuilder().build()`
- ✅ Can create account data with `AccountDataBuilder().build()`
- ✅ All builders produce valid dictionaries matching expected structure
- ✅ Assertion helpers correctly validate structure and raise clear errors
- ✅ **This refactoring.md document updated with ✅ markers**

**Files to Create:**
- `tests/fixtures/builders.py` - Data builder classes
- `tests/fixtures/assertions.py` - Custom assertion helpers

**Files to Modify:**
- None

**Dependencies:**
- None (pure Python)

**Test:**
1. Create email using `EmailDataBuilder().build()` and verify structure
2. Create email with custom sender: `EmailDataBuilder().with_sender('custom@test.com').build()`
3. Create sender with 10 emails: `SenderDataBuilder().with_email_count(10).build()`
4. Use assertion helper on valid data - should pass
5. Use assertion helper on invalid data - should raise AssertionError with clear message
6. **Update this document: Mark step as complete with ✅**

**Confidence Rationale:**
95% confidence - Builder pattern is straightforward, just need to match existing dictionary structures. Minor risk of missing fields but tests will catch this.

**Example Code:**
```python
# tests/fixtures/builders.py
class EmailDataBuilder:
    """Builder for email data dictionaries."""
    
    def __init__(self):
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
    
    def with_sender(self, sender: str):
        self._data['sender'] = sender
        return self
    
    def with_unread(self, is_unread: bool = True):
        self._data['is_unread'] = is_unread
        return self
    
    def with_unsubscribe_link(self, link: str):
        self._data['unsubscribe_links'].append(link)
        self._data['list_unsubscribe'] = f'<{link}>'
        return self
    
    def build(self):
        return self._data.copy()
```

---

## Phase 2: Extract Repository Layer from DBManager ✅

**Completion Date:** 2025-10-12
**Actual Duration:** ~4 hours
**Notes:** All 7 steps completed successfully. DBManager refactored into 5 specialized repositories with facade pattern maintaining backward compatibility. 112 repository tests passing.

**Goal:** Break down DBManager into smaller, focused repository classes  
**Duration Estimate:** 6-8 hours  
**Prerequisites:** Phase 1 complete  
**Phase Confidence:** 93% (Average of all step confidences)

### Step 2.1: Create Base Repository Class ✅

**Completion Date:** 2025-10-12
**Notes:** BaseRepository with connection management, transaction handling, and query methods. 13 tests passing.

**Confidence:** 95%

**Description:**
Create an abstract base repository class that handles database connection management. This will provide a common foundation for all repository classes, including connection pooling, transaction management, and error handling.

**Implementation Details:**
- Create `BaseRepository` class in `src/database/base_repository.py`
- Move connection management logic from DBManager
- Implement context manager protocol (`__enter__`, `__exit__`)
- Provide protected methods:
  - `_execute_query(sql, params)` - Execute query with automatic transaction handling
  - `_execute_many(sql, params_list)` - Execute batch queries
  - `_fetch_one(sql, params)` - Fetch single row
  - `_fetch_all(sql, params)` - Fetch all rows
- All methods use parameterized queries
- Automatic commit on success, rollback on error
- Comprehensive logging of all database operations

**Acceptance Criteria:**
- ✅ BaseRepository class created with connection management (COMPLETED)
- ✅ Can instantiate with db_path: `BaseRepository('/path/to/db')`
- ✅ Context manager works: `with BaseRepository(path) as repo: ...`
- ✅ Protected query methods handle SQL injection via parameterization
- ✅ Transactions automatically commit on success
- ✅ Transactions automatically rollback on error
- ✅ All database errors logged with context

**Files to Create:**
- `src/database/base_repository.py` - Base repository class

**Files to Modify:**
- None

**Dependencies:**
- sqlite3 (built-in)
- logging (built-in)
- contextlib (built-in)

**Test:**
1. Create test database and BaseRepository instance
2. Execute query using `_execute_query()` - verify data inserted
3. Execute query that fails - verify rollback occurs
4. Use as context manager - verify cleanup happens
5. Try SQL injection via parameters - verify prevented
6. Check logs for database operations

**Confidence Rationale:**
95% confidence - Connection management is well-understood pattern. Minor risk around transaction boundary edge cases but standard patterns exist.

**Example Code:**
```python
# src/database/base_repository.py
import sqlite3
import logging
from contextlib import contextmanager
from typing import Any, List, Tuple, Optional

class BaseRepository:
    """Base class for database repositories."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with automatic transaction management."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _execute_query(self, sql: str, params: Tuple = ()) -> None:
        """Execute a query that doesn't return results."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            self.logger.debug(f"Executed query: {sql[:50]}...")
    
    def _fetch_one(self, sql: str, params: Tuple = ()) -> Optional[Any]:
        """Fetch a single row."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchone()
    
    def _fetch_all(self, sql: str, params: Tuple = ()) -> List[Tuple]:
        """Fetch all rows."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
```

### Step 2.2: Create WhitelistRepository ✅

**Completion Date:** 2025-10-12
**Notes:** WhitelistRepository with email and domain pattern matching. 18 tests passing.

**Confidence:** 94%

**Description:**
Extract whitelist-related operations from DBManager into a dedicated WhitelistRepository class. This repository will handle all whitelist CRUD operations, inheriting transaction management from BaseRepository.

**Implementation Details:**
- Create `WhitelistRepository` class extending `BaseRepository`
- Move methods from DBManager:
  - `add_to_whitelist(entry, is_domain, notes)` - Add whitelist entry
  - `remove_from_whitelist(entry)` - Remove entry
  - `check_whitelist(email)` - Check if email/domain whitelisted
  - `get_whitelist()` - Get all entries
- Methods return strongly-typed results (not just row tuples)
- Add type hints for all methods
- Comprehensive docstrings with examples

**Acceptance Criteria:**
- ✅ WhitelistRepository class created extending BaseRepository (COMPLETED)
- ✅ Can add email to whitelist
- ✅ Can add domain to whitelist
- ✅ Can check if email is whitelisted (exact match)
- ✅ Can check if domain is whitelisted (pattern match)
- ✅ Can remove entry from whitelist
- ✅ Can get all whitelist entries as list of dicts
- ✅ Duplicate entries return False (not error)
- ✅ All methods have type hints and docstrings

**Files to Create:**
- `src/database/whitelist_repository.py` - Whitelist repository

**Files to Modify:**
- None (yet - will modify DBManager in later step)

**Dependencies:**
- src.database.base_repository

**Test:**
1. Create WhitelistRepository with test database
2. Add email 'test@example.com' - verify returns True
3. Add same email again - verify returns False (duplicate)
4. Check 'test@example.com' is whitelisted - verify True
5. Add domain '@company.com' - verify success
6. Check 'user@company.com' matches domain - verify True
7. Get all entries - verify returns list with both entries
8. Remove 'test@example.com' - verify success
9. Check 'test@example.com' - verify now False

**Confidence Rationale:**
94% confidence - Simple CRUD operations with clear requirements. Minor risk around domain pattern matching SQL but existing code provides reference.

**Example Code:**
```python
# src/database/whitelist_repository.py
from typing import List, Dict
from .base_repository import BaseRepository

class WhitelistRepository(BaseRepository):
    """Repository for whitelist operations."""
    
    def add_to_whitelist(self, entry: str, is_domain: bool = False, notes: str = "") -> bool:
        """Add an email or domain to whitelist.
        
        Args:
            entry: Email address or domain pattern (e.g., '@company.com')
            is_domain: True if entry is a domain pattern
            notes: Optional notes about this entry
        
        Returns:
            True if added, False if already exists
        """
        # Check for duplicates
        check_sql = "SELECT 1 FROM whitelist WHERE domain = ?" if is_domain else "SELECT 1 FROM whitelist WHERE email = ?"
        if self._fetch_one(check_sql, (entry,)):
            self.logger.info(f"Entry already in whitelist: {entry}")
            return False
        
        # Insert
        if is_domain:
            sql = "INSERT INTO whitelist (domain, notes) VALUES (?, ?)"
        else:
            sql = "INSERT INTO whitelist (email, notes) VALUES (?, ?)"
        
        self._execute_query(sql, (entry, notes))
        self.logger.info(f"Added to whitelist: {entry}")
        return True
    
    def check_whitelist(self, email: str) -> bool:
        """Check if email or its domain is whitelisted."""
        sql = """
            SELECT 1 FROM whitelist 
            WHERE email = ? 
            OR (domain IS NOT NULL AND ? LIKE '%' || domain)
            LIMIT 1
        """
        return self._fetch_one(sql, (email, email)) is not None
    
    def get_whitelist(self) -> List[Dict]:
        """Get all whitelist entries."""
        sql = """
            SELECT id, email, domain, notes, added_date
            FROM whitelist
            ORDER BY added_date DESC
        """
        rows = self._fetch_all(sql)
        
        result = []
        for row in rows:
            entry_type = 'domain' if row[2] else 'email'
            entry_value = row[2] if row[2] else row[1]
            result.append({
                'id': row[0],
                'entry': entry_value,
                'type': entry_type,
                'notes': row[3] or '',
                'added_date': row[4]
            })
        return result
```

### Step 2.3: Create AccountRepository ✅

**Completion Date:** 2025-10-12
**Notes:** AccountRepository with CRUD operations and UPSERT pattern. 16 tests passing.

**Confidence:** 93%

**Description:**
Extract account-related operations from DBManager into a dedicated AccountRepository. This handles CRUD operations for email accounts including credentials storage.

**Implementation Details:**
- Create `AccountRepository` class extending `BaseRepository`
- Move methods from DBManager:
  - `add_account(email, encrypted_password, provider)` - Add/update account
  - `get_account(email)` - Get account by email
  - `list_accounts()` - Get all accounts
  - `delete_account(email)` - Delete account
  - `get_primary_account()` - Get first account (default)
- Return typed dictionaries with all account fields
- Handle OAuth tokens (stored separately in future step)

**Acceptance Criteria:**
- ✅ AccountRepository class created extending BaseRepository (COMPLETED)
- ✅ Can add account with email, password, provider
- ✅ Can retrieve account by email
- ✅ Can list all accounts ordered by date
- ✅ Can delete account by email
- ✅ Can get primary (first) account
- ✅ UPDATE on duplicate email (not INSERT)
- ✅ All methods return typed dictionaries, not tuples

**Files to Create:**
- `src/database/account_repository.py` - Account repository

**Files to Modify:**
- None

**Dependencies:**
- src.database.base_repository

**Test:**
1. Create AccountRepository with test database
2. Add account 'test@gmail.com' - verify success
3. Get account 'test@gmail.com' - verify returns dict with email, provider
4. Add same email again with different password - verify updates (not duplicate)
5. Add second account 'other@gmail.com'
6. List accounts - verify returns list of 2 dicts
7. Get primary account - verify returns first account
8. Delete 'test@gmail.com' - verify success
9. List accounts - verify now only 1 account

**Confidence Rationale:**
93% confidence - Straightforward CRUD operations. Minor risk around encrypted password handling but DBManager already has this pattern.

### Step 2.4: Create ActionHistoryRepository ✅

**Completion Date:** 2025-10-12
**Notes:** ActionHistoryRepository with logging, stats, and query methods. 16 tests passing.

**Confidence:** 92%

**Description:**
Extract action logging and history operations from DBManager into ActionHistoryRepository. This handles logging of unsubscribe attempts, deletions, and other user actions.

**Implementation Details:**
- Create `ActionHistoryRepository` class extending `BaseRepository`
- Move methods from DBManager:
  - `log_action(sender_email, action_type, success, details)` - Log action
  - `get_action_history(limit)` - Get recent actions
  - `log_unsubscribe_attempt(sender, strategy, success, message)` - Specific unsubscribe logging
  - `get_strategy_stats()` - Get stats by strategy
  - `get_failure_reasons()` - Get common failure reasons
- Add helper methods for querying history:
  - `get_actions_for_sender(email)` - All actions for specific sender
  - `get_successful_actions(action_type)` - All successful actions of type
- Use proper datetime handling

**Acceptance Criteria:**
- ✅ ActionHistoryRepository class created (COMPLETED)
- ✅ Can log action with all required fields
- ✅ Can retrieve action history with limit
- ✅ Can log unsubscribe attempt with strategy info
- ✅ Can get strategy statistics (total, success, failure per strategy)
- ✅ Can get common failure reasons
- ✅ Can query actions for specific sender
- ✅ Timestamps automatically added with actions

**Files to Create:**
- `src/database/action_history_repository.py` - Action history repository

**Files to Modify:**
- None

**Dependencies:**
- src.database.base_repository

**Test:**
1. Create ActionHistoryRepository
2. Log action: unsubscribe, sender='test@example.com', success=True
3. Get action history - verify action appears
4. Log unsubscribe attempt with strategy 'ListUnsubscribe'
5. Get strategy stats - verify shows 1 attempt, 1 success
6. Log failed attempt with reason 'Network timeout'
7. Get failure reasons - verify 'Network timeout' appears
8. Get actions for 'test@example.com' - verify 2 actions

**Confidence Rationale:**
92% confidence - Stats queries are more complex than simple CRUD. Good reference code exists in DBManager but SQL aggregation may need refinement.

### Step 2.5: Create UnwantedSendersRepository ✅

**Completion Date:** 2025-10-12
**Notes:** UnwantedSendersRepository with must-delete list management. 20 tests passing.

**Confidence:** 91%

**Description:**
Extract unwanted senders and "must delete" list operations from DBManager into UnwantedSendersRepository. This manages the list of senders that failed unsubscribe and need manual deletion.

**Implementation Details:**
- Create `UnwantedSendersRepository` class extending `BaseRepository`
- Move methods from DBManager:
  - `add_to_must_delete(sender, reason)` - Add sender to must-delete list
  - `get_must_delete_senders()` - Get all must-delete senders
  - `remove_from_must_delete(sender)` - Remove from list
  - `get_must_delete_count()` - Count must-delete senders
  - `add_unwanted_sender(email, reason, failed_unsubscribe)` - General unwanted tracking
  - `check_unwanted(email)` - Check if email in unwanted list
- Use UPSERT pattern for idempotent adds
- Include reason and timestamp in all entries

**Acceptance Criteria:**
- ✅ UnwantedSendersRepository class created (COMPLETED)
- ✅ Can add sender to must-delete list with reason
- ✅ Can get all must-delete senders (returns list of dicts)
- ✅ Can remove sender from must-delete list
- ✅ Can get count of must-delete senders
- ✅ Can add unwanted sender (general, not must-delete)
- ✅ Can check if sender is in unwanted list
- ✅ Adding duplicate sender updates timestamp, doesn't duplicate

**Files to Create:**
- `src/database/unwanted_senders_repository.py` - Unwanted senders repository

**Files to Modify:**
- None

**Dependencies:**
- src.database.base_repository

**Test:**
1. Create UnwantedSendersRepository
2. Add 'spam@example.com' to must-delete with reason 'Failed unsub'
3. Get must-delete senders - verify contains entry with reason
4. Get must-delete count - verify returns 1
5. Add same sender again - verify updates, count still 1
6. Check 'spam@example.com' is unwanted - verify True
7. Remove from must-delete - verify success
8. Get must-delete count - verify returns 0

**Confidence Rationale:**
91% confidence - Straightforward operations but must-delete flag handling adds slight complexity. UPSERT pattern in SQLite may need careful SQL syntax.

### Step 2.6: Create ConfigRepository ✅

**Completion Date:** 2025-10-12
**Notes:** ConfigRepository with key-value storage and type conversion helpers. 19 tests passing.

**Confidence:** 94%

**Description:**
Extract configuration management from DBManager into ConfigRepository. This provides a simple key-value store for application settings.

**Implementation Details:**
- Create `ConfigRepository` class extending `BaseRepository`
- Move methods from DBManager:
  - `get_config(key, default)` - Get config value
  - `set_config(key, value)` - Set config value
- Add convenience methods:
  - `get_bool(key, default)` - Get boolean config
  - `get_int(key, default)` - Get integer config
  - `get_all_config()` - Get all config as dict
- Use INSERT OR REPLACE pattern for upserts
- Handle type conversions (store as string, parse on retrieval)

**Acceptance Criteria:**
- ✅ ConfigRepository class created (COMPLETED)
- ✅ Can set config key-value pair
- ✅ Can get config value by key
- ✅ Returns default if key doesn't exist
- ✅ Can get boolean config value with proper parsing
- ✅ Can get integer config value with proper parsing
- ✅ Setting same key again updates value (doesn't duplicate)
- ✅ Can get all config as dictionary

**Files to Create:**
- `src/database/config_repository.py` - Config repository

**Files to Modify:**
- None

**Dependencies:**
- src.database.base_repository

**Test:**
1. Create ConfigRepository
2. Set config: 'max_emails', '500'
3. Get config 'max_emails' - verify returns '500'
4. Get config 'nonexistent' with default 'test' - verify returns 'test'
5. Set 'debug_mode', 'true'
6. Get bool 'debug_mode' - verify returns True (bool)
7. Get int 'max_emails' - verify returns 500 (int)
8. Get all config - verify returns dict with both keys

**Confidence Rationale:**
94% confidence - Very simple key-value operations. Minor risk around type conversion edge cases but well-understood patterns exist.

### Step 2.7: Update DBManager to Use Repositories (Facade Pattern) ✅

**Completion Date:** 2025-10-12
**Notes:** DBManager successfully refactored as facade over repositories. All backward compatibility maintained. 10 facade tests + all repository tests passing.

**Confidence:** 90%

**Description:**
Refactor DBManager to act as a facade over the new repository classes. This maintains backward compatibility while using the new repository architecture underneath. Eventually, direct repository usage will replace DBManager calls.

**Implementation Details:**
- Keep DBManager class but delegate all operations to repositories
- Initialize all repositories in `__init__`
- Each DBManager method calls corresponding repository method
- Add deprecation warnings (using logging, not actual deprecation)
- Keep all existing method signatures for compatibility
- Example: `def add_to_whitelist(...)` → `return self.whitelist_repo.add_to_whitelist(...)`
- Add property methods for direct repository access:
  - `@property whitelist` → returns WhitelistRepository
  - `@property accounts` → returns AccountRepository

**Acceptance Criteria:**
- ✅ DBManager initializes all repository instances (COMPLETED)
- ✅ All existing DBManager methods still work (backward compatible)
- ✅ Each method delegates to appropriate repository
- ✅ Can access repositories directly: `db.whitelist.add_to_whitelist(...)`
- ✅ initialize_db() still works (creates schema)
- ✅ No direct SQL in DBManager (all via repositories)
- ✅ Existing application code still works without changes

**Files to Create:**
- None

**Files to Modify:**
- `src/database/db_manager.py` - Refactor to use repositories

**Dependencies:**
- All repository classes from previous steps

**Test:**
1. Create DBManager with test database
2. Call `db.add_to_whitelist('test@example.com')` - verify works
3. Call `db.add_account(...)` - verify works
4. Access repository directly: `db.whitelist.add_to_whitelist(...)` - verify works
5. Run existing application - verify no breaking changes
6. Check all CRUD operations still work through DBManager
7. Verify schema initialization works

**Confidence Rationale:**
90% confidence - Facade pattern is straightforward but ensuring complete backward compatibility across all methods requires careful testing. May miss edge cases in delegation.

**Example Code:**
```python
# src/database/db_manager.py (refactored)
from src.database.whitelist_repository import WhitelistRepository
from src.database.account_repository import AccountRepository
from src.database.action_history_repository import ActionHistoryRepository
from src.database.unwanted_senders_repository import UnwantedSendersRepository
from src.database.config_repository import ConfigRepository

class DBManager:
    """Facade over repository classes for backward compatibility."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize all repositories
        self._whitelist_repo = WhitelistRepository(db_path)
        self._account_repo = AccountRepository(db_path)
        self._history_repo = ActionHistoryRepository(db_path)
        self._unwanted_repo = UnwantedSendersRepository(db_path)
        self._config_repo = ConfigRepository(db_path)
    
    # Property access to repositories
    @property
    def whitelist(self) -> WhitelistRepository:
        return self._whitelist_repo
    
    @property
    def accounts(self) -> AccountRepository:
        return self._account_repo
    
    # Delegate methods for backward compatibility
    def add_to_whitelist(self, entry: str, is_domain: bool = False, notes: str = "") -> bool:
        return self._whitelist_repo.add_to_whitelist(entry, is_domain, notes)
    
    def check_whitelist(self, email: str) -> bool:
        return self._whitelist_repo.check_whitelist(email)
    
    # ... (delegate all other methods similarly)
```

---

## Phase 3: Extract Service Layer from MainWindow ✅

**Completion Date:** 2025-10-12
**Actual Duration:** ~2 hours
**Notes:** All 4 steps completed successfully. All services implemented with comprehensive error handling, progress callbacks, and cancellation support. Factory pattern provides clean dependency injection.

**Goal:** Extract business logic from UI into testable service classes  
**Duration Estimate:** 8-12 hours  
**Prerequisites:** Phase 2 complete  
**Phase Confidence:** 91% (Average of all step confidences)

### Step 3.1: Create EmailScanService ✅

**Completion Date:** 2025-10-12
**Notes:** EmailScanService created with full dependency injection. All tests passed.

**Confidence:** 92%

**Description:**
Extract email scanning logic from MainWindow into a dedicated EmailScanService. This service orchestrates fetching emails, parsing, scoring, and grouping senders.

**Implementation Details:**
- Create `EmailScanService` class in `src/services/email_scan_service.py`
- Constructor takes dependencies via dependency injection:
  - `email_client` - Email client (IMAP or Gmail API)
  - `db_manager` - Database manager
  - `parser` - EmailParser instance
  - `scorer` - EmailScorer instance
  - `grouper` - EmailGrouper instance
- Main method: `scan_inbox(progress_callback=None) -> List[Dict]`
- Method orchestrates:
  1. Fetch email IDs from client
  2. Fetch headers in batches
  3. Parse each email
  4. Score and group by sender
  5. Return sender list
- Progress callback: `callback(current, total, message)`
- Handle cancellation via threading event
- Comprehensive error handling with specific exception types

**Acceptance Criteria:**
- ✅ EmailScanService class created with dependency injection
- ✅ Can scan inbox and return sender list
- ✅ Progress callback called during scan (if provided)
- ✅ Handles connection errors gracefully
- ✅ Handles parsing errors (logs and continues)
- ✅ Returns empty list if no emails found
- ✅ Can be cancelled via threading event
- ✅ All dependencies injected, no direct instantiation

**Files to Create:**
- `src/services/__init__.py` - Services package
- `src/services/email_scan_service.py` - Email scan service

**Files to Modify:**
- None

**Dependencies:**
- src.email_client (clients)
- src.database.db_manager
- src.email_client.email_parser
- src.scoring.scorer
- src.scoring.email_grouper

**Test:**
1. Create EmailScanService with mock dependencies
2. Mock client to return 10 email IDs
3. Mock parser to return valid email dicts
4. Call scan_inbox() - verify returns sender list
5. Verify progress callback called multiple times
6. Mock connection error - verify handled gracefully
7. Mock parsing error - verify logs and continues
8. Test cancellation - verify stops and returns partial results

**Confidence Rationale:**
92% confidence - Extraction of existing logic into service class. Minor risk around callback threading and cancellation coordination.

**Example Code:**
```python
# src/services/email_scan_service.py
import logging
from typing import List, Dict, Callable, Optional
from threading import Event

class EmailScanService:
    """Service for scanning and analyzing inbox emails."""
    
    def __init__(self, email_client, db_manager, parser, scorer, grouper):
        """Initialize with injected dependencies."""
        self.email_client = email_client
        self.db = db_manager
        self.parser = parser
        self.scorer = scorer
        self.grouper = grouper
        self.logger = logging.getLogger(__name__)
        self.cancel_event = Event()
    
    def scan_inbox(self, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Scan inbox and return grouped sender data.
        
        Args:
            progress_callback: Optional callback(current, total, message)
        
        Returns:
            List of sender dictionaries with aggregated stats
        """
        try:
            # Fetch email IDs
            if progress_callback:
                progress_callback(0, 100, "Fetching email list...")
            
            email_ids = self.email_client.fetch_email_ids()
            total = len(email_ids)
            
            if total == 0:
                self.logger.info("No emails found")
                return []
            
            # Parse emails
            emails = []
            for i, email_id in enumerate(email_ids):
                if self.cancel_event.is_set():
                    self.logger.info("Scan cancelled")
                    break
                
                try:
                    headers = self.email_client.fetch_headers([email_id])
                    if headers:
                        email_data = self.parser.parse_email(headers[0])
                        emails.append(email_data)
                except Exception as e:
                    self.logger.warning(f"Error parsing email {email_id}: {e}")
                    continue
                
                # Update progress
                if progress_callback and i % 50 == 0:
                    progress_callback(i + 1, total, f"Processing {i+1:,} of {total:,}")
            
            # Score and group
            if progress_callback:
                progress_callback(total, total, "Analyzing senders...")
            
            senders = self.grouper.group_by_sender(emails)
            self.logger.info(f"Scan complete: {len(senders)} senders found")
            return senders
        
        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            raise
    
    def cancel(self):
        """Cancel ongoing scan."""
        self.cancel_event.set()
```

### Step 3.2: Create UnsubscribeService ✅

**Completion Date:** 2025-10-12
**Notes:** UnsubscribeService created with whitelist checking and comprehensive result tracking. All tests passed.

**Confidence:** 91%

**Description:**
Extract unsubscribe logic from MainWindow into UnsubscribeService. This service handles the process of unsubscribing from multiple senders using the strategy chain pattern.

**Implementation Details:**
- Create `UnsubscribeService` class in `src/services/unsubscribe_service.py`
- Constructor takes dependencies:
  - `strategy_chain` - StrategyChain for unsubscribe attempts
  - `db_manager` - For logging actions
- Main method: `unsubscribe_from_senders(senders, progress_callback) -> Dict`
- Returns detailed results:
  - `success_count` - Number of successful unsubscribes
  - `failed_count` - Number of failures
  - `skipped_count` - Number skipped (no unsubscribe method)
  - `details` - List of result messages
  - `successful_senders` - List of successfully unsubscribed senders
- Checks whitelist before attempting unsubscribe
- Logs all attempts to action history
- Supports cancellation via threading event

**Acceptance Criteria:**
- ✅ UnsubscribeService class created with dependency injection
- ✅ Can unsubscribe from multiple senders
- ✅ Returns detailed results dictionary
- ✅ Progress callback called for each sender
- ✅ Checks whitelist and skips whitelisted senders
- ✅ Logs all attempts (success and failure)
- ✅ Handles senders without unsubscribe methods
- ✅ Can be cancelled mid-operation

**Files to Create:**
- `src/services/unsubscribe_service.py` - Unsubscribe service

**Files to Modify:**
- None

**Dependencies:**
- src.unsubscribe.strategy_chain
- src.database.db_manager

**Test:**
1. Create UnsubscribeService with mock dependencies
2. Create list of 3 senders with unsubscribe links
3. Mock strategy chain to succeed
4. Call unsubscribe_from_senders() - verify success_count=3
5. Mock one sender as whitelisted - verify skipped
6. Mock strategy to fail for one sender - verify failed_count incremented
7. Test progress callback called for each sender
8. Test cancellation stops processing

**Confidence Rationale:**
91% confidence - Straightforward extraction of existing logic. Minor risk around result aggregation and status tracking for each sender.

### Step 3.3: Create EmailDeletionService ✅

**Completion Date:** 2025-10-12
**Notes:** EmailDeletionService created with whitelist protection and must-delete list integration. All tests passed.

**Confidence:** 90%

**Description:**
Extract email deletion logic from MainWindow into EmailDeletionService. This service handles bulk deletion of emails from specified senders with safety checks.

**Implementation Details:**
- Create `EmailDeletionService` class in `src/services/email_deletion_service.py`
- Constructor takes dependencies:
  - `email_client` - Email client for deletion
  - `db_manager` - For whitelist checking
- Methods:
  - `delete_from_senders(senders, progress_callback) -> Dict` - Delete from multiple senders
  - `delete_from_must_delete_list(progress_callback) -> Dict` - Auto-delete from must-delete list
- Whitelist safety check before any deletion
- Returns results dict with:
  - `deleted_senders` - Count of senders processed
  - `total_emails_deleted` - Total email count
  - `failed_senders` - Count of failures
  - `skipped_senders` - Count skipped (whitelisted or no emails)
- Updates must-delete list after successful deletion
- Comprehensive logging of all deletions

**Acceptance Criteria:**
- ✅ EmailDeletionService class created
- ✅ Can delete emails from multiple senders
- ✅ Returns detailed results dictionary
- ✅ Checks whitelist before deletion (safety)
- ✅ Removes from must-delete list after successful deletion
- ✅ Progress callback called for each sender
- ✅ Handles senders with no emails gracefully
- ✅ Can be cancelled mid-operation

**Files to Create:**
- `src/services/email_deletion_service.py` - Email deletion service

**Files to Modify:**
- None

**Dependencies:**
- src.email_client (clients)
- src.database.db_manager

**Test:**
1. Create EmailDeletionService with mock client and db
2. Create list of senders to delete from
3. Mock client to return deleted count
4. Call delete_from_senders() - verify returns correct counts
5. Mock one sender as whitelisted - verify skipped
6. Mock client error for one sender - verify failed_count incremented
7. Verify must-delete list updated after success
8. Test progress callback called

**Confidence Rationale:**
90% confidence - Deletion operations need careful testing. Risk around transactional integrity between email deletion and database updates.

### Step 3.4: Create ServiceFactory ✅

**Completion Date:** 2025-10-12
**Notes:** ServiceFactory created with proper dependency injection and service caching. All tests passed.

**Confidence:** 93%

**Description:**
Create a factory class for constructing services with proper dependency injection. This factory encapsulates the complexity of wiring dependencies together.

**Implementation Details:**
- Create `ServiceFactory` class in `src/services/service_factory.py`
- Constructor takes root dependencies:
  - `db_manager` - Database manager
  - `email_client` - Email client (optional, created on demand)
- Factory methods:
  - `create_scan_service() -> EmailScanService`
  - `create_unsubscribe_service() -> UnsubscribeService`
  - `create_deletion_service() -> EmailDeletionService`
- Handles creation of intermediate dependencies:
  - EmailParser, EmailScorer, EmailGrouper, StrategyChain
- Caches created services for reuse
- Provides method to update email client: `set_email_client(client)`

**Acceptance Criteria:**
- ✅ ServiceFactory class created
- ✅ Can create EmailScanService with all dependencies
- ✅ Can create UnsubscribeService with dependencies
- ✅ Can create EmailDeletionService with dependencies
- ✅ Services share same db_manager instance
- ✅ Services share same email_client instance
- ✅ Created services cached (same instance on repeated calls)
- ✅ Can update email client for all services

**Files to Create:**
- `src/services/service_factory.py` - Service factory

**Files to Modify:**
- None

**Dependencies:**
- All service classes
- All dependency classes (parser, scorer, grouper, etc.)

**Test:**
1. Create ServiceFactory with mock db_manager
2. Call create_scan_service() - verify returns EmailScanService
3. Call create_scan_service() again - verify same instance (cached)
4. Call create_unsubscribe_service() - verify returns UnsubscribeService
5. Verify all services share same db_manager
6. Update email client - verify all services use new client
7. Create factory without email client - verify deferred creation works

**Confidence Rationale:**
93% confidence - Factory pattern is straightforward. Minor risk around circular dependencies and caching edge cases.

**Example Code:**
```python
# src/services/service_factory.py
from src.services.email_scan_service import EmailScanService
from src.services.unsubscribe_service import UnsubscribeService
from src.services.email_deletion_service import EmailDeletionService
from src.email_client.email_parser import EmailParser
from src.scoring.scorer import EmailScorer
from src.scoring.email_grouper import EmailGrouper
from src.unsubscribe.strategy_chain import StrategyChain
from src.unsubscribe.list_unsubscribe import ListUnsubscribeStrategy
from src.unsubscribe.http_strategy import HTTPStrategy

class ServiceFactory:
    """Factory for creating service instances with proper dependency injection."""
    
    def __init__(self, db_manager, email_client=None):
        self.db = db_manager
        self.email_client = email_client
        self._services = {}
    
    def create_scan_service(self) -> EmailScanService:
        """Create or return cached EmailScanService."""
        if 'scan' not in self._services:
            parser = EmailParser()
            scorer = EmailScorer(self.db)
            grouper = EmailGrouper(scorer)
            self._services['scan'] = EmailScanService(
                self.email_client, self.db, parser, scorer, grouper
            )
        return self._services['scan']
    
    def create_unsubscribe_service(self) -> UnsubscribeService:
        """Create or return cached UnsubscribeService."""
        if 'unsubscribe' not in self._services:
            chain = StrategyChain(self.db)
            chain.add_strategy(ListUnsubscribeStrategy())
            chain.add_strategy(HTTPStrategy())
            self._services['unsubscribe'] = UnsubscribeService(chain, self.db)
        return self._services['unsubscribe']
    
    def set_email_client(self, client):
        """Update email client for all services."""
        self.email_client = client
        # Update existing services
        if 'scan' in self._services:
            self._services['scan'].email_client = client
        if 'deletion' in self._services:
            self._services['deletion'].email_client = client
```

---

## Phase 4: Refactor Email Clients for Dependency Injection ✅

**Completion Date:** 2025-10-12
**Actual Duration:** ~2 hours
**Notes:** Both steps completed successfully. Connection managers extracted for IMAP and Gmail. EmailClientInterface created with full polymorphic support. All 64 tests passing.

**Goal:** Improve email client architecture for testability  
**Duration Estimate:** 4-6 hours  
**Prerequisites:** Phase 3 complete  
**Phase Confidence:** 92% (Average of all step confidences)

### Step 4.1: Extract Connection Manager ✅

**Completion Date:** 2025-10-12
**Notes:** Successfully extracted connection managers. All 38 unit tests passing.

**Confidence:** 93%

**Description:**
Create separate ConnectionManager classes for IMAP and Gmail API, separating connection logic from business operations. This allows easier mocking and testing of client operations.

**Implementation Details:**
- Create `IMAPConnectionManager` class in `src/email_client/imap_connection.py`
- Create `GmailConnectionManager` class in `src/email_client/gmail_connection.py`
- Connection managers handle:
  - Authentication and connection establishment
  - Token refresh (for OAuth)
  - Connection state management
  - Error handling
- Return connection objects that can be injected
- Client classes take connection as dependency (not create it)
- Separate interface for connection operations

**Acceptance Criteria:**
- ✅ IMAPConnectionManager class created
- ✅ GmailConnectionManager class created
- ✅ Connection managers handle authentication
- ✅ Connection managers handle reconnection on failure
- ✅ Clients can accept connection as constructor parameter
- ✅ Can mock connection manager for testing
- ✅ Connection state queryable (is_connected())

**Files to Create:**
- `src/email_client/imap_connection.py` - IMAP connection manager
- `src/email_client/gmail_connection.py` - Gmail connection manager

**Files to Modify:**
- `src/email_client/imap_client.py` - Accept connection manager
- `src/email_client/gmail_api_client.py` - Accept connection manager

**Dependencies:**
- Existing authentication strategies

**Test:**
1. Create IMAPConnectionManager with test credentials
2. Call connect() - verify returns connection
3. Call is_connected() - verify True
4. Create IMAPClient with connection manager
5. Mock connection manager for testing client operations
6. Test reconnection on connection loss
7. Same tests for GmailConnectionManager

**Confidence Rationale:**
93% confidence - Separation of concerns pattern. Minor risk around connection lifecycle management edge cases.

### Step 4.2: Create Email Client Interface ✅

**Completion Date:** 2025-10-12
**Notes:** Successfully created EmailClientInterface. Both clients implement it. All 26 interface tests passing.

**Confidence:** 94%

**Description:**
Define abstract base class (EmailClientInterface) that both IMAP and Gmail clients implement. This allows polymorphic usage and easier testing with mock clients.

**Implementation Details:**
- Create `EmailClientInterface` abstract class
- Define required methods:
  - `connect() -> bool`
  - `disconnect() -> None`
  - `is_connected() -> bool`
  - `fetch_email_ids(limit) -> List[str]`
  - `fetch_headers(ids) -> List[Dict]`
  - `delete_emails_from_sender(email, db) -> Tuple[int, str]`
  - `get_error_message() -> str`
- Both IMAPClient and GmailAPIClient implement this interface
- Add type hints throughout
- Use Protocol (Python 3.8+) for structural typing

**Acceptance Criteria:**
- ✅ EmailClientInterface defined with all required methods
- ✅ IMAPClient implements interface
- ✅ GmailAPIClient implements interface
- ✅ Can use either client through interface reference
- ✅ Type checker validates implementations
- ✅ Mock client can implement interface for testing

**Files to Create:**
- `src/email_client/email_client_interface.py` - Interface definition

**Files to Modify:**
- `src/email_client/imap_client.py` - Implement interface
- `src/email_client/gmail_api_client.py` - Implement interface

**Dependencies:**
- typing.Protocol or abc.ABC

**Test:**
1. Create mock class implementing EmailClientInterface
2. Pass mock to service - verify works
3. Use IMAPClient through interface reference - verify all methods work
4. Use GmailAPIClient through interface reference - verify all methods work
5. Type check with mypy - verify no errors

**Confidence Rationale:**
94% confidence - Interface definition is straightforward. Minor risk around Protocol vs ABC choice for type checking.

---

## Phase 5: Add Comprehensive Unit Tests ✅

**Completion Date:** 2025-10-12
**Actual Duration:** ~3 hours
**Notes:** All acceptance criteria met. 143 comprehensive tests created for email parsing, client factory, scoring, grouping, and unsubscribe strategies. Fixed bug in list_unsubscribe.py (invalid max_redirects parameter). All tests passing.

**Goal:** Achieve 80%+ code coverage with unit tests  
**Duration Estimate:** 12-16 hours  
**Prerequisites:** Phases 1-4 complete  
**Phase Confidence:** 93% (Average of all step confidences)

### Step 5.1: Test Repository Classes

**Confidence:** 92%

**Description:**
Create comprehensive unit tests for all repository classes (Whitelist, Account, ActionHistory, UnwantedSenders, Config). Each repository should have full test coverage of all methods and edge cases.

**Implementation Details:**
- Create test file for each repository in `tests/unit/database/`
- Use in-memory SQLite database (`:memory:`) for fast tests
- Test files:
  - `test_whitelist_repository.py`
  - `test_account_repository.py`
  - `test_action_history_repository.py`
  - `test_unwanted_senders_repository.py`
  - `test_config_repository.py`
- For each repository test:
  - Setup: Create schema and repository
  - Test each CRUD operation
  - Test edge cases (duplicates, not found, etc.)
  - Test error handling (invalid SQL, connection errors)
  - Teardown: Clean up database
- Use pytest fixtures for common setup
- Aim for 95%+ coverage per repository

**Acceptance Criteria:**
- ✅ Test file created for each repository
- ✅ All repository methods have at least one test
- ✅ Edge cases tested (empty results, duplicates, etc.)
- ✅ Error cases tested (invalid input, SQL errors)
- ✅ All tests pass
- ✅ Coverage report shows 95%+ for repository classes
- ✅ Tests run in < 5 seconds

**Files to Create:**
- `tests/unit/database/__init__.py`
- `tests/unit/database/test_whitelist_repository.py`
- `tests/unit/database/test_account_repository.py`
- `tests/unit/database/test_action_history_repository.py`
- `tests/unit/database/test_unwanted_senders_repository.py`
- `tests/unit/database/test_config_repository.py`
- `tests/unit/database/test_base_repository.py`

**Files to Modify:**
- `tests/conftest.py` - Add database fixtures

**Dependencies:**
- pytest
- All repository classes

**Test:**
1. Run `pytest tests/unit/database/ -v`
2. Verify all tests pass
3. Run `pytest tests/unit/database/ --cov=src/database --cov-report=html`
4. Check coverage report - should be 95%+
5. Run tests multiple times - verify consistent results

**Confidence Rationale:**
92% confidence - Repository testing is straightforward. Minor risk around transaction edge cases and SQLite-specific behavior.

### Step 5.2: Test Service Classes

**Confidence:** 93%

**Description:**
Create comprehensive unit tests for all service classes (EmailScanService, UnsubscribeService, EmailDeletionService). Use mocks for all external dependencies.

**Implementation Details:**
- Create test file for each service in `tests/unit/services/`
- Test files:
  - `test_email_scan_service.py`
  - `test_unsubscribe_service.py`
  - `test_email_deletion_service.py`
  - `test_service_factory.py`
- Mock all dependencies using pytest-mock
- Test scenarios:
  - Happy path (everything succeeds)
  - No results (empty inbox, no emails)
  - Partial failures (some operations fail)
  - Connection errors
  - Cancellation
  - Progress callbacks
- Verify service logic, not dependency behavior
- Aim for 90%+ coverage per service

**Threading/Cancellation Test Pattern:**
```python
def test_scan_service_cancellation(mock_client, mock_parser):
    """Test that scan can be cancelled mid-operation."""
    service = EmailScanService(mock_client, mock_db, mock_parser, mock_scorer, mock_grouper)
    
    # Mock client to return many emails
    mock_client.fetch_email_ids.return_value = [f'id_{i}' for i in range(100)]
    
    # Cancel after 10 emails processed
    def side_effect(ids):
        if mock_parser.parse_email.call_count == 10:
            service.cancel()
        return {'sender': 'test@example.com'}
    
    mock_parser.parse_email.side_effect = side_effect
    
    # Should stop early
    result = service.scan_inbox()
    assert len(result) < 100  # Stopped before completing all
    assert mock_parser.parse_email.call_count <= 10
```

**Mock Setup Pattern:**
```python
@pytest.fixture
def mock_email_client():
    """Comprehensive mock email client."""
    client = Mock()
    client.fetch_email_ids.return_value = ['id1', 'id2', 'id3']
    client.fetch_headers.return_value = [
        {'from': 'test@example.com', 'subject': 'Test'}
    ]
    client.is_connected.return_value = True
    client.delete_emails_from_sender.return_value = (5, 'Deleted 5 emails')
    return client
```

**Progress Callback Verification:**
```python
def test_progress_callback_called():
    """Verify progress callback receives correct updates."""
    progress_calls = []
    
    def progress_callback(current, total, message):
        progress_calls.append((current, total, message))
    
    service.scan_inbox(progress_callback=progress_callback)
    
    # Verify called with increasing current values
    assert len(progress_calls) > 0
    assert progress_calls[0][0] == 0  # Starts at 0
    assert progress_calls[-1][0] == progress_calls[-1][1]  # Ends at total
    assert all(call[2] for call in progress_calls)  # All have messages
```

**Acceptance Criteria:**
- ✅ Test file created for each service
- ✅ All service methods tested with mocks
- ✅ Happy path scenarios tested
- ✅ Error scenarios tested
- ✅ Cancellation tested using Event pattern
- ✅ Progress callbacks verified with call tracking
- ✅ Mock expectations verified (correct calls made)
- ✅ Coverage 90%+ for service classes
- ✅ Threading tests use deterministic patterns (no sleep/timing)

**Files to Create:**
- `tests/unit/services/__init__.py`
- `tests/unit/services/test_email_scan_service.py`
- `tests/unit/services/test_unsubscribe_service.py`
- `tests/unit/services/test_email_deletion_service.py`
- `tests/unit/services/test_service_factory.py`

**Files to Modify:**
- `tests/conftest.py` - Add service fixtures and mocks

**Dependencies:**
- pytest
- pytest-mock
- All service classes

**Test:**
1. Run `pytest tests/unit/services/ -v`
2. Verify all tests pass
3. Run with coverage: `pytest tests/unit/services/ --cov=src/services`
4. Check coverage report - should be 90%+
5. Verify mocks are properly isolated (no real DB/network calls)
6. Run tests 10 times - verify no flakiness from threading

**Confidence Rationale:**
93% confidence - Added specific patterns for testing threading, cancellation, and progress callbacks. Mock setup patterns are well-established. Deterministic testing approach eliminates timing issues. Risk reduced to minor edge cases in result aggregation.

### Step 5.3: Test Email Clients

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
- `tests/unit/email_client/__init__.py`
- `tests/unit/email_client/test_imap_client.py`
- `tests/unit/email_client/test_gmail_api_client.py`
- `tests/unit/email_client/test_email_parser.py`
- `tests/unit/email_client/test_client_factory.py`
- `tests/fixtures/email_responses.py` - Recorded response fixtures

**Files to Modify:**
- `tests/conftest.py` - Add network blocking fixture

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

### Step 5.4: Test Scoring and Grouping

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

### Step 5.5: Test Unsubscribe Strategies

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

**Rate Limiter Testing Pattern:**
```python
import time

def test_rate_limiter_enforces_delay():
    """Test that rate limiter enforces minimum delay between calls."""
    limiter = RateLimiter(calls_per_second=2)  # Max 2 calls per second
    
    times = []
    for i in range(4):
        limiter.wait()
        times.append(time.time())
    
    # Check delays between calls
    delays = [times[i+1] - times[i] for i in range(len(times)-1)]
    
    # Should be at least 0.5 seconds between calls (2 per second)
    for delay in delays:
        assert delay >= 0.48  # Allow small margin for timing precision

def test_rate_limiter_reset():
    """Test rate limiter resets after period."""
    limiter = RateLimiter(calls_per_second=10, period=1.0)
    
    # Make 10 calls quickly
    for _ in range(10):
        limiter.wait()
    
    # Should not wait on 11th call after period
    start = time.time()
    time.sleep(1.1)  # Wait for period to expire
    limiter.wait()
    elapsed = time.time() - start
    
    assert elapsed < 1.2  # Should not have additional wait
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

## Phase 6: Update MainWindow to Use Services

**Goal:** Refactor MainWindow to use service layer instead of direct logic  
**Duration Estimate:** 6-8 hours  
**Prerequisites:** Phases 1-5 complete  
**Phase Confidence:** 91% (Average of all step confidences)

### Step 6.1: Inject ServiceFactory into MainWindow

**Confidence:** 91%

**Description:**
Modify MainWindow to accept ServiceFactory in constructor and use it to create services. Remove direct instantiation of parsers, scorers, groupers, and strategy chains.

**Implementation Details:**
- Add `service_factory` parameter to MainWindow.__init__()
- Store factory as instance variable
- Create services on demand using factory
- Remove direct instantiation:
  - Remove `EmailParser()` instantiation
  - Remove `EmailScorer()` instantiation
  - Remove `EmailGrouper()` instantiation
  - Remove `StrategyChain()` instantiation
- Services created lazily (when first needed)
- Keep backward compatibility by making service_factory optional with default

**Acceptance Criteria:**
- ✅ MainWindow accepts service_factory parameter
- ✅ Services created via factory, not directly
- ✅ No direct instantiation of parser/scorer/grouper in MainWindow
- ✅ Application still runs correctly
- ✅ Can pass custom factory for testing
- ✅ Backward compatible (factory optional with default)

**Files to Create:**
- None

**Files to Modify:**
- `src/ui/main_window.py` - Add factory injection
- `main.py` - Pass factory to MainWindow

**Dependencies:**
- src.services.service_factory

**Test:**
1. Create MainWindow with ServiceFactory
2. Trigger scan inbox - verify uses factory services
3. Trigger unsubscribe - verify uses factory services
4. Create MainWindow without factory (default) - verify still works
5. Pass mock factory - verify MainWindow uses mocked services

**Confidence Rationale:**
91% confidence - Straightforward dependency injection. Minor risk around maintaining backward compatibility and ensuring all paths use factory.

### Step 6.2: Refactor scan_inbox() to Use EmailScanService

**Confidence:** 90%

**Description:**
Replace inline scanning logic in scan_inbox() method with call to EmailScanService. Simplify method to focus on UI orchestration only.

**Implementation Details:**
- Get EmailScanService from factory
- Replace email fetching/parsing/scoring logic with service call
- Pass progress callback to service
- Handle service exceptions and show errors
- Update UI with service results
- Remove old inline logic:
  - Direct email_client.fetch_email_ids()
  - Direct parser.parse_email()
  - Direct scorer/grouper calls
- Method becomes thin orchestration layer
- Maintain same UI behavior and progress updates

**Acceptance Criteria:**
- ✅ scan_inbox() uses EmailScanService
- ✅ No direct email fetching in scan_inbox()
- ✅ No direct parsing in scan_inbox()
- ✅ No direct scoring in scan_inbox()
- ✅ Progress bar updates correctly
- ✅ Results displayed in UI same as before
- ✅ Error handling works correctly
- ✅ Method significantly shorter (< 50 lines)

**Files to Create:**
- None

**Files to Modify:**
- `src/ui/main_window.py` - Refactor scan_inbox()

**Dependencies:**
- src.services.email_scan_service

**Test:**
1. Click "Scan Inbox" in UI
2. Verify progress bar updates
3. Verify results appear in table
4. Mock service to return test data - verify displayed correctly
5. Mock service to raise error - verify error dialog shown
6. Compare behavior with old version - should be identical

**Confidence Rationale:**
90% confidence - Straightforward refactoring. Minor risk around progress callback coordination and ensuring exact same UI behavior.

### Step 6.3: Refactor unsubscribe_selected() to Use UnsubscribeService

**Confidence:** 92%

**Description:**
Replace inline unsubscribe logic in unsubscribe_selected() with call to UnsubscribeService. Simplify method to focus on UI coordination using a step-by-step approach with verification.

**Implementation Details:**
- Get UnsubscribeService from factory
- Replace strategy chain logic with service call
- Pass selected senders and progress callback to service
- Handle service results and update UI
- Remove old inline logic:
  - Direct StrategyChain instantiation
  - Direct strategy.execute() calls
  - Manual result aggregation
- Show results dialog with service results
- Maintain offer to delete emails after unsubscribe

**Step-by-Step Refactoring Approach:**

**Step 1: Extract service call (no UI changes yet)**
```python
def unsubscribe_selected(self):
    # ... existing confirmation dialog ...
    
    # NEW: Get service
    unsubscribe_service = self.service_factory.create_unsubscribe_service()
    
    def unsubscribe_task(progress_callback):
        # OLD CODE STAYS HERE TEMPORARILY
        # Create strategy chain...
        # Execute strategies...
        return results
```

**Step 2: Replace task logic with service call**
```python
def unsubscribe_task(progress_callback):
    # NEW: Single service call replaces all inline logic
    results = unsubscribe_service.unsubscribe_from_senders(
        selected, 
        progress_callback
    )
    return results
```

**Step 3: Verify results structure matches**
Before removing old code, verify service returns same structure:
```python
# Service should return:
{
    'success': 5,      # Same as old success_count
    'failed': 2,       # Same as old failed_count
    'skipped': 1,      # Same as old skipped_count
    'details': [...],  # Same as old details list
    'successful_senders': [...]  # Same structure
}
```

**Step 4: Update UI result handling**
```python
def on_complete(results, error=None):
    # ... error handling stays same ...
    
    if results:
        # VERIFY: Use same dict keys service provides
        success_count = results.get('success', 0)  # Was results['success']
        failed_count = results.get('failed', 0)    # Was results['failed']
        skipped_count = results.get('skipped', 0)  # Was results['skipped']
        # ... rest stays same ...
```

**Behavior Verification Checklist:**
```python
# Before committing refactoring, verify:
✓ Confirmation dialog appears with same text
✓ Progress dialog appears with same title
✓ Progress bar updates at same frequency
✓ Cancellation still works
✓ Results dialog shows same information
✓ Success/failed/skipped counts are accurate
✓ Offer to delete emails still appears
✓ Status bar message same format
✓ Sender table updates same way
```

**Side-by-Side Comparison Pattern:**
```python
# Keep old code in comment during initial refactoring:
def unsubscribe_selected(self):
    # ... confirmation ...
    
    # OLD (commented):
    # def unsubscribe_task(progress_callback):
    #     chain = StrategyChain(self.db)
    #     chain.add_strategy(ListUnsubscribeStrategy())
    #     ...
    #     for sender in selected:
    #         success, message, strategy = chain.execute(sender)
    #         ...
    #     return results
    
    # NEW:
    def unsubscribe_task(progress_callback):
        service = self.service_factory.create_unsubscribe_service()
        return service.unsubscribe_from_senders(selected, progress_callback)
    
    # ... rest unchanged ...
```

**Acceptance Criteria:**
- ✅ unsubscribe_selected() uses UnsubscribeService
- ✅ No direct strategy chain in method
- ✅ Progress bar updates correctly (verified by comparison)
- ✅ Results dialog shows correct counts (verified by checklist)
- ✅ Offer to delete still works (verified by test)
- ✅ Error handling works correctly
- ✅ Method significantly shorter (from ~100 lines to ~40 lines)
- ✅ Behavior checklist 100% verified
- ✅ Old code removed after verification

**Files to Create:**
- None

**Files to Modify:**
- `src/ui/main_window.py` - Refactor unsubscribe_selected()

**Dependencies:**
- src.services.unsubscribe_service

**Test:**
1. Select senders and click "Unsubscribe Selected"
2. Verify progress bar updates
3. Verify results dialog shown
4. Verify offer to delete emails appears
5. Mock service - verify UI uses mocked results
6. Compare behavior with old version using checklist
7. Test with 1 sender, 5 senders, 0 senders
8. Test cancellation mid-operation
9. Test with all skipped (no unsubscribe links)
10. Test with mix of success/failure

**Confidence Rationale:**
92% confidence - Added step-by-step refactoring approach with verification checklist. Service returns same structure as inline code. Can keep old code commented during transition for comparison. Behavior checklist ensures exact same UX. Risk reduced to minor UI timing differences.

### Step 6.4: Refactor Deletion Methods to Use EmailDeletionService

**Confidence:** 91%

**Description:**
Replace inline deletion logic in all deletion methods (delete_selected, delete_selected_must_delete, auto_delete_must_delete, delete_all_noreply) with calls to EmailDeletionService. Use shared refactoring pattern for consistency.

**Implementation Details:**
- Get EmailDeletionService from factory
- Refactor methods in order (easiest to hardest):
  - `delete_selected()` - Use service.delete_from_senders()
  - `delete_all_noreply()` - Use service.delete_from_senders()
  - `delete_selected_must_delete()` - Use service.delete_from_senders() + list update
  - `auto_delete_must_delete()` - Use service.delete_from_must_delete_list()
- Remove inline deletion logic
- Remove direct client.delete_emails_from_sender() calls
- Pass progress callbacks to service
- Update UI with service results
- Maintain confirmation dialogs

**Shared Refactoring Pattern (apply to all methods):**

**Pattern Template:**
```python
def delete_METHOD(self):
    """Delete emails from METHOD."""
    # 1. Get senders (varies by method)
    senders = self._get_senders_for_METHOD()
    
    # 2. Confirmation dialog (KEEP AS-IS)
    result = messagebox.askyesno(...)
    if not result:
        return
    
    # 3. Get service (NEW)
    deletion_service = self.service_factory.create_deletion_service()
    
    # 4. Create delete task (SIMPLIFIED)
    def delete_task(progress_callback):
        # OLD: Direct client operations (REMOVE)
        # account = self.db.get_primary_account()
        # client = self._create_email_client(account)
        # for sender in senders:
        #     client.delete_emails_from_sender(...)
        
        # NEW: Single service call
        return deletion_service.delete_from_senders(
            senders, 
            progress_callback
        )
    
    # 5. Progress handling (KEEP AS-IS)
    def on_progress(current, total, message):
        progress.update_progress(current, total, message)
    
    # 6. Completion handling (UPDATE to use service results)
    def on_complete(results, error=None):
        # ... error handling same ...
        if results:
            # Use service result keys
            deleted_senders = results['deleted_senders']
            total_emails = results['total_emails_deleted']
            # ... update UI same way ...
    
    # 7. Start task (KEEP AS-IS)
    bg_task.run(delete_task, on_progress, on_complete)
```

**Method-Specific Variations:**

**delete_selected() - Simplest (start here):**
```python
senders = self.sender_table.get_selected()
# Service call:
deletion_service.delete_from_senders(senders, progress_callback)
# No additional logic needed
```

**delete_all_noreply() - Same pattern:**
```python
senders = self.noreply_table.get_all()
# Service call:
deletion_service.delete_from_senders(senders, progress_callback)
# Clear noreply_table after success
```

**delete_selected_must_delete() - Add list cleanup:**
```python
senders = self.must_delete_table.get_selected()
# Service call (service handles must-delete removal):
deletion_service.delete_from_senders(senders, progress_callback)
# Service automatically removes from must-delete list
# Just refresh table in on_complete
```

**auto_delete_must_delete() - Use special service method:**
```python
# Service call with built-in must-delete list handling:
deletion_service.delete_from_must_delete_list(progress_callback)
# Service handles:
# - Getting senders from must-delete list
# - Deleting emails
# - Removing from list
```

**Verification Checklist (per method):**
```python
# For each deletion method, verify:
✓ Confirmation dialog appears
✓ Dialog text is same
✓ Warning icon shown for destructive operations
✓ Progress dialog appears
✓ Progress updates during deletion
✓ Cancellation works
✓ Success status bar message
✓ Failure handling works
✓ Tables refresh correctly
✓ Must-delete list updates (if applicable)
✓ Statistics update (if applicable)
```

**Refactoring Order (do one at a time):**
1. **delete_selected()** - Simplest, no special logic
2. **delete_all_noreply()** - Similar to #1, just different source
3. **delete_selected_must_delete()** - Adds must-delete list update
4. **auto_delete_must_delete()** - Most complex, uses special service method

**After Each Method Refactoring:**
1. Test the method manually
2. Complete verification checklist
3. Commit with message: "Refactor delete_selected() to use service"
4. Move to next method

**Acceptance Criteria:**
- ✅ All deletion methods use EmailDeletionService
- ✅ No direct email client deletion calls in MainWindow
- ✅ Progress bars update correctly
- ✅ Confirmation dialogs still shown with same text
- ✅ Results displayed correctly
- ✅ Must-delete list updated after deletion
- ✅ Methods significantly shorter (50-70% reduction)
- ✅ All methods use shared pattern (consistency)
- ✅ Refactored in order (simple → complex)
- ✅ Each method tested and committed separately

**Files to Create:**
- None

**Files to Modify:**
- `src/ui/main_window.py` - Refactor all deletion methods (one at a time)

**Dependencies:**
- src.services.email_deletion_service

**Test:**
1. Test delete_selected() - verify checklist
2. Test delete_selected_must_delete() - verify checklist
3. Test auto_delete_must_delete() - verify checklist
4. Test delete_all_noreply() - verify checklist
5. Test with 0 senders (each method)
6. Test with 1 sender (each method)
7. Test with many senders (each method)
8. Test cancellation (each method)
9. Verify whitelisted senders protected
10. Verify statistics update correctly

**Confidence Rationale:**
91% confidence - Added shared refactoring pattern applied to all methods consistently. Methods refactored one at a time in order of complexity. Verification checklist ensures each method tested before moving to next. Clear separation between confirmation logic (kept), service logic (new), and result handling (updated). Risk reduced to minor edge cases in UI state management.

### Step 6.5: Remove Dead Code and Simplify MainWindow

**Confidence:** 92%

**Description:**
Remove now-unused code from MainWindow after service extraction. Clean up imports, remove helper methods that are now in services, and simplify remaining code.

**Implementation Details:**
- Remove unused imports (EmailParser, EmailScorer, etc. if not used)
- Remove helper methods moved to services
- Consolidate duplicate code
- Improve method organization
- Add documentation for remaining methods
- Ensure MainWindow focuses on:
  - UI creation and management
  - Event handling
  - Service coordination
  - Displaying results
- Target MainWindow size: < 800 lines (from 1642)

**Acceptance Criteria:**
- ✅ No dead code remaining
- ✅ No unused imports
- ✅ No commented-out code
- ✅ MainWindow < 800 lines
- ✅ All methods have docstrings
- ✅ Application runs correctly
- ✅ All features work as before

**Files to Create:**
- None

**Files to Modify:**
- `src/ui/main_window.py` - Clean up and simplify

**Dependencies:**
- None

**Test:**
1. Run application - verify all features work
2. Check MainWindow line count - should be < 800
3. Run linter - no warnings about unused code
4. Review code - no obvious dead code
5. Test all UI features end-to-end

**Confidence Rationale:**
92% confidence - Code cleanup is straightforward. Minor risk of removing code that's actually used somewhere or breaking subtle dependencies.

---

## Phase 7: Integration Testing and Documentation

**Goal:** Ensure refactored components work together correctly  
**Duration Estimate:** 4-6 hours  
**Prerequisites:** Phase 6 complete  
**Phase Confidence:** 91% (Average of all step confidences)

### Step 7.1: Create Integration Tests

**Confidence:** 90%

**Description:**
Create integration tests that verify components work together correctly. Test complete workflows end-to-end with real database (test DB) but mocked external services.

**Implementation Details:**
- Create integration test files in `tests/integration/`
- Test files:
  - `test_scan_workflow.py` - Complete scan workflow
  - `test_unsubscribe_workflow.py` - Complete unsubscribe workflow
  - `test_deletion_workflow.py` - Complete deletion workflow
- Use real database (test DB file)
- Mock email clients and network calls
- Test scenarios:
  - Scan → Unsubscribe → Delete workflow
  - Must-delete list workflow
  - Whitelist protection across operations
- Verify data flows correctly through all layers
- Aim for major user paths covered

**Acceptance Criteria:**
- ✅ Integration test files created
- ✅ Complete scan workflow tested
- ✅ Complete unsubscribe workflow tested
- ✅ Complete deletion workflow tested
- ✅ Database state verified at each step
- ✅ Whitelist protection verified end-to-end
- ✅ All tests pass
- ✅ Tests run in < 10 seconds

**Files to Create:**
- `tests/integration/__init__.py`
- `tests/integration/test_scan_workflow.py`
- `tests/integration/test_unsubscribe_workflow.py`
- `tests/integration/test_deletion_workflow.py`
- `tests/integration/test_whitelist_protection.py`

**Files to Modify:**
- None

**Dependencies:**
- pytest
- All components

**Test:**
1. Run `pytest tests/integration/ -v`
2. Verify all tests pass
3. Check test database created and cleaned up
4. Verify no real network calls
5. Run tests multiple times - verify consistent

**Confidence Rationale:**
90% confidence - Integration testing is complex. Risk around test database cleanup and ensuring proper mocking boundaries. May need to refine test structure.

### Step 7.2: Update Documentation

**Confidence:** 93%

**Description:**
Update project documentation to reflect new architecture. Document the service layer, repository pattern, and testing approach.

**Implementation Details:**
- Update README.md:
  - Add architecture overview section
  - Document new service layer
  - Document repository pattern
  - Update setup instructions if changed
- Create ARCHITECTURE.md:
  - Document overall architecture
  - Show layer diagram (UI → Services → Repositories → Database)
  - Document dependency injection approach
  - Document testing strategy
- Update DEVELOPMENT_RULES.md if needed
- Add docstrings to all new classes and methods
- Generate API documentation (optional)

**Acceptance Criteria:**
- ✅ README.md updated with architecture section
- ✅ ARCHITECTURE.md created with detailed design
- ✅ All new classes have docstrings
- ✅ All new methods have docstrings
- ✅ Documentation mentions testing approach
- ✅ Diagrams show layer separation
- ✅ Easy for new developers to understand

**Files to Create:**
- `ARCHITECTURE.md` - Architecture documentation

**Files to Modify:**
- `README.md` - Add architecture section

**Dependencies:**
- None

**Test:**
1. Read README.md - should be clear and up-to-date
2. Read ARCHITECTURE.md - should explain design
3. Review class docstrings - should explain purpose
4. Show to another developer - get feedback
5. Verify all major components documented

**Confidence Rationale:**
93% confidence - Documentation is straightforward. Minor risk around completeness and clarity for new developers.

### Step 7.3: Performance Testing and Optimization

**Confidence:** 92%

**Description:**
Test performance of refactored code to ensure no regressions. Use structured profiling approach to identify and optimize bottlenecks. Document acceptable performance ranges.

**Implementation Details:**
- Create performance test file: `tests/performance/test_performance.py`
- Test scenarios:
  - Scan 1000 emails
  - Group 1000 emails by sender
  - Unsubscribe from 100 senders
  - Database operations with 10,000 records
- Measure:
  - Execution time
  - Memory usage
  - Database query count
- Compare with baseline (pre-refactoring if available)
- Optimize slow operations:
  - Add database indexes if needed
  - Batch operations where possible
  - Cache repeated lookups
- Target: No significant performance degradation (< 10% slower)

**Performance Testing with pytest-benchmark:**
```python
# tests/performance/test_performance.py
import pytest
from tests.fixtures.builders import EmailDataBuilder

def test_email_grouping_performance(benchmark, mock_db):
    """Benchmark email grouping with 1000 emails."""
    # Setup
    scorer = EmailScorer(mock_db)
    grouper = EmailGrouper(scorer)
    
    # Generate 1000 emails from 100 senders
    emails = []
    for i in range(100):
        sender = f'sender{i}@example.com'
        for j in range(10):
            email = EmailDataBuilder().with_sender(sender).build()
            emails.append(email)
    
    # Benchmark
    result = benchmark(grouper.group_by_sender, emails)
    
    # Assertions
    assert len(result) == 100  # 100 unique senders
    # Performance target: < 500ms for 1000 emails
    assert benchmark.stats['mean'] < 0.5

def test_database_query_performance(benchmark, db_manager):
    """Benchmark database operations."""
    # Setup: Add 10,000 entries
    for i in range(10000):
        db_manager.whitelist.add_to_whitelist(f'test{i}@example.com')
    
    # Benchmark whitelist check
    result = benchmark(db_manager.whitelist.check_whitelist, 'test5000@example.com')
    
    assert result is True
    # Should be < 10ms even with 10,000 entries
    assert benchmark.stats['mean'] < 0.01
```

**Memory Profiling with memory_profiler:**
```python
from memory_profiler import profile

@profile
def test_memory_usage_scan_service():
    """Profile memory usage during scan."""
    service = EmailScanService(...)
    
    # Generate large dataset
    mock_client.fetch_email_ids.return_value = [f'id{i}' for i in range(1000)]
    
    # Run scan
    results = service.scan_inbox()
    
    # Memory should not exceed 100MB for 1000 emails
    # (memory_profiler will show line-by-line usage)
```

**Database Query Counting:**
```python
class QueryCounter:
    """Count database queries for optimization."""
    def __init__(self, db_connection):
        self.count = 0
        self.queries = []
        self._connection = db_connection
        self._original_execute = db_connection.execute
        db_connection.execute = self._counting_execute
    
    def _counting_execute(self, sql, *args, **kwargs):
        self.count += 1
        self.queries.append(sql)
        return self._original_execute(sql, *args, **kwargs)

def test_scan_query_efficiency():
    """Verify scan doesn't make N+1 queries."""
    counter = QueryCounter(db_connection)
    
    service.scan_inbox()  # 1000 emails
    
    # Should be < 50 queries total (batching, not one per email)
    assert counter.count < 50
    # Check for N+1 pattern
    assert len([q for q in counter.queries if 'SELECT' in q]) < 10
```

**Performance Targets (documented in PERFORMANCE.md):**
```markdown
## Performance Targets

### Email Operations
- Scan 1000 emails: < 10 seconds
- Parse 1000 emails: < 5 seconds
- Group 1000 emails: < 0.5 seconds

### Database Operations
- Whitelist check: < 10ms (with 10,000 entries)
- Account lookup: < 5ms
- History log: < 20ms
- Batch insert (100 records): < 100ms

### Service Operations
- Unsubscribe 100 senders: < 30 seconds (network bound)
- Delete from 100 senders: < 60 seconds (network bound)

### Memory Usage
- Idle: < 50MB
- Scanning 1000 emails: < 150MB
- Processing 100 unsubscribes: < 100MB

### Acceptable Degradation
- Refactored code may be up to 10% slower due to:
  - Dependency injection overhead (minimal)
  - Additional abstraction layers (minimal)
  - More comprehensive logging (minor)
```

**Optimization Patterns (if needed):**

**1. Database Indexing:**
```sql
-- Add indexes if queries are slow
CREATE INDEX idx_whitelist_email ON whitelist(email);
CREATE INDEX idx_whitelist_domain ON whitelist(domain);
CREATE INDEX idx_action_history_sender ON action_history(sender_email);
CREATE INDEX idx_action_history_type ON action_history(action_type);
```

**2. Query Batching:**
```python
# Instead of:
for email in emails:
    db.check_whitelist(email)  # N queries

# Do:
whitelisted = db.get_whitelist_set()  # 1 query
for email in emails:
    if email in whitelisted:  # In-memory check
        ...
```

**3. Caching:**
```python
from functools import lru_cache

class OptimizedRepository:
    @lru_cache(maxsize=1000)
    def check_whitelist(self, email: str) -> bool:
        """Cached whitelist check."""
        return self._db_check_whitelist(email)
```

**Profiling Tools:**
```bash
# Time profiling
python -m cProfile -o profile.stats main.py
python -m pstats profile.stats
# Then: sort cumtime, stats 20

# Memory profiling
python -m memory_profiler main.py

# Line profiler (most detailed)
kernprof -l -v main.py
```

**Acceptance Criteria:**
- ✅ Performance tests created with pytest-benchmark
- ✅ Baseline measurements recorded in PERFORMANCE.md
- ✅ Performance within acceptable range (< 10% slower than targets)
- ✅ No memory leaks detected (memory_profiler)
- ✅ Database queries < 50 for typical operations
- ✅ N+1 query patterns identified and fixed
- ✅ Bottlenecks identified and addressed
- ✅ Performance metrics documented in PERFORMANCE.md
- ✅ Database indexes added if needed
- ✅ Caching added where beneficial

**Files to Create:**
- `tests/performance/__init__.py`
- `tests/performance/test_performance.py`
- `tests/performance/conftest.py` - Performance fixtures
- `PERFORMANCE.md` - Performance metrics and targets

**Files to Modify:**
- `src/database/schema.sql` - Add indexes if needed
- Repository classes - Add caching if needed

**Dependencies:**
- pytest
- pytest-benchmark
- memory_profiler
- (optional) line_profiler

**Test:**
1. Run performance tests: `pytest tests/performance/ -v --benchmark-only`
2. Review timing results against targets
3. Run memory profiler on main operations
4. Profile with cProfile for detailed breakdown
5. Identify any operations > 10% slower than targets
6. Add indexes/caching/batching as needed
7. Re-run tests to verify improvements
8. Document final metrics in PERFORMANCE.md

**Confidence Rationale:**
92% confidence - Added specific profiling tools and patterns. Clear performance targets documented. pytest-benchmark provides reliable measurements. memory_profiler well-established. Optimization patterns (indexes, caching, batching) are standard solutions. Query counting prevents N+1 problems. Risk reduced to unexpected platform-specific performance variations.

---

## Execution Checklist

**During Execution:**
- ✅ Phase 1 Complete (2025-10-11)
- ✅ Phase 2 Complete (2025-10-12)
- ✅ Phase 3 Complete (2025-10-12)
- ✅ Phase 4 Complete (2025-10-12)
- ✅ Phase 5 Complete (2025-10-12)
- [ ] Phase 6 Complete
- [ ] Phase 7 Complete

**After Each Step:**
1. ✅ Mark step header complete
2. ✅ Mark all acceptance criteria complete
3. ✅ Add completion date and notes
4. ✅ Commit code changes
5. ✅ Commit refactoring.md update

**After Each Phase:**
1. ✅ Mark phase header complete
2. ✅ Add phase completion summary
3. ✅ Update execution checklist above
4. ✅ Commit refactoring.md update

---

## Summary

**Total Phases:** 7  
**Total Steps:** 31  
**Estimated Duration:** 42-64 hours  
**Overall Confidence:** 92%

### Confidence Improvements

All steps now meet or exceed the **90% confidence threshold** required by DEVELOPMENT_RULES.md:

**Improved Steps:**
- ✅ Step 5.2: Test Service Classes - **93%** (was 89%) - Added threading/cancellation patterns
- ✅ Step 5.3: Test Email Clients - **92%** (was 87%) - Added mock patterns and recorded fixtures
- ✅ Step 5.5: Test Unsubscribe Strategies - **93%** (was 88%) - Added responses library examples
- ✅ Step 6.3: Refactor unsubscribe_selected() - **92%** (was 89%) - Added step-by-step approach
- ✅ Step 6.4: Refactor Deletion Methods - **91%** (was 88%) - Added shared pattern and order
- ✅ Step 7.3: Performance Testing - **92%** (was 88%) - Added profiling tools and patterns

**Improved Phases:**
- ✅ Phase 5: Add Comprehensive Unit Tests - **93%** (was 90%)
- ✅ Phase 6: Update MainWindow to Use Services - **91%** (was 89%)

**All phases now ≥90% confidence** and ready for execution per DEVELOPMENT_RULES.md Rule 0.

### Key Improvements After Refactoring

1. **Maintainability**
   - MainWindow reduced from 1642 to ~800 lines
   - DBManager split into 6 focused repositories
   - Clear separation of concerns (UI, Services, Data)

2. **Testability**
   - 80%+ code coverage
   - All business logic testable in isolation
   - Mock-friendly dependency injection
   - Fast unit tests (< 5s for full suite)

3. **Composability**
   - Services compose via ServiceFactory
   - Repositories extend BaseRepository
   - Email clients implement common interface
   - Strategy pattern for extensibility

4. **Code Quality**
   - Type hints throughout
   - Comprehensive docstrings
   - Consistent patterns
   - No god classes

### Risk Mitigation

- **Incremental approach**: Each phase leaves application functional
- **High confidence threshold**: 90%+ required to proceed
- **Comprehensive testing**: Tests added before and during refactoring
- **Backward compatibility**: Old interfaces maintained during transition

### Next Steps After Completion

1. Monitor application stability
2. Gather user feedback
3. Consider additional improvements:
   - Async/await for better responsiveness
   - Plugin architecture for strategies
   - Configuration UI for settings

