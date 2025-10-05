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

### Confidence Scoring Factors

**Increase confidence (+):**
- ✅ Clear, specific acceptance criteria
- ✅ Well-documented libraries/frameworks
- ✅ Similar code examples available
- ✅ Team has prior experience with technology
- ✅ Simple, single-purpose functionality
- ✅ No external service dependencies
- ✅ Standard design patterns apply

**Decrease confidence (-):**
- ❌ Vague or ambiguous requirements
- ❌ Experimental or poorly documented technology
- ❌ No examples or reference implementations
- ❌ Complex multi-step process
- ❌ Relies on external APIs or services
- ❌ Browser automation or JavaScript handling
- ❌ Security-critical functionality
- ❌ Performance-critical functionality
- ❌ Cross-platform compatibility required

### Composite Phase Confidence

**Calculation:**
```
Phase Confidence = Average of all step confidences in the phase
```

**Example:**
```
Phase 2: Email Client
- Step 2.1: Credential Encryption (95%)
- Step 2.2: IMAP Connection (92%)
- Step 2.3: Fetch Emails (88%)  ⚠️
- Step 2.4: Email Parser (93%)
- Step 2.5: Account Management (94%)

Phase Confidence = (95 + 92 + 88 + 93 + 94) / 5 = 92.4% ✅ CAN EXECUTE

Note: Step 2.3 has <90% confidence but phase is >90%.
Action: Either revise Step 2.3 or accept the risk at phase level.
```

### Handling Low Confidence Steps/Phases

**If step confidence < 90%:**

1. **Break it down** - Split into smaller, clearer steps
   ```
   Step 2.3: Fetch Emails (88%) 
   
   Becomes:
   Step 2.3a: Fetch email count (95%)
   Step 2.3b: Fetch email headers only (93%)
   Step 2.3c: Fetch email bodies (91%)
   ```

2. **Clarify requirements** - Add more specific acceptance criteria
   ```
   Before: "Can fetch emails" (vague)
   After: "Can fetch emails in batches of 500, excluding attachments,
           with timeout handling and error recovery"
   ```

3. **Add research step** - Create a spike/research step before the actual implementation
   ```
   Step 2.2a: Research IMAP SSL/TLS connection methods (95%)
   Step 2.2b: Implement IMAP connection (now 93%)
   ```

4. **Defer to later phase** - Move risky steps to Phase N+1 after gaining more knowledge
   ```
   Move from Phase 2 to Phase 8 (after core functionality proven)
   ```

**If phase confidence < 90%:**
- ⛔ STOP - Do not begin the phase
- ✅ Revise the phase by applying above strategies to low-confidence steps
- ✅ Consider splitting phase into two phases
- ✅ Move high-risk steps to later phase
- ✅ Recalculate phase confidence after revisions
- ✅ Only begin phase when confidence ≥ 90%

### Build Plan Template with Confidence

**Each step MUST include enough detail for an LLM to implement without ambiguity.**

```markdown
## Phase X: [Phase Name]

**Goal:** [What this phase achieves]
**Duration Estimate:** [Time estimate]
**Prerequisites:** [What must be complete before this phase]
**Phase Confidence:** XX% [Average of all step confidences]

### Step X.1: [Step Name]

**Confidence:** XX%

**Description:**
[2-4 sentences explaining what this step accomplishes and why it's needed]

**Implementation Details:**
[Specific implementation guidance that an LLM can follow:]
- What classes/functions to create
- Key methods and their signatures
- Important algorithms or logic
- Data structures to use
- Error handling requirements
- Integration points with other components

**Acceptance Criteria:**
- ✅ [Specific, testable criterion with measurable outcome]
- ✅ [Another criterion with clear success condition]
- ✅ [Include both functional and non-functional criteria]

**Files to Create:**
- `path/to/file.py` - [Brief description of file's purpose]

**Files to Modify:**
- `path/to/existing.py` - [What changes to make and why]

**Dependencies:**
- [List any libraries or modules this step requires]
- [Note if any new imports are needed]

**Test:**
[Detailed test steps:]
1. [Specific action to take]
2. [Expected result to verify]
3. [How to confirm success]

**Confidence Rationale:**
[1-2 sentences explaining the confidence score, noting any risks or unknowns]

**Example Code/Pseudocode:** (Optional but helpful)
```python
# Example showing the expected structure
class MyClass:
    def key_method(self, param: str) -> bool:
        # Implementation approach
        pass
```
```

### Step Detail Requirements

**Minimum requirements for each step:**

1. **Description** (Required)
   - Must explain WHAT the step does
   - Must explain WHY it's needed
   - Should be 2-4 sentences
   - Should provide context within the larger system

2. **Implementation Details** (Required)
   - Must be specific enough for LLM to implement
   - Should include class names, method signatures
   - Should describe key algorithms or logic
   - Should mention important data structures
   - Should specify error handling approach
   - Should identify integration points

3. **Acceptance Criteria** (Required)
   - Must be testable and measurable
   - Must include both happy path and error cases
   - Should specify expected behavior clearly
   - Should include performance criteria if relevant

4. **Files to Create/Modify** (Required)
   - Must list specific file paths
   - Must include brief purpose for each file
   - Must distinguish between new files and modifications

5. **Dependencies** (Required if applicable)
   - Must list any new libraries needed
   - Must list any new imports required
   - Must note any external service dependencies

6. **Test** (Required)
   - Must provide step-by-step test instructions
   - Must specify expected results
   - Must be executable by a human or LLM
   - Should include at least one error case

7. **Confidence Rationale** (Required)
   - Must explain the confidence score
   - Must note any risks or unknowns
   - Must identify potential blockers

8. **Example Code** (Optional but recommended)
   - Helpful for complex steps
   - Shows expected structure or approach
   - Can be pseudocode or actual code
   - Clarifies any ambiguous requirements

**Bad Example (Too Vague):**
```markdown
### Step 2.1: Create Database
**Confidence:** 95%
**Acceptance Criteria:**
- Database works
**Files to Create:**
- database.py
**Test:** Try to use it
```

**Good Example (Sufficient Detail):**
```markdown
### Step 2.1: Database Manager Implementation

**Confidence:** 95%

**Description:**
Create a DBManager class that handles all database operations for the application.
This class will manage SQLite connections, execute queries, and provide methods
for all CRUD operations needed by the application.

**Implementation Details:**
- Create `DBManager` class with context manager support (`__enter__`, `__exit__`)
- Implement connection pooling with single connection for SQLite
- Create methods:
  - `initialize_db(schema_path)` - Creates tables from schema.sql
  - `add_to_whitelist(email, domain, notes)` - Adds entry to whitelist table
  - `check_whitelist(email)` - Returns True if email or domain is whitelisted
  - `add_unwanted_sender(email, reason)` - Adds to unwanted_senders table
  - `log_action(sender, action_type, success, details)` - Logs to action_history
- Use parameterized queries to prevent SQL injection
- Implement proper error handling with try/except for sqlite3.Error
- Close connections properly in __exit__ method

**Acceptance Criteria:**
- ✅ Can create database file in specified location
- ✅ Can initialize schema from schema.sql file
- ✅ Can insert records into all tables
- ✅ Can query records with proper error handling
- ✅ Connection closes properly even on errors
- ✅ SQL injection prevented through parameterized queries

**Files to Create:**
- `src/database/db_manager.py` - Main database manager class

**Dependencies:**
- `sqlite3` (built-in)
- `contextlib` (built-in)
- `logging` (for error logging)

**Test:**
1. Create DBManager instance with test database path
2. Call initialize_db() and verify database file created
3. Insert test record into whitelist: `db.add_to_whitelist('test@example.com', None, 'test')`
4. Query whitelist: `result = db.check_whitelist('test@example.com')`
5. Verify result is True
6. Test with invalid email, verify returns False
7. Verify database file exists and contains data

**Confidence Rationale:**
95% confidence - SQLite is well-documented, straightforward implementation,
similar examples available. Minor risk around connection management but
standard patterns exist.

**Example Code:**
```python
import sqlite3
from contextlib import contextmanager

class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def initialize_db(self, schema_path: str):
        with open(schema_path, 'r') as f:
            schema = f.read()
        with self.get_connection() as conn:
            conn.executescript(schema)
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise
        finally:
            conn.close()
```
```


### Build Plan Validation Checklist

Before starting any phase, verify:

- [ ] All steps have confidence scores (0-100%)
- [ ] Phase composite confidence calculated
- [ ] Phase confidence ≥ 90%
- [ ] All steps with confidence < 90% have been addressed (revised, split, or deferred)
- [ ] Acceptance criteria are specific and testable
- [ ] Dependencies between steps are clear
- [ ] Files to create/modify are specified
- [ ] Test descriptions are actionable

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
   - Include ALL steps with full details (no abridging or summarizing)
   - Include ALL implementation details for each step
   - Include ALL acceptance criteria
   - Include ALL example code snippets
   - Include ALL dependencies, files to create/modify
   - Include ALL test descriptions
   - Include phase goals, prerequisites, confidence scores
   - **DO NOT create abridged or shortened versions**
2. ⛔ **CRITICAL: Copy the ENTIRE DEVELOPMENT_RULES.md file**
   - Copy all rules without modification
   - Include all sections, examples, and guidelines
3. ✅ Create CURRENT_PHASE.md with both complete contents
   - Format: Development Rules first, then Phase content
   - This becomes the single source of truth for execution
4. ✅ Work exclusively with CURRENT_PHASE.md during phase execution
   - Do not refer back to BUILD_PLAN.md during execution
   - All information needed must be in CURRENT_PHASE.md

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
   - This prevents confusion about which phase is active
   - Ensures clean state before starting next phase
   - **DO NOT proceed to next phase without deleting CURRENT_PHASE.md**

**Why use CURRENT_PHASE.md:**
- Reduces token usage (only load current phase, not entire plan)
- Focuses attention on immediate work
- Prevents accidental modification of master BUILD_PLAN.md
- Clear separation between plan and execution
- **Must contain COMPLETE content** - all implementation details, examples, and acceptance criteria needed for execution without referring back to BUILD_PLAN.md
- Self-contained document ensures consistent execution without context switching

---

## Rule 5: Testing Requirements

**Manual testing approach:**
- ✅ Test each step immediately after coding
- ✅ Verify functionality works as expected
- ✅ Test happy path (expected usage)
- ✅ Test at least one error case (invalid input, missing data, etc.)
- ✅ Document test results in commit message

**What to test:**
- Unit level: Individual functions/methods work correctly
- Integration level: Components work together
- User level: Feature works from user perspective

**When automated tests are NOT required:**
- Early phases focused on infrastructure setup
- MVP/prototype development
- Exploratory/experimental features

**When automated tests ARE required:**
- Core business logic that rarely changes
- Bug fixes (write test that catches the bug first)
- Public APIs or library functions
- When specified in build plan

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
- ✅ Not required for obvious types (e.g., `count = 0`)
- ✅ Required for function parameters and return values (when not obvious)

**Error handling:**
- ✅ Catch specific exceptions, not generic Exception
- ✅ Provide meaningful error messages
- ✅ Log errors appropriately
- ✅ Clean up resources (use context managers when possible)

**Code organization:**
- ✅ Group related functions together
- ✅ Order: imports, constants, classes, functions, main
- ✅ Separate concerns (UI code separate from business logic)
- ✅ Use appropriate design patterns when beneficial

---

## Rule 7: File Organization

**File creation:**
- ✅ Create files exactly as specified in project structure
- ✅ Use specified file names (consistency matters)
- ✅ Create files in specified directories
- ✅ Create necessary __init__.py files (for Python packages)

**File modification:**
- ✅ Only modify files listed in "Files to Modify"
- ✅ Keep related changes together (don't scatter a feature across multiple commits)
- ✅ Don't refactor unrelated code in the same commit

**File deletion:**
- ❌ Don't delete files unless explicitly specified
- ✅ If a file needs deletion, document why in commit message
- ✅ Ensure no orphaned imports or references remain

**Project structure:**
- ✅ Follow the project structure defined in BUILD_PLAN.md
- ✅ If structure changes are needed, update BUILD_PLAN.md first
- ✅ Document reasoning for structure changes
- ✅ Keep structure consistent throughout project

**Configuration files:**
- ✅ Keep configuration separate from code
- ✅ Use environment variables for sensitive data
- ✅ Provide example configuration files (.example or .template)
- ✅ Document all configuration options

---

## Rule 8: Git Workflow

**Commits:**
- ✅ Commit after each completed step
- ✅ Use descriptive commit messages (see Rule 2 for format)
- ✅ Commit only working code (code that compiles/runs)
- ✅ Don't commit commented-out code (delete it, git remembers)

**Branches:**
- ✅ Work on feature branches if desired (optional for solo projects)
- ✅ Main/master branch should always be stable
- ✅ Merge to main after phase completion

**What to commit:**
- ✅ Source code
- ✅ Configuration files
- ✅ Documentation
- ✅ Build scripts

**What NOT to commit:**
- ❌ Generated files (__pycache__, *.pyc, etc.)
- ❌ IDE-specific files (.idea/, .vscode/ unless shared config)
- ❌ Sensitive data (passwords, API keys)
- ❌ Large binary files (unless necessary)
- ❌ User-specific data (databases, logs)

**.gitignore essentials:**
```
# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
venv/
env/

# IDEs
.vscode/
.idea/
*.swp

# Data
data/
*.db
*.log

# Build
dist/
build/
*.spec

# OS
.DS_Store
Thumbs.db
```

---

## Rule 9: Progress Tracking

**In CURRENT_PHASE.md:**
- ✅ Mark completed steps with ✅
- ✅ Mark current step with 🔄
- ✅ Leave incomplete steps with ❌ or blank
- ✅ Add notes about challenges or decisions

**In BUILD_PLAN.md:**
- ✅ Only update after phase completion
- ✅ Mark completed phases with ✅ in progress tracker
- ✅ Don't modify step details (unless revising plan)

**Progress visibility:**
```markdown
## Phase Progress
- ✅ Step 1.1: Completed
- ✅ Step 1.2: Completed  
- 🔄 Step 1.3: In progress
- ❌ Step 1.4: Not started
- ❌ Step 1.5: Not started
```

---

## Rule 10: Communication and Documentation

**When to ask for help:**
- ⛔ Acceptance criteria are unclear
- ⛔ Technical blocker cannot be resolved
- ⛔ Design decision needed that affects other phases
- ⛔ Security or safety concern identified

**When to document decisions:**
- ✅ Deviation from build plan
- ✅ Alternative approach chosen
- ✅ Technical limitation discovered
- ✅ Assumption made due to missing information

**Where to document:**
- Inline: Code comments for implementation details
- Commit message: Reasoning for changes
- CURRENT_PHASE.md: Notes about challenges or decisions
- Separate doc: If decision affects multiple components

---

## Rule 11: Phase Transition Checklist

**Before moving to next phase:**

- [ ] All steps in current phase marked complete ✅
- [ ] All acceptance criteria verified
- [ ] All tests passing
- [ ] No linter errors or warnings
- [ ] All files committed to git
- [ ] Integration test passed (components work together)
- [ ] CURRENT_PHASE.md notes reviewed
- [ ] BUILD_PLAN.md updated with phase completion
- [ ] CURRENT_PHASE.md deleted
- [ ] Ready to start next phase with clean slate

---

## Summary: The Process

1. **Start Phase**: Copy phase + rules to CURRENT_PHASE.md
2. **Execute Step**: Code, test, commit
3. **Mark Complete**: Update CURRENT_PHASE.md with ✅
4. **Repeat**: Until all phase steps complete
5. **Finish Phase**: Update BUILD_PLAN.md, delete CURRENT_PHASE.md
6. **Next Phase**: Go to step 1

**Key Principles:**
- 🎯 **Focus**: One step at a time
- ✅ **Quality**: Test before proceeding
- 📝 **Document**: Track progress and decisions
- 🚫 **Discipline**: Stop if blocked, fix before continuing
- 🔄 **Iterate**: Each phase builds on the previous

---

These rules ensure consistent, high-quality development while keeping the process manageable and token-efficient.

