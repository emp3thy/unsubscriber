# Email Unsubscriber - Build Plan

## Development Rules

**📋 See DEVELOPMENT_RULES.md for complete development rules**

This build plan follows the general development rules defined in `DEVELOPMENT_RULES.md`. Those rules cover:
- Step progression and completion criteria
- Testing requirements
- Code quality standards
- Git workflow
- Phase execution process
- Stopping conditions

**Quick Reference:**
- ✅ Complete steps in order, don't skip
- ✅ Test each step before marking complete
- ✅ Commit after each step
- ✅ Copy phase + rules to CURRENT_PHASE.md when starting
- ⛔ Stop if linter errors, import failures, or unhandled exceptions
- ✅ Update BUILD_PLAN.md only after phase completion

---

## Confidence Scoring Summary

**Phase Confidence Scores:**
- Phase 1: 96% ✅ CAN EXECUTE
- Phase 2: 92% ✅ CAN EXECUTE  
- Phase 3: 94% ✅ CAN EXECUTE
- Phase 4: 93% ✅ CAN EXECUTE
- Phase 5: 93% ✅ CAN EXECUTE
- Phase 6: 92% ✅ CAN EXECUTE
- Phase 7: 93% ✅ CAN EXECUTE
- Phase 8: 93% ✅ CAN EXECUTE (revised - browser automation deferred to post-MVP)
- Phase 9: 92% ✅ CAN EXECUTE

**Validation:** All phases meet ≥90% confidence threshold per DEVELOPMENT_RULES.md

**Key Revisions from Original Plan:**
- Phase 8: Deferred complex browser automation (Steps 8.1, 8.2) to post-MVP
- Added threading infrastructure to Phase 4 for reuse in later phases
- Enhanced implementation details for all steps per DEVELOPMENT_RULES.md template
- All low-confidence steps improved with detailed implementation guidance

---

## Project Structure

```
unsubscriber/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── BUILD_PLAN.md                    # This file
├── CURRENT_PHASE.md                 # Active phase being worked on
├── emailunsubscriber.md             # Design specification
├── DEPENDENCIES.md                  # Dependency documentation
│
├── src/                             # Source code
│   ├── __init__.py
│   ├── database/                    # Database layer
│   │   ├── __init__.py
│   │   ├── db_manager.py           # Database connection and operations
│   │   └── schema.sql              # Database schema
│   │
│   ├── email_client/                # Email access layer
│   │   ├── __init__.py
│   │   ├── imap_client.py          # IMAP connection and email fetching
│   │   ├── email_parser.py         # Parse email content
│   │   └── credentials.py          # Credential encryption/storage
│   │
│   ├── scoring/                     # Email scoring system
│   │   ├── __init__.py
│   │   ├── scorer.py               # Scoring algorithm
│   │   └── email_grouper.py        # Group emails by sender
│   │
│   ├── unsubscribe/                 # Unsubscribe strategies
│   │   ├── __init__.py
│   │   ├── strategy_base.py        # Base strategy class
│   │   ├── strategy_chain.py       # Strategy coordinator
│   │   ├── list_unsubscribe.py     # Strategy 1: RFC 2369 headers
│   │   ├── http_strategy.py        # Strategy 2: Direct HTTP
│   │   ├── browser_click.py        # Strategy 3: Browser automation
│   │   ├── browser_form.py         # Strategy 4: Form filling
│   │   └── mailto_strategy.py      # Strategy 5: Email-based
│   │
│   ├── ui/                          # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py          # Main application window
│   │   ├── sender_table.py         # Sender list table widget
│   │   ├── progress_dialog.py      # Progress bar dialog
│   │   ├── settings_dialog.py      # Settings/preferences
│   │   └── dialogs.py              # Confirmation dialogs
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── logger.py               # Logging setup
│       ├── config.py               # Configuration management
│       └── threading_utils.py      # Threading helpers
│
├── data/                            # Runtime data (created automatically)
│   ├── emailunsubscriber.db        # SQLite database
│   ├── key.key                     # Encryption key
│   └── logs/                       # Log files
│       └── app.log
│
└── tests/                           # Unit tests (future)
    └── __init__.py
```

---

## Phase 1: Foundation & Database

**Goal:** Set up project structure, database, and basic infrastructure

**Duration Estimate:** 2-3 hours

**Prerequisites:** None (starting from scratch)

**Phase Confidence:** 96% ✅

### Step 1.1: Project Setup

**Confidence:** 98%

**Description:**
Create the complete project directory structure, initialize version control, and set up dependency management. This establishes the foundation for all subsequent development work. The structure follows Python best practices with separation between source code, data, and tests.

**Implementation Details:**
- Create directory structure matching the project layout (see Project Structure section)
- Initialize git repository with `git init`
- Create `.gitignore` with Python-specific exclusions:
  - `__pycache__/`, `*.py[cod]`, `*.so`, `*.egg-info/`
  - `venv/`, `env/`
  - `data/`, `*.db`, `*.log`, `*.key`
  - `.vscode/`, `.idea/`
  - `dist/`, `build/`, `*.spec`
- Create empty `__init__.py` files in: `src/`, `src/database/`, `src/email_client/`, `src/scoring/`, `src/unsubscribe/`, `src/ui/`, `src/utils/`, `tests/`
- Create `requirements.txt` with MVP dependencies (see below)
- No code logic required, purely structural setup

**Acceptance Criteria:**
- ✅ All directories from Project Structure section exist
- ✅ `requirements.txt` file exists with MVP dependencies only
- ✅ Git repository initialized (`.git/` folder exists)
- ✅ `.gitignore` file created with proper exclusions
- ✅ All `__init__.py` files created in src/ subdirectories
- ✅ Running `git status` shows tracked files correctly

**Files to Create:**
- `.gitignore` - Git exclusion rules
- `requirements.txt` - Python dependencies (MVP only)
- `src/__init__.py`, `src/database/__init__.py`, `src/email_client/__init__.py`, `src/scoring/__init__.py`, `src/unsubscribe/__init__.py`, `src/ui/__init__.py`, `src/utils/__init__.py`, `tests/__init__.py`

**Dependencies:**

Create `requirements.txt` with the following content:
```
# Email Unsubscriber - MVP Dependencies
# Python 3.8+ required

# Security - Password encryption (Phase 2.1)
cryptography>=41.0.0

# HTML Parsing - Extract unsubscribe links from email body (Phase 2.4, 3.5)
beautifulsoup4>=4.12.0
lxml>=5.0.0

# HTTP Requests - Unsubscribe via HTTP GET/POST (Phase 5.3, 8.2)
requests>=2.31.0

# Note: selenium/webdriver-manager deferred to post-MVP (see Phase 8 notes)
# Note: All other dependencies are Python built-ins (imaplib, tkinter, sqlite3, etc.)
```

**Test:**
1. Run `ls -R` (or `dir /s` on Windows) and verify all directories exist
2. Run `git status` and verify repository initialized
3. Verify `.gitignore` excludes `__pycache__` by creating a test `.pyc` file
4. Run `pip install -r requirements.txt` and verify dependencies install
5. Verify 4 packages installed: cryptography, beautifulsoup4, lxml, requests

**Confidence Rationale:**
98% confidence - Purely structural work with no complex logic. Git and file system operations are well-understood. Only minor risk is typos in directory names or file paths.

---

### Step 1.2: Database Schema Implementation

**Confidence:** 95%

**Description:**
Create the SQLite database schema with all required tables, indexes, and constraints. This schema supports the core functionality: whitelisting, unwanted sender tracking, action logging, configuration storage, and multi-account management. The schema must be optimized for common query patterns.

**Implementation Details:**
- Create `schema.sql` file with 5 tables:
  1. **whitelist** (id, email TEXT NULL, domain TEXT NULL, notes TEXT, added_date)
  2. **unwanted_senders** (id, email TEXT UNIQUE, reason TEXT, failed_unsubscribe BOOLEAN, added_date)
  3. **action_history** (id, sender_email, action_type TEXT, timestamp, success BOOLEAN, details TEXT)
  4. **config** (key TEXT PRIMARY KEY, value TEXT)
  5. **accounts** (id, email TEXT UNIQUE, encrypted_password TEXT, provider TEXT, added_date)
- Add indexes for performance:
  - `CREATE INDEX idx_whitelist_email ON whitelist(email);`
  - `CREATE INDEX idx_whitelist_domain ON whitelist(domain);`
  - `CREATE INDEX idx_unwanted_email ON unwanted_senders(email);`
  - `CREATE INDEX idx_action_history_sender ON action_history(sender_email);`
  - `CREATE INDEX idx_action_history_timestamp ON action_history(timestamp);`
- Use appropriate SQLite types and constraints
- Add CHECK constraints where appropriate (e.g., email format validation)

**Acceptance Criteria:**
- ✅ `schema.sql` file created with all 5 tables
- ✅ All tables have PRIMARY KEY defined
- ✅ UNIQUE constraints on account emails and unwanted sender emails
- ✅ All 5 indexes created for query optimization
- ✅ Schema matches design in emailunsubscriber.md
- ✅ SQL syntax is valid (no syntax errors)

**Files to Create:**
- `src/database/schema.sql` - Complete database schema

**Dependencies:**
- SQLite3 (built-in with Python)
- No external dependencies required

**Test:**
1. Run `sqlite3 test.db < src/database/schema.sql` to create test database
2. Run `.schema` in sqlite3 command line to view created tables
3. Verify all 5 tables exist with correct columns
4. Run `.indices` to verify all indexes created
5. Try inserting test data to verify constraints work
6. Delete test.db after verification

**Confidence Rationale:**
95% confidence - SQL schema creation is straightforward with clear requirements. SQLite syntax is well-documented. Minor risk around optimal index strategy, but the indexes chosen match common query patterns from the design document.

**Example Code:**
```sql
-- Example table structure
CREATE TABLE whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    domain TEXT,
    notes TEXT,
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (email IS NOT NULL OR domain IS NOT NULL)
);

CREATE INDEX idx_whitelist_email ON whitelist(email);
CREATE INDEX idx_whitelist_domain ON whitelist(domain);
```

---

### Step 1.3: Database Manager

**Confidence:** 95%

**Description:**
Create a DBManager class that provides a clean API for all database operations. This class encapsulates SQLite connection management, query execution, and error handling. It uses the context manager pattern for safe resource handling and parameterized queries to prevent SQL injection.

**Implementation Details:**
- Create `DBManager` class with:
  - `__init__(self, db_path: str)` - Store path, don't open connection yet
  - `initialize_db(self, schema_path: str)` - Read and execute schema.sql
  - `get_connection(self)` - Context manager returning connection
  - `add_to_whitelist(self, email: str = None, domain: str = None, notes: str = "")` - INSERT into whitelist
  - `check_whitelist(self, email: str) -> bool` - Check if email or its domain is whitelisted
  - `add_unwanted_sender(self, email: str, reason: str, failed_unsubscribe: bool = False)` - INSERT or IGNORE
  - `check_unwanted(self, email: str) -> bool` - Check if sender in unwanted list
  - `log_action(self, sender_email: str, action_type: str, success: bool, details: str)` - INSERT action history
  - `get_config(self, key: str, default: Any = None) -> Any` - Get config value
  - `set_config(self, key: str, value: Any)` - Set config value (INSERT OR REPLACE)
- Use parameterized queries exclusively (no string formatting)
- Implement try/except blocks for `sqlite3.Error`
- Log all database errors using logger
- Context manager handles commit/rollback automatically

**Acceptance Criteria:**
- ✅ `DBManager` class created with all specified methods
- ✅ Can initialize database from schema.sql file
- ✅ Can open/close database connections safely
- ✅ All methods use parameterized queries (no SQL injection risk)
- ✅ Context manager pattern implemented for connections
- ✅ Proper error handling with try/except for sqlite3.Error
- ✅ All errors logged appropriately
- ✅ Multiple calls work correctly (connection handling is safe)

**Files to Create:**
- `src/database/db_manager.py` - Main database manager class

**Dependencies:**
- `sqlite3` (built-in)
- `contextlib` (built-in)
- `logging` (will use logger from Step 1.4, but can use basic logging for now)
- `typing` (built-in, for type hints)

**Test:**
1. Create DBManager instance: `db = DBManager('test.db')`
2. Initialize database: `db.initialize_db('src/database/schema.sql')`
3. Verify test.db file created
4. Add to whitelist: `db.add_to_whitelist(email='test@example.com', notes='test entry')`
5. Check whitelist: `result = db.check_whitelist('test@example.com')`
6. Verify result is True
7. Check non-whitelisted: `result = db.check_whitelist('other@example.com')`
8. Verify result is False
9. Test domain whitelist: Add `domain='@company.com'`, check `user@company.com` returns True
10. Test log_action: `db.log_action('test@example.com', 'test', True, 'test details')`
11. Verify no exceptions raised
12. Delete test.db after verification

**Confidence Rationale:**
95% confidence - SQLite operations are well-documented with excellent Python support. Context manager pattern is standard. Parameterized queries are straightforward. Minor risk around edge cases in whitelist domain matching logic (LIKE queries with wildcards).

**Example Code:**
```python
import sqlite3
from contextlib import contextmanager
from typing import Any, Optional
import logging

class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def initialize_db(self, schema_path: str):
        """Initialize database from schema file."""
        try:
            with open(schema_path, 'r') as f:
                schema = f.read()
            with self.get_connection() as conn:
                conn.executescript(schema)
            self.logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
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
    
    def check_whitelist(self, email: str) -> bool:
        """Check if email or its domain is whitelisted."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Check exact email match or domain match
                cursor.execute("""
                    SELECT 1 FROM whitelist 
                    WHERE email = ? 
                    OR (domain IS NOT NULL AND ? LIKE '%' || domain)
                    LIMIT 1
                """, (email, email))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            self.logger.error(f"Error checking whitelist: {e}")
            return False
```

---

### Step 1.4: Logging Setup

**Confidence:** 97%

**Description:**
Set up centralized logging configuration for the application. This creates a consistent logging interface that writes to both console (for development) and rotating log files (for troubleshooting). The logger uses Python's built-in logging module with file rotation to prevent disk space issues.

**Implementation Details:**
- Create `setup_logger()` function that configures root logger
- Use `logging.basicConfig()` or explicit `logging.getLogger()` configuration
- Add two handlers:
  1. **StreamHandler** - Output to console with INFO level
  2. **RotatingFileHandler** - Output to `data/logs/app.log` with DEBUG level
- Set log format: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`
- Configure rotation: max 10MB per file, keep 30 backup files (≈30 days)
- Create `data/logs/` directory if it doesn't exist (use `os.makedirs`)
- Return configured logger or set up root logger for import from other modules
- Function should be idempotent (safe to call multiple times)

**Acceptance Criteria:**
- ✅ Logger configured to write to both console and file
- ✅ Log file location: `data/logs/app.log`
- ✅ Log rotation configured (10MB per file, 30 backups)
- ✅ Log format includes timestamp, logger name, level, message
- ✅ Can be imported and used from any module via `import logging; logging.getLogger(__name__)`
- ✅ `data/logs/` directory created automatically if missing
- ✅ Console shows INFO and above, file shows DEBUG and above

**Files to Create:**
- `src/utils/logger.py` - Logging configuration module

**Dependencies:**
- `logging` (built-in)
- `logging.handlers` (built-in, for RotatingFileHandler)
- `os` (built-in, for path operations)

**Test:**
1. Import logger: `from src.utils.logger import setup_logger`
2. Initialize: `setup_logger()`
3. Get logger: `logger = logging.getLogger(__name__)`
4. Log messages: `logger.debug('debug')`, `logger.info('info')`, `logger.warning('warning')`, `logger.error('error')`
5. Verify console shows info, warning, error (not debug)
6. Verify `data/logs/app.log` exists and contains all messages
7. Verify log format matches expected format
8. Test rotation by logging enough data to exceed 10MB (or manually test with smaller size)

**Confidence Rationale:**
97% confidence - Python's logging module is mature and well-documented. RotatingFileHandler is a standard component. Directory creation with os.makedirs is straightforward. Only minor risk is platform-specific path handling (Windows vs Unix), but Python's os module handles this.

**Example Code:**
```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(log_dir: str = 'data/logs', log_file: str = 'app.log', 
                level: int = logging.DEBUG):
    """Configure application-wide logging."""
    
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)
    
    # Define log format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers (idempotent)
    logger.handlers = []
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation (DEBUG and above)
    file_handler = RotatingFileHandler(
        log_path, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=30
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized. Log file: {log_path}")
    
    return logger
```

---

### Step 1.5: Configuration Management

**Confidence:** 95%

**Description:**
Create a Config class that provides a simple API for storing and retrieving application settings. This class wraps the database config table and provides type-safe access with default values. It handles serialization of complex types (lists, dicts) to JSON for storage.

**Implementation Details:**
- Create `Config` class with:
  - `__init__(self, db_manager: DBManager)` - Store reference to database
  - `get(self, key: str, default: Any = None) -> Any` - Retrieve config value, deserialize JSON if needed
  - `set(self, key: str, value: Any)` - Store config value, serialize to JSON if needed
  - `get_bool(self, key: str, default: bool = False) -> bool` - Type-safe boolean getter
  - `get_int(self, key: str, default: int = 0) -> int` - Type-safe integer getter
  - `get_str(self, key: str, default: str = "") -> str` - Type-safe string getter
- Use JSON serialization for complex types (lists, dicts)
- Leverage DBManager's get_config/set_config methods
- Handle type conversion errors gracefully (return default on error)
- Cache values in memory for performance (optional enhancement)

**Acceptance Criteria:**
- ✅ `Config` class created with get/set methods
- ✅ Can read/write to config table via DBManager
- ✅ Handles default values when key doesn't exist
- ✅ Type-safe getter methods (get_bool, get_int, get_str) work correctly
- ✅ Can store and retrieve complex types (lists, dicts) via JSON
- ✅ Handles missing keys gracefully (returns default, no exception)
- ✅ Handles type conversion errors gracefully

**Files to Create:**
- `src/utils/config.py` - Configuration management class

**Dependencies:**
- `json` (built-in, for serialization)
- `typing` (built-in, for type hints)
- `src.database.db_manager.DBManager` (from Step 1.3)

**Test:**
1. Create DBManager and initialize database
2. Create Config instance: `config = Config(db_manager)`
3. Set string value: `config.set('app_name', 'Email Unsubscriber')`
4. Get string value: `name = config.get('app_name')`
5. Verify value matches
6. Set boolean: `config.set('first_run', True)`
7. Get boolean: `first_run = config.get_bool('first_run')`
8. Verify returns True
9. Get non-existent key: `val = config.get('nonexistent', 'default')`
10. Verify returns 'default'
11. Set complex type: `config.set('whitelist_patterns', ['*.edu', '*.gov'])`
12. Get and verify list is retrieved correctly
13. Test type conversion error handling

**Confidence Rationale:**
95% confidence - This is a thin wrapper around DBManager with straightforward logic. JSON serialization is standard. Type conversion with error handling is well-understood. Minor risk around edge cases in type detection (when to JSON serialize vs store as string).

**Example Code:**
```python
import json
from typing import Any
import logging
from src.database.db_manager import DBManager

class Config:
    """Configuration management with database persistence."""
    
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default."""
        try:
            value = self.db.get_config(key)
            if value is None:
                return default
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Not JSON, return as-is
                return value
        except Exception as e:
            self.logger.error(f"Error getting config '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        try:
            # Serialize complex types to JSON
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value)
            elif isinstance(value, bool):
                value = json.dumps(value)
            else:
                value = str(value)
            
            self.db.set_config(key, value)
        except Exception as e:
            self.logger.error(f"Error setting config '{key}': {e}")
            raise
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        try:
            return int(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_str(self, key: str, default: str = "") -> str:
        """Get string configuration value."""
        return str(self.get(key, default))
```

---

**Phase 1 Completion Criteria:**
- All 5 steps complete
- Database can be created and queried
- Logging works
- No linter errors
- Git commits for each step

---

## Phase 2: Email Client & Credentials

**Goal:** Connect to IMAP servers, fetch emails, manage credentials

**Duration Estimate:** 3-4 hours

**Prerequisites:** Phase 1 complete

**Phase Confidence:** 92% ✅

### Step 2.1: Credential Encryption

**Confidence:** 95%

**Description:**
Implement secure credential encryption using Fernet (symmetric encryption) from the cryptography library. This ensures email passwords are never stored in plaintext. The encryption key is stored in a secure location and reused for all encryption/decryption operations.

**Implementation Details:**
- Create `CredentialManager` class with:
  - `__init__(self, key_path: str = 'data/key.key')` - Initialize with key file path
  - `_load_or_create_key(self) -> bytes` - Load existing key or generate new one
  - `encrypt_password(self, password: str) -> str` - Encrypt and return base64 string
  - `decrypt_password(self, encrypted_password: str) -> str` - Decrypt from base64 string
- Use `cryptography.fernet.Fernet` for encryption
- Generate key with `Fernet.generate_key()` if not exists
- Store key in `data/key.key` with appropriate file permissions (600 on Unix)
- Create `data/` directory if it doesn't exist
- Encode passwords to bytes before encryption, decode after decryption
- Handle errors: corrupt key, invalid encrypted data, missing key file

**Acceptance Criteria:**
- ✅ Can generate encryption key using Fernet
- ✅ Can save key to `data/key.key` securely
- ✅ Can encrypt app passwords (returns encrypted string)
- ✅ Can decrypt app passwords (returns original password)
- ✅ Key file created automatically if doesn't exist
- ✅ Encrypted password differs from original (verify encryption works)
- ✅ Multiple encrypt/decrypt cycles work correctly
- ✅ Handles errors gracefully (corrupt data, missing key)

**Files to Create:**
- `src/email_client/credentials.py` - Credential encryption manager

**Dependencies:**
- `cryptography` (already in requirements.txt)
- `os` (built-in, for file operations)
- `logging` (for error logging)

**Test:**
1. Create CredentialManager: `cm = CredentialManager()`
2. Verify `data/key.key` created
3. Encrypt password: `encrypted = cm.encrypt_password('my_secure_password')`
4. Verify encrypted string is not the original password
5. Decrypt password: `decrypted = cm.decrypt_password(encrypted)`
6. Verify `decrypted == 'my_secure_password'`
7. Create second CredentialManager instance with same key path
8. Verify it can decrypt the password (key reuse works)
9. Test with special characters: `!@#$%^&*()[]{}?/\|`
10. Test error handling: pass invalid encrypted data

**Confidence Rationale:**
95% confidence - Fernet is a well-documented, high-level encryption interface from the cryptography library. Key generation and file I/O are straightforward. Minor risk around file permissions on different platforms, but basic file operations are sufficient for MVP.

**Example Code:**
```python
from cryptography.fernet import Fernet
import os
import logging

class CredentialManager:
    """Manages encryption and decryption of email passwords."""
    
    def __init__(self, key_path: str = 'data/key.key'):
        self.key_path = key_path
        self.logger = logging.getLogger(__name__)
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)
    
    def _load_or_create_key(self) -> bytes:
        """Load existing key or generate new one."""
        try:
            # Create data directory if needed
            os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
            
            if os.path.exists(self.key_path):
                # Load existing key
                with open(self.key_path, 'rb') as key_file:
                    key = key_file.read()
                self.logger.info("Encryption key loaded")
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(self.key_path, 'wb') as key_file:
                    key_file.write(key)
                self.logger.info(f"New encryption key generated: {self.key_path}")
            
            return key
        except Exception as e:
            self.logger.error(f"Error with encryption key: {e}")
            raise
    
    def encrypt_password(self, password: str) -> str:
        """Encrypt password and return as base64 string."""
        try:
            encrypted_bytes = self.fernet.encrypt(password.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error encrypting password: {e}")
            raise
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt password from base64 string."""
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_password.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error decrypting password: {e}")
            raise
```

---

### Step 2.2: IMAP Client - Connection

**Confidence:** 92%

**Description:**
Create an IMAP client that can connect to Gmail and Outlook mail servers using SSL/TLS. This class handles authentication using email addresses and app passwords, automatically detects the provider, and maintains a persistent connection for email operations. Proper error handling ensures clear feedback when connections fail.

**Implementation Details:**
- Create `IMAPClient` class with:
  - `__init__(self, email: str, password: str, provider: str = None)` - Store credentials
  - `_detect_provider(self, email: str) -> str` - Auto-detect from email domain
  - `connect(self) -> bool` - Establish IMAP SSL connection
  - `disconnect(self)` - Close connection safely
  - `is_connected(self) -> bool` - Check connection status
- Provider detection logic:
  - If email ends with `@gmail.com` or `@googlemail.com` → `'gmail'`
  - If email ends with `@outlook.com`, `@hotmail.com`, `@live.com` → `'outlook'`
  - Otherwise, raise ValueError or allow manual provider specification
- Server configurations:
  - Gmail: `imap.gmail.com:993` with SSL
  - Outlook: `outlook.office365.com:993` with SSL
- Use `imaplib.IMAP4_SSL` for secure connection
- Authentication with `self.imap.login(email, password)`
- Error handling for:
  - Invalid credentials (imaplib.IMAP4.error)
  - Network/connection errors (socket.error)
  - SSL certificate errors
  - Timeout errors
- Log all connection attempts and results

**Acceptance Criteria:**
- ✅ Can connect to Gmail IMAP (imap.gmail.com:993) with SSL
- ✅ Can connect to Outlook IMAP (outlook.office365.com:993) with SSL
- ✅ Can authenticate with email + app password
- ✅ Auto-detects provider from email address
- ✅ Handles invalid credentials gracefully (returns clear error)
- ✅ Handles network errors gracefully
- ✅ Can check connection status
- ✅ Can disconnect cleanly
- ✅ Logs all connection attempts

**Files to Create:**
- `src/email_client/imap_client.py` - IMAP client class (initial implementation)

**Dependencies:**
- `imaplib` (built-in)
- `socket` (built-in, for error handling)
- `ssl` (built-in, for SSL errors)
- `logging` (for connection logging)

**Test:**
1. Create IMAPClient with Gmail credentials: `client = IMAPClient('user@gmail.com', 'app_password')`
2. Verify provider auto-detected as 'gmail'
3. Connect: `success = client.connect()`
4. Verify success is True
5. Check connection: `assert client.is_connected()`
6. Disconnect: `client.disconnect()`
7. Test with Outlook credentials
8. Verify provider detected as 'outlook'
9. Test with invalid password
10. Verify returns False with clear error message
11. Test with unreachable server (disconnect network)
12. Verify handles network error gracefully

**Confidence Rationale:**
92% confidence - IMAP over SSL is well-documented and standard. Provider detection is simple string matching. imaplib is part of standard library with good documentation. Minor risk around SSL certificate issues on some systems, but these are typically handled by the ssl module.

**Example Code:**
```python
import imaplib
import socket
import logging
from typing import Optional

class IMAPClient:
    """IMAP client for Gmail and Outlook."""
    
    def __init__(self, email: str, password: str, provider: str = None):
        self.email = email
        self.password = password
        self.provider = provider or self._detect_provider(email)
        self.imap = None
        self.logger = logging.getLogger(__name__)
    
    def _detect_provider(self, email: str) -> str:
        """Auto-detect email provider from address."""
        email_lower = email.lower()
        if email_lower.endswith(('@gmail.com', '@googlemail.com')):
            return 'gmail'
        elif email_lower.endswith(('@outlook.com', '@hotmail.com', '@live.com')):
            return 'outlook'
        else:
            raise ValueError(f"Unsupported email provider: {email}")
    
    def connect(self) -> bool:
        """Connect to IMAP server."""
        try:
            # Get server settings
            if self.provider == 'gmail':
                server = 'imap.gmail.com'
            elif self.provider == 'outlook':
                server = 'outlook.office365.com'
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            # Connect with SSL
            self.logger.info(f"Connecting to {server}:993...")
            self.imap = imaplib.IMAP4_SSL(server, 993)
            
            # Authenticate
            self.imap.login(self.email, self.password)
            self.logger.info(f"Successfully connected to {self.provider}")
            return True
            
        except imaplib.IMAP4.error as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
        except socket.error as e:
            self.logger.error(f"Network error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Close IMAP connection."""
        if self.imap:
            try:
                self.imap.logout()
                self.logger.info("Disconnected from IMAP server")
            except:
                pass
            finally:
                self.imap = None
    
    def is_connected(self) -> bool:
        """Check if connected to IMAP server."""
        return self.imap is not None
```

---

### Step 2.3: IMAP Client - Fetch Emails

**Confidence:** 93% (improved from 88%)

**Description:**
Implement email fetching functionality with batching support and progress tracking. This step builds on the IMAP connection to retrieve email metadata and bodies efficiently. Batching prevents memory issues with large mailboxes, and selective fetching avoids downloading attachments.

**Implementation Details:**
Split into two focused sub-methods for clarity:

**Part A: Basic Fetching (Headers Only)**
- Add method `get_email_count(self) -> int`:
  - Use `self.imap.select('INBOX', readonly=True)`
  - Parse response to get email count
  - Handle empty mailbox (return 0)

- Add method `fetch_email_ids(self, batch_size: int = 500) -> List[bytes]`:
  - Use `self.imap.search(None, 'ALL')` to get all message IDs
  - Split into batches of `batch_size`
  - Return list of message IDs as bytes

- Add method `fetch_headers(self, message_ids: List[bytes]) -> List[Dict]`:
  - For each ID in message_ids:
    - Fetch using `self.imap.fetch(msg_id, '(RFC822.HEADER FLAGS)')`
    - Parse headers: From, Subject, Date
    - Check FLAGS for \\Seen (read status)
  - Return list of dicts with: {id, from, subject, date, is_read}
  - Handle malformed headers gracefully (use email.header.decode_header)

**Part B: Body Fetching**
- Add method `fetch_body(self, message_id: bytes) -> Dict`:
  - Fetch using `self.imap.fetch(message_id, '(BODY.PEEK[TEXT])')`
  - Use BODY.PEEK to avoid marking as read
  - Parse response to extract body content
  - Decode content (handle various encodings: utf-8, iso-8859-1, etc.)
  - Return dict with: {id, body_text, body_html}

- Error handling for each method:
  - Catch `imaplib.IMAP4.error`
  - Log error with message ID context
  - Continue processing other emails (don't fail entire batch)

**Acceptance Criteria:**
- ✅ Can select INBOX folder (readonly mode)
- ✅ Can get total email count from mailbox
- ✅ Can fetch message IDs in batches of 500
- ✅ Can fetch email headers (From, Subject, Date) in batch
- ✅ Can fetch email body (text/html) individually
- ✅ Can check read/unread status from FLAGS
- ✅ Uses BODY.PEEK to avoid marking emails as read
- ✅ Does NOT download attachments (only TEXT part)
- ✅ Handles malformed headers gracefully
- ✅ Handles various character encodings
- ✅ Returns consistent data structure

**Files to Modify:**
- `src/email_client/imap_client.py` - Add fetching methods to IMAPClient class

**Dependencies:**
- `imaplib` (built-in)
- `email` (built-in, for header parsing)
- `email.header` (for decode_header)
- `typing` (for type hints)

**Test:**
1. Connect to test IMAP account
2. Get email count: `count = client.get_email_count()`
3. Verify count is reasonable (> 0 for test account)
4. Fetch IDs: `ids = client.fetch_email_ids(batch_size=10)`
5. Verify len(ids) <= 10 or total count
6. Fetch headers: `headers = client.fetch_headers(ids[:5])`
7. Verify each header has: id, from, subject, date, is_read
8. Print sample header to verify format
9. Fetch body: `body = client.fetch_body(ids[0])`
10. Verify body has text or html content
11. Verify emails are still marked as unread (PEEK worked)
12. Test with empty folder
13. Test with folder containing 1000+ emails (verify batching)

**Confidence Rationale:**
93% confidence (improved from 88%) - Breaking into focused sub-methods reduces complexity. IMAP fetch operations are well-documented. BODY.PEEK is standard. Email parsing has edge cases (malformed headers, unusual encodings) but the email module handles most of these. Explicit error handling for each email prevents batch failures.

**Example Code:**
```python
import imaplib
import email
from email.header import decode_header
from typing import List, Dict
import logging

class IMAPClient:
    # ... existing connection code ...
    
    def get_email_count(self) -> int:
        """Get total number of emails in INBOX."""
        try:
            status, messages = self.imap.select('INBOX', readonly=True)
            if status == 'OK':
                count = int(messages[0].decode('utf-8'))
                self.logger.info(f"Found {count} emails in INBOX")
                return count
            return 0
        except Exception as e:
            self.logger.error(f"Error getting email count: {e}")
            return 0
    
    def fetch_email_ids(self, batch_size: int = 500) -> List[bytes]:
        """Fetch all message IDs, limited by batch size."""
        try:
            status, messages = self.imap.search(None, 'ALL')
            if status == 'OK':
                ids = messages[0].split()
                # Return up to batch_size IDs
                return ids[:batch_size] if batch_size else ids
            return []
        except Exception as e:
            self.logger.error(f"Error fetching email IDs: {e}")
            return []
    
    def fetch_headers(self, message_ids: List[bytes]) -> List[Dict]:
        """Fetch headers for a batch of message IDs."""
        headers = []
        for msg_id in message_ids:
            try:
                status, data = self.imap.fetch(msg_id, '(RFC822.HEADER FLAGS)')
                if status != 'OK':
                    continue
                
                # Parse headers
                header_data = data[0][1]
                flags = str(data[1]).decode('utf-8', errors='ignore')
                msg = email.message_from_bytes(header_data)
                
                # Extract and decode headers
                from_header = self._decode_header(msg.get('From', ''))
                subject = self._decode_header(msg.get('Subject', ''))
                date = msg.get('Date', '')
                is_read = '\\Seen' in flags
                
                headers.append({
                    'id': msg_id.decode('utf-8'),
                    'from': from_header,
                    'subject': subject,
                    'date': date,
                    'is_read': is_read
                })
            except Exception as e:
                self.logger.warning(f"Error parsing email {msg_id}: {e}")
                continue
        
        return headers
    
    def _decode_header(self, header: str) -> str:
        """Decode email header handling various encodings."""
        try:
            decoded_parts = decode_header(header)
            return ''.join([
                part.decode(encoding or 'utf-8', errors='ignore') 
                if isinstance(part, bytes) else part
                for part, encoding in decoded_parts
            ])
        except Exception:
            return header
```

---

### Step 2.4: Email Parser

**Confidence:** 90%

**Description:**
Create an email parser that transforms raw email data from IMAP into a consistent, structured format. This parser extracts key metadata (sender, subject, date), decodes headers with various character encodings, and handles both HTML and plain text bodies. Robust error handling ensures the parser never fails completely, even with malformed emails.

**Implementation Details:**
- Create `EmailParser` class with:
  - `parse_email(self, raw_email: bytes) -> Dict` - Main parsing method
  - `_extract_sender(self, msg: email.message.Message) -> str` - Get sender email address
  - `_extract_subject(self, msg: email.message.Message) -> str` - Decode subject
  - `_extract_date(self, msg: email.message.Message) -> str` - Parse date header
  - `_extract_body(self, msg: email.message.Message) -> Dict` - Get text and HTML bodies
  - `_decode_header_value(self, header: str) -> str` - Handle encoded headers
- Use `email.message_from_bytes()` to parse raw email
- Extract sender from 'From' header:
  - Parse format: "Name <email@domain.com>" or "email@domain.com"
  - Use `email.utils.parseaddr()` to extract email address
- Subject decoding:
  - Use `email.header.decode_header()` for encoded subjects
  - Handle multiple encodings (UTF-8, ISO-8859-1, Windows-1252, etc.)
- Body extraction:
  - Walk multipart messages to find text/plain and text/html parts
  - Decode content using specified charset
  - Return both `body_text` and `body_html` if available
  - Handle missing bodies gracefully (return empty string)
- Return structure:
  ```python
  {
      'sender': 'email@example.com',
      'subject': 'Email subject',
      'date': 'Thu, 1 Jan 2024 12:00:00 +0000',
      'body_text': 'Plain text content',
      'body_html': '<html>HTML content</html>'
  }
  ```
- Error handling: catch and log exceptions, return partial data

**Acceptance Criteria:**
- ✅ Can parse raw email bytes into structured data
- ✅ Extracts sender email address correctly
- ✅ Extracts and decodes subject line
- ✅ Extracts date header
- ✅ Extracts plain text body
- ✅ Extracts HTML body
- ✅ Handles missing fields gracefully (returns empty string, not None)
- ✅ Handles multiple character encodings
- ✅ Returns consistent dictionary structure
- ✅ Never crashes on malformed emails (returns partial data)

**Files to Create:**
- `src/email_client/email_parser.py` - Email parsing class

**Dependencies:**
- `email` (built-in)
- `email.header` (built-in, for decode_header)
- `email.utils` (built-in, for parseaddr)
- `logging` (for error logging)
- `typing` (for type hints)

**Test:**
1. Get raw email from IMAP (from Step 2.3)
2. Create parser: `parser = EmailParser()`
3. Parse email: `data = parser.parse_email(raw_email)`
4. Verify `data['sender']` contains email address
5. Verify `data['subject']` is decoded properly
6. Verify `data['date']` is present
7. Verify `data['body_text']` or `data['body_html']` has content
8. Test with email containing non-ASCII characters in subject
9. Test with multipart email (text + HTML)
10. Test with malformed email (missing headers)
11. Verify parser doesn't crash, returns partial data

**Confidence Rationale:**
90% confidence - Python's email module is mature and handles most edge cases. Character encoding and malformed emails are the main risks, but decode with errors='ignore' handles most issues. The structure is straightforward with good library support.

**Example Code:**
```python
import email
from email.header import decode_header
from email.utils import parseaddr
from typing import Dict
import logging

class EmailParser:
    """Parse raw email data into structured format."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_email(self, raw_email: bytes) -> Dict:
        """Parse raw email bytes into structured data."""
        try:
            msg = email.message_from_bytes(raw_email)
            
            return {
                'sender': self._extract_sender(msg),
                'subject': self._extract_subject(msg),
                'date': self._extract_date(msg),
                'body_text': self._extract_body(msg).get('text', ''),
                'body_html': self._extract_body(msg).get('html', '')
            }
        except Exception as e:
            self.logger.error(f"Error parsing email: {e}")
            return {
                'sender': '',
                'subject': '',
                'date': '',
                'body_text': '',
                'body_html': ''
            }
    
    def _extract_sender(self, msg: email.message.Message) -> str:
        """Extract sender email address from From header."""
        from_header = msg.get('From', '')
        name, email_addr = parseaddr(from_header)
        return email_addr
    
    def _extract_subject(self, msg: email.message.Message) -> str:
        """Extract and decode subject line."""
        subject = msg.get('Subject', '')
        return self._decode_header_value(subject)
    
    def _extract_date(self, msg: email.message.Message) -> str:
        """Extract date header."""
        return msg.get('Date', '')
    
    def _extract_body(self, msg: email.message.Message) -> Dict[str, str]:
        """Extract text and HTML body parts."""
        body_text = ''
        body_html = ''
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' and not body_text:
                    body_text = self._decode_payload(part)
                elif content_type == 'text/html' and not body_html:
                    body_html = self._decode_payload(part)
        else:
            content_type = msg.get_content_type()
            if content_type == 'text/plain':
                body_text = self._decode_payload(msg)
            elif content_type == 'text/html':
                body_html = self._decode_payload(msg)
        
        return {'text': body_text, 'html': body_html}
    
    def _decode_payload(self, part: email.message.Message) -> str:
        """Decode email part payload."""
        try:
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or 'utf-8'
                return payload.decode(charset, errors='ignore')
        except Exception as e:
            self.logger.warning(f"Error decoding payload: {e}")
        return ''
    
    def _decode_header_value(self, header: str) -> str:
        """Decode email header handling various encodings."""
        try:
            decoded_parts = decode_header(header)
            result = []
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    result.append(part.decode(encoding or 'utf-8', errors='ignore'))
                else:
                    result.append(part)
            return ''.join(result)
        except Exception as e:
            self.logger.warning(f"Error decoding header: {e}")
            return header
```

---

### Step 2.5: Account Management in Database

**Confidence:** 94%

**Description:**
Extend the DBManager class with methods for managing email accounts in the database. This includes storing encrypted credentials, retrieving accounts for connection, listing all configured accounts, and removing accounts. Integration with CredentialManager ensures passwords are encrypted before storage.

**Implementation Details:**
- Add methods to `DBManager` class:
  - `add_account(self, email: str, encrypted_password: str, provider: str) -> bool`
    - INSERT INTO accounts table
    - Use INSERT OR REPLACE to allow updates
    - Return True on success, False on failure
  - `get_account(self, email: str) -> Optional[Dict]`
    - SELECT * FROM accounts WHERE email = ?
    - Return dict with: {email, encrypted_password, provider, added_date}
    - Return None if account not found
  - `list_accounts(self) -> List[Dict]`
    - SELECT * FROM accounts ORDER BY added_date DESC
    - Return list of account dictionaries
    - Return empty list if no accounts
  - `delete_account(self, email: str) -> bool`
    - DELETE FROM accounts WHERE email = ?
    - Return True if deleted, False if not found
  - `get_primary_account(self) -> Optional[Dict]`
    - Return first account (oldest) as default primary
    - Useful for single-account mode
- Use parameterized queries for all operations
- Log all account operations (without logging passwords)
- Integration notes:
  - Password must be encrypted by CredentialManager before calling add_account
  - Password must be decrypted by CredentialManager after calling get_account
  - This separation maintains security boundaries

**Acceptance Criteria:**
- ✅ Can save account with encrypted password to database
- ✅ Can retrieve account by email address
- ✅ Can list all accounts
- ✅ Can delete account by email
- ✅ Can get primary (first) account
- ✅ Uses accounts table from schema
- ✅ Returns None for non-existent accounts
- ✅ All queries use parameterization (no SQL injection)
- ✅ Logs operations without exposing passwords
- ✅ UPDATE capability (INSERT OR REPLACE)

**Files to Modify:**
- `src/database/db_manager.py` - Add account management methods

**Dependencies:**
- `sqlite3` (already used in DBManager)
- `typing` (for Optional, List, Dict)
- No new dependencies required

**Test:**
1. Initialize DBManager and CredentialManager
2. Encrypt password: `enc_pwd = cred_manager.encrypt_password('test_password')`
3. Add account: `success = db.add_account('test@gmail.com', enc_pwd, 'gmail')`
4. Verify success is True
5. Retrieve account: `account = db.get_account('test@gmail.com')`
6. Verify account is not None
7. Verify account['email'] == 'test@gmail.com'
8. Verify account['provider'] == 'gmail'
9. Decrypt password: `pwd = cred_manager.decrypt_password(account['encrypted_password'])`
10. Verify pwd == 'test_password'
11. List accounts: `accounts = db.list_accounts()`
12. Verify len(accounts) >= 1
13. Delete account: `success = db.delete_account('test@gmail.com')`
14. Verify success is True
15. Try to get deleted account: `account = db.get_account('test@gmail.com')`
16. Verify account is None

**Confidence Rationale:**
94% confidence - This is straightforward CRUD operations building on existing DBManager infrastructure. SQLite operations are well-understood. The main logic is simple INSERT/SELECT/DELETE queries with parameterization. High confidence due to clear requirements and standard patterns.

**Example Code:**
```python
# Add to DBManager class in src/database/db_manager.py

from typing import Optional, List, Dict

class DBManager:
    # ... existing methods ...
    
    def add_account(self, email: str, encrypted_password: str, provider: str) -> bool:
        """Add or update email account in database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO accounts 
                    (email, encrypted_password, provider, added_date)
                    VALUES (?, ?, ?, datetime('now'))
                """, (email, encrypted_password, provider))
                self.logger.info(f"Account added/updated: {email}")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error adding account: {e}")
            return False
    
    def get_account(self, email: str) -> Optional[Dict]:
        """Retrieve account by email address."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT email, encrypted_password, provider, added_date
                    FROM accounts WHERE email = ?
                """, (email,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'email': row[0],
                        'encrypted_password': row[1],
                        'provider': row[2],
                        'added_date': row[3]
                    }
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving account: {e}")
            return None
    
    def list_accounts(self) -> List[Dict]:
        """List all accounts."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT email, encrypted_password, provider, added_date
                    FROM accounts ORDER BY added_date DESC
                """)
                rows = cursor.fetchall()
                
                return [{
                    'email': row[0],
                    'encrypted_password': row[1],
                    'provider': row[2],
                    'added_date': row[3]
                } for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error listing accounts: {e}")
            return []
    
    def delete_account(self, email: str) -> bool:
        """Delete account from database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM accounts WHERE email = ?", (email,))
                deleted = cursor.rowcount > 0
                if deleted:
                    self.logger.info(f"Account deleted: {email}")
                return deleted
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting account: {e}")
            return False
    
    def get_primary_account(self) -> Optional[Dict]:
        """Get primary (first) account."""
        accounts = self.list_accounts()
        return accounts[0] if accounts else None
```

---

**Phase 2 Completion Criteria:**
- All 5 steps complete
- Can connect to Gmail and Hotmail IMAP
- Can fetch and parse emails
- Credentials encrypted and stored
- No linter errors

---

## Phase 3: Scoring & Grouping

**Goal:** Implement email scoring algorithm and sender grouping

**Duration Estimate:** 2-3 hours

**Prerequisites:** Phase 2 complete

**Phase Confidence:** 94% ✅

### Step 3.1: Email Scorer - Basic Scoring

**Confidence:** 95%

**Description:**
Create the foundation of the email scoring system that evaluates individual emails based on simple criteria. This scorer assigns points based on whether an email is unread and whether it contains an unsubscribe link. The score breakdown provides transparency about why each score was assigned, which is crucial for user trust.

**Implementation Details:**
- Create `EmailScorer` class with:
  - `__init__(self)` - Initialize scorer (no dependencies yet)
  - `calculate_score(self, email_data: Dict) -> Tuple[int, Dict]` - Main scoring method
  - `_check_unread(self, email_data: Dict) -> int` - Check if unread (+1)
  - `_check_unsubscribe_link(self, email_data: Dict) -> int` - Check for unsub link (+1)
- Scoring rules:
  - Unread email: +1 point (key: 'unread')
  - Has unsubscribe link: +1 point (key: 'has_unsubscribe')
- Return tuple: (total_score, breakdown_dict)
- Breakdown dict format: `{'unread': 1, 'has_unsubscribe': 1, 'total': 2}`
- Simple conditional logic, no external dependencies yet
- Methods are pure functions for easy testing

**Acceptance Criteria:**
- ✅ Can calculate score for individual email
- ✅ Implements unread scoring (+1 if is_unread is True)
- ✅ Implements unsubscribe link scoring (+1 if unsubscribe_links present)
- ✅ Returns tuple: (score: int, breakdown: Dict)
- ✅ Breakdown dict explains each point clearly
- ✅ Returns 0 score for read email with no unsubscribe link
- ✅ Returns 2 score for unread email with unsubscribe link
- ✅ Handles missing fields gracefully (no KeyError)

**Files to Create:**
- `src/scoring/scorer.py` - Email scoring class

**Dependencies:**
- `typing` (built-in, for type hints)
- No external dependencies

**Test:**
1. Create scorer: `scorer = EmailScorer()`
2. Test unread email with unsub link: `score, breakdown = scorer.calculate_score({'is_unread': True, 'unsubscribe_links': ['http://unsub.com']})`
3. Verify score == 2
4. Verify breakdown has 'unread' and 'has_unsubscribe' keys
5. Test read email without unsub: `score, breakdown = scorer.calculate_score({'is_unread': False, 'unsubscribe_links': []})`
6. Verify score == 0
7. Test unread without unsub: verify score == 1
8. Test with missing fields: `scorer.calculate_score({})`
9. Verify no exceptions raised, score == 0

**Confidence Rationale:**
95% confidence - Pure logic with no external dependencies. Simple conditional scoring is straightforward. Type hints and clear return structure make it easy to test. Only minor risk is ensuring all edge cases handled gracefully.

**Example Code:**
```python
from typing import Dict, Tuple

class EmailScorer:
    """Calculate spam/unwanted email scores."""
    
    def calculate_score(self, email_data: Dict) -> Tuple[int, Dict]:
        """Calculate score for an email."""
        score = 0
        breakdown = {}
        
        # Check if unread
        if email_data.get('is_unread', False):
            score += 1
            breakdown['unread'] = 1
        
        # Check for unsubscribe link
        if email_data.get('unsubscribe_links'):
            score += 1
            breakdown['has_unsubscribe'] = 1
        
        breakdown['total'] = score
        return (score, breakdown)
```

---

### Step 3.2: Email Scorer - Frequency Scoring

**Confidence:** 95%

**Description:**
Enhance the scorer to account for email frequency from the same sender. High-frequency senders are more likely to be unwanted, so each additional email from the same sender adds to the score. This step integrates frequency counting with the basic scoring from Step 3.1.

**Implementation Details:**
- Modify `EmailScorer` class to accept email frequency data:
  - Update `calculate_score(self, email_data: Dict, frequency: int = 1) -> Tuple[int, Dict]`
  - Add frequency parameter with default of 1
- Add frequency scoring method:
  - `_calculate_frequency_score(self, frequency: int) -> int`
  - Formula: max(0, frequency - 1) 
  - First email = 0 points, 2nd email = +1, 3rd = +2, etc.
- Update breakdown dict:
  - Add 'frequency' key with points earned
  - Example: 5 emails from sender = `{'frequency': 4}`
- Integration:
  - Frequency score is calculated independently
  - Added to total score from Step 3.1
  - Caller must pass frequency count from email grouping

**Acceptance Criteria:**
- ✅ Accepts frequency parameter in calculate_score()
- ✅ Calculates frequency bonus: +1 per additional email
- ✅ First email gets 0 frequency points
- ✅ 5 emails from same sender gets +4 points
- ✅ Integrates with basic scoring (unread, unsub link)
- ✅ Breakdown includes 'frequency' key
- ✅ Default frequency of 1 works (backwards compatible)
- ✅ Handles frequency = 0 or negative gracefully

**Files to Modify:**
- `src/scoring/scorer.py` - Add frequency scoring to EmailScorer

**Dependencies:**
- No new dependencies (extends existing class)

**Test:**
1. Create scorer: `scorer = EmailScorer()`
2. Score single email: `score, bd = scorer.calculate_score({'is_unread': True}, frequency=1)`
3. Verify score includes base points only
4. Score with frequency: `score, bd = scorer.calculate_score({'is_unread': True}, frequency=5)`
5. Verify score = 1 (unread) + 4 (frequency) = 5
6. Verify breakdown['frequency'] == 4
7. Test with frequency=0: verify no error, 0 frequency points
8. Test without frequency param: verify defaults to 1 (no bonus)

**Confidence Rationale:**
95% confidence - Simple arithmetic calculation extending existing code. Backwards compatible with default parameter. Clear formula with no edge cases beyond zero/negative handling. Integration is straightforward parameter passing.

**Example Code:**
```python
class EmailScorer:
    def calculate_score(self, email_data: Dict, frequency: int = 1) -> Tuple[int, Dict]:
        """Calculate score for an email including frequency."""
        score = 0
        breakdown = {}
        
        # Basic scoring (from Step 3.1)
        if email_data.get('is_unread', False):
            score += 1
            breakdown['unread'] = 1
        
        if email_data.get('unsubscribe_links'):
            score += 1
            breakdown['has_unsubscribe'] = 1
        
        # Frequency scoring (new)
        freq_score = self._calculate_frequency_score(frequency)
        if freq_score > 0:
            score += freq_score
            breakdown['frequency'] = freq_score
        
        breakdown['total'] = score
        return (score, breakdown)
    
    def _calculate_frequency_score(self, frequency: int) -> int:
        """Calculate score based on email frequency."""
        return max(0, frequency - 1)
```

---

### Step 3.3: Email Scorer - Historical Scoring

**Confidence:** 95%

**Description:**
Integrate database lookups to add historical context to scoring. If a sender was previously marked as unwanted, their future emails receive a significant score boost. This creates a learning effect where the system remembers past user decisions and prioritizes similar senders.

**Implementation Details:**
- Modify `EmailScorer.__init__()` to accept DBManager:
  - `__init__(self, db_manager: DBManager = None)`
  - Store as instance variable
  - If None, historical scoring is skipped (useful for testing)
- Add historical scoring method:
  - `_check_historical_unwanted(self, sender: str) -> int`
  - Query: `self.db.check_unwanted(sender)`
  - If sender in unwanted_senders table: +5 points
  - If database error or not found: 0 points
- Update `calculate_score()` to accept sender parameter:
  - `calculate_score(self, email_data: Dict, frequency: int = 1, sender: str = None) -> Tuple[int, Dict]`
  - If sender provided and db_manager exists, check historical
- Update breakdown dict:
  - Add 'historical_unwanted' key if +5 applied
  - Include sender email for reference

**Acceptance Criteria:**
- ✅ Can initialize with DBManager reference
- ✅ Checks unwanted_senders table when sender provided
- ✅ Adds +5 points if sender previously marked unwanted
- ✅ Adds 0 points if sender not in unwanted list
- ✅ Handles missing sender gracefully (skips check)
- ✅ Handles missing db_manager gracefully (skips check)
- ✅ Handles database errors gracefully (logs, returns 0)
- ✅ Breakdown includes 'historical_unwanted' when applied
- ✅ Integrates with basic and frequency scoring

**Files to Modify:**
- `src/scoring/scorer.py` - Add historical scoring to EmailScorer

**Dependencies:**
- `DBManager` from `src.database.db_manager` (Phase 1)

**Test:**
1. Create DBManager and initialize database
2. Create scorer with DB: `scorer = EmailScorer(db_manager)`
3. Add sender to unwanted: `db_manager.add_unwanted_sender('spam@example.com', 'test', False)`
4. Score email from that sender: `score, bd = scorer.calculate_score({'is_unread': True}, frequency=1, sender='spam@example.com')`
5. Verify score includes +5 historical bonus
6. Verify breakdown['historical_unwanted'] == 5
7. Score from unknown sender: verify no historical bonus
8. Test without db_manager: `scorer = EmailScorer()` - verify no errors
9. Test without sender param: verify no errors

**Confidence Rationale:**
95% confidence - Straightforward database lookup building on existing DBManager from Phase 1. Error handling for missing database or connection issues is standard. The main logic is a simple conditional check with well-defined behavior.

**Example Code:**
```python
from typing import Dict, Tuple, Optional
from src.database.db_manager import DBManager
import logging

class EmailScorer:
    def __init__(self, db_manager: Optional[DBManager] = None):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def calculate_score(self, email_data: Dict, frequency: int = 1, 
                       sender: str = None) -> Tuple[int, Dict]:
        """Calculate score for an email."""
        score = 0
        breakdown = {}
        
        # Basic scoring
        if email_data.get('is_unread', False):
            score += 1
            breakdown['unread'] = 1
        
        if email_data.get('unsubscribe_links'):
            score += 1
            breakdown['has_unsubscribe'] = 1
        
        # Frequency scoring
        freq_score = self._calculate_frequency_score(frequency)
        if freq_score > 0:
            score += freq_score
            breakdown['frequency'] = freq_score
        
        # Historical scoring (new)
        if sender and self.db:
            hist_score = self._check_historical_unwanted(sender)
            if hist_score > 0:
                score += hist_score
                breakdown['historical_unwanted'] = hist_score
        
        breakdown['total'] = score
        return (score, breakdown)
    
    def _check_historical_unwanted(self, sender: str) -> int:
        """Check if sender was previously marked unwanted."""
        try:
            if self.db.check_unwanted(sender):
                return 5
        except Exception as e:
            self.logger.error(f"Error checking historical data: {e}")
        return 0
```

---

### Step 3.4: Email Grouper

**Confidence:** 94%

**Description:**
Create an email grouping system that aggregates emails by sender and calculates summary statistics for each sender. This transforms individual email scores into actionable sender-level data, making it easy for users to identify and act on problematic senders. The grouper integrates with the Email Scorer to provide comprehensive sender profiles.

**Implementation Details:**
- Create `EmailGrouper` class with:
  - `__init__(self, scorer: EmailScorer)`
  - `group_by_sender(self, emails: List[Dict]) -> List[Dict]` - Main grouping method
  - `_aggregate_sender_data(self, sender: str, emails: List[Dict]) -> Dict` - Calculate stats
  - `_sort_by_score(self, senders: List[Dict]) -> List[Dict]` - Sort descending
- Use `collections.defaultdict(list)` to group emails by sender
- For each sender, calculate:
  - `sender`: sender email address
  - `total_count`: len(emails from sender)
  - `unread_count`: count of unread emails
  - `average_score`: mean score across all emails
  - `total_score`: sum of all email scores (for sorting)
  - `has_unsubscribe`: True if any email has unsubscribe link
  - `sample_links`: List of up to 3 unsubscribe URLs
  - `last_email_date`: Most recent email date
- Scoring integration:
  - Call `scorer.calculate_score()` for each email
  - Pass frequency count for accurate scoring
  - Aggregate scores per sender
- Sort by `total_score` descending (highest priority senders first)
- Return list of sender dictionaries

**Acceptance Criteria:**
- ✅ Groups emails by sender email address
- ✅ Calculates total email count per sender
- ✅ Calculates unread count per sender
- ✅ Calculates average score per sender
- ✅ Calculates total score per sender (for sorting)
- ✅ Detects if sender has any unsubscribe links
- ✅ Extracts sample unsubscribe links (up to 3)
- ✅ Returns sorted list (descending by total_score)
- ✅ Handles empty email list gracefully
- ✅ Integrates with EmailScorer for scoring

**Files to Create:**
- `src/scoring/email_grouper.py` - Email grouping class

**Dependencies:**
- `collections.defaultdict` (built-in)
- `EmailScorer` from `src.scoring.scorer` (Step 3.3)
- `typing` (built-in)

**Test:**
1. Create scorer and grouper
2. Create test emails from 3 senders (10 emails total)
3. Group: `senders = grouper.group_by_sender(emails)`
4. Verify len(senders) == 3
5. Find sender with most emails: verify total_count correct
6. Verify unread_count matches test data
7. Verify average_score calculated correctly
8. Verify senders sorted by total_score (descending)
9. Verify sample_links present for senders with unsub links
10. Test with empty list: verify returns []

**Confidence Rationale:**
94% confidence - Standard grouping and aggregation logic using built-in data structures. Integration with EmailScorer is straightforward. Main risk is ensuring all statistics calculated correctly, but comprehensive testing will catch issues. Sorting and filtering are standard Python operations.

**Example Code:**
```python
from collections import defaultdict
from typing import List, Dict
from src.scoring.scorer import EmailScorer

class EmailGrouper:
    """Group and aggregate emails by sender."""
    
    def __init__(self, scorer: EmailScorer):
        self.scorer = scorer
    
    def group_by_sender(self, emails: List[Dict]) -> List[Dict]:
        """Group emails by sender and calculate aggregate stats."""
        # Group emails
        groups = defaultdict(list)
        for email in emails:
            sender = email.get('sender', 'unknown@example.com')
            groups[sender].append(email)
        
        # Aggregate stats for each sender
        senders = []
        for sender, sender_emails in groups.items():
            sender_data = self._aggregate_sender_data(sender, sender_emails)
            senders.append(sender_data)
        
        # Sort by total score descending
        return sorted(senders, key=lambda x: x['total_score'], reverse=True)
    
    def _aggregate_sender_data(self, sender: str, emails: List[Dict]) -> Dict:
        """Calculate aggregate statistics for a sender."""
        frequency = len(emails)
        unread_count = sum(1 for e in emails if e.get('is_unread', False))
        
        # Calculate scores
        scores = []
        for email in emails:
            score, _ = self.scorer.calculate_score(
                email, 
                frequency=frequency, 
                sender=sender
            )
            scores.append(score)
        
        # Collect unsubscribe links
        all_links = []
        for email in emails:
            links = email.get('unsubscribe_links', [])
            all_links.extend(links)
        sample_links = list(set(all_links))[:3]  # Unique, up to 3
        
        return {
            'sender': sender,
            'total_count': frequency,
            'unread_count': unread_count,
            'average_score': sum(scores) / len(scores) if scores else 0,
            'total_score': sum(scores),
            'has_unsubscribe': len(all_links) > 0,
            'sample_links': sample_links,
            'last_email_date': emails[-1].get('date', '') if emails else ''
        }
```

---

### Step 3.5: Unsubscribe Link Detection

**Confidence:** 92% (improved from 89%)

**Description:**
Enhance the EmailParser to detect unsubscribe links using multiple strategies. This step implements comprehensive link detection that handles RFC 2369 List-Unsubscribe headers, HTML body parsing, and plain text regex matching. The multi-strategy approach maximizes the chance of finding unsubscribe links across varied email formats.

**Implementation Details:**
- Add to `EmailParser` class:
  - `detect_unsubscribe_links(self, email_data: Dict) -> List[str]` - Main detection method
  - `_extract_from_header(self, email_data: Dict) -> List[str]` - Strategy 1
  - `_extract_from_html(self, html: str) -> List[str]` - Strategy 2  
  - `_extract_from_text(self, text: str) -> List[str]` - Strategy 3
  - `_clean_url(self, url: str) -> str` - Remove tracking parameters

**Strategy 1: List-Unsubscribe Header (RFC 2369)**
- Check for `list_unsubscribe` header in email_data
- Parse URLs from header: `<http://example.com/unsub>` format
- Handle both HTTP and mailto: links
- Regex: `r'<(.*?)>'` to extract URLs

**Strategy 2: HTML Body Parsing**
- Use BeautifulSoup to parse HTML
- Find all `<a>` tags with href attribute
- Check href and link text for keywords (case-insensitive):
  - "unsubscribe", "opt-out", "opt out", "remove", "stop receiving", "cancel subscription"
- Extract href URL if match found
- Handle relative URLs (prepend domain if needed)

**Strategy 3: Plain Text Regex**
- Apply regex patterns to plain text body
- **URL pattern:** `r'https?://[^\s<>"]+(?:unsubscribe|opt-out|optout|remove|stop)[^\s<>"]*'`
- **mailto pattern:** `r'mailto:[^\s<>"]+(?:unsubscribe|opt-out|remove)[^\s<>"]*'`
- Case-insensitive matching (re.IGNORECASE)

**Integration and Cleanup:**
- Combine results from all 3 strategies
- Remove duplicates (convert to set, back to list)
- Clean URLs: remove common tracking parameters (?utm_*, ?ref=, etc.)
- Return up to 5 unique links
- Log how many links found and which strategies succeeded

**Acceptance Criteria:**
- ✅ Detects links from List-Unsubscribe header
- ✅ Parses HTML with BeautifulSoup to find unsubscribe links
- ✅ Finds links with keywords in href URL
- ✅ Finds links with keywords in anchor text
- ✅ Uses regex to find links in plain text
- ✅ Handles mailto: links
- ✅ Returns list of unique URLs
- ✅ Removes duplicate links
- ✅ Handles missing headers/body gracefully
- ✅ Case-insensitive keyword matching
- ✅ Returns empty list if no links found

**Files to Modify:**
- `src/email_client/email_parser.py` - Add unsubscribe detection methods

**Dependencies:**
- `beautifulsoup4` (already in requirements.txt)
- `re` (built-in, for regex)
- `urllib.parse` (built-in, for URL parsing)

**Test:**
1. Test with email containing List-Unsubscribe header
2. Verify header link extracted
3. Test with HTML email with "Unsubscribe" link
4. Verify HTML link extracted
5. Test with plain text email with unsubscribe URL
6. Verify regex finds URL
7. Test with email containing multiple strategies
8. Verify all unique links found
9. Test with mailto: link
10. Verify mailto: extracted
11. Test with no unsubscribe links
12. Verify returns empty list
13. Test case sensitivity: "UNSUBSCRIBE" vs "unsubscribe"
14. Verify both detected

**Confidence Rationale:**
92% confidence (improved from 89%) - Multiple detection strategies reduce risk of missing links. BeautifulSoup and regex are well-documented. Specific patterns documented above eliminate ambiguity. Main risk is unusual email formats, but three-strategy approach provides good coverage. Explicit error handling ensures graceful degradation.

**Example Code:**
```python
import re
from bs4 import BeautifulSoup
from typing import Dict, List
import logging

class EmailParser:
    # ... existing methods ...
    
    def detect_unsubscribe_links(self, email_data: Dict) -> List[str]:
        """Detect unsubscribe links using multiple strategies."""
        links = []
        
        # Strategy 1: List-Unsubscribe header
        links.extend(self._extract_from_header(email_data))
        
        # Strategy 2: HTML body
        if email_data.get('body_html'):
            links.extend(self._extract_from_html(email_data['body_html']))
        
        # Strategy 3: Plain text regex
        if email_data.get('body_text'):
            links.extend(self._extract_from_text(email_data['body_text']))
        
        # Remove duplicates and return up to 5
        unique_links = list(set(links))
        self.logger.info(f"Found {len(unique_links)} unsubscribe links")
        return unique_links[:5]
    
    def _extract_from_header(self, email_data: Dict) -> List[str]:
        """Extract links from List-Unsubscribe header."""
        links = []
        header = email_data.get('list_unsubscribe', '')
        if header:
            # Extract URLs from <url> format
            found = re.findall(r'<(.*?)>', header)
            links.extend(found)
        return links
    
    def _extract_from_html(self, html: str) -> List[str]:
        """Extract unsubscribe links from HTML body."""
        links = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            keywords = ['unsubscribe', 'opt-out', 'opt out', 'remove', 
                       'stop receiving', 'cancel subscription']
            
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                text = link.get_text().lower()
                
                # Check if keyword in URL or text
                if any(kw in href or kw in text for kw in keywords):
                    links.append(link['href'])
        except Exception as e:
            self.logger.warning(f"Error parsing HTML: {e}")
        return links
    
    def _extract_from_text(self, text: str) -> List[str]:
        """Extract unsubscribe links from plain text using regex."""
        links = []
        
        # HTTP/HTTPS URLs with unsubscribe keywords
        url_pattern = r'https?://[^\s<>"]+(?:unsubscribe|opt-out|optout|remove|stop)[^\s<>"]*'
        links.extend(re.findall(url_pattern, text, re.IGNORECASE))
        
        # mailto: links with unsubscribe keywords
        mailto_pattern = r'mailto:[^\s<>"]+(?:unsubscribe|opt-out|remove)[^\s<>"]*'
        links.extend(re.findall(mailto_pattern, text, re.IGNORECASE))
        
        return links
```

---

**Phase 3 Completion Criteria:**
- All 5 steps complete
- Scoring algorithm works correctly
- Emails grouped by sender
- Unsubscribe links detected
- No linter errors

---

## Phase 4: User Interface - Basic Window

**Goal:** Create Tkinter GUI with basic layout and sender table

**Duration Estimate:** 3-4 hours

**Prerequisites:** Phase 3 complete

**Phase Confidence:** 93% ✅

### Step 4.1: Main Window Structure

**Confidence:** 95%

**Description:**
Create the main application window using Tkinter with a professional layout including menu bar, content area, and status bar. This establishes the UI framework that all other interface components will build upon. The window provides the container for displaying sender data, progress indicators, and user controls.

**Implementation Details:**
- Create `main.py` as application entry point:
  - Import and call logging setup
  - Initialize DBManager
  - Create Tkinter root window
  - Instantiate MainWindow
  - Start main event loop
- Create `MainWindow` class in `src/ui/main_window.py`:
  - Inherit from `tk.Frame` or composition with `tk.Tk`
  - `__init__(self, root, db_manager)` - Initialize with root window and database
  - `_create_menu_bar(self)` - Create File, Settings, Help menus
  - `_create_main_content(self)` - Create central content area
  - `_create_status_bar(self)` - Create bottom status bar
- Window configuration:
  - Default size: 800x600
  - Title: "Email Unsubscriber"
  - Minimum size: 600x400
  - Resizable: True
  - Center on screen
- Menu bar structure:
  - File: Add Account, Exit
  - Settings: Preferences, View Logs
  - Help: About, Generate App Password
- Status bar: Label for showing current operation status
- Main content area: Frame for tabs/tables (populated in later steps)

**Acceptance Criteria:**
- ✅ Main window opens with 800x600 default size
- ✅ Window title displays "Email Unsubscriber"
- ✅ Menu bar present with File, Settings, Help menus
- ✅ Status bar visible at bottom
- ✅ Main content area properly sized and expandable
- ✅ Window is resizable and maintains layout
- ✅ Window centers on screen at startup
- ✅ All menu items present (can be disabled if not implemented yet)
- ✅ Clean shutdown when closed

**Files to Create:**
- `main.py` - Application entry point
- `src/ui/main_window.py` - Main window class

**Dependencies:**
- `tkinter` (built-in)
- `DBManager` from `src.database.db_manager` (Phase 1)
- `setup_logger` from `src.utils.logger` (Phase 1)

**Test:**
1. Run `python main.py`
2. Verify window opens and displays
3. Verify window is 800x600 pixels
4. Verify title bar shows "Email Unsubscriber"
5. Click File menu: verify items present
6. Click Settings menu: verify items present
7. Click Help menu: verify items present
8. Resize window: verify layout adjusts properly
9. Close window: verify clean exit (no errors)

**Confidence Rationale:**
95% confidence - Tkinter window creation is straightforward with extensive documentation. Menu bar and status bar are standard widgets. Layout management with frames is well-understood. Only minor risk is platform-specific appearance differences, but functionality is consistent.

**Example Code:**
```python
# main.py
import tkinter as tk
from src.utils.logger import setup_logger
from src.database.db_manager import DBManager
from src.ui.main_window import MainWindow

def main():
    # Setup logging
    setup_logger()
    
    # Initialize database
    db = DBManager('data/emailunsubscriber.db')
    db.initialize_db('src/database/schema.sql')
    
    # Create main window
    root = tk.Tk()
    app = MainWindow(root, db)
    root.mainloop()

if __name__ == '__main__':
    main()

# src/ui/main_window.py
import tkinter as tk
from tkinter import ttk
import logging

class MainWindow:
    """Main application window."""
    
    def __init__(self, root, db_manager):
        self.root = root
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Configure window
        self.root.title("Email Unsubscriber")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self._center_window()
        
        # Create UI components
        self._create_menu_bar()
        self._create_main_content()
        self._create_status_bar()
    
    def _center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_menu_bar(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Account", command=self._add_account)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences", state=tk.DISABLED)
        settings_menu.add_command(label="View Logs", state=tk.DISABLED)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", state=tk.DISABLED)
        help_menu.add_command(label="Generate App Password", state=tk.DISABLED)
    
    def _create_main_content(self):
        """Create main content area."""
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_status_bar(self):
        """Create status bar at bottom."""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _add_account(self):
        """Show add account dialog (placeholder)."""
        self.logger.info("Add account clicked")
```

---

### Step 4.2: Account Setup Dialog

**Confidence:** 93%

**Description:**
Create a dialog for adding and testing email account credentials. This dialog provides a user-friendly interface for entering email addresses and app passwords, with built-in connection testing to verify credentials before saving. Auto-detection of email providers simplifies the setup process.

**Implementation Details:**
- Create `AccountDialog` class in `src/ui/settings_dialog.py`:
  - `__init__(self, parent, db_manager, cred_manager)` - Initialize dialog
  - `_create_form_fields()` - Email entry, password entry (show/hide toggle), provider label
  - `_test_connection()` - Test IMAP connection before saving
  - `_save_account()` - Encrypt and save to database
  - `_validate_email(email: str) -> bool` - Basic email format validation
- Form fields:
  - Email: Entry widget with validation (basic email format check)
  - App Password: Entry widget with show/hide button
  - Provider: Auto-detected label (Gmail/Outlook) or dropdown for manual selection
- "Test Connection" button: Creates IMAPClient, attempts connection, shows result
- "Save" button: Enabled only after successful test
- Password visibility toggle for user convenience
- Progress indicator while testing connection (cursor change or small spinner)
- Clear error messages for connection failures with suggestions
- Dialog is modal (blocks parent window)

**Acceptance Criteria:**
- ✅ Dialog opens from File menu "Add Account"
- ✅ Has email and app password entry fields
- ✅ Auto-detects provider from email address (@gmail.com = Gmail, etc.)
- ✅ Test Connection button attempts IMAP connection
- ✅ Shows success message if connection works
- ✅ Shows error message with details if connection fails
- ✅ Save button encrypts password and stores in database
- ✅ Dialog closes after successful save
- ✅ Password field has show/hide toggle button
- ✅ Form validation prevents empty submissions
- ✅ Provider detection works for Gmail and Outlook

**Files to Create:**
- `src/ui/settings_dialog.py` - Account setup dialog

**Dependencies:**
- `tkinter`, `tkinter.messagebox` (built-in)
- `IMAPClient` from `src.email_client.imap_client` (Phase 2)
- `CredentialManager` from `src.email_client.credentials` (Phase 2)
- `DBManager` from `src.database.db_manager` (Phase 1)

**Test:**
1. Open dialog from File > Add Account menu
2. Enter Gmail address: test@gmail.com
3. Enter app password
4. Verify provider label shows "Gmail"
5. Click Test Connection
6. Verify connection attempt (may fail if invalid credentials, that's ok)
7. If successful, verify "Save" button enabled
8. Click Save
9. Verify account saved to database
10. Close and reopen app
11. Verify account persists in database
12. Test with invalid email format: verify validation error
13. Test show/hide password toggle

**Confidence Rationale:**
93% confidence - Standard Tkinter dialog with form validation. IMAP connection testing uses existing IMAPClient from Phase 2. Password encryption uses existing CredentialManager. Main risk is handling various connection error scenarios gracefully, but comprehensive error messages mitigate this.

**Example Code:**
```python
import tkinter as tk
from tkinter import ttk, messagebox
import re
from src.email_client.imap_client import IMAPClient
from src.email_client.credentials import CredentialManager
from src.database.db_manager import DBManager

class AccountDialog(tk.Toplevel):
    """Dialog for adding email accounts."""
    
    def __init__(self, parent, db_manager: DBManager, cred_manager: CredentialManager):
        super().__init__(parent)
        self.db = db_manager
        self.cred = cred_manager
        self.connection_tested = False
        
        self.title("Add Email Account")
        self.geometry("400x300")
        self.resizable(False, False)
        
        self._create_form_fields()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
    
    def _create_form_fields(self):
        """Create form fields."""
        # Email
        ttk.Label(self, text="Email Address:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.email_entry = ttk.Entry(self, width=30)
        self.email_entry.grid(row=0, column=1, padx=10, pady=5)
        self.email_entry.bind('<FocusOut>', self._detect_provider)
        
        # Password
        ttk.Label(self, text="App Password:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Show/Hide password
        self.show_password = tk.BooleanVar()
        ttk.Checkbutton(self, text="Show password", variable=self.show_password,
                       command=self._toggle_password).grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Provider
        ttk.Label(self, text="Provider:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.provider_label = ttk.Label(self, text="(auto-detect)")
        self.provider_label.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.test_btn = ttk.Button(button_frame, text="Test Connection", command=self._test_connection)
        self.test_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="Save", command=self._save_account, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def _detect_provider(self, event=None):
        """Auto-detect provider from email."""
        email = self.email_entry.get().lower()
        if '@gmail.com' in email or '@googlemail.com' in email:
            self.provider_label.config(text="Gmail")
        elif '@outlook.com' in email or '@hotmail.com' in email or '@live.com' in email:
            self.provider_label.config(text="Outlook")
        else:
            self.provider_label.config(text="Unknown")
    
    def _toggle_password(self):
        """Toggle password visibility."""
        if self.show_password.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
    
    def _test_connection(self):
        """Test IMAP connection."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
        
        try:
            self.config(cursor="watch")
            self.update()
            
            client = IMAPClient(email, password)
            if client.connect():
                self.connection_tested = True
                self.save_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Success", "Connection successful!")
                client.disconnect()
            else:
                messagebox.showerror("Error", "Connection failed. Check credentials.")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
        finally:
            self.config(cursor="")
    
    def _save_account(self):
        """Save account to database."""
        if not self.connection_tested:
            messagebox.showwarning("Warning", "Please test connection first")
            return
        
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        provider = self.provider_label.cget("text").lower()
        
        # Encrypt password
        encrypted = self.cred.encrypt_password(password)
        
        # Save to database
        if self.db.add_account(email, encrypted, provider):
            messagebox.showinfo("Success", "Account saved successfully")
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save account")
```

---

### Step 4.3: Sender Table Widget

**Confidence:** 92%

**Description:**
Create a sortable table widget to display grouped sender data using Tkinter Treeview. This table is the primary interface for viewing and selecting unwanted senders. Color coding provides visual priority cues, and sorting allows users to organize data by different criteria.

**Implementation Details:**
- Create `SenderTable` class in `src/ui/sender_table.py`:
  - `__init__(self, parent)` - Initialize Treeview widget
  - `populate(self, senders: List[Dict])` - Fill table with data
  - `get_selected() -> List[Dict]` - Return selected sender dictionaries  
  - `clear()` - Remove all items
  - `_setup_columns()` - Define column headers and widths
  - `_sort_by_column(col, reverse)` - Sort table by clicked column
  - `_apply_color_coding(item, score)` - Color rows by score
- Columns with widths:
  - Sender (300px) - Email address
  - Count (80px) - Total email count
  - Unread (80px) - Unread count
  - Score (80px) - Total score
  - Has Unsub (100px) - Yes/No
  - Status (120px) - Action status
- Treeview configuration:
  - `selectmode='extended'` for multi-select
  - Vertical scrollbar for scrolling
  - Column headers clickable for sorting
  - Store sender data in item tags for retrieval
- Color coding by score:
  - Score < 3: Normal (white/system default)
  - Score 3-6: Light yellow background (#FFFACD)
  - Score 7+: Light red background (#FFB6C1)
- Sorting: Click column header to sort ascending, click again for descending
- Right-click context menu (placeholder for future whitelist feature)

**Acceptance Criteria:**
- ✅ Table displays with all 6 columns
- ✅ Columns properly sized and readable
- ✅ Sortable by clicking any column header
- ✅ Alternate between ascending/descending sort
- ✅ Multi-select enabled with Ctrl/Shift
- ✅ Color coding applied based on score thresholds
- ✅ Scrollbar appears when needed
- ✅ Can populate with sender data from EmailGrouper
- ✅ Can retrieve selected senders with full data
- ✅ Can clear all data
- ✅ Performance adequate with 100+ senders
- ✅ Displays formatted numbers (e.g., "1,234")

**Files to Create:**
- `src/ui/sender_table.py` - Sender table widget

**Dependencies:**
- `tkinter.ttk.Treeview` (built-in)
- Sender data from `EmailGrouper` (Phase 3)
- `typing` (built-in)

**Test:**
1. Create SenderTable widget
2. Populate with 20 test senders
3. Verify all columns display correctly
4. Click Score header: verify sorts by score descending
5. Click again: verify sorts ascending
6. Click Sender header: verify alphabetical sort
7. Select multiple rows with Ctrl+click
8. Call get_selected(): verify returns correct data
9. Verify color coding: high-score senders have red background
10. Test with 200 senders: verify performance and scrolling
11. Clear table: verify all items removed

**Confidence Rationale:**
92% confidence - Tkinter Treeview is well-documented with extensive examples. Sorting and selection are standard features. Color coding requires tag configuration but is straightforward. Main risk is performance with large datasets, but Treeview efficiently handles hundreds of items.

**Example Code:**
```python
import tkinter as tk
from tkinter import ttk
from typing import List, Dict

class SenderTable:
    """Table widget for displaying sender data."""
    
    def __init__(self, parent):
        self.parent = parent
        self.sender_data = {}  # Store full data by item ID
        
        # Create frame with scrollbar
        self.frame = ttk.Frame(parent)
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL)
        
        # Create Treeview
        self.tree = ttk.Treeview(
            self.frame,
            columns=('sender', 'count', 'unread', 'score', 'has_unsub', 'status'),
            show='headings',
            selectmode='extended',
            yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.tree.yview)
        
        # Setup columns
        self._setup_columns()
        
        # Configure color tags
        self.tree.tag_configure('normal', background='white')
        self.tree.tag_configure('medium', background='#FFFACD')  # Light yellow
        self.tree.tag_configure('high', background='#FFB6C1')     # Light red
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _setup_columns(self):
        """Define column headers and properties."""
        columns = {
            'sender': ('Sender', 300),
            'count': ('Count', 80),
            'unread': ('Unread', 80),
            'score': ('Score', 80),
            'has_unsub': ('Has Unsub', 100),
            'status': ('Status', 120)
        }
        
        for col, (heading, width) in columns.items():
            self.tree.heading(col, text=heading,
                            command=lambda c=col: self._sort_by_column(c, False))
            self.tree.column(col, width=width)
    
    def populate(self, senders: List[Dict]):
        """Populate table with sender data."""
        self.clear()
        
        for sender in senders:
            # Determine color tag
            score = sender.get('total_score', 0)
            if score < 3:
                tag = 'normal'
            elif score < 7:
                tag = 'medium'
            else:
                tag = 'high'
            
            # Format values
            values = (
                sender.get('sender', ''),
                f"{sender.get('total_count', 0):,}",
                f"{sender.get('unread_count', 0):,}",
                f"{score:.1f}",
                'Yes' if sender.get('has_unsubscribe') else 'No',
                sender.get('status', 'Ready')
            )
            
            # Insert item
            item_id = self.tree.insert('', tk.END, values=values, tags=(tag,))
            self.sender_data[item_id] = sender
    
    def get_selected(self) -> List[Dict]:
        """Get selected sender data."""
        selected_ids = self.tree.selection()
        return [self.sender_data[item_id] for item_id in selected_ids
                if item_id in self.sender_data]
    
    def clear(self):
        """Clear all items."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.sender_data.clear()
    
    def _sort_by_column(self, col, reverse):
        """Sort table by column."""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Try numeric sort, fall back to string
        try:
            items.sort(key=lambda t: float(t[0].replace(',', '')), reverse=reverse)
        except ValueError:
            items.sort(reverse=reverse)
        
        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Toggle sort direction for next click
        self.tree.heading(col, command=lambda: self._sort_by_column(col, not reverse))
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
```

---

### Step 4.4: Scan Inbox Button & Progress

**Confidence:** 93% (improved from 87%)

**Description:**
Implement email scanning functionality with background thread execution and progress tracking. This step creates reusable threading infrastructure that safely updates the UI from background threads. The progress dialog provides feedback during long-running operations and supports cancellation. This threading pattern will be reused in Phases 5 and 6.

**Implementation Details:**

**Part A: Threading Infrastructure (`src/utils/threading_utils.py`)**
Create `BackgroundTask` class for managing threaded operations:
- `__init__(self, root: tk.Tk)` - Initialize with Tkinter root
- `run(task_func, on_progress, on_complete)` - Execute task in background
- `progress_callback(current, total, message)` - Thread-safe progress reporting
- `cancel()` - Cancel running task
- `_check_queue(on_progress, on_complete)` - Poll queue using .after()
- Uses `queue.Queue()` for thread-safe communication
- Uses `root.after(100)` for UI updates (Tkinter-safe)
- Daemon thread prevents blocking app exit

**Part B: Progress Dialog (`src/ui/progress_dialog.py`)**
Create `ProgressDialog` class:
- `__init__(self, parent, title)` - Modal dialog
- `update_progress(current, total, message)` - Update progress bar
- `set_cancel_callback(callback)` - Set cancellation handler
- Shows: progress bar, percentage, current/total, status message
- Cancel button that calls callback
- Auto-closes on completion

**Part C: Scan Integration (`src/ui/main_window.py`)**
Add scanning functionality:
- Add "Scan Inbox" button to toolbar/menu
- `scan_inbox()` method that:
  1. Retrieves account from database
  2. Creates ProgressDialog
  3. Creates BackgroundTask
  4. Defines scan task function that:
     - Connects to IMAP (IMAPClient)
     - Fetches emails in batches (500 at a time)
     - Parses emails (EmailParser)
     - Scores emails (EmailScorer)
     - Groups by sender (EmailGrouper)
     - Reports progress via callback
  5. Handles completion: populate SenderTable
  6. Handles errors: show error dialog
  7. Updates status bar throughout process

**Acceptance Criteria:**
- ✅ `threading_utils.py` created with BackgroundTask class
- ✅ BackgroundTask safely updates UI from background thread
- ✅ Uses queue.Queue for thread communication
- ✅ Uses root.after() for UI updates (thread-safe)
- ✅ `progress_dialog.py` created with ProgressDialog
- ✅ Progress dialog shows percentage and message
- ✅ "Scan Inbox" button added to main window
- ✅ Click triggers scan in background thread
- ✅ Progress dialog shows during scan
- ✅ Progress updates every 500 emails (or batch)
- ✅ Can cancel scan mid-operation
- ✅ Sender table populates when scan complete
- ✅ Status bar updates with current operation
- ✅ No UI freezing during scan
- ✅ Error handling for connection failures
- ✅ Handles no account configured gracefully

**Files to Create:**
- `src/ui/progress_dialog.py` - Progress dialog widget
- `src/utils/threading_utils.py` - Reusable threading infrastructure

**Files to Modify:**
- `src/ui/main_window.py` - Add scan functionality

**Dependencies:**
- `threading`, `queue` (built-in)
- `tkinter` (built-in)
- All Phase 2 components (IMAP, Email Parser)
- All Phase 3 components (Scorer, Grouper)

**Test:**
1. Add test account to database
2. Click "Scan Inbox" button
3. Verify progress dialog appears
4. Verify progress bar updates during scan
5. Verify message shows "Processing email X of Y"
6. Let scan complete: verify sender table populated
7. Verify statistics updated
8. Test cancellation: click Cancel mid-scan
9. Verify scan stops cleanly
10. Test with no account: verify helpful error message
11. Test with connection failure: verify error handling
12. Test with 1000+ emails: verify UI responsive

**Confidence Rationale:**
93% confidence (improved from 87%) - BackgroundTask pattern provides proven, thread-safe solution. Queue-based communication eliminates race conditions. Tkinter .after() is the recommended approach for UI updates from threads. Complete error handling and cancellation support mitigate risks. This pattern will be reused in Phases 5 and 6, providing consistent threading behavior throughout the application.

**Example Code:**
```python
# src/utils/threading_utils.py
import threading
import queue
from typing import Callable, Any
import tkinter as tk

class BackgroundTask:
    """Manages background tasks with progress updates for Tkinter UI."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.queue = queue.Queue()
        self.is_cancelled = False
        self.thread = None
    
    def run(self, task_func: Callable, on_progress: Callable, on_complete: Callable):
        """Run task in background thread with progress updates.
        
        Args:
            task_func: Function to run. Must accept progress_callback parameter.
            on_progress: Called with (current, total, message) for updates.
            on_complete: Called with result on completion or error.
        """
        self.is_cancelled = False
        
        def wrapper():
            try:
                result = task_func(self.progress_callback)
                if not self.is_cancelled:
                    self.queue.put(('complete', result))
            except Exception as e:
                self.queue.put(('error', str(e)))
        
        self.thread = threading.Thread(target=wrapper, daemon=True)
        self.thread.start()
        
        # Start checking queue
        self._check_queue(on_progress, on_complete)
    
    def progress_callback(self, current: int, total: int, message: str = ""):
        """Called by task to report progress (thread-safe)."""
        if not self.is_cancelled:
            self.queue.put(('progress', (current, total, message)))
    
    def _check_queue(self, on_progress, on_complete):
        """Check queue for updates and schedule next check."""
        try:
            while True:
                msg_type, data = self.queue.get_nowait()
                if msg_type == 'progress':
                    on_progress(*data)
                elif msg_type == 'complete':
                    on_complete(data)
                    return
                elif msg_type == 'error':
                    on_complete(None, error=data)
                    return
        except queue.Empty:
            pass
        
        # Schedule next check in 100ms (Tkinter-safe)
        if not self.is_cancelled:
            self.root.after(100, lambda: self._check_queue(on_progress, on_complete))
    
    def cancel(self):
        """Cancel the task."""
        self.is_cancelled = True

# src/ui/progress_dialog.py
import tkinter as tk
from tkinter import ttk

class ProgressDialog(tk.Toplevel):
    """Dialog showing progress of long-running operations."""
    
    def __init__(self, parent, title="Processing"):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Progress bar
        self.progress = ttk.Progressbar(self, length=350, mode='determinate')
        self.progress.pack(pady=20)
        
        # Status label
        self.status_label = ttk.Label(self, text="Initializing...")
        self.status_label.pack(pady=10)
        
        # Progress text
        self.progress_label = ttk.Label(self, text="0%")
        self.progress_label.pack()
        
        # Cancel button
        self.cancel_btn = ttk.Button(self, text="Cancel", command=self._on_cancel)
        self.cancel_btn.pack(pady=10)
        
        self.cancel_callback = None
        self.cancelled = False
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """Update progress bar and message."""
        if total > 0:
            percent = (current / total) * 100
            self.progress['value'] = percent
            self.progress_label.config(text=f"{percent:.1f}%")
        
        if message:
            self.status_label.config(text=message)
        else:
            self.status_label.config(text=f"Processing {current:,} of {total:,}")
        
        self.update_idletasks()
    
    def set_cancel_callback(self, callback):
        """Set function to call when cancelled."""
        self.cancel_callback = callback
    
    def _on_cancel(self):
        """Handle cancel button."""
        if self.cancel_callback and not self.cancelled:
            self.cancelled = True
            self.cancel_callback()
            self.status_label.config(text="Cancelling...")
            self.cancel_btn.config(state=tk.DISABLED)

# src/ui/main_window.py additions
from src.utils.threading_utils import BackgroundTask
from src.ui.progress_dialog import ProgressDialog
from src.email_client.imap_client import IMAPClient
from src.email_client.email_parser import EmailParser
from src.scoring.scorer import EmailScorer
from src.scoring.email_grouper import EmailGrouper

class MainWindow:
    # ... existing code ...
    
    def _create_toolbar(self):
        """Add toolbar with scan button."""
        toolbar = ttk.Frame(self.content_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        self.scan_btn = ttk.Button(toolbar, text="Scan Inbox", command=self.scan_inbox)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
    
    def scan_inbox(self):
        """Scan inbox for emails."""
        # Get account
        account = self.db.get_primary_account()
        if not account:
            messagebox.showerror("Error", "No account configured. Please add an account first.")
            return
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Scanning Inbox")
        
        # Create background task
        bg_task = BackgroundTask(self.root)
        progress.set_cancel_callback(bg_task.cancel)
        
        def scan_task(progress_callback):
            """Scan task to run in background."""
            # Decrypt password
            from src.email_client.credentials import CredentialManager
            cred = CredentialManager()
            password = cred.decrypt_password(account['encrypted_password'])
            
            # Connect to IMAP
            client = IMAPClient(account['email'], password)
            if not client.connect():
                raise Exception("Failed to connect to email server")
            
            # Fetch emails
            progress_callback(0, 100, "Fetching email list...")
            email_ids = client.fetch_email_ids(batch_size=500)
            total = len(email_ids)
            
            # Parse emails
            parser = EmailParser()
            emails = []
            for i, email_id in enumerate(email_ids):
                if bg_task.is_cancelled:
                    break
                
                # Fetch and parse
                headers = client.fetch_headers([email_id])
                if headers:
                    email_data = parser.parse_email(headers[0])
                    emails.append(email_data)
                
                # Update progress every 50 emails
                if i % 50 == 0:
                    progress_callback(i, total, f"Processing email {i+1:,} of {total:,}")
            
            client.disconnect()
            
            # Score and group
            progress_callback(total, total, "Analyzing senders...")
            scorer = EmailScorer(self.db)
            grouper = EmailGrouper(scorer)
            senders = grouper.group_by_sender(emails)
            
            return senders
        
        def on_progress(current, total, message):
            """Update progress dialog."""
            progress.update_progress(current, total, message)
        
        def on_complete(result, error=None):
            """Handle completion."""
            progress.destroy()
            
            if error:
                messagebox.showerror("Error", f"Scan failed: {error}")
            elif result:
                self.sender_table.populate(result)
                self.update_statistics(result)
                self.status_bar.config(text=f"Scan complete: {len(result)} senders found")
            else:
                self.status_bar.config(text="Scan cancelled")
        
        # Start scan
        bg_task.run(scan_task, on_progress, on_complete)
```

---

### Step 4.5: Summary Statistics Display

**Confidence:** 96%

**Description:**
Add summary statistics display to show aggregated metrics from the email scan. This provides users with a quick overview of their inbox status and helps them understand the scope of unwanted emails. Statistics update automatically after each scan and clearly communicate actionable information.

**Implementation Details:**
- Add statistics frame to main window (top of content area, above sender table):
  - Use grid layout for clean label pairs (title + value)
  - 4 statistics in 2x2 or 1x4 layout
  - Style: Bold labels, larger font for values
- Statistics to display:
  - **Total Senders:** Count of unique senders from scan
  - **Can Unsubscribe:** Count with `has_unsubscribe=True`
  - **Must Delete:** Count from unwanted_senders with `failed_unsubscribe=True`
  - **Total Emails:** Sum of all `total_count` across senders
- Add `update_statistics(self, senders: List[Dict])` method:
  - Calculate statistics from sender data
  - Query database for must-delete count
  - Update labels with formatted numbers
  - Apply color coding (red for must-delete if > 0)
- Update statistics after:
  - Scan completion
  - Unsubscribe operations (Phase 5)
  - Delete operations (Phase 6)
- Reset to zeros when no data or on app start

**Acceptance Criteria:**
- ✅ Statistics frame visible above sender table
- ✅ Shows total senders count
- ✅ Shows can unsubscribe count (senders with unsubscribe links)
- ✅ Shows must delete count (from database)
- ✅ Shows total emails count (sum across all senders)
- ✅ Updates automatically after scan completes
- ✅ Values formatted with commas (e.g., "1,234" not "1234")
- ✅ Must-delete count highlighted in red if > 0
- ✅ Layout responsive to window resizing
- ✅ Resets to zeros when appropriate

**Files to Modify:**
- `src/ui/main_window.py` - Add statistics frame and update method

**Dependencies:**
- Sender data from EmailGrouper
- Must-delete data from DBManager
- `tkinter` (built-in)

**Test:**
1. Run scan with test account
2. Verify total senders matches number of table rows
3. Calculate manually: verify can unsubscribe count correct
4. Add sender to unwanted_senders with failed_unsubscribe=True
5. Verify must delete count reflects database
6. Verify total emails is sum of all counts
7. Resize window: verify layout maintains
8. Clear table: verify statistics reset to zeros
9. Verify number formatting includes commas

**Confidence Rationale:**
96% confidence - Simple label widgets with data aggregation from existing structures. No complex logic or external dependencies beyond what's already in place. Formatting and layout are straightforward Tkinter operations. Very low risk, high clarity.

**Example Code:**
```python
# Add to MainWindow class in src/ui/main_window.py

def _create_statistics_frame(self):
    """Create statistics display above sender table."""
    self.stats_frame = ttk.LabelFrame(self.content_frame, text="Summary", padding=10)
    self.stats_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
    
    # Create statistics labels
    stats_grid = ttk.Frame(self.stats_frame)
    stats_grid.pack()
    
    # Total Senders
    ttk.Label(stats_grid, text="Total Senders:", font=('', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=10)
    self.stat_total_senders = ttk.Label(stats_grid, text="0", font=('', 14))
    self.stat_total_senders.grid(row=0, column=1, padx=10)
    
    # Can Unsubscribe
    ttk.Label(stats_grid, text="Can Unsubscribe:", font=('', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=10)
    self.stat_can_unsub = ttk.Label(stats_grid, text="0", font=('', 14))
    self.stat_can_unsub.grid(row=0, column=3, padx=10)
    
    # Must Delete
    ttk.Label(stats_grid, text="Must Delete:", font=('', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=10)
    self.stat_must_delete = ttk.Label(stats_grid, text="0", font=('', 14), foreground='black')
    self.stat_must_delete.grid(row=1, column=1, padx=10)
    
    # Total Emails
    ttk.Label(stats_grid, text="Total Emails:", font=('', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, padx=10)
    self.stat_total_emails = ttk.Label(stats_grid, text="0", font=('', 14))
    self.stat_total_emails.grid(row=1, column=3, padx=10)

def update_statistics(self, senders: List[Dict]):
    """Update statistics from sender data."""
    if not senders:
        # Reset to zeros
        self.stat_total_senders.config(text="0")
        self.stat_can_unsub.config(text="0")
        self.stat_must_delete.config(text="0")
        self.stat_total_emails.config(text="0")
        return
    
    # Calculate statistics
    total_senders = len(senders)
    can_unsubscribe = sum(1 for s in senders if s.get('has_unsubscribe'))
    total_emails = sum(s.get('total_count', 0) for s in senders)
    
    # Query must-delete from database
    # (This would be from unwanted_senders where failed_unsubscribe = True)
    must_delete = 0  # Placeholder - implement in Phase 6
    
    # Update labels with formatting
    self.stat_total_senders.config(text=f"{total_senders:,}")
    self.stat_can_unsub.config(text=f"{can_unsubscribe:,}")
    self.stat_total_emails.config(text=f"{total_emails:,}")
    
    # Must delete with color coding
    self.stat_must_delete.config(
        text=f"{must_delete:,}",
        foreground='red' if must_delete > 0 else 'black'
    )
```

---

**Phase 4 Completion Criteria:**
- All 5 steps complete
- GUI opens and displays correctly
- Can scan inbox and see results
- Progress indication works
- No linter errors

---

## Phase 5: Unsubscribe Strategies (Core)

**Goal:** Implement first 2 unsubscribe strategies (simplest)

**Duration Estimate:** 3-4 hours

**Prerequisites:** Phase 4 complete

**Phase Confidence:** 93% ✅

### Step 5.1: Strategy Base Class

**Confidence:** 96%

**Description:**
Create abstract base class for all unsubscribe strategies. This establishes the Strategy pattern that allows different unsubscribe methods to be selected dynamically based on email properties. The base class defines the interface and common error handling, ensuring consistency across all strategy implementations.

**Implementation Details:**
- Create `UnsubscribeStrategy` abstract base class in `src/unsubscribe/strategy_base.py`:
  - `__init__(self)` - Initialize strategy with logger
  - `can_handle(self, email_data: Dict) -> bool` - Abstract method to check if strategy applies
  - `execute(self, email_data: Dict) -> Tuple[bool, str]` - Abstract method to perform unsubscribe
  - `_log_attempt(self, email, method)` - Log unsubscribe attempt
  - `_log_result(self, email, success, message)` - Log result
- Use `abc.ABC` and `@abstractmethod` decorators
- Return tuple: `(success: bool, message: str)`
  - success=True: Unsubscribe completed successfully
  - success=False: Unsubscribe failed
  - message: Detailed result message for logging/display
- Common error handling wrapper for all strategies
- Type hints throughout for clarity
- Docstrings with examples

**Acceptance Criteria:**
- ✅ `UnsubscribeStrategy` abstract base class created
- ✅ Uses `abc.ABC` for abstract enforcement
- ✅ `can_handle()` abstract method defined
- ✅ `execute()` abstract method defined
- ✅ Returns `Tuple[bool, str]` from execute
- ✅ Has logging methods for attempts and results
- ✅ Type hints on all methods
- ✅ Comprehensive docstrings
- ✅ Cannot instantiate abstract class directly
- ✅ Subclasses must implement abstract methods

**Files to Create:**
- `src/unsubscribe/strategy_base.py` - Strategy base class
- `src/unsubscribe/__init__.py` - Package init

**Dependencies:**
- `abc` (built-in)
- `typing` (built-in)
- `logging` (built-in)

**Test:**
1. Try to instantiate UnsubscribeStrategy directly
2. Verify TypeError raised (cannot instantiate abstract class)
3. Create test subclass without implementing methods
4. Verify TypeError raised
5. Create test subclass with all methods implemented
6. Verify successful instantiation
7. Test can_handle() and execute() return correct types
8. Verify logging methods work correctly

**Confidence Rationale:**
96% confidence - Python's abc module is well-established for abstract base classes. Strategy pattern is proven and straightforward. No external dependencies or complex logic. Very low risk.

**Example Code:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Tuple
import logging

class UnsubscribeStrategy(ABC):
    """Abstract base class for unsubscribe strategies."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def can_handle(self, email_data: Dict) -> bool:
        """Check if this strategy can handle the given email.
        
        Args:
            email_data: Email data dictionary with sender, links, etc.
        
        Returns:
            True if strategy can handle this email, False otherwise.
        """
        pass
    
    @abstractmethod
    def execute(self, email_data: Dict) -> Tuple[bool, str]:
        """Execute unsubscribe for the given email.
        
        Args:
            email_data: Email data dictionary with sender, links, etc.
        
        Returns:
            Tuple of (success, message):
                - success: True if unsubscribe successful, False otherwise
                - message: Human-readable result message
        """
        pass
    
    def _log_attempt(self, email: str, method: str):
        """Log unsubscribe attempt."""
        self.logger.info(f"Attempting unsubscribe for {email} via {method}")
    
    def _log_result(self, email: str, success: bool, message: str):
        """Log unsubscribe result."""
        level = logging.INFO if success else logging.WARNING
        status = "SUCCESS" if success else "FAILED"
        self.logger.log(level, f"Unsubscribe {status} for {email}: {message}")
```

---

### Step 5.2: Strategy 1 - List-Unsubscribe Header

**Confidence:** 91%

**Description:**
Implement RFC 2369 List-Unsubscribe header strategy. This is the most reliable unsubscribe method as it uses standardized email headers designed specifically for mailing list unsubscription. Many professional email marketers implement this header correctly, making it a high-success first strategy.

**Implementation Details:**
- Create `ListUnsubscribeStrategy` class in `src/unsubscribe/list_unsubscribe.py`:
  - Extends `UnsubscribeStrategy`
  - `can_handle()`: Returns True if email has `List-Unsubscribe` header
  - `execute()`: Processes header value
    - Parse header for URLs (HTTP/HTTPS) or mailto links
    - If `List-Unsubscribe-Post` header present: Use POST with `List-Unsubscribe=One-Click`
    - Otherwise use GET request
    - Handle mailto: by opening email client (out of scope for MVP, return False)
- Use `requests` library for HTTP requests:
  - 10 second timeout
  - Custom User-Agent: "Mozilla/5.0 (Email Unsubscriber)"
  - Follow redirects (max 5)
  - Check response: 2xx = success, 4xx/5xx = failure
- Extract URLs from header format: `<url1>, <url2>` or `<mailto:...>`
- Try HTTP URLs first, skip mailto for MVP
- Log all attempts and results

**Acceptance Criteria:**
- ✅ Extends UnsubscribeStrategy base class
- ✅ `can_handle()` checks for List-Unsubscribe header
- ✅ Parses header with angle brackets `<url>`
- ✅ Handles multiple URLs in header (tries first HTTP URL)
- ✅ Uses POST when List-Unsubscribe-Post header present
- ✅ Uses GET when only List-Unsubscribe present
- ✅ Sends List-Unsubscribe=One-Click body for POST
- ✅ 10 second timeout on requests
- ✅ Custom User-Agent header
- ✅ Follows redirects
- ✅ Returns success for 2xx responses
- ✅ Returns failure for 4xx/5xx or network errors
- ✅ Skips mailto: links (not implemented in MVP)
- ✅ Logs attempts and results

**Files to Create:**
- `src/unsubscribe/list_unsubscribe.py` - List-Unsubscribe strategy

**Dependencies:**
- `UnsubscribeStrategy` from `src.unsubscribe.strategy_base` (Phase 5.1)
- `requests` library (already in requirements.txt)
- `re` (built-in) for URL extraction

**Test:**
1. Get test email with List-Unsubscribe header
2. Verify can_handle() returns True
3. Call execute()
4. Verify HTTP request made to URL
5. Test with List-Unsubscribe-Post: verify POST used
6. Test without Post header: verify GET used
7. Test with 200 response: verify success returned
8. Test with 404 response: verify failure returned
9. Test with network timeout: verify failure handled
10. Test with mailto: link: verify skipped/returns False

**Confidence Rationale:**
91% confidence - RFC 2369 headers are well-defined. Requests library is mature and reliable. Main risk is server-side variations in header implementation, but following the spec closely mitigates this. One-Click POST is well-documented.

**Example Code:**
```python
from src.unsubscribe.strategy_base import UnsubscribeStrategy
from typing import Dict, Tuple
import requests
import re

class ListUnsubscribeStrategy(UnsubscribeStrategy):
    """Strategy using RFC 2369 List-Unsubscribe header."""
    
    def __init__(self):
        super().__init__()
        self.timeout = 10
        self.headers = {'User-Agent': 'Mozilla/5.0 (Email Unsubscriber)'}
    
    def can_handle(self, email_data: Dict) -> bool:
        """Check if email has List-Unsubscribe header."""
        return 'list_unsubscribe' in email_data and bool(email_data['list_unsubscribe'])
    
    def execute(self, email_data: Dict) -> Tuple[bool, str]:
        """Execute unsubscribe using List-Unsubscribe header."""
        header = email_data.get('list_unsubscribe', '')
        sender = email_data.get('sender', 'unknown')
        
        self._log_attempt(sender, 'List-Unsubscribe header')
        
        # Extract URLs from header (format: <url1>, <url2> or <mailto:...>)
        urls = re.findall(r'<(https?://[^>]+)>', header)
        
        if not urls:
            message = "No HTTP URLs in List-Unsubscribe header"
            self._log_result(sender, False, message)
            return (False, message)
        
        # Use first HTTP URL
        url = urls[0]
        
        try:
            # Check if List-Unsubscribe-Post header exists
            if 'list_unsubscribe_post' in email_data:
                # Use POST with One-Click
                response = requests.post(
                    url,
                    data={'List-Unsubscribe': 'One-Click'},
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
            else:
                # Use GET
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
            
            # Check response
            if 200 <= response.status_code < 300:
                message = f"Unsubscribed successfully (HTTP {response.status_code})"
                self._log_result(sender, True, message)
                return (True, message)
            else:
                message = f"Unsubscribe failed (HTTP {response.status_code})"
                self._log_result(sender, False, message)
                return (False, message)
        
        except requests.Timeout:
            message = "Unsubscribe request timed out"
            self._log_result(sender, False, message)
            return (False, message)
        except requests.RequestException as e:
            message = f"Network error: {str(e)}"
            self._log_result(sender, False, message)
            return (False, message)
```

---

### Step 5.3: Strategy 2 - Direct HTTP GET/POST

**Confidence:** 90%

**Description:**
Implement direct HTTP request strategy for unsubscribe links found in email body (HTML or plain text). This strategy handles URLs that don't use the List-Unsubscribe header. It tries GET first (most common), then POST if GET returns Method Not Allowed (405). This covers the majority of unsubscribe links embedded in emails.

**Implementation Details:**
- Create `HTTPStrategy` class in `src/unsubscribe/http_strategy.py`:
  - Extends `UnsubscribeStrategy`
  - `can_handle()`: Returns True if email has `unsubscribe_links` list
  - `execute()`: Tries each link in order
    - Try GET request first
    - If 405 (Method Not Allowed): Try POST
    - If 2xx: Success
    - If 4xx/5xx: Try next link
- Request configuration:
  - Timeout: 15 seconds (longer than List-Unsubscribe to allow for page loading)
  - User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  - Follow redirects: max 5
  - Session cookies enabled (some require cookies)
- Try up to 3 links from unsubscribe_links list
- Stop on first success
- Return failure if all links fail

**Acceptance Criteria:**
- ✅ Extends UnsubscribeStrategy base class
- ✅ `can_handle()` checks for unsubscribe_links in email data
- ✅ Tries GET request first for each URL
- ✅ If GET returns 405: tries POST
- ✅ If GET/POST returns 2xx: returns success
- ✅ Tries up to 3 different links if available
- ✅ Stops on first successful link
- ✅ 15 second timeout per request
- ✅ Custom User-Agent
- ✅ Follows redirects (max 5)
- ✅ Uses session for cookie support
- ✅ Returns failure if all links fail
- ✅ Logs each attempt and result

**Files to Create:**
- `src/unsubscribe/http_strategy.py` - HTTP strategy

**Dependencies:**
- `UnsubscribeStrategy` from `src.unsubscribe.strategy_base` (Phase 5.1)
- `requests` library

**Test:**
1. Create test email with unsubscribe_links
2. Verify can_handle() returns True
3. Call execute() with GET-only link
4. Verify GET request made and success returned
5. Test with 405 response: verify POST attempted
6. Test with multiple links: verify tries each in order
7. Test with all links failing: verify failure returned
8. Test with 2nd link succeeding: verify stopped after success
9. Test timeout: verify handled gracefully
10. Test redirect: verify follows and succeeds

**Confidence Rationale:**
90% confidence - HTTP requests are straightforward with requests library. GET-then-POST fallback is a proven pattern. Main risk is diversity of unsubscribe page implementations (CAPTCHAs, JavaScript requirements) which can't be handled without browser automation. However, many simple unsubscribe pages work fine with direct HTTP.

**Example Code:**
```python
from src.unsubscribe.strategy_base import UnsubscribeStrategy
from typing import Dict, Tuple, List
import requests

class HTTPStrategy(UnsubscribeStrategy):
    """Strategy using direct HTTP GET/POST to unsubscribe links."""
    
    def __init__(self):
        super().__init__()
        self.timeout = 15
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.max_links = 3
    
    def can_handle(self, email_data: Dict) -> bool:
        """Check if email has unsubscribe links."""
        links = email_data.get('unsubscribe_links', [])
        return len(links) > 0
    
    def execute(self, email_data: Dict) -> Tuple[bool, str]:
        """Execute unsubscribe using HTTP requests."""
        links = email_data.get('unsubscribe_links', [])
        sender = email_data.get('sender', 'unknown')
        
        self._log_attempt(sender, 'HTTP Strategy')
        
        # Try up to max_links
        for i, url in enumerate(links[:self.max_links]):
            self.logger.info(f"Trying link {i+1}/{min(len(links), self.max_links)}: {url}")
            
            success, message = self._try_url(url)
            if success:
                self._log_result(sender, True, message)
                return (True, message)
        
        # All links failed
        message = f"All {min(len(links), self.max_links)} unsubscribe links failed"
        self._log_result(sender, False, message)
        return (False, message)
    
    def _try_url(self, url: str) -> Tuple[bool, str]:
        """Try a single URL with GET, then POST if needed."""
        session = requests.Session()
        
        try:
            # Try GET first
            response = session.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            if 200 <= response.status_code < 300:
                return (True, f"Unsubscribed via GET (HTTP {response.status_code})")
            
            # If Method Not Allowed, try POST
            if response.status_code == 405:
                self.logger.info(f"GET returned 405, trying POST")
                response = session.post(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                if 200 <= response.status_code < 300:
                    return (True, f"Unsubscribed via POST (HTTP {response.status_code})")
            
            return (False, f"HTTP {response.status_code}")
        
        except requests.Timeout:
            return (False, "Request timed out")
        except requests.RequestException as e:
            return (False, f"Network error: {str(e)[:50]}")
        finally:
            session.close()
```

---

### Step 5.4: Strategy Chain Coordinator

**Confidence:** 94%

**Description:**
Create a coordinator that manages multiple unsubscribe strategies and executes them in priority order. This implements the Chain of Responsibility pattern, trying each strategy until one succeeds. It provides a single interface for unsubscribe operations while managing the complexity of multiple strategies behind the scenes.

**Implementation Details:**
- Create `StrategyChain` class in `src/unsubscribe/strategy_chain.py`:
  - `__init__(self, db_manager: DBManager)` - Initialize with database manager
  - `add_strategy(self, strategy: UnsubscribeStrategy)` - Add strategy to chain
  - `execute(self, email_data: Dict) -> Tuple[bool, str, str]` - Try all strategies
  - Returns `(success, message, strategy_name)`
- Strategy priority order (hardcoded):
  1. `ListUnsubscribeStrategy` - Most reliable
  2. `HTTPStrategy` - Fallback for body links
- For each strategy:
  - Check `can_handle(email_data)`
  - If True: call `execute(email_data)`
  - If success: Stop and return
  - If failure: Try next strategy
- Log results to `unsubscribe_attempts` table:
  - sender, strategy_used, success, timestamp, message
- If all strategies fail: Return failure with combined message

**Acceptance Criteria:**
- ✅ StrategyChain class created
- ✅ Can add strategies to chain
- ✅ Maintains strategy order
- ✅ Tries strategies in priority order
- ✅ Checks can_handle() before execute()
- ✅ Stops on first success
- ✅ Returns success, message, and strategy name
- ✅ Logs all attempts to database
- ✅ Returns failure if all strategies fail
- ✅ Handles exceptions from strategies gracefully
- ✅ Works with any strategy implementing base interface

**Files to Create:**
- `src/unsubscribe/strategy_chain.py` - Strategy coordinator

**Dependencies:**
- `UnsubscribeStrategy` from `src.unsubscribe.strategy_base` (Phase 5.1)
- `ListUnsubscribeStrategy` from `src.unsubscribe.list_unsubscribe` (Phase 5.2)
- `HTTPStrategy` from `src.unsubscribe.http_strategy` (Phase 5.3)
- `DBManager` from `src.database.db_manager` (Phase 1)

**Test:**
1. Create StrategyChain with test database
2. Add ListUnsubscribeStrategy
3. Add HTTPStrategy
4. Test email with List-Unsubscribe header
5. Call execute(): verify ListUnsubscribeStrategy used
6. Verify returns success and strategy name
7. Test email with only body links (no header)
8. Call execute(): verify HTTPStrategy used
9. Test email with no unsubscribe options
10. Verify returns failure
11. Verify all attempts logged to database
12. Test with strategy raising exception: verify handled

**Confidence Rationale:**
94% confidence - Chain of Responsibility is a well-established pattern. Strategy interface is clean and consistent. Database logging is straightforward. Main risk is ensuring proper exception handling for strategy failures, which is mitigated by try/except blocks.

**Example Code:**
```python
from typing import Dict, Tuple, List
import logging
from src.unsubscribe.strategy_base import UnsubscribeStrategy
from src.database.db_manager import DBManager

class StrategyChain:
    """Coordinates multiple unsubscribe strategies."""
    
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self.strategies: List[UnsubscribeStrategy] = []
        self.logger = logging.getLogger(__name__)
    
    def add_strategy(self, strategy: UnsubscribeStrategy):
        """Add a strategy to the chain."""
        self.strategies.append(strategy)
        self.logger.info(f"Added strategy: {strategy.__class__.__name__}")
    
    def execute(self, email_data: Dict) -> Tuple[bool, str, str]:
        """Execute strategies in order until one succeeds.
        
        Returns:
            Tuple of (success, message, strategy_name)
        """
        sender = email_data.get('sender', 'unknown')
        self.logger.info(f"Starting unsubscribe for {sender}")
        
        # Try each strategy
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            
            try:
                # Check if strategy can handle this email
                if not strategy.can_handle(email_data):
                    self.logger.debug(f"{strategy_name} cannot handle this email")
                    continue
                
                # Execute strategy
                self.logger.info(f"Trying {strategy_name} for {sender}")
                success, message = strategy.execute(email_data)
                
                # Log attempt to database
                self._log_attempt(sender, strategy_name, success, message)
                
                # If successful, return immediately
                if success:
                    self.logger.info(f"{strategy_name} succeeded for {sender}")
                    return (True, message, strategy_name)
                else:
                    self.logger.warning(f"{strategy_name} failed for {sender}: {message}")
            
            except Exception as e:
                # Strategy raised an exception
                error_msg = f"Strategy error: {str(e)}"
                self.logger.error(f"{strategy_name} raised exception: {e}")
                self._log_attempt(sender, strategy_name, False, error_msg)
        
        # All strategies failed
        message = "All unsubscribe strategies failed"
        self.logger.warning(f"All strategies failed for {sender}")
        return (False, message, "None")
    
    def _log_attempt(self, sender: str, strategy: str, success: bool, message: str):
        """Log unsubscribe attempt to database."""
        try:
            self.db.log_unsubscribe_attempt(sender, strategy, success, message)
        except Exception as e:
            self.logger.error(f"Failed to log attempt: {e}")
```

---

### Step 5.5: Unsubscribe Button Integration

**Confidence:** 92%

**Description:**
Integrate unsubscribe functionality into the main UI with a button that processes selected senders. This step reuses the threading infrastructure from Phase 4 to keep the UI responsive during batch unsubscribe operations. Users can select multiple senders and unsubscribe from all with one click, with clear confirmation and progress feedback.

**Implementation Details:**
- Add "Unsubscribe Selected" button to main window toolbar
- Implement `unsubscribe_selected()` method in MainWindow:
  1. Get selected senders from SenderTable
  2. Show confirmation dialog with count
  3. Create StrategyChain with both strategies
  4. Create BackgroundTask (reuse from Phase 4)
  5. Create ProgressDialog
  6. Define unsubscribe task function:
     - For each sender:
       - Get sample email data (from most recent email)
       - Call strategy_chain.execute()
       - Update sender status in table
       - Report progress
  7. Handle completion: Update statistics, refresh table
- Confirmation dialog shows:
  - Number of senders to unsubscribe from
  - Warning about irreversibility
  - "Proceed" and "Cancel" buttons
- Progress dialog shows:
  - Current sender being processed
  - Success/failure count
  - Overall progress bar
- After completion:
  - Show summary dialog (X succeeded, Y failed)
  - Update sender table with status
  - Update statistics

**Acceptance Criteria:**
- ✅ "Unsubscribe Selected" button in toolbar
- ✅ Button disabled when no senders selected
- ✅ Confirmation dialog before starting
- ✅ Dialog shows count of selected senders
- ✅ Runs in background thread using BackgroundTask
- ✅ Progress dialog shows current status
- ✅ Progress updates for each sender
- ✅ Can cancel operation mid-process
- ✅ UI remains responsive during operation
- ✅ Sender table updates with success/failure status
- ✅ Statistics refresh after completion
- ✅ Summary dialog shows results
- ✅ All attempts logged to database
- ✅ Handles errors gracefully

**Files to Modify:**
- `src/ui/main_window.py` - Add button and unsubscribe logic

**Dependencies:**
- `StrategyChain` from `src.unsubscribe.strategy_chain` (Phase 5.4)
- `ListUnsubscribeStrategy` from `src.unsubscribe.list_unsubscribe` (Phase 5.2)
- `HTTPStrategy` from `src.unsubscribe.http_strategy` (Phase 5.3)
- `BackgroundTask` from `src.utils.threading_utils` (Phase 4.4)
- `ProgressDialog` from `src.ui.progress_dialog` (Phase 4.4)
- `SenderTable` from `src.ui.sender_table` (Phase 4.3)

**Test:**
1. Scan inbox to populate senders
2. Select 3 senders with unsubscribe links
3. Click "Unsubscribe Selected" button
4. Verify confirmation dialog appears
5. Click Proceed
6. Verify progress dialog shows
7. Verify progress updates for each sender
8. Let operation complete
9. Verify summary dialog shows results
10. Verify sender table updated with statuses
11. Verify statistics updated
12. Test cancellation: click Cancel mid-operation
13. Verify operation stops cleanly
14. Test with no selection: verify button disabled
15. Test with failed unsubscribes: verify proper logging

**Confidence Rationale:**
92% confidence - Reuses proven threading infrastructure from Phase 4. Strategy chain provides clean interface. Confirmation and progress dialogs are standard Tkinter patterns. Main risk is coordinating UI updates during batch operations, but BackgroundTask's queue-based approach handles this well.

**Example Code:**
```python
# Add to MainWindow class in src/ui/main_window.py

from src.unsubscribe.strategy_chain import StrategyChain
from src.unsubscribe.list_unsubscribe import ListUnsubscribeStrategy
from src.unsubscribe.http_strategy import HTTPStrategy

def _create_toolbar(self):
    """Add toolbar with scan and unsubscribe buttons."""
    toolbar = ttk.Frame(self.content_frame)
    toolbar.pack(side=tk.TOP, fill=tk.X, pady=5)
    
    self.scan_btn = ttk.Button(toolbar, text="Scan Inbox", command=self.scan_inbox)
    self.scan_btn.pack(side=tk.LEFT, padx=5)
    
    self.unsub_btn = ttk.Button(toolbar, text="Unsubscribe Selected",
                                command=self.unsubscribe_selected, state=tk.DISABLED)
    self.unsub_btn.pack(side=tk.LEFT, padx=5)

def _on_sender_selection_changed(self):
    """Enable/disable unsubscribe button based on selection."""
    selected = self.sender_table.get_selected()
    self.unsub_btn.config(state=tk.NORMAL if selected else tk.DISABLED)

def unsubscribe_selected(self):
    """Unsubscribe from selected senders."""
    selected = self.sender_table.get_selected()
    if not selected:
        return
    
    # Confirmation dialog
    count = len(selected)
    result = messagebox.askyesno(
        "Confirm Unsubscribe",
        f"Unsubscribe from {count} sender(s)?\n\n"
        "This will attempt to unsubscribe using available methods."
    )
    if not result:
        return
    
    # Create progress dialog
    progress = ProgressDialog(self.root, "Unsubscribing")
    
    # Create background task
    bg_task = BackgroundTask(self.root)
    progress.set_cancel_callback(bg_task.cancel)
    
    def unsubscribe_task(progress_callback):
        """Unsubscribe task to run in background."""
        # Create strategy chain
        chain = StrategyChain(self.db)
        chain.add_strategy(ListUnsubscribeStrategy())
        chain.add_strategy(HTTPStrategy())
        
        results = {'success': 0, 'failed': 0}
        
        for i, sender_data in enumerate(selected):
            if bg_task.is_cancelled:
                break
            
            sender = sender_data['sender']
            progress_callback(i, count, f"Processing {sender}")
            
            # Execute unsubscribe
            success, message, strategy = chain.execute(sender_data)
            
            if success:
                results['success'] += 1
                sender_data['status'] = f'Unsubscribed ({strategy})'
            else:
                results['failed'] += 1
                sender_data['status'] = f'Failed: {message[:30]}'
        
        return results
    
    def on_progress(current, total, message):
        """Update progress dialog."""
        progress.update_progress(current, total, message)
    
    def on_complete(results, error=None):
        """Handle completion."""
        progress.destroy()
        
        if error:
            messagebox.showerror("Error", f"Unsubscribe failed: {error}")
        elif results:
            # Show summary
            msg = f"Unsubscribe complete:\n\n"
            msg += f"  Successful: {results['success']}\n"
            msg += f"  Failed: {results['failed']}"
            messagebox.showinfo("Unsubscribe Complete", msg)
            
            # Refresh UI
            self.sender_table.refresh()
            self.update_statistics(self.sender_table.get_all())
            self.status_bar.config(text=f"Unsubscribe complete: {results['success']} succeeded")
        else:
            self.status_bar.config(text="Unsubscribe cancelled")
    
    # Start unsubscribe
    bg_task.run(unsubscribe_task, on_progress, on_complete)
```

---

**Phase 5 Completion Criteria:**
- All 5 steps complete
- Can unsubscribe using Strategy 1 & 2
- Strategy chain works correctly
- UI button triggers unsubscribe
- Results logged to database
- No linter errors

---

## Phase 6: Email Deletion & Must-Delete List

**Goal:** Implement email deletion and "Must Delete" functionality

**Duration Estimate:** 2-3 hours

**Prerequisites:** Phase 5 complete

**Phase Confidence:** 92% ✅

### Step 6.1: IMAP Delete Functionality

**Confidence:** 91%

**Description:**
Add email deletion capabilities to IMAPClient, allowing bulk deletion of emails from specific senders. This implements "delete all emails from this sender" functionality for senders where unsubscribe failed. Uses IM AP STORE command to mark emails as deleted and EXPUNGE to permanently remove them.

**Implementation Details:**
- Add methods to `IMAPClient` class in `src/email_client/imap_client.py`:
  - `delete_emails_from_sender(self, sender_email: str) -> Tuple[int, str]` - Main method
  - `_search_by_sender(self, sender: str) -> List[bytes]` - Find all email IDs from sender
  - `_mark_deleted(self, message_ids: List[bytes])` - Mark emails with \Deleted flag
  - `_expunge()` - Permanently delete marked emails
- Search for emails: `SEARCH FROM "sender@example.com"`
- Mark for deletion: `STORE message_id +FLAGS (\\Deleted)`
- Permanently delete: `EXPUNGE`
- Return tuple: `(count_deleted, message)`
- Handle errors:
  - No emails found from sender
  - Connection errors
  - Permission errors (some servers restrict deletion)
- Log all operations
- Whitelist check before deletion (safety check)

**Acceptance Criteria:**
- ✅ `delete_emails_from_sender()` method added to IMAPClient
- ✅ Searches for all emails from specified sender
- ✅ Marks emails with \\Deleted flag
- ✅ Expunges (permanently deletes) marked emails
- ✅ Returns count of deleted emails
- ✅ Returns descriptive message
- ✅ Checks whitelist before deleting (safety)
- ✅ Handles "no emails found" gracefully
- ✅ Handles connection errors
- ✅ Handles permission errors
- ✅ Logs all operations
- ✅ Can delete 100+ emails efficiently

**Files to Modify:**
- `src/email_client/imap_client.py` - Add deletion methods

**Dependencies:**
- Existing `IMAPClient` class (Phase 2)
- `imaplib` (built-in)
- `DBManager` for whitelist check (Phase 1)

**Test:**
1. Connect to test IMAP account
2. Send test emails from test sender
3. Call delete_emails_from_sender(test_sender)
4. Verify returns correct count
5. Check inbox: verify emails deleted
6. Test with non-existent sender: verify returns 0
7. Test with whitelisted sender: verify deletion prevented
8. Test with connection error: verify error handled
9. Test with 50+ emails: verify bulk deletion works
10. Verify all operations logged

**Confidence Rationale:**
91% confidence - IMAP deletion commands are well-documented and straightforward. Main risks are server-specific variations in deletion behavior and permission issues, but error handling mitigates these. Whitelist check provides safety net.

**Example Code:**
```python
# Add to IMAPClient class in src/email_client/imap_client.py

def delete_emails_from_sender(self, sender_email: str, db_manager=None) -> Tuple[int, str]:
    """Delete all emails from a specific sender.
    
    Args:
        sender_email: Email address of sender
        db_manager: Optional DBManager for whitelist check
    
    Returns:
        Tuple of (count_deleted, message)
    """
    # Safety check: whitelist
    if db_manager and db_manager.check_whitelist(sender_email):
        message = f"Cannot delete: {sender_email} is whitelisted"
        self.logger.warning(message)
        return (0, message)
    
    try:
        # Select inbox
        self.imap.select('INBOX')
        
        # Search for emails from sender
        self.logger.info(f"Searching for emails from {sender_email}")
        status, data = self.imap.search(None, f'FROM "{sender_email}"')
        
        if status != 'OK':
            return (0, "Search failed")
        
        message_ids = data[0].split()
        count = len(message_ids)
        
        if count == 0:
            return (0, f"No emails found from {sender_email}")
        
        self.logger.info(f"Found {count} emails from {sender_email}, marking for deletion")
        
        # Mark all for deletion
        for msg_id in message_ids:
            self.imap.store(msg_id, '+FLAGS', '\\Deleted')
        
        # Permanently delete
        self.imap.expunge()
        
        message = f"Deleted {count} emails from {sender_email}"
        self.logger.info(message)
        return (count, message)
    
    except imaplib.IMAP4.error as e:
        message = f"IMAP error during deletion: {str(e)}"
        self.logger.error(message)
        return (0, message)
    except Exception as e:
        message = f"Unexpected error during deletion: {str(e)}"
        self.logger.error(message)
        return (0, message)
```

---

### Step 6.2: Must-Delete List Tracking

**Confidence:** 94%

**Description:**
Automatically track senders where unsubscribe fails by adding them to the `unwanted_senders` table with a `failed_unsubscribe` flag. This creates a "Must Delete" list for users to review and delete emails manually when automatic unsubscribe doesn't work.

**Implementation Details:**
- Add method to `DBManager`: `add_to_must_delete(sender, reason)`
  - Insert into `unwanted_senders` table
  - Set `failed_unsubscribe = True`
  - Store failure reason
  - Store timestamp
- Modify `StrategyChain.execute()`:
  - If all strategies fail: call `db.add_to_must_delete(sender, message)`
  - Log to database
- Add query method: `get_must_delete_senders() -> List[Dict]`
  - Returns all senders with `failed_unsubscribe = True`
  - Includes sender, count, reason, timestamp

**Acceptance Criteria:**
- ✅ `add_to_must_delete()` method in DBManager
- ✅ Inserts sender into unwanted_senders table
- ✅ Sets failed_unsubscribe flag to True
- ✅ Stores failure reason
- ✅ StrategyChain calls add_to_must_delete() on failure
- ✅ `get_must_delete_senders()` query method added
- ✅ Returns list of failed senders with details
- ✅ Prevents duplicate entries (upsert)
- ✅ Updates failure reason if already exists

**Files to Modify:**
- `src/database/db_manager.py` - Add must-delete methods
- `src/unsubscribe/strategy_chain.py` - Call on failure

**Dependencies:**
- Existing database schema (Phase 1)
- StrategyChain (Phase 5.4)

**Test:**
1. Create test sender
2. Simulate unsubscribe failure
3. Verify sender added to unwanted_senders
4. Verify failed_unsubscribe = True
5. Verify reason stored
6. Query get_must_delete_senders()
7. Verify sender in results
8. Fail same sender again: verify reason updated
9. Verify statistics reflect must-delete count

**Confidence Rationale:**
94% confidence - Straightforward database operations using existing schema. Integration with StrategyChain is clean. Upsert logic prevents duplicates.

**Example Code:**
```python
# Add to DBManager class

def add_to_must_delete(self, sender: str, reason: str):
    """Add sender to must-delete list."""
    try:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO unwanted_senders (sender, failed_unsubscribe, failure_reason, marked_date)
                VALUES (?, 1, ?, datetime('now'))
                ON CONFLICT(sender) DO UPDATE SET
                    failed_unsubscribe = 1,
                    failure_reason = excluded.failure_reason,
                    marked_date = datetime('now')
            """, (sender, reason))
            self.logger.info(f"Added {sender} to must-delete list: {reason}")
    except Exception as e:
        self.logger.error(f"Error adding to must-delete: {e}")

def get_must_delete_senders(self) -> List[Dict]:
    """Get all senders that need manual deletion."""
    try:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sender, failure_reason, marked_date
                FROM unwanted_senders
                WHERE failed_unsubscribe = 1
                ORDER BY marked_date DESC
            """)
            return [{'sender': row[0], 'reason': row[1], 'date': row[2]}
                    for row in cursor.fetchall()]
    except Exception as e:
        self.logger.error(f"Error getting must-delete senders: {e}")
        return []

# Modify StrategyChain.execute() to add:
if not success:
    # All strategies failed - add to must-delete
    self.db.add_to_must_delete(sender, message)
```

---

### Step 6.3: Must-Delete Tab in UI

**Confidence:** 91%

**Description:**
Add a dedicated tab or section for managing senders that failed unsubscribe. This provides a clear interface for users to review and batch-delete emails from senders where automatic unsubscribe didn't work. Simple UI using existing patterns.

**Implementation Details:**
- Add "Must Delete" tab to main window (using ttk.Notebook or separate frame)
- Create `MustDeleteTable` widget (similar to SenderTable):
  - Columns: Sender, Reason, Date Added, Email Count, Select (checkbox)
  - All checked by default for convenience
  - Multi-select support
- Add "Delete Selected" button
- Load data from `db.get_must_delete_senders()`
- Clicking row shows failure reason details

**Acceptance Criteria:**
- ✅ Must Delete tab/section added to UI
- ✅ Table shows all failed unsubscribe senders
- ✅ Shows sender email, failure reason, date
- ✅ Checkboxes for selecting senders (all checked by default)
- ✅ Delete Selected button
- ✅ Refreshes after delete operations
- ✅ Shows empty state message if no must-delete senders

**Files to Modify:**
- `src/ui/main_window.py` - Add must-delete tab

**Test:**
1. Add senders to must-delete list
2. Open must-delete tab
3. Verify all senders displayed
4. Verify checkboxes all checked
5. Uncheck one sender
6. Verify selection tracking works

**Confidence Rationale:**
91% confidence - Reuses table patterns from SenderTable. Standard Tkinter widgets. Straightforward database integration.

---

### Step 6.4: Bulk Delete After Successful Unsubscribe

**Confidence:** 93% (improved from 88%)

**Description:**
Offer users the option to immediately delete all emails from a sender after successful unsubscribe. This provides a complete cleanup workflow in one action. Implemented with proper confirmation, progress tracking, and threading using existing `BackgroundTask` infrastructure.

**Implementation Details:**
- After successful unsubscribe in `unsubscribe_selected()`:
  - Show dialog: "Unsubscribe successful! Delete all emails from this sender?"
  - Show email count
  - Buttons: "Delete Emails", "Keep Emails", "Cancel"
- If "Delete Emails":
  - Create BackgroundTask
  - Create ProgressDialog
  - For each successfully unsubscribed sender:
    - Call `imap_client.delete_emails_from_sender()`
    - Update progress
  - Show summary of deleted emails
- Threading ensures UI remains responsive
- Progress shows: "Deleting emails from sender X of Y"

**Acceptance Criteria:**
- ✅ Dialog appears after successful unsubscribe
- ✅ Shows email count for each sender
- ✅ "Delete Emails" and "Keep Emails" options
- ✅ Deletion runs in background thread (using BackgroundTask)
- ✅ Progress dialog shows deletion status
- ✅ Updates UI after completion
- ✅ Summary shows total emails deleted
- ✅ Handles errors gracefully (some deletions may fail)

**Files to Modify:**
- `src/ui/main_window.py` - Add post-unsubscribe deletion option

**Dependencies:**
- `IMAPClient.delete_emails_from_sender()` (Phase 6.1)
- `BackgroundTask` (Phase 4.4)
- `ProgressDialog` (Phase 4.4)

**Test:**
1. Unsubscribe from sender
2. Verify dialog offers deletion
3. Click "Delete Emails"
4. Verify progress dialog shows
5. Verify emails deleted
6. Verify summary correct
7. Test "Keep Emails": verify emails remain

**Confidence Rationale:**
93% confidence (improved) - Uses existing threading infrastructure (BackgroundTask). IMAP deletion already implemented in 6.1. Main complexity is UI flow coordination, mitigated by clear separation of concerns and existing patterns.

---

### Step 6.5: Delete Must-Delete Button

**Confidence:** 90%

**Description:**
Provide one-click batch deletion of all must-delete senders. This completes the deletion workflow for senders where unsubscribe failed. Uses threading for responsive UI with large batches.

**Implementation Details:**
- Add "Delete All Must-Delete" button to must-delete tab
- On click:
  - Get selected senders from MustDeleteTable
  - Show confirmation dialog with:
    - Count of senders
    - Total approximate email count
    - Warning about irreversibility
  - If confirmed:
    - Create BackgroundTask
    - Create ProgressDialog
    - For each sender:
      - Call `imap_client.delete_emails_from_sender()`
      - Remove from unwanted_senders table
      - Update progress
    - Show summary dialog
    - Refresh must-delete tab

**Acceptance Criteria:**
- ✅ "Delete All Must-Delete" button in must-delete tab
- ✅ Confirmation dialog shows count and warning
- ✅ Runs in background thread
- ✅ Progress dialog shows current sender
- ✅ Deletes emails from each sender
- ✅ Removes from unwanted_senders table after deletion
- ✅ Updates statistics and UI
- ✅ Summary shows results (X senders, Y emails deleted)
- ✅ Handles partial failures gracefully

**Files to Modify:**
- `src/ui/main_window.py` - Add delete must-delete button and logic

**Dependencies:**
- `IMAPClient.delete_emails_from_sender()` (Phase 6.1)
- `BackgroundTask` (Phase 4.4)
- `ProgressDialog` (Phase 4.4)
- `DBManager.get_must_delete_senders()` (Phase 6.2)

**Test:**
1. Add 3 senders to must-delete list
2. Open must-delete tab
3. Click "Delete All Must-Delete"
4. Verify confirmation dialog
5. Click Proceed
6. Verify progress dialog
7. Verify all emails deleted
8. Verify senders removed from must-delete list
9. Verify must-delete tab now empty
10. Verify statistics updated

**Confidence Rationale:**
90% confidence - Reuses established threading patterns. IMAP deletion proven in 6.1. Database operations straightforward. Main risk is coordinating UI updates across multiple components, mitigated by clear event flow.

---

**Phase 6 Completion Criteria:**
- All 5 steps complete
- Can delete emails via IMAP
- Must-delete tracking works
- UI supports deletion workflows
- No linter errors

---

## Phase 7: Whitelist & Settings

**Goal:** Implement whitelist functionality and settings dialog

**Duration Estimate:** 2-3 hours

**Prerequisites:** Phase 6 complete

**Phase Confidence:** 94% ✅

### Step 7.1: Whitelist Management in Database

**Confidence:** 95%

**Description:**
Implement whitelist database operations supporting both individual emails and domain-level entries. Provides protection for important senders, preventing them from being marked as unwanted or having emails deleted.

**Implementation Details:**
- Add methods to `DBManager`:
  - `add_to_whitelist(entry, is_domain)` - Add email or domain
  - `remove_from_whitelist(entry)` - Remove entry
  - `check_whitelist(email) -> bool` - Check if email or its domain whitelisted
  - `get_whitelist() -> List[Dict]` - Get all whitelist entries
- Domain matching: Check if email ends with whitelisted domain (e.g., "@company.com")

**Acceptance Criteria:**
- ✅ Can add individual email addresses to whitelist
- ✅ Can add domain patterns (e.g., "@company.com")
- ✅ Can remove from whitelist
- ✅ check_whitelist() works for exact and domain matches
- ✅ Domain matching: "user@company.com" matches "@company.com"
- ✅ get_whitelist() returns all entries
- ✅ Prevents duplicate entries

**Files to Modify:**
- `src/database/db_manager.py` - Add whitelist methods

**Dependencies:**
- Existing whitelist table (Phase 1)

**Test:**
1. Add "important@example.com"
2. check_whitelist("important@example.com"): verify True
3. Add "@company.com" domain
4. check_whitelist("user@company.com"): verify True
5. Remove entry: verify works

**Confidence Rationale:**
95% confidence - Simple CRUD operations. Domain matching is straightforward string comparison. Clear requirements and test cases.

**Example Code:**
```python
def add_to_whitelist(self, entry: str, is_domain: bool = False):
    try:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if is_domain:
                cursor.execute("INSERT OR IGNORE INTO whitelist (domain) VALUES (?)", (entry,))
            else:
                cursor.execute("INSERT OR IGNORE INTO whitelist (email) VALUES (?)", (entry,))
            self.logger.info(f"Added to whitelist: {entry}")
    except Exception as e:
        self.logger.error(f"Error: {e}")

def check_whitelist(self, email: str) -> bool:
    try:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check exact match
            cursor.execute("SELECT 1 FROM whitelist WHERE email = ?", (email,))
            if cursor.fetchone():
                return True
            # Check domain match
            cursor.execute("SELECT domain FROM whitelist WHERE domain IS NOT NULL")
            for row in cursor.fetchall():
                if email.endswith(row[0]):
                    return True
            return False
    except Exception as e:
        return False
```

---

### Step 7.2: Whitelist Protection in Scoring

**Confidence:** 93%

**Description:**
Integrate whitelist into scoring and UI to visually mark and protect whitelisted senders from unwanted operations.

**Implementation Details:**
- Modify `EmailScorer`: Check whitelist, return score=-1 if whitelisted
- Modify `SenderTable`: Show green background for whitelisted (score=-1)
- Disable selection/operations for whitelisted senders

**Acceptance Criteria:**
- ✅ Whitelisted senders get score = -1
- ✅ UI shows green background for whitelisted
- ✅ Cannot select whitelisted for operations
- ✅ Delete/unsubscribe check whitelist (safety)

**Files to Modify:**
- `src/scoring/scorer.py`, `src/ui/sender_table.py`

**Test:**
1. Whitelist sender
2. Scan inbox
3. Verify green background
4. Try operations: verify excluded

**Confidence Rationale:**
93% confidence - Clear integration points. Standard UI styling. Safety checks prevent accidents.

---

### Step 7.3: Whitelist UI Tab

**Confidence:** 92%

**Description:**
Add dedicated tab for managing whitelist with add/remove functionality.

**Implementation Details:**
- Add "Whitelist" tab with table (Entry, Type, Date)
- "Add" button opens dialog (Email/Domain radio + entry field)
- "Remove" button deletes selected entry

**Acceptance Criteria:**
- ✅ Whitelist tab with table
- ✅ Add/Remove buttons
- ✅ Dialog for new entries
- ✅ Validation
- ✅ Refreshes after changes

**Files to Modify:**
- `src/ui/main_window.py`

**Test:**
1. Open whitelist tab
2. Add entry
3. Remove entry
4. Verify persistence

**Confidence Rationale:**
92% confidence - Reuses established UI patterns. Simple CRUD interface.

---

### Step 7.4: Settings Dialog - Full Implementation

**Confidence:** 90%

**Description:**
Create comprehensive settings dialog for accounts, preferences, and app info.

**Implementation Details:**
- `SettingsDialog` with tabs: Accounts, Preferences, About
- Accounts: List, add, remove
- Preferences: Batch size, timeouts
- About: Version, logs location

**Acceptance Criteria:**
- ✅ Settings menu opens dialog
- ✅ Can manage accounts
- ✅ Can configure preferences
- ✅ Settings persist
- ✅ Shows app version

**Files to Modify:**
- `src/ui/settings_dialog.py`

**Test:**
1. Open settings
2. Add account
3. Change batch size
4. Restart app
5. Verify persisted

**Confidence Rationale:**
90% confidence - Standard dialog with tabs. Config system already implemented.

---

### Step 7.5: Quick Whitelist from Table

**Confidence:** 91%

**Description:**
Add right-click context menu for quick whitelist access from sender table.

**Implementation Details:**
- Right-click handler on SenderTable
- Context menu: "Add to Whitelist"
- Calls `db.add_to_whitelist()`, refreshes table

**Acceptance Criteria:**
- ✅ Right-click shows menu
- ✅ "Add to Whitelist" option
- ✅ Immediately updates UI
- ✅ Shows confirmation

**Files to Modify:**
- `src/ui/sender_table.py`

**Test:**
1. Right-click sender
2. Click "Add to Whitelist"
3. Verify marked as whitelisted

**Confidence Rationale:**
91% confidence - Tkinter context menus well-documented. Clean integration.

---

**Phase 7 Completion Criteria:**
- All 5 steps complete
- Whitelist functionality works
- Settings dialog complete
- Can protect important senders
- No linter errors

---

## Phase 8: Enhanced Unsubscribe Strategies

**Goal:** Implement additional unsubscribe strategies and production hardening

**Duration Estimate:** 3-4 hours

**Prerequisites:** Phase 7 complete

**Phase Confidence:** 93% ✅

**Note:** Browser automation strategies (Selenium-based) have been deferred to post-MVP due to complexity and fragility (see Future Enhancements). This phase focuses on reliable, production-ready strategies.

### Step 8.1: Mailto Strategy

**Confidence:** 93%

**Description:**
Implement email-based unsubscribe handling for List-Unsubscribe mailto: links. This strategy sends unsubscribe requests via SMTP when the email provider supports RFC 2369 mailto: unsubscribe links. It's reliable and standards-compliant.

**Implementation Details:**
- Create `MailtoStrategy` class inheriting from `UnsubscribeStrategy`
- Implement `can_handle(self, email_data: Dict) -> bool`:
  - Check if List-Unsubscribe header contains mailto: link
  - Parse the mailto: URL to validate format
  - Return True if valid mailto: link exists
- Implement `execute(self, email_data: Dict) -> Tuple[bool, str]`:
  - Parse mailto: URL for: recipient, subject, body
  - Use smtplib to send email via user's SMTP server
  - Gmail: smtp.gmail.com:587, Outlook: smtp.office365.com:587
  - Use existing account credentials from database
  - Log as "pending_verification" (human must check it worked)
  - Return (True, "Unsubscribe email sent")
- Error handling: catch SMTP errors, connection timeouts
- Use TLS for security

**Acceptance Criteria:**
- ✅ Can detect mailto: links in List-Unsubscribe header
- ✅ Parses mailto: URL correctly (recipient, subject, body)
- ✅ Sends email via SMTP using existing account credentials
- ✅ Uses TLS encryption for SMTP connection
- ✅ Logs action as "pending_verification"
- ✅ Handles SMTP errors gracefully
- ✅ Returns descriptive success/failure messages

**Files to Create:**
- `src/unsubscribe/mailto_strategy.py` - Email-based unsubscribe strategy

**Dependencies:**
- `smtplib` (built-in)
- `email.utils` (built-in, for parsing mailto:)
- `urllib.parse` (built-in, for URL parsing)

**Test:**
1. Find email with List-Unsubscribe mailto: link
2. Parse link: `strategy.can_handle(email_data)`
3. Verify returns True
4. Execute: `success, msg = strategy.execute(email_data)`
5. Verify email sent to correct recipient
6. Check database logs show "pending_verification"
7. Test with malformed mailto: link
8. Test SMTP error handling

**Confidence Rationale:**
93% confidence - SMTP is well-documented with straightforward Python support. mailto: URL parsing is standard. Using existing account credentials simplifies authentication. Minor risk around different SMTP server configurations, but Gmail/Outlook are well-documented.

**Example Code:**
```python
import smtplib
from email.mime.text import MIMEText
from urllib.parse import urlparse, parse_qs
from typing import Dict, Tuple

class MailtoStrategy(UnsubscribeStrategy):
    def can_handle(self, email_data: Dict) -> bool:
        """Check if email has mailto: unsubscribe link."""
        unsub_header = email_data.get('list_unsubscribe', '')
        return 'mailto:' in unsub_header.lower()
    
    def execute(self, email_data: Dict) -> Tuple[bool, str]:
        """Send unsubscribe email via SMTP."""
        try:
            # Parse mailto: link
            mailto_link = self._extract_mailto(email_data['list_unsubscribe'])
            recipient, subject, body = self._parse_mailto(mailto_link)
            
            # Send email via SMTP
            msg = MIMEText(body)
            msg['To'] = recipient
            msg['From'] = self.account_email
            msg['Subject'] = subject
            
            with smtplib.SMTP(self.smtp_server, 587) as server:
                server.starttls()
                server.login(self.account_email, self.account_password)
                server.send_message(msg)
            
            return (True, f"Unsubscribe email sent to {recipient}")
        except Exception as e:
            return (False, f"Failed to send email: {str(e)}")
```

---

### Step 8.2: Enhanced HTTP Strategy with Retries

**Confidence:** 92%

**Description:**
Enhance the existing HTTP strategy (from Phase 5) with retry logic, better error handling, and email address parameter injection. Many unsubscribe links require passing the email address as a query parameter or POST data.

**Implementation Details:**
- Modify `HTTPStrategy` class to add retry logic:
  - Implement `_make_request_with_retry(url, method='GET', max_retries=3)`
  - Exponential backoff: 2s, 4s, 8s between retries
  - Retry on: 5xx errors, connection timeouts, connection errors
  - Don't retry on: 4xx errors (except 429), successful responses
- Add email address injection:
  - Check URL for common parameters: `email`, `e`, `address`, `unsubscribe_email`
  - If parameter exists (e.g., `?email={EMAIL_ADDRESS}`), replace placeholder
  - Otherwise, try adding `?email=user@example.com` to URL
- Add POST data support:
  - Try POST with form data: `{'email': user@example.com}`
  - Try POST with JSON: `{"email": "user@example.com"}`
- Improve success detection:
  - Check for success keywords in response: "success", "unsubscribed", "removed"
  - Check HTTP status codes: 200, 201, 204 = likely success
  - Log full response for human verification
- Add user-agent rotation (3-5 common user agents)

**Acceptance Criteria:**
- ✅ Implements retry logic with exponential backoff
- ✅ Retries on 5xx errors and timeouts (up to 3 attempts)
- ✅ Injects email address into URL parameters when placeholders found
- ✅ Tries POST with form data if GET fails
- ✅ Detects success from response content or status codes
- ✅ Rotates user-agent strings to avoid bot detection
- ✅ Logs full response for verification
- ✅ Handles all HTTP errors gracefully

**Files to Modify:**
- `src/unsubscribe/http_strategy.py` - Enhance existing HTTP strategy

**Dependencies:**
- `requests` (already in requirements.txt)
- `time` (built-in, for delays)
- `random` (built-in, for backoff jitter)

**Test:**
1. Test retry on 503 error (mock or use test endpoint)
2. Verify 3 retries with increasing delays
3. Test URL with `{EMAIL_ADDRESS}` placeholder
4. Verify email is correctly injected
5. Test POST fallback when GET returns 405
6. Verify success detection from response body
7. Test with various HTTP status codes
8. Verify user-agent rotation

**Confidence Rationale:**
92% confidence - Building on existing HTTP strategy. Retry logic and exponential backoff are standard patterns. Email injection is string manipulation. Minor risk around diverse unsubscribe link formats, but the approach covers common cases.

---

### Step 8.3: Unsubscribe Result Analytics

**Confidence:** 94%

**Description:**
Add analytics tracking to understand which strategies work best and identify problematic senders. This data helps improve the unsubscribe process over time and provides insights to users.

**Implementation Details:**
- Extend `action_history` table queries in DBManager:
  - Add `get_strategy_stats() -> Dict`: Count successes/failures per strategy
  - Add `get_failure_reasons() -> List[Dict]`: Common failure patterns
  - Add `get_success_rate() -> float`: Overall success percentage
- Create `UnsubscribeAnalytics` class:
  - `generate_report() -> Dict`: Summary of all unsubscribe attempts
  - `get_top_failures() -> List[str]`: Senders with most failures
  - `get_strategy_effectiveness() -> Dict`: Win rate per strategy
- Add to main window UI:
  - "View Analytics" button
  - Dialog showing: success rate, strategy breakdown, common failures
  - Export to CSV option

**Acceptance Criteria:**
- ✅ Can query strategy success/failure stats from database
- ✅ Can calculate overall success rate
- ✅ Can identify most problematic senders
- ✅ Can show strategy effectiveness breakdown
- ✅ Analytics dialog displays in UI
- ✅ Can export analytics to CSV file
- ✅ Updates in real-time as unsubscribes execute

**Files to Create:**
- `src/scoring/analytics.py` - Analytics calculation class

**Files to Modify:**
- `src/database/db_manager.py` - Add analytics queries
- `src/ui/main_window.py` - Add analytics dialog

**Dependencies:**
- `csv` (built-in, for export)
- `collections` (built-in, for Counter)

**Test:**
1. Run several unsubscribes with mixed success/failure
2. Call `get_strategy_stats()`
3. Verify counts are accurate
4. Calculate success rate
5. Open analytics dialog in UI
6. Verify data displays correctly
7. Export to CSV
8. Verify CSV format is correct

**Confidence Rationale:**
94% confidence - Database queries are straightforward extensions of existing code. Analytics calculations are simple aggregations. UI dialog follows established patterns. Export to CSV is well-documented.

---

### Step 8.4: Rate Limiting & Delays

**Confidence:** 91% (improved from 88%)

**Description:**
Implement comprehensive rate limiting to prevent abuse, respect server limits, and avoid being flagged as a bot. Uses threading.Semaphore for concurrency control and exponential backoff for 429 responses.

**Implementation Details:**
- Create `RateLimiter` class:
  - `__init__(self, max_concurrent=3, min_delay=2, max_delay=5)`
  - Use `threading.Semaphore(max_concurrent)` to limit concurrent operations
  - Implement `@contextmanager def acquire()`: Acquire semaphore, add delay, release
  - Random delay between `min_delay` and `max_delay` seconds
  - Add jitter to avoid thundering herd
- Implement 429 (Too Many Requests) handling:
  - Parse Retry-After header if present
  - If no header, use exponential backoff: 30s, 60s, 120s, 240s
  - Log rate limit hits
  - Option to pause all operations temporarily
- Integrate with strategy chain:
  - Wrap each strategy execution in rate limiter
  - Update progress UI with delay status ("Rate limiting: waiting 3s...")
  - Allow user to configure delays in settings
- Domain-specific rate limiting (optional):
  - Track requests per domain
  - Different limits for different domains

**Acceptance Criteria:**
- ✅ Limits concurrent unsubscribe operations (max 3 by default)
- ✅ Adds randomized 2-5 second delay between requests
- ✅ Respects 429 Too Many Requests responses
- ✅ Implements exponential backoff on repeated 429s
- ✅ Parses and respects Retry-After header
- ✅ Updates UI with rate limiting status
- ✅ User can configure delays in settings
- ✅ Thread-safe (uses threading.Semaphore)

**Files to Create:**
- `src/unsubscribe/rate_limiter.py` - Rate limiting implementation

**Files to Modify:**
- `src/unsubscribe/strategy_chain.py` - Integrate rate limiter
- `src/ui/settings_dialog.py` - Add rate limit settings

**Dependencies:**
- `threading` (built-in)
- `time` (built-in)
- `random` (built-in)
- `contextlib` (built-in, for contextmanager)

**Test:**
1. Create RateLimiter with max_concurrent=2
2. Start 5 operations simultaneously
3. Verify only 2 run concurrently
4. Verify delays between operations
5. Mock 429 response
6. Verify exponential backoff applied
7. Test Retry-After header parsing
8. Verify thread safety with concurrent access
9. Update settings and verify new limits applied

**Confidence Rationale:**
91% confidence (improved from 88%) - Semaphore-based concurrency control is standard and well-documented. Exponential backoff is a proven pattern. Integration with strategy chain is straightforward. Minor risk around edge cases in threading and timing, but testing will catch these.

**Example Code:**
```python
import threading
import time
import random
from contextlib import contextmanager
import logging

class RateLimiter:
    """Rate limiter with concurrency control and delays."""
    
    def __init__(self, max_concurrent=3, min_delay=2, max_delay=5):
        self.semaphore = threading.Semaphore(max_concurrent)
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.logger = logging.getLogger(__name__)
        self.last_request_time = 0
        self.lock = threading.Lock()
    
    @contextmanager
    def acquire(self):
        """Acquire rate limiter, add delay, then release."""
        self.semaphore.acquire()
        try:
            # Add delay since last request
            with self.lock:
                now = time.time()
                elapsed = now - self.last_request_time
                delay = random.uniform(self.min_delay, self.max_delay)
                if elapsed < delay:
                    sleep_time = delay - elapsed
                    self.logger.debug(f"Rate limiting: sleeping {sleep_time:.1f}s")
                    time.sleep(sleep_time)
                self.last_request_time = time.time()
            yield
        finally:
            self.semaphore.release()
    
    def handle_429(self, retry_after=None):
        """Handle 429 Too Many Requests response."""
        if retry_after:
            wait_time = int(retry_after)
        else:
            wait_time = 30  # Default 30 seconds
        
        self.logger.warning(f"Rate limited (429). Waiting {wait_time}s")
        time.sleep(wait_time)
```

---

### Step 8.5: Logging & Error Recovery

**Confidence:** 94%

**Description:**
Enhance logging throughout the unsubscribe process and implement error recovery mechanisms. This ensures failures are debuggable and the system can recover from transient errors gracefully.

**Implementation Details:**
- Enhance logging in all strategies:
  - Log attempt start: strategy name, sender, timestamp
  - Log HTTP requests: method, URL, status code, response time
  - Log decisions: why strategy was chosen, why it failed/succeeded
  - Log full stack traces on unexpected errors
  - Use structured logging (JSON format for easy parsing)
- Implement error recovery:
  - Add `mark_for_retry(sender, reason)` to database
  - Create "Retry Failed" button in UI
  - Implement `retry_failed_unsubscribes()` function
  - Skip senders that failed 3+ times (move to must-delete)
  - Option to manually mark sender as "needs human intervention"
- Add error categorization:
  - Network errors (can retry)
  - Authentication errors (needs user action)
  - Invalid link errors (can't fix)
  - Rate limiting (retry with backoff)
  - Unknown errors (log for investigation)
- Create error report export:
  - Export failed unsubscribes with full details to JSON/CSV
  - Helps with troubleshooting and pattern identification

**Acceptance Criteria:**
- ✅ All strategies log detailed attempt information
- ✅ HTTP requests logged with full details
- ✅ Stack traces logged on unexpected errors
- ✅ Failed attempts can be marked for retry
- ✅ "Retry Failed" button in UI works
- ✅ Senders with 3+ failures moved to must-delete
- ✅ Errors categorized by type
- ✅ Can export error report to JSON/CSV
- ✅ Structured logging for easy parsing

**Files to Modify:**
- `src/unsubscribe/strategy_base.py` - Add detailed logging
- `src/unsubscribe/list_unsubscribe.py` - Enhance logging
- `src/unsubscribe/http_strategy.py` - Enhance logging
- `src/unsubscribe/mailto_strategy.py` - Enhance logging
- `src/database/db_manager.py` - Add retry tracking
- `src/ui/main_window.py` - Add retry button

**Dependencies:**
- `json` (built-in, for structured logging)
- `traceback` (built-in, for stack traces)
- `datetime` (built-in, for timestamps)

**Test:**
1. Trigger a successful unsubscribe
2. Verify detailed logs in log file
3. Trigger a failed unsubscribe
4. Verify error logged with full details
5. Mark sender for retry
6. Click "Retry Failed" button
7. Verify retry attempted
8. Fail same sender 3 times
9. Verify moved to must-delete
10. Export error report
11. Verify JSON/CSV format correct

**Confidence Rationale:**
94% confidence - Logging enhancements are straightforward. Retry logic builds on existing database operations. Error categorization is simple conditional logic. Export functionality follows established patterns. High confidence because this is mostly extending existing functionality.

---

**Phase 8 Completion Criteria:**
- All 5 steps complete
- Mailto strategy works reliably
- HTTP strategy enhanced with retries and email injection
- Analytics provide useful insights
- Rate limiting prevents abuse
- Comprehensive logging and error recovery
- No linter errors

**Deferred to Post-MVP (Future Enhancements):**
- Step 8.1 (Browser): Browser Strategy 3 - Simple Click (78% confidence)
- Step 8.2 (Browser): Browser Strategy 4 - Form Fill (72% confidence)
- Reason: Selenium-based strategies are fragile, have many edge cases, and require significant testing across diverse website structures. MVP focuses on reliable, proven strategies.

---

## Phase 9: Polish & Distribution

**Goal:** Final touches, packaging, and distribution

**Duration Estimate:** 2-3 hours

**Prerequisites:** Phase 8 complete

**Phase Confidence:** 92% ✅

### Step 9.1: Error Handling & User Feedback

**Confidence:** 94%

**Description:**
Polish all error messages to be user-friendly with actionable guidance. Hide technical details while logging comprehensively for debugging.

**Implementation Details:**
- Audit all exception handlers
- Replace technical messages with friendly ones
- Add helpful next steps
- Log full technical details separately

**Acceptance Criteria:**
- ✅ All error messages user-friendly
- ✅ Connection errors show helpful guidance
- ✅ Invalid credentials give clear next steps
- ✅ No stack traces shown to users
- ✅ All exceptions caught and logged

**Files to Modify:**
- All existing files (add friendly error handling)

**Test:** Trigger various errors, verify helpful messages shown

**Confidence Rationale:**
94% confidence - Straightforward message replacement following clear guidelines.

---

### Step 9.2: Score Explanation Tooltips

**Confidence:** 91%

**Description:**
Add tooltips to scores showing breakdown for transparency.

**Implementation Details:**
- Store breakdown from `calculate_score()`
- Add hover tooltips to score column
- Format: "Score 8 = 1 (unread) + 4 (frequency) + 1 (unsub) + 5 (hist)"

**Acceptance Criteria:**
- ✅ Hover over score shows breakdown
- ✅ Tooltip format clear
- ✅ Shows all components
- ✅ Makes scoring transparent

**Files to Modify:**
- `src/ui/sender_table.py`

**Test:** Hover over scores, verify tooltips display correctly

**Confidence Rationale:**
91% confidence - Tkinter tooltips straightforward. Breakdown already calculated.

---

### Step 9.3: Help & Documentation

**Confidence:** 95%

**Description:**
Create comprehensive help resources and documentation for users.

**Implementation Details:**
- Help menu: About dialog, App Password links (Gmail/Outlook), View Logs
- `README.md`: Features, installation, setup guide, usage, troubleshooting, FAQ

**Acceptance Criteria:**
- ✅ Help menu -> "About" dialog with app info
- ✅ Help menu -> "Generate App Password" with links to Google/Microsoft
- ✅ README.md file with installation instructions
- ✅ User guide section in README

**Files to Create:**
- `README.md`

**Files to Modify:**
- `src/ui/main_window.py` (help menu)

**Test:** Open help dialogs, verify information is accurate

**Confidence Rationale:**
95% confidence - Documentation writing straightforward. Help dialogs simple messagebox calls. No technical complexity.

---

### Step 9.4: PyInstaller Build Script

**Confidence:** 92% (improved from 85%)

**Description:**
Package application as standalone Windows executable using PyInstaller.

**Implementation Details:**
- `build.spec`: bundle dependencies, schema.sql, icon; one-file mode
- `build.bat` script for easy building
- Test on clean Windows machine without Python

**Acceptance Criteria:**
- ✅ Build script creates standalone .exe
- ✅ All dependencies bundled
- ✅ Database and logs stored in AppData
- ✅ .exe is 50-80MB
- ✅ Runs without Python installation

**Files to Create:**
- `build.bat` (Windows build script)
- `build.spec` (PyInstaller spec file)

**Test:** Build .exe, run on machine without Python, verify it works

**Confidence Rationale:**
92% confidence (improved) - PyInstaller mature for Python/Tkinter apps. One-file mode simplifies distribution. Data file inclusion well-documented. Comprehensive testing plan mitigates hidden dependency risks.

---

### Step 9.5: Final Testing & Release

**Confidence:** 90%

**Description:**
Comprehensive end-to-end testing with real accounts validates production-readiness.

**Implementation Details:**
- Test with real Gmail and Outlook accounts  
- Full workflow testing: scan → unsubscribe → delete
- Performance testing (1000+ emails <2 min)
- Linter validation (flake8/pylint)
- Memory monitoring (<500MB)
- Crash recovery testing
- Clean system testing

**Acceptance Criteria:**
- ✅ Test with real Gmail account (scan, unsubscribe, delete)
- ✅ Test with real Hotmail account
- ✅ Test all workflows end-to-end
- ✅ No crashes or unhandled errors
- ✅ Performance is acceptable (10,000 emails in < 1 minute)
- ✅ Create GitHub release with .exe

**Files to Create:**
- `CHANGELOG.md`

**Test:** Full end-to-end testing with real accounts

**Confidence Rationale:**
90% confidence - Testing inherently may reveal issues, but systematic approach with clear acceptance criteria and comprehensive test plan validates production-readiness. Performance benchmarks provide measurable quality gates.

---

**Phase 9 Completion Criteria:**
- All 5 steps complete
- Application is polished and user-friendly
- .exe builds correctly
- Ready for distribution
- No linter errors

---

## Overall Progress Tracking

- [x] Phase 1: Foundation & Database (5 steps) ✅
- [x] Phase 2: Email Client & Credentials (5 steps) ✅
- [x] Phase 3: Scoring & Grouping (5 steps) ✅
- [x] Phase 4: User Interface - Basic Window (5 steps) ✅
- [x] Phase 5: Unsubscribe Strategies (Core) (5 steps) ✅
- [x] Phase 6: Email Deletion & Must-Delete List (5 steps) ✅
- [x] Phase 7: Whitelist & Settings (5 steps) ✅
- [x] Phase 8: Enhanced Unsubscribe Strategies (5 steps) ✅
- [ ] Phase 9: Polish & Distribution (5 steps)

**Total Steps:** 45
**Estimated Total Time:** 22-30 hours

---

## Future Enhancements (Post-MVP)

These features are not in the MVP build plan but can be added later:

### Deferred from Phase 8 (Browser Automation)

**Browser Strategy 3 - Simple Click (78% confidence):**
- Opens URL in headless Chrome/Selenium
- Looks for button/link with "unsubscribe" text
- Clicks button and waits for confirmation
- **Reason for deferral:** Fragile, requires extensive testing across varied page structures
- **Requirements before implementation:**
  - Research spike: test with 50+ real unsubscribe pages
  - Document common page patterns
  - Create robust element detection strategies
  - Handle CAPTCHAs and anti-bot measures

**Browser Strategy 4 - Form Fill (72% confidence):**
- Opens URL in browser
- Detects and fills form fields (email address, dropdowns)
- Handles multi-step unsubscribe processes
- **Reason for deferral:** Very complex, many unknowns, high failure rate
- **Requirements before implementation:**
  - Complete Browser Strategy 3 first
  - Research form detection patterns
  - Handle diverse form structures
  - Test with 25+ form-based unsubscribe flows

### Additional Features

- OAuth2 authentication support
- Configurable scoring weights
- Additional scoring factors (keywords, age)
- Import whitelist from contacts
- Regex pattern support for whitelist
- Automated testing suite (unit tests for all modules)
- Cross-platform builds (Mac, Linux)
- Auto-update functionality
- Multiple language support (i18n)
- Export/import settings
- Email preview in UI
- Scheduled scans (daily/weekly automation)
- Enhanced statistics dashboard
- Unsubscribe success prediction (ML-based)
- Batch operations across multiple accounts
- Cloud sync for whitelist/settings

