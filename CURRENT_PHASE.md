# CURRENT PHASE: Phase 3 - Extract Service Layer from MainWindow

This document contains the complete development rules and the current phase details for execution.

---

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

---

## Part B: Executing a Build Plan

These rules apply when executing a build plan that has been validated per Part A.

---

## Rule 1: Step Progression

**When you CAN proceed to next step:**
- ✅ Current step's acceptance criteria are fully met
- ✅ All files specified in "Files to Create/Modify" have been created/modified
- ✅ Tests specified in the "Test" section have passed
- ✅ Code has been committed to git

**When you CANNOT proceed:**
- ❌ Acceptance criteria not met
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
- ✅ Test that the step works before marking complete
- ✅ Commit to git after step completion with descriptive message
- ✅ Update CURRENT_PHASE.md to mark step as complete (add ✅)

**Commit message format:**
```
Phase X, Step X.X: [Brief description]

- Acceptance criteria met:
  - [List what was achieved]
- Files modified: [List files]
- Test results: [Brief test outcome]
```

---

## Rule 3: Stopping Conditions

**MUST STOP immediately if:**
- ⛔ Linter errors are introduced (must fix before proceeding)
- ⛔ Import statements fail (missing dependencies must be resolved)
- ⛔ Unhandled exceptions occur during testing
- ⛔ Acceptance criteria cannot be met (must revise plan or step)
- ⛔ Git commit fails (must resolve conflicts or issues)

**When stopped:**
1. Document the issue in CURRENT_PHASE.md
2. Fix the blocking issue
3. Re-test to ensure issue is resolved
4. Only then proceed with next step

---

## Rule 4: Phase Execution Workflow

**Starting a new phase:**
1. ⛔ **CRITICAL: Copy the COMPLETE phase content from BUILD_PLAN.md**
2. ⛔ **CRITICAL: Copy the ENTIRE DEVELOPMENT_RULES.md file**
3. ✅ Create CURRENT_PHASE.md with both complete contents
4. ✅ Work exclusively with CURRENT_PHASE.md during phase execution

**During phase execution:**
1. ✅ Update CURRENT_PHASE.md to mark completed steps with ✅
2. ✅ Add notes about challenges or decisions made
3. ✅ Keep CURRENT_PHASE.md as the single source of truth for progress

**Completing a phase:**
1. ✅ Verify all steps in phase are marked complete
2. ✅ Run integration test across all phase components
3. ✅ Commit all phase changes with message: "Phase X complete: [Phase name]"
4. ✅ Update BUILD_PLAN.md to mark phase complete with ✅
5. ⛔ **CRITICAL: Delete CURRENT_PHASE.md** after all files are committed

---

## Rule 5: Testing Requirements

**Manual testing approach:**
- ✅ Test each step immediately after coding
- ✅ Verify functionality works as expected
- ✅ Test happy path (expected usage)
- ✅ Test at least one error case (invalid input, missing data, etc.)
- ✅ Document test results in commit message

---

## Rule 6: Code Quality Standards

**Code style:**
- ✅ Follow language-specific style guide (PEP 8 for Python, etc.)
- ✅ Use consistent naming conventions
- ✅ Use meaningful variable and function names
- ✅ Keep functions small (< 50 lines preferred, < 100 lines max)
- ✅ Single responsibility principle (one function = one purpose)

**Documentation:**
- ✅ Add docstrings to classes and public methods
- ✅ Document complex algorithms or business logic
- ✅ Add inline comments for non-obvious code
- ✅ Keep comments up-to-date with code changes

**Type hints (language-dependent):**
- ✅ Use type hints where they add clarity
- ✅ Required for function parameters and return values (when not obvious)

**Error handling:**
- ✅ Catch specific exceptions, not generic Exception
- ✅ Provide meaningful error messages
- ✅ Log errors appropriately
- ✅ Clean up resources (use context managers when possible)

---

## Rule 7: File Organization

**File creation:**
- ✅ Create files exactly as specified in project structure
- ✅ Use specified file names (consistency matters)
- ✅ Create files in specified directories
- ✅ Create necessary __init__.py files (for Python packages)

---

## Rule 8: Git Workflow

**Commits:**
- ✅ Commit after each completed step
- ✅ Use descriptive commit messages (see Rule 2 for format)
- ✅ Commit only working code (code that compiles/runs)
- ✅ Don't commit commented-out code (delete it, git remembers)

---

## Rule 9: Progress Tracking

**In CURRENT_PHASE.md:**
- ✅ Mark completed steps with ✅
- ✅ Mark current step with 🔄
- ✅ Leave incomplete steps with ❌ or blank
- ✅ Add notes about challenges or decisions

---

---

# PHASE 3: Extract Service Layer from MainWindow

**Goal:** Extract business logic from UI into testable service classes  
**Duration Estimate:** 8-12 hours  
**Prerequisites:** Phase 2 complete  
**Phase Confidence:** 91% (Average of all step confidences)

**Phase Progress:**
- ✅ Step 3.1: Create EmailScanService
- ✅ Step 3.2: Create UnsubscribeService
- 🔄 Step 3.3: Create EmailDeletionService
- ❌ Step 3.4: Create ServiceFactory

---

## Step 3.1: Create EmailScanService

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

---

## Step 3.2: Create UnsubscribeService

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

---

## Step 3.3: Create EmailDeletionService

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
- ❌ EmailDeletionService class created
- ❌ Can delete emails from multiple senders
- ❌ Returns detailed results dictionary
- ❌ Checks whitelist before deletion (safety)
- ❌ Removes from must-delete list after successful deletion
- ❌ Progress callback called for each sender
- ❌ Handles senders with no emails gracefully
- ❌ Can be cancelled mid-operation

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

---

## Step 3.4: Create ServiceFactory

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
- ❌ ServiceFactory class created
- ❌ Can create EmailScanService with all dependencies
- ❌ Can create UnsubscribeService with dependencies
- ❌ Can create EmailDeletionService with dependencies
- ❌ Services share same db_manager instance
- ❌ Services share same email_client instance
- ❌ Created services cached (same instance on repeated calls)
- ❌ Can update email client for all services

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

## Phase Completion Notes

(Notes will be added as phase progresses)

