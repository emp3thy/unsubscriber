# Email Unsubscriber

## Overview

An automated tool to help unsubscribe from unwanted emails across multiple email providers (Hotmail/Outlook and Gmail). This tool will scan your inbox, identify subscription emails, and help you unsubscribe from them in bulk to reduce email clutter.

## Problem Statement

- Thousands of junk emails in both Hotmail and Gmail accounts
- Manual unsubscribing is time-consuming and tedious
- Need automated solution to identify and unsubscribe from unwanted subscriptions

## Features

- [ ] **Unified IMAP Connection** - Single codebase for both Gmail and Hotmail
- [ ] Connect to Gmail via IMAP (imap.gmail.com:993)
- [ ] Connect to Hotmail/Outlook via IMAP (outlook.office365.com:993)
- [ ] Scan inbox for subscription emails
- [ ] **Email Scoring System** - Weighted scoring based on multiple criteria
- [ ] Identify unsubscribe links in emails
- [ ] Bulk unsubscribe functionality
- [ ] Whitelist important senders
- [ ] **Decision History Tracking** - Remember which senders were marked as unwanted
- [ ] **Learning System** - Use past decisions to improve future scoring
- [ ] Progress tracking and reporting
- [ ] Safe mode (preview before unsubscribing)
- [ ] **Smart Email Grouping** - Group emails by sender for bulk operations
- [ ] **Bulk Email Deletion** - Delete multiple emails from same sender
- [ ] **Sender-based Operations** - Group and manage emails by sender

## Technical Requirements

### Email Provider Support
- **Gmail**: IMAP access (imap.gmail.com:993)
- **Hotmail/Outlook**: IMAP access (outlook.office365.com:993)
- **Unified Protocol**: Using IMAP for both providers enables consistent email handling
- **Authentication**: 
  - Gmail: App passwords (if 2FA enabled) or OAuth2
  - Hotmail/Outlook: App passwords or OAuth2

### Core Functionality
- Email parsing and analysis
- **Email Scoring Algorithm** - Multi-criteria scoring system
- **Unsubscribe Link Detection** - Parse HTML and text content for unsubscribe links
- **Automated Unsubscribing** - Execute unsubscribe requests via browser automation or REST calls
- **Browser Management** - Open/close browser instances for unsubscribe links
- **REST API Integration** - Direct API calls when possible (preferred method)
- Error handling and retry logic
- Logging and audit trail

## Email Scoring System

The tool uses a weighted scoring mechanism to identify emails that are likely candidates for unsubscribing. Each email is scored based on the following criteria:

### Scoring Criteria (Non-exclusive)

1. **Unread Status** (+1 point)
   - Emails that have never been opened/read
   - Indicates low engagement with the sender

2. **Repeated Sender** (+1 point per additional email from same sender)
   - Senders who have sent multiple emails
   - Higher frequency = higher score
   - Helps identify spammy or overly promotional senders

3. **Unsubscribe Link Present** (+1 point)
   - Emails containing unsubscribe links
   - Indicates legitimate subscription emails
   - Makes automated unsubscribing possible

4. **Previously Marked as Unwanted** (+5 points)
   - Sender was previously unsubscribed from or deleted
   - User has already identified this sender as junk
   - Highest weight - strong signal of unwanted content
   - Auto-flagged for immediate processing in future runs

### Scoring Algorithm

```
Total Score = Unread Status + (Sender Frequency - 1) + Unsubscribe Link Present + Previously Unwanted
```

**Example Scoring:**

*First-time sender:*
- Email from "newsletter@company.com" (unread, 5th email from this sender, has unsubscribe link)
- Score = 1 (unread) + 4 (5-1 for frequency) + 1 (unsubscribe link) + 0 (new sender) = **6 points**

*Previously marked unwanted:*
- Email from "spam@promotions.com" (read, 2nd email, has unsubscribe link, previously deleted)
- Score = 0 (read) + 1 (2-1 for frequency) + 1 (unsubscribe link) + 5 (previously unwanted) = **7 points**

*Auto-flagged for immediate action:*
- Email from sender previously unsubscribed will automatically score ≥5 points
- Ensures consistent handling of known unwanted senders

### Grouping and Prioritization

- **High Priority (Score ≥ 4)**: Immediate unsubscribe candidates
- **Medium Priority (Score 2-3)**: Review before unsubscribing
- **Low Priority (Score 0-1)**: Manual review recommended

### Bulk Operations

- Group emails by sender for efficient bulk unsubscribing
- Process high-scoring senders first
- Provide summary statistics before executing unsubscribes
- **Bulk Email Deletion**: Delete all emails from specific senders
- **Sender Management**: View and manage all emails from a single sender

## Automated Unsubscribing

The tool implements multiple strategies for executing unsubscribe requests, prioritizing efficiency and reliability.

### Unsubscribe Link Detection

- **HTML Parsing**: Extract unsubscribe links from email HTML content
- **Text Parsing**: Find unsubscribe links in plain text emails
- **Pattern Recognition**: Identify common unsubscribe link patterns:
  - `unsubscribe`, `opt-out`, `remove`, `stop`
  - Links containing `unsubscribe` in URL
  - List-unsubscribe headers (RFC 2369)

### Unsubscribe Execution Methods

#### 1. REST API Calls (Preferred)
- **Direct HTTP Requests**: Execute unsubscribe links via REST calls
- **Advantages**: 
  - No browser overhead
  - Faster execution
  - Better error handling
  - Headless operation
- **Implementation**: Use Python `requests` library
- **Fallback**: Browser automation if REST fails

#### 2. Browser Automation (Fallback)
- **Selenium WebDriver**: Automated browser control
- **Browser Management**:
  - Open browser instance for each unsubscribe link
  - Navigate to unsubscribe URL
  - Handle form submissions if required
  - Close browser instance after completion
- **Headless Mode**: Run browsers in background when possible
- **Browser Options**: Chrome, Firefox, or Edge support

### Unsubscribe Process Flow

1. **Link Extraction**: Parse email content for unsubscribe links
2. **Method Selection**: 
   - Try REST API call first
   - Fall back to browser automation if needed
3. **Execution**: 
   - REST: Direct HTTP request to unsubscribe URL
   - Browser: Open browser, navigate, submit, close
4. **Verification**: Confirm successful unsubscribe
5. **Logging**: Record success/failure for each attempt

### Technical Implementation

```python
# Example unsubscribe execution
def execute_unsubscribe(unsubscribe_url, method='rest'):
    if method == 'rest':
        # Direct HTTP request
        response = requests.post(unsubscribe_url)
        return response.status_code == 200
    else:
        # Browser automation
        driver = webdriver.Chrome()
        try:
            driver.get(unsubscribe_url)
            # Handle form submission if needed
            return True
        finally:
            driver.quit()
```

### Error Handling

- **Network Errors**: Retry with exponential backoff
- **Invalid Links**: Skip and log error
- **CAPTCHA Challenges**: Flag for manual review
- **Rate Limiting**: Implement delays between requests
- **Browser Crashes**: Automatic browser cleanup and retry

## Bulk Email Management

The tool provides comprehensive email management capabilities beyond just unsubscribing, including bulk deletion and sender-based operations.

### Sender-based Email Operations

#### 1. Email Grouping by Sender
- **Automatic Grouping**: Group all emails by sender email address
- **Sender Statistics**: 
  - Total email count per sender
  - Date range of emails
  - Read/unread status breakdown
  - Scoring summary per sender

#### 2. Bulk Email Deletion
- **Selective Deletion**: Choose which senders to delete emails from
- **Deletion Options**:
  - Delete all emails from a sender
  - Delete only unread emails from a sender
  - Delete emails within a date range
  - Delete emails matching specific criteria (score, subject patterns)

#### 3. Sender Management Interface
- **Sender List View**: 
  - Sorted by email count (highest first)
  - Sorted by score (most problematic first)
  - Sorted by date (most recent first)
- **Sender Details**: 
  - View all emails from a specific sender
  - Preview email subjects and dates
  - Select individual emails for deletion

### Bulk Operations Workflow

1. **Scan and Group**: Identify all senders and group emails
2. **Review Senders**: Display sender statistics and email counts
3. **Select Operations**: Choose which senders to unsubscribe from
4. **Choose Deletion**: Select which emails to delete after unsubscribing
5. **Preview Changes**: Review what will be unsubscribed and deleted
6. **Execute**: Run unsubscribe and deletion operations
7. **Cleanup**: Remove processed emails from inbox

### Deletion Safety Features

- **Preview Mode**: Show exactly which emails will be deleted
- **Backup Option**: Create backup before bulk deletion
- **Whitelist Protection**: Prevent deletion of whitelisted senders
- **Confirmation Required**: User confirmation for bulk operations
- **Undo Capability**: Restore deleted emails if needed (within email provider limits)

### Technical Implementation

```python
# Example bulk deletion functionality
def delete_emails_from_sender(sender_email, criteria=None):
    """
    Delete emails from a specific sender based on criteria
    """
    emails = get_emails_from_sender(sender_email)
    
    if criteria:
        emails = filter_emails_by_criteria(emails, criteria)
    
    # Preview deletion
    preview_deletion(emails)
    
    # Confirm with user
    if confirm_deletion():
        for email in emails:
            delete_email(email.id)
        log_deletion(sender_email, len(emails))
```

### Sender Analysis Dashboard

- **Top Senders**: Senders with most emails
- **High-Score Senders**: Most problematic senders
- **Previously Marked**: Senders previously identified as unwanted (auto-flagged)
- **Recent Activity**: Senders with recent email activity
- **Unsubscribe Candidates**: Senders with unsubscribe links
- **Deletion Candidates**: Senders with high email counts and low engagement

### Decision Tracking and Learning

**How It Works:**
1. User reviews sender list and marks senders for unsubscribe/delete
2. System records decisions in persistent storage (SQLite or JSON)
3. Next time tool runs, previously marked senders get +5 bonus points
4. Tool becomes smarter over time, learning user preferences

**Benefits:**
- Consistent handling of repeat offenders
- Reduces manual review time in subsequent runs
- Automatically catches senders who bypass unsubscribe
- Provides audit trail of all actions taken

## Getting Started

### Prerequisites

- **Python 3.8+** (for development)
- **OR** - Just download the standalone .exe (for end users - no Python needed)
- **Email Account Setup:**
  - Valid Gmail and/or Hotmail accounts
  - IMAP access enabled (usually enabled by default)
  - **Gmail**: App password if 2FA enabled (recommended)
    - Generate at: https://myaccount.google.com/apppasswords
  - **Hotmail/Outlook**: App password if 2FA enabled
    - Generate at: https://account.microsoft.com/security
- **Python Libraries:**
  - `tkinter` (built-in) for GUI
  - `imaplib` (built-in) for IMAP connections
  - `email` (built-in) for email parsing
  - `sqlite3` (built-in) for database
  - `threading` (built-in) for async operations
  - `requests` for REST API calls
  - `beautifulsoup4` for HTML parsing
  - `selenium` for browser automation (fallback)
- **Browser Dependencies** (for fallback automation):
  - Chrome/Chromium browser
  - ChromeDriver (for Selenium)
  - Selenium WebDriver Python package
- **Packaging** (for distribution):
  - `pyinstaller` to create standalone executable

### Installation

**For End Users (No Python Required):**
1. Download `EmailUnsubscriber.exe` from releases
2. Double-click to run
3. Configure email accounts on first launch

**For Developers:**
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

**Building Executable:**
```bash
pyinstaller --onefile --windowed --name EmailUnsubscriber main.py
```

## Usage

1. **Setup**: Configure your email accounts
2. **Scan**: Run initial scan to identify and score all emails
3. **Review Scoring**: Review the scoring results and sender groupings
4. **Whitelist**: Mark important senders to prevent accidental unsubscribing
5. **Preview**: Review high-scoring senders before unsubscribing
6. **Execute**: Run bulk unsubscribe process on selected senders
7. **Bulk Deletion**: Delete emails from processed senders
8. **Cleanup**: Remove processed emails from inbox
9. **Monitor**: Track progress and handle any errors

## Safety Features

- Preview mode to review before unsubscribing
- Whitelist functionality for important senders
- Rollback capability for accidental unsubscribes
- Detailed logging of all actions

## Critical Implementation Questions

To successfully implement this tool, you need to answer the following questions and make key decisions:

### 1. Application Architecture

**✅ DECISION: Python + Tkinter Desktop GUI**

**Why This Choice:**
- **Simple UI**: Tkinter is built into Python - no extra installation
- **Desktop-only**: Runs entirely locally, no server needed
- **Easy to install**: Single executable via PyInstaller
- **No technical setup**: Double-click to run
- **Cross-platform**: Works on Windows, Mac, Linux
- **Python ecosystem**: Best libraries for IMAP, HTML parsing, web scraping

**Architecture:**
- **Frontend**: Tkinter GUI with tabs/panels for different views
- **Backend**: Python with async/await for email operations
- **Threading**: Background threads for long operations (keep UI responsive)
- **Packaging**: PyInstaller to create single .exe file for Windows

**Alternative Considered:**
- Electron (web-based UI) - Rejected: Large bundle size, more complex
- PyQt - Rejected: Requires separate Qt installation
- CLI - Rejected: Needs UI for reviewing sender lists easily

### 2. Email Access and Authentication

**✅ DECISION: Using IMAP for both Gmail and Hotmail**

**Benefits of IMAP:**
- Unified codebase - same protocol for both providers
- Simpler implementation - standard IMAP library (`imaplib` in Python)
- No API registration complexity
- Standard email operations across providers

**IMAP Connection Details:**
- **Gmail**: `imap.gmail.com:993` (SSL/TLS)
- **Hotmail/Outlook**: `outlook.office365.com:993` (SSL/TLS)

**Still Need to Decide:**
- **Authentication Method:**
  - App passwords (simpler, requires 2FA enabled)
  - OAuth2 (more secure, no password storage)
  - Username/password (not recommended for Gmail if 2FA enabled)
- **Credentials Storage:** Where will you store credentials?
  - Environment variables?
  - Encrypted configuration file?
  - Operating system keyring (Windows Credential Manager)?
  - Database with encryption?
- **Multi-Account Support:** How to handle multiple accounts?
  - Store multiple credentials?
  - Switch between accounts?
  - Process multiple accounts in sequence?

### 3. Email Scanning Strategy

**✅ DECISIONS:**
- **Scan Scope:** Inbox only
  - No Spam or Trash folders (not interesting)
  - No Archive/All Mail folders (focus on active inbox)
  - Clean start each time (no historical tracking)
- **Volume Limits:** Scan ALL emails in inbox
  - No date restrictions
  - No email count limits
  - Accept that first scan will take time (spring cleaning approach)
- **Incremental Scanning:** NO
  - Fresh scan every time
  - No database to track processed emails
  - Clean slate approach for each run

**Implications:**
- First run may take significant time (10,000+ emails)
- Each run is independent - no state carried over
- Users should understand this is a periodic "spring cleaning" tool
- Progress indication will be important for long scans

### 4. Data Storage and State Management

**✅ DECISION: Hybrid approach - In-memory processing + Persistent decision history**

**What This Means:**
- All email data processed in memory during each run (no email metadata stored)
- User decisions about unsubscribe/delete ARE persisted
- Tool learns from past decisions to improve future scoring

**Must Persist (Database or JSON):**
- **Whitelist** - Important senders to never unsubscribe/delete
  - Manually added by user
  - Domain-level whitelisting support (e.g., @company.com)
- **Blacklist/Unwanted Senders** - Senders marked as junk/unwanted
  - Track which senders user chose to unsubscribe from
  - Track which senders user chose to delete emails from
  - Use this history to auto-score future emails from same sender
- **Configuration** - Email credentials, preferences (config file)
- **Action History** - Persistent log of decisions
  - Sender email address
  - Action taken (unsubscribed, deleted, or both)
  - Timestamp
  - Success/failure status

**Won't Persist:**
- Individual email metadata (sender, subject, date, read status)
- Full email content
- Temporary scoring results (recalculated each run)

**✅ DECISION: Using SQLite database**
- Query flexibility for sender lookups
- Built-in to Python (no extra dependencies)
- Efficient for growing data over time
- Simple schema with 3-4 tables

### Database Schema Design

#### Table: `whitelist`
Stores senders that should never be unsubscribed or deleted.

```sql
CREATE TABLE whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_address TEXT NOT NULL UNIQUE,
    domain TEXT,  -- For domain-level whitelisting (e.g., 'company.com')
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_whitelist_email ON whitelist(email_address);
CREATE INDEX idx_whitelist_domain ON whitelist(domain);
```

#### Table: `unwanted_senders`
Tracks senders that user has marked as unwanted (unsubscribed/deleted).

```sql
CREATE TABLE unwanted_senders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_address TEXT NOT NULL UNIQUE,
    first_marked_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    times_encountered INTEGER DEFAULT 1,
    notes TEXT
);

CREATE INDEX idx_unwanted_email ON unwanted_senders(email_address);
```

#### Table: `action_history`
Detailed log of all actions taken (unsubscribe/delete operations).

```sql
CREATE TABLE action_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_email TEXT NOT NULL,
    action_type TEXT NOT NULL,  -- 'unsubscribe', 'delete', 'both'
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL,
    email_count INTEGER,  -- Number of emails affected
    unsubscribe_url TEXT,  -- URL used for unsubscribe
    error_message TEXT,  -- If action failed
    notes TEXT
);

CREATE INDEX idx_action_sender ON action_history(sender_email);
CREATE INDEX idx_action_date ON action_history(action_date);
CREATE INDEX idx_action_type ON action_history(action_type);
```

#### Table: `config`
Application configuration and preferences.

```sql
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example config entries:
-- INSERT INTO config (key, value) VALUES ('last_scan_date', '2025-10-04T10:30:00');
-- INSERT INTO config (key, value) VALUES ('high_score_threshold', '4');
-- INSERT INTO config (key, value) VALUES ('previously_unwanted_bonus', '5');
```

### Database Queries

**Check if sender is whitelisted:**
```sql
SELECT 1 FROM whitelist 
WHERE email_address = ? OR domain = ?
LIMIT 1;
```

**Check if sender was previously marked unwanted:**
```sql
SELECT 1 FROM unwanted_senders 
WHERE email_address = ?
LIMIT 1;
```

**Add sender to unwanted list:**
```sql
INSERT OR REPLACE INTO unwanted_senders (email_address, last_seen_date, times_encountered)
VALUES (?, CURRENT_TIMESTAMP, 
    COALESCE((SELECT times_encountered + 1 FROM unwanted_senders WHERE email_address = ?), 1)
);
```

**Log action taken:**
```sql
INSERT INTO action_history (sender_email, action_type, success, email_count, unsubscribe_url)
VALUES (?, ?, ?, ?, ?);
```

### 5. Unsubscribe Strategy Pattern - Layered Approach

**✅ DECISION: Use Strategy Pattern with multiple unsubscribe methods**

Instead of a single "one size fits all" approach, use a **chain of strategies** ordered from simplest/safest to most complex. Each strategy attempts to unsubscribe, and if it fails, the next strategy is tried.

#### Unsubscribe Strategy Chain:

**Strategy 1: RFC 2369 List-Unsubscribe Header (Simplest)**
- **Method**: Email header-based unsubscribe
- **Detection**: Check for `List-Unsubscribe` and `List-Unsubscribe-Post` headers
- **Execution**: 
  - One-click unsubscribe via POST to header URL
  - Or mailto: link in header
- **Pros**: Standards-compliant, no web scraping needed
- **Cons**: Not all emails have these headers
- **Fallback**: Try Strategy 2

**Strategy 2: Direct HTTP GET/POST Request (Simple)**
- **Method**: Direct REST API call to unsubscribe link
- **Detection**: Parse email HTML/text for unsubscribe links
- **Execution**:
  - Try HTTP GET first (most common)
  - If GET returns 405 Method Not Allowed, try POST
  - Follow redirects (max 3)
- **Link Patterns**: URLs containing "unsubscribe", "opt-out", "remove", "stop"
- **Pros**: Fast, no browser overhead
- **Cons**: Doesn't work for JavaScript-heavy pages
- **Fallback**: Try Strategy 3

**Strategy 3: Browser Automation - Simple Click (Moderate)**
- **Method**: Selenium WebDriver to open page and click unsubscribe
- **Detection**: Unsubscribe link exists but requires JavaScript
- **Execution**:
  - Open URL in headless browser
  - Look for unsubscribe button/link by text
  - Click and wait for confirmation
  - Close browser
- **Button Patterns**: Text contains "unsubscribe", "opt out", "remove me"
- **Pros**: Handles JavaScript-required pages
- **Cons**: Slower, requires browser
- **Fallback**: Try Strategy 4

**Strategy 4: Browser Automation - Form Fill (Complex)**
- **Method**: Selenium to handle multi-step unsubscribe forms
- **Detection**: Unsubscribe requires form submission
- **Execution**:
  - Open URL in browser
  - Detect form fields (email confirmation, reason dropdown, etc.)
  - Fill required fields
  - Submit form
  - Handle confirmation pages
- **Pros**: Handles complex unsubscribe flows
- **Cons**: Most complex, can fail on unusual forms
- **Fallback**: Try Strategy 5

**Strategy 5: mailto: Link (Email-based)**
- **Method**: Send unsubscribe email
- **Detection**: Link is `mailto:unsubscribe@domain.com`
- **Execution**: 
  - Parse mailto link
  - Send email with subject/body from link
  - Log as "pending" (requires manual verification)
- **Pros**: Works for email-based unsubscribe
- **Cons**: Asynchronous, requires waiting for confirmation
- **Fallback**: Mark as "Manual Required"

**Strategy 6: Failed - Add to "Must Delete" List**
- **Method**: All strategies failed
- **Action**: 
  - Mark sender as "hard to unsubscribe"
  - Add to special "Must Delete" category
  - Suggest user to delete all emails from this sender
  - Block sender if possible (email filter rule)
- **User Notification**: "This sender makes unsubscribing difficult. Recommend: Delete all & block."

#### Implementation Pattern:

```python
class UnsubscribeStrategy:
    def can_handle(self, email) -> bool:
        """Check if this strategy can handle this email"""
        pass
    
    def execute(self, email) -> tuple[bool, str]:
        """Execute unsubscribe. Returns (success, message)"""
        pass

class UnsubscribeStrategyChain:
    def __init__(self):
        self.strategies = [
            ListUnsubscribeStrategy(),      # Strategy 1
            HttpGetPostStrategy(),          # Strategy 2  
            BrowserSimpleClickStrategy(),   # Strategy 3
            BrowserFormFillStrategy(),      # Strategy 4
            MailtoStrategy(),               # Strategy 5
        ]
    
    def unsubscribe(self, email):
        for strategy in self.strategies:
            if strategy.can_handle(email):
                success, message = strategy.execute(email)
                if success:
                    log_success(email, strategy.name, message)
                    return True
                # Try next strategy
        
        # All strategies failed
        mark_as_must_delete(email.sender)
        return False
```

#### Multiple Unsubscribe Links Handling:

If an email has multiple unsubscribe links:
1. **Prioritize by type**:
   - List-Unsubscribe header (highest priority)
   - HTTP links containing "unsubscribe" in URL
   - HTTP links with "unsubscribe" anchor text
   - mailto: links (lowest priority)
2. **Try highest priority first**
3. **If fails, try next link with appropriate strategy**
4. **Stop on first success**

#### Link Validation:

Before executing any strategy:
- ✅ Validate URL format
- ✅ Check domain is not obviously malicious (basic blacklist)
- ✅ HTTPS preferred over HTTP
- ✅ Timeout after 30 seconds
- ❌ Don't follow redirects to different domains (security)

#### Rate Limiting Strategy:

- **Delay between requests**: 2-5 seconds (randomized)
- **Max concurrent operations**: 3 unsubscribes at once
- **Respect 429 Too Many Requests**: Back off exponentially
- **User-agent**: `Mozilla/5.0 (Windows NT 10.0; Win64; x64)` (standard browser)

#### "Must Delete" List:

Special category for senders that:
- All unsubscribe strategies failed
- Deliberately make unsubscribing difficult
- Use dark patterns (fake unsubscribe buttons, CAPTCHAs, etc.)

**User Actions:**
1. See list of "Must Delete" senders
2. Review why unsubscribe failed
3. Bulk delete all emails from these senders
4. Optional: Create email filter to auto-delete future emails

**Benefits:**
- ✅ User informed about bad actors
- ✅ Still provides value (delete existing emails)
- ✅ Prevents future emails via filtering
- ✅ Can manually unsubscribe later if desired

### 7. User Interface and Experience

**✅ DECISION: High-level bulk action interface, NOT an inbox replica**

**Core Philosophy:**
- Group emails by sender
- Show sender-level statistics and actions
- Bulk operations only (no individual email management)
- High-level view for quick cleanup
- Minimize clicks and decisions

#### Main Workflow:

**1. Initial Scan**
- User clicks "Scan Inbox" button
- Progress bar shows: "Scanning 3,482 emails..."
- App fetches all emails, groups by sender, calculates scores
- Results displayed in sender-grouped view

**2. Sender-Grouped View (Main Interface)**

Display senders in a table/list with columns:
- **Sender** (email address or name)
- **Email Count** (e.g., "47 emails")
- **Unread Count** (e.g., "42 unread")
- **Score** (e.g., "8" with color coding)
- **Has Unsubscribe?** (✓ or ✗)
- **Status** (New / Previously Unwanted / Whitelisted)
- **Action Buttons** (see below)

**3. Three Main Action Categories:**

**Category A: "Can Unsubscribe" (Has unsubscribe link)**
- Top button: **"Unsubscribe from All" button**
  - One click unsubscribes from ALL senders with unsubscribe links
  - Groups unsubscribe calls by sender (only one call per sender)
  - Shows progress: "Unsubscribing from 47 senders..."
  - After unsubscribe succeeds, emails from that sender can be deleted

**Category B: "Previously Failed" (Unsubscribe attempts failed before)**
- These senders appear in "Must Delete" section
- Button: **"Delete All Failed Unsubscribes"**
  - Bulk deletes all emails from all failed-unsubscribe senders
- Or: **"Delete by Sender"** with checkboxes to select specific senders

**Category C: "No Unsubscribe Link" (Can only delete)**
- Senders without unsubscribe links
- Button: **"Review & Delete"**
  - Shows list of senders, user selects which to delete
  - Bulk delete all emails from selected senders

#### Interface Layout:

```
┌─────────────────────────────────────────────────────────────┐
│  Email Unsubscriber                          [Settings] [?] │
├─────────────────────────────────────────────────────────────┤
│  Accounts: ✓ gmail@example.com  ✓ outlook@example.com       │
│  [Scan Inbox]  [Refresh]                                    │
├─────────────────────────────────────────────────────────────┤
│  Summary:                                                    │
│    Total Senders: 127                                       │
│    Can Unsubscribe: 89 senders (2,341 emails)              │
│    Must Delete: 23 senders (487 emails)                    │
│    No Action Needed: 15 (whitelisted)                      │
│                                                              │
│  [🔴 Unsubscribe from All (89)]  [🗑️ Delete Must-Delete (23)]│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  📊 Senders - Sorted by Score (High to Low)                 │
├──────────────┬────────┬────────┬───────┬──────────┬─────────┤
│ Sender       │ Emails │ Unread │ Score │ Unsub?   │ Actions │
├──────────────┼────────┼────────┼───────┼──────────┼─────────┤
│ promo@sale   │   47   │   42   │   9   │    ✓     │ [Unsub] │
│ news@daily   │   38   │   38   │   8   │    ✓     │ [Unsub] │
│ spam@junk    │   15   │   10   │   7   │    ✗     │ [Delete]│
│ ...          │  ...   │  ...   │  ...  │   ...    │   ...   │
└──────────────┴────────┴────────┴───────┴──────────┴─────────┘

Tabs: [All] [Can Unsubscribe] [Must Delete] [Whitelisted]
```

#### User Flow - Bulk Unsubscribe:

1. **User clicks "Unsubscribe from All (89)"**
2. **Confirmation dialog**: 
   ```
   Unsubscribe from 89 senders?
   This will unsubscribe from all senders with unsubscribe links.
   Emails will be deleted after successful unsubscribe.
   
   [Cancel]  [Preview List]  [Yes, Unsubscribe All]
   ```
3. **Processing**:
   - Groups unsubscribe requests by sender
   - Only one unsubscribe call per sender (even if 100 emails)
   - Progress bar: "Unsubscribing 23/89..."
   - Shows real-time status updates
4. **Results**:
   ```
   Unsubscribe Complete:
   ✓ 78 successful
   ✗ 11 failed (moved to "Must Delete")
   
   Delete emails from successful unsubscribes?
   2,089 emails from 78 senders
   
   [Keep Emails]  [Delete All]
   ```

#### User Flow - Delete Must-Delete:

1. **User clicks "Delete Must-Delete (23)"**
2. **Shows list**:
   ```
   These senders failed unsubscribe attempts:
   
   [x] badactor@spam.com (47 emails) - Reason: All strategies failed
   [x] difficult@promo.net (32 emails) - Reason: CAPTCHA required
   [x] fake@news.org (18 emails) - Reason: Invalid unsubscribe link
   ... (all checked by default)
   
   [Uncheck All]  [Cancel]  [Delete Selected]
   ```

#### Grouping Strategy:

**How grouping reduces unsubscribe calls:**
- Sender "promo@store.com" has 100 emails
- User selects "Unsubscribe from All"
- App finds ONE unsubscribe link from any email from that sender
- Makes ONE unsubscribe call for that sender
- If successful, ALL 100 emails can be deleted
- Result: 100 emails → 1 unsubscribe call

**Benefits:**
- ✅ Faster processing (fewer HTTP requests)
- ✅ Less likely to trigger rate limits
- ✅ Cleaner user experience
- ✅ Respects sender's servers

#### Minimal User Decisions:

**Only 3-4 clicks needed for full cleanup:**
1. Click "Scan Inbox"
2. Click "Unsubscribe from All"
3. Click "Yes, Delete All" (for successful unsubscribes)
4. Click "Delete Must-Delete" (for failed unsubscribes)

**Done!** Thousands of emails cleaned up in 4 clicks.

#### No Individual Email Management:

- ❌ No email list view
- ❌ No read/preview individual emails
- ❌ No select individual emails to delete
- ✅ Only sender-level bulk actions
- ✅ Focus: High-level cleanup, not inbox management

#### Optional Features:

- **Filter by score**: "Only show senders with score ≥ 5"
- **Search senders**: Quick find specific sender
- **Sort options**: By email count, score, date, alphabetical
- **Whitelist quick-add**: Right-click sender → "Add to Whitelist"

### 8. Safety and Validation

**✅ DECISIONS:**

**No Dry Run Mode Needed:**
- Unsubscribing is not harmful - it's what users want
- Deleting emails with unsubscribe links is safe
- Personal emails won't have unsubscribe links (safe by design)
- "Must Delete" list only contains senders with failed unsubscribe attempts
- Real risk is minimal - proceed with confidence

**Whitelist Management:**
- Manual add via UI (simple form)
- Domain-level whitelisting support (e.g., `@company.com`)
- Whitelist prevents any actions on those senders
- No import from contacts (v1.0)
- No regex patterns (v1.0)

**Undo/Rollback:**
- Move emails to trash (rely on email provider's undo capability)
- Most providers keep trash for 30 days
- No local backups needed (adds complexity without much benefit)
- User can manually recover from provider's trash if needed

### 9. Scoring Algorithm Refinements

**✅ DECISIONS:**

**Fixed Scoring Weights (Not Configurable in v1.0):**
- Unread Status: +1 point
- Repeated Sender: +1 per additional email from same sender
- Unsubscribe Link Present: +1 point
- Previously Marked Unwanted: +5 points
- **Rationale**: Simple, predictable, works for most users

**No Additional Scoring Factors (v1.0):**
- No email age weighting
- No keyword analysis
- No domain reputation checks
- No attachment presence scoring
- **Rationale**: Keep it simple, add later if users request

**Fixed Score Thresholds (Not Adjustable in v1.0):**
- High Priority: Score ≥ 4
- Medium Priority: Score 2-3
- Low Priority: Score 0-1
- **Rationale**: Clear categories, avoid configuration paralysis

**Score Explanation Feature (Important!):**
- Users should understand WHY a sender got a specific score
- Show score breakdown in UI tooltip or detail panel
- Example: "Score 8 = 1 (unread) + 4 (5 emails) + 1 (unsubscribe link) + 5 (previously unwanted)"
- Makes scoring transparent and builds user trust

### 10. Error Handling and Logging

**✅ DECISIONS:**

**What to Log:**
- Actions taken (unsubscribe, delete operations)
- Errors and failures
- Strategy used for each unsubscribe attempt
- NOT every email scanned (too verbose, unnecessary)
- Summary statistics per run

**Log Format:**
- Database table (`action_history`) for structured queries
- Text log file for debugging (`%APPDATA%/EmailUnsubscriber/logs/app.log`)
- Each log entry includes timestamp, sender, action, success/failure, error message

**Log Retention:**
- Database logs: Keep indefinitely (small data, valuable history)
- Text log files: Keep last 30 days, rotate monthly
- User can clear logs via settings if desired

**Error Recovery:**
- Skip and continue processing (don't stop on first error)
- Mark failed operations in database
- No automatic retry (user can manually retry from "Must Delete" list)
- Show summary of successes and failures at end
- User can review failures and retry individually if desired

### 11. Performance and Scale

**✅ DECISIONS: Optimize for users with full inboxes**

**Multi-threaded Processing:**
- Use half of user's CPU cores for processing
- Assume 2 threads per core (e.g., 4-core CPU = 8 threads, use 4)
- Parallel operations:
  - Email fetching from IMAP
  - Email parsing and scoring
  - Unsubscribe requests (max 3 concurrent per rate limiting)
- UI remains responsive on main thread

**Memory Usage - Store Only Essential Fields:**
- **Download full email** for processing (to find unsubscribe links)
- **Store in memory only**:
  - Sender email address
  - Email subject/title
  - Score and score breakdown
  - List of unsubscribe links/options found
  - Read/unread status
- **Never download attachments** (IMAP flag to exclude)
- **Don't persist email content** after processing
- Estimate: ~1KB per email metadata = 10MB for 10,000 emails (very manageable)

**Batch Processing Strategy:**
- Fetch emails in batches of 500 from IMAP
- Process batch while fetching next batch (pipeline)
- Update progress bar after each batch: "Processing 1,500 / 8,342 emails..."
- Allows user to see progress and provides cancel opportunity

**Processing Time Expectations:**
- First run will be expensive (users have full inboxes - that's why they need this tool!)
- Estimate: 2-5 seconds per 1000 emails (depends on network speed)
- 10,000 emails ≈ 20-50 seconds (acceptable for one-time cleanup)
- Subsequent runs faster (fewer new emails)

**Cancel/Pause Operations:**
- Add "Cancel" button during scan and unsubscribe operations
- Gracefully stop processing (finish current batch, don't corrupt state)
- User can resume by running scan again (stateless design)

**Network Optimization:**
- Batch IMAP fetches (500 at a time)
- Parallel unsubscribe requests (3 concurrent, per rate limiting)
- No local caching (fresh data each run, already decided)

### 12. Deployment and Distribution

**✅ DECISION: Single executable with GUI-based setup**

**Packaging:**
- PyInstaller to create standalone .exe for Windows
- `--onefile` flag for single executable
- `--windowed` flag to hide console window
- All dependencies bundled (no Python installation needed)

**Configuration:**
- GUI-based setup wizard on first launch
- Settings accessible through menu/preferences
- SQLite database and config stored in user's AppData folder
- No command-line arguments needed (GUI-driven)

**Distribution:**
- GitHub Releases for .exe download
- Simple download and run - no installer needed
- Portable application (can run from USB drive)

**Updates:**
- Manual download initially (simpler)
- Future: Auto-update check on launch (optional feature)

## Recommended Next Steps

### Decisions Made:
1. **✅ Email Access Method** - Using IMAP for both Gmail and Hotmail
2. **✅ Scan Scope** - Inbox only, no Spam/Trash
3. **✅ Volume** - Scan ALL emails in inbox (spring cleaning approach)
4. **✅ Data Storage** - Hybrid: In-memory email processing + SQLite for decision history
5. **✅ Database** - SQLite with 4 tables (whitelist, unwanted_senders, action_history, config)
6. **✅ State Management** - Track user decisions (whitelist/blacklist/actions) for learning
7. **✅ Learning System** - Previously marked unwanted senders get +5 score bonus
8. **✅ Technology Stack** - Python + Tkinter desktop GUI
9. **✅ Packaging** - Single .exe via PyInstaller (no installation needed)
10. **✅ Distribution** - Portable desktop app, double-click to run

### UI/UX Decisions Made:
11. **✅ UI Layout** - Sender-grouped table view with bulk action buttons
12. **✅ Bulk Operations** - "Unsubscribe from All" and "Delete Must-Delete" buttons
13. **✅ Minimal Clicks** - 3-4 clicks for full inbox cleanup
14. **✅ Sender Grouping** - One unsubscribe call per sender (not per email)
15. **✅ No Email Replica** - High-level cleanup view only, no individual email management

### Authentication Decisions Made:
16. **✅ Authentication Method** - App passwords (simpler than OAuth2)
17. **✅ Persistent Storage** - Encrypted credentials in SQLite + key file
18. **✅ User Experience** - Login once on first launch, auto-login thereafter

### Unsubscribe Strategy Decisions Made:
19. **✅ Strategy Pattern** - Chain of 6 strategies from simplest to most complex
20. **✅ Graceful Degradation** - Try each strategy in order until one succeeds
21. **✅ "Must Delete" List** - Special category for failed unsubscribes
22. **✅ Extensible Design** - Easy to add new strategies for edge cases

### Implementation Details Decisions Made:
23. **✅ Safety** - No dry run needed; unsubscribing and deleting spam is safe by design
24. **✅ Scoring** - Fixed weights and thresholds; show score breakdown for transparency
25. **✅ Logging** - Actions + errors to database and text logs; skip and continue on errors
26. **✅ Performance** - Multi-threaded (use half of CPU cores); batch IMAP fetches (500 at a time)
27. **✅ Memory** - Store only essential fields (sender, subject, score, unsubscribe links, read status)
28. **✅ Attachments** - Never download attachments (IMAP flag to exclude)

## Authentication Complexity - Important Considerations

### The Challenge:

**Gmail and Hotmail/Outlook both now require OAuth2 for IMAP access** (as of 2022). This presents a significant complexity:

### OAuth2 Requirements:

**Gmail:**
- Requires Google Cloud Console project setup
- Need to create OAuth2 credentials (Client ID & Secret)
- Must handle OAuth2 flow (browser redirect for user authorization)
- Need to manage token refresh
- Libraries needed: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`

**Hotmail/Outlook:**
- Requires Azure Portal app registration
- Need Client ID and Tenant ID
- OAuth2 flow with Microsoft authentication
- Token management and refresh
- Libraries needed: `msal` (Microsoft Authentication Library)

### Complexity Impact:

**OAuth2 adds significant complexity:**
1. **Setup burden**: Users need to create their own OAuth2 apps (complex for non-technical users)
2. **Browser integration**: OAuth2 requires opening browser for authentication
3. **Token management**: Access tokens expire and need refresh
4. **No "simple setup"**: Contradicts the "no technical fiddling" requirement

### Alternative: App Passwords (Simpler but Limited)

**Gmail App Passwords:**
- Only available if 2FA is enabled on the account
- User generates app password from Google Account settings
- Works with basic IMAP authentication (username + app password)
- **Much simpler**: No OAuth2 complexity, just use `imaplib` directly
- **Limitation**: Requires users to enable 2FA first

**Hotmail/Outlook App Passwords:**
- Available if 2FA is enabled
- Generate from Microsoft Account security settings
- Works with basic IMAP authentication
- Same simplicity benefits as Gmail

### Recommendation:

**Two-tier approach:**

1. **Primary (Simple)**: App Passwords
   - Require users to enable 2FA and generate app passwords
   - Dead simple: Just enter email + app password in GUI
   - Uses standard `imaplib` - no extra complexity
   - One-time setup, store encrypted in SQLite

2. **Future Enhancement**: OAuth2 support
   - More complex but more secure
   - Add later if app password approach doesn't work

### Implementation with App Passwords:

```python
import imaplib
import ssl

# Simple IMAP connection with app password
def connect_gmail(email, app_password):
    imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    imap.login(email, app_password)
    return imap

def connect_outlook(email, app_password):
    imap = imaplib.IMAP4_SSL('outlook.office365.com', 993)
    imap.login(email, app_password)
    return imap
```

**This is dead simple** - built-in Python libraries, no external OAuth2 dependencies!

## Persistent Authentication - Login Once, Use Forever

### The Goal:
Users should only need to authenticate **once** when they first set up the app, then credentials are stored securely for future sessions.

### Best Approach: Encrypted App Passwords in SQLite

#### How It Works:
1. **First Launch**: User enters email + app password
2. **Encrypt & Store**: Credentials encrypted and saved to SQLite database
3. **Future Launches**: App automatically retrieves and decrypts credentials
4. **No re-authentication**: User just opens app and it works

#### Implementation Strategy:

**Option 1: Encryption with Python's `cryptography` library (Recommended)**

```python
from cryptography.fernet import Fernet
import sqlite3
import os

# Generate encryption key (do this once, store in local file)
def get_or_create_key():
    key_file = os.path.join(os.environ['APPDATA'], 'EmailUnsubscriber', 'key.key')
    if not os.path.exists(key_file):
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, 'wb') as f:
            f.write(key)
    else:
        with open(key_file, 'rb') as f:
            key = f.read()
    return key

# Encrypt password before storing
def encrypt_password(password, key):
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

# Decrypt password when retrieving
def decrypt_password(encrypted_password, key):
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

# Store credentials
def save_credentials(email, app_password):
    key = get_or_create_key()
    encrypted_pwd = encrypt_password(app_password, key)
    
    conn = sqlite3.connect('emailunsubscriber.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO config (key, value) 
                 VALUES (?, ?)''', (f'email_{email}', encrypted_pwd))
    conn.commit()
    conn.close()

# Retrieve credentials
def load_credentials(email):
    key = get_or_create_key()
    
    conn = sqlite3.connect('emailunsubscriber.db')
    c = conn.cursor()
    c.execute('SELECT value FROM config WHERE key = ?', (f'email_{email}',))
    row = c.fetchone()
    conn.close()
    
    if row:
        return decrypt_password(row[0], key)
    return None
```

**Option 2: Windows Credential Manager (Windows-specific, most secure)**

```python
import keyring

# Store credentials (Windows Credential Manager)
def save_credentials_secure(email, app_password):
    keyring.set_password('EmailUnsubscriber', email, app_password)

# Retrieve credentials
def load_credentials_secure(email):
    return keyring.get_password('EmailUnsubscriber', email)
```

### Recommended Approach: **Hybrid Solution**

Use **encrypted storage in SQLite** for simplicity and cross-platform support:

1. **Encryption key** stored in AppData folder (Windows: `%APPDATA%\EmailUnsubscriber\key.key`)
2. **Encrypted passwords** stored in SQLite database
3. **Email addresses** stored in plain text (not sensitive)
4. **Auto-login** on app startup using stored credentials

### User Experience Flow:

**First Launch:**
1. App detects no stored credentials
2. Shows setup wizard: "Add Email Account"
3. User enters email address
4. App shows instructions to generate app password with links
5. User enters app password
6. App tests connection (validates credentials)
7. If successful: Encrypts and stores credentials
8. App connects and shows inbox scan

**Subsequent Launches:**
1. App loads stored credentials automatically
2. Connects to IMAP servers
3. No user interaction needed - just works!

**Managing Multiple Accounts:**
- Store multiple email/password pairs in database
- UI shows list of configured accounts
- User can add/remove accounts in settings
- Switch between accounts or scan all at once

### Security Considerations:

**Pros:**
- ✅ Passwords encrypted at rest
- ✅ Key stored separately from database
- ✅ Better than plain text storage
- ✅ Convenient user experience

**Cons:**
- ⚠️ Encryption key on same machine (if someone has file access, they could decrypt)
- ⚠️ Not as secure as OAuth2 token storage
- ⚠️ If key.key file is deleted, credentials are lost

**Mitigation:**
- Store key in OS-specific secure location
- Consider Windows Credential Manager as optional enhancement
- Show warning in UI: "Credentials stored locally for convenience"

### Database Schema Addition:

```sql
-- Store encrypted credentials in config table
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_address TEXT NOT NULL UNIQUE,
    provider TEXT NOT NULL,  -- 'gmail' or 'outlook'
    encrypted_password TEXT NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

### Libraries Needed:

```python
# requirements.txt
cryptography>=41.0.0  # For password encryption/decryption
keyring>=24.0.0       # Optional: for Windows Credential Manager
```

This approach gives you **"login once, use forever"** while maintaining reasonable security!

### Implementation Steps:

**Phase 1: Core Infrastructure**
1. **Set up Python project** - Create project structure, requirements.txt
2. **Create database initialization** - SQL script to create tables and indexes
3. **Build database access layer** - Python class to handle all DB operations
4. **Build basic Tkinter window** - Main application window skeleton

**Phase 2: Email Connection**
5. **Set up email accounts** - Generate app passwords for Gmail and Hotmail
6. **Build IMAP connection module** - Connect to both Gmail and Hotmail
7. **Implement email fetching** - Fetch emails from inbox
8. **Implement email parsing** - Extract sender, subject, read status, body content

**Phase 3: Scoring and Analysis**
9. **Build in-memory data structures** - Store emails efficiently during processing
10. **Implement decision history lookup** - Check if sender was previously marked unwanted
11. **Build scoring system** - Score emails based on all 4 criteria (including history)
12. **Implement sender grouping** - Group emails by sender for bulk operations

**Phase 4: User Interface**
13. **Build sender list view** - Display senders with scores in sortable table
14. **Add progress indicators** - Show progress during long inbox scans
15. **Build settings/config UI** - Email account setup wizard
16. **Add whitelist management UI** - Add/remove whitelisted senders

**Phase 5: Unsubscribe Logic**
17. **Implement unsubscribe link detection** - Parse HTML/text for unsubscribe links
18. **Build unsubscribe execution** - Start with HTTP GET/POST requests
19. **Add browser automation fallback** - Selenium for complex unsubscribe pages
20. **Record user decisions** - Save unsubscribe/delete actions to persistent storage

**Phase 6: Polish and Distribution**
21. **Add bulk delete functionality** - Delete emails from selected senders
22. **Add safety features** - Preview mode, whitelist protection, logging
23. **Test with real email accounts** - End-to-end testing
24. **Build executable with PyInstaller** - Create standalone .exe
25. **Create README and documentation** - User guide for the tool

## Contributing

Guidelines for contributing to the project.

## License

License information for the project.
