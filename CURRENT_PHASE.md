# CURRENT PHASE: Phase 4 - Refactor Email Clients for Dependency Injection

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

**Commit message format:**
```
Phase X, Step X.X: [Brief description]

- Acceptance criteria met:
  - [List what was achieved]
- Files modified: [List files]
- Unit tests: [Created/updated test file(s)]
- Test results: [Brief test outcome - unit tests + manual tests]
```

## Rule 3: Stopping Conditions

**MUST STOP immediately if:**
- ⛔ Unit tests not written for code created/modified in current step
- ⛔ Linter errors are introduced (must fix before proceeding)
- ⛔ Import statements fail (missing dependencies must be resolved)
- ⛔ Unhandled exceptions occur during testing
- ⛔ Acceptance criteria cannot be met (must revise plan or step)
- ⛔ Git commit fails (must resolve conflicts or issues)

## Rule 5: Testing Requirements

**⛔ CRITICAL RULE: Unit Tests Must Be Written in the Same Step**
- **ALWAYS write unit tests for any code created or modified in a step**
- **NEVER defer unit testing to later steps or phases**
- This applies to ALL code: services, repositories, utilities, parsers, etc.
- Unit tests MUST be in the same commit as the code they test

**Unit test requirements:**
- ✅ Write tests in `tests/unit/` directory matching the source structure
- ✅ Test file naming: `test_<module_name>.py`
- ✅ Use pytest framework (or project's standard framework)
- ✅ Achieve reasonable coverage (aim for >80% of new/modified code)
- ✅ Include both success and failure cases
- ✅ Mock external dependencies (databases, APIs, file systems)
- ✅ Tests must be fast (< 1 second per test preferred)

---

# Phase 4: Refactor Email Clients for Dependency Injection

**Goal:** Improve email client architecture for testability  
**Duration Estimate:** 4-6 hours  
**Prerequisites:** Phase 3 complete  
**Phase Confidence:** 92% (Average of all step confidences)

## Phase Progress
- ✅ Step 4.1: Extract Connection Manager - COMPLETED
- ❌ Step 4.2: Create Email Client Interface

---

## Step 4.1: Extract Connection Manager ✅

**Completion Date:** 2025-10-12
**Notes:** Successfully extracted connection managers for both IMAP and Gmail. All 38 unit tests passing. Backward compatibility maintained.

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

---

## Step 4.2: Create Email Client Interface

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

## Phase Completion Checklist

**Before moving to next phase:**

- [ ] All steps in current phase marked complete ✅
- [ ] All acceptance criteria verified
- [ ] **Unit tests written for all code created/modified in the phase**
- [ ] All unit tests passing
- [ ] All manual tests passing
- [ ] No linter errors or warnings
- [ ] All files committed to git
- [ ] Integration test passed (components work together)
- [ ] CURRENT_PHASE.md notes reviewed
- [ ] refactoring.md updated with phase completion
- [ ] CURRENT_PHASE.md deleted
- [ ] Ready to start next phase with clean slate

---

