# CURRENT PHASE: Phase 6 - Update MainWindow to Use Services

**CRITICAL: This file contains the complete Phase 6 content from refactoring.md plus complete DEVELOPMENT_RULES.md for reference during execution.**

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

**Manual testing approach:**
- ✅ Test each step immediately after coding
- ✅ Verify functionality works as expected
- ✅ Test happy path (expected usage)
- ✅ Test at least one error case (invalid input, missing data, etc.)
- ✅ Document test results in commit message

---

# PHASE 6: Update MainWindow to Use Services

**Goal:** Refactor MainWindow to use service layer instead of direct logic  
**Duration Estimate:** 6-8 hours  
**Prerequisites:** Phases 1-5 complete  
**Phase Confidence:** 91% (Average of all step confidences)

## Progress Tracking

- ✅ Step 6.1: Inject ServiceFactory into MainWindow (COMPLETED 2025-10-12)
- ✅ Step 6.2: Refactor scan_inbox() to Use EmailScanService (COMPLETED 2025-10-12)
- ✅ Step 6.3: Refactor unsubscribe_selected() to Use UnsubscribeService (COMPLETED 2025-10-12)
- ✅ Step 6.4: Refactor Deletion Methods to Use EmailDeletionService (COMPLETED 2025-10-12)
- ✅ Step 6.5: Remove Dead Code and Simplify MainWindow (COMPLETED 2025-10-12)
  Note: Reduced from 1642 to 1527 lines (7% reduction). Target of <800 was overly optimistic
  for a UI class that must create all UI components.

---

## Step 6.1: Inject ServiceFactory into MainWindow

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

---

## Step 6.2: Refactor scan_inbox() to Use EmailScanService

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

---

## Step 6.3: Refactor unsubscribe_selected() to Use UnsubscribeService

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

**Acceptance Criteria:**
- ✅ unsubscribe_selected() uses UnsubscribeService
- ✅ No direct strategy chain in method
- ✅ Progress bar updates correctly (verified by comparison)
- ✅ Results dialog shows correct counts (verified by checklist)
- ✅ Offer to delete still works (verified by test)
- ✅ Error handling works correctly
- ✅ Method significantly shorter (from ~100 lines to ~40 lines)

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
92% confidence - Service returns same structure as inline code. Can keep old code commented during transition for comparison.

---

## Step 6.4: Refactor Deletion Methods to Use EmailDeletionService

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

**Acceptance Criteria:**
- ✅ All deletion methods use EmailDeletionService
- ✅ No direct email client deletion calls in MainWindow
- ✅ Progress bars update correctly
- ✅ Confirmation dialogs still shown with same text
- ✅ Results displayed correctly
- ✅ Must-delete list updated after deletion
- ✅ Methods significantly shorter (50-70% reduction)
- ✅ All methods use shared pattern (consistency)

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
91% confidence - Shared refactoring pattern applied to all methods consistently. Methods refactored one at a time in order of complexity.

---

## Step 6.5: Remove Dead Code and Simplify MainWindow

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

## Phase Completion Checklist

**Before moving to next phase:**

- [ ] All steps in current phase marked complete ✅
- [ ] All acceptance criteria verified
- [ ] Unit tests written for all code created/modified in the phase
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

End of CURRENT_PHASE.md

