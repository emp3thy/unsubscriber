# Outlook/Hotmail Integration - Complete Action Plan

## Document Overview

This is your master action plan for integrating Outlook/Hotmail OAuth 2.0 authentication into the Email Unsubscriber application. This document references the detailed guides and provides a step-by-step execution plan.

---

## Quick Links to Documentation

1. **[OUTLOOK_OAUTH_INTEGRATION_STRATEGY.md](OUTLOOK_OAUTH_INTEGRATION_STRATEGY.md)** - Complete technical strategy and architecture
2. **[AZURE_APP_SETUP_GUIDE.md](AZURE_APP_SETUP_GUIDE.md)** - Step-by-step Azure portal setup
3. **[OAUTH_PROVIDER_COMPARISON.md](OAUTH_PROVIDER_COMPARISON.md)** - Side-by-side Gmail vs Outlook comparison

---

## Executive Summary

**Goal**: Enable users to register outlook.com, hotmail.com, and live.com email addresses using OAuth 2.0, mirroring the existing Gmail OAuth functionality.

**Timeline**: 4-5 weeks (setup to production)

**Effort**:
- External Setup: 2-4 hours
- Implementation: 2-3 weeks  
- Testing: 1 week
- Documentation: 3-5 days

**Prerequisites**:
- Microsoft account (any outlook.com, hotmail.com, or live.com account)
- Python 3.8+
- Existing Email Unsubscriber codebase with Gmail OAuth

---

## Phase 1: External/Infrastructure Setup (2-4 hours)

### Step 1.1: Azure App Registration

**Action**: Follow **[AZURE_APP_SETUP_GUIDE.md](AZURE_APP_SETUP_GUIDE.md)** completely

**Key Steps**:
1. Sign in to Azure Portal (https://portal.azure.com/)
2. Create app registration named "Email Unsubscriber"
3. Configure for multi-tenant + personal Microsoft accounts
4. Set redirect URI: `http://localhost` (Public client/native)
5. Copy Application (client) ID

**Deliverable**: Application (client) ID saved

**Time**: 15-20 minutes

---

### Step 1.2: Configure API Permissions

**Action**: Continue with **[AZURE_APP_SETUP_GUIDE.md](AZURE_APP_SETUP_GUIDE.md)** Part 2

**Key Steps**:
1. Add `IMAP.AccessAsUser.All` permission (Office 365 Exchange Online)
2. Add `offline_access` permission (Microsoft Graph)
3. Verify permissions are listed

**Deliverable**: API permissions configured in Azure

**Time**: 10 minutes

---

### Step 1.3: Enable Public Client Flows

**Action**: Continue with **[AZURE_APP_SETUP_GUIDE.md](AZURE_APP_SETUP_GUIDE.md)** Part 3

**Key Steps**:
1. Navigate to Authentication settings
2. Verify redirect URI is configured
3. Set "Allow public client flows" to Yes
4. Save changes

**Deliverable**: Public client flows enabled

**Time**: 5 minutes

---

### Step 1.4: Create Configuration File

**Action**: Create `data/outlook_credentials.json`

**Template**:
```json
{
  "client_id": "YOUR-APPLICATION-ID-HERE",
  "authority": "https://login.microsoftonline.com/common",
  "scope": [
    "https://outlook.office.com/IMAP.AccessAsUser.All",
    "offline_access"
  ],
  "redirect_uri": "http://localhost"
}
```

**Instructions**:
1. Create `data/` folder if it doesn't exist
2. Create file `data/outlook_credentials.json`
3. Copy template above
4. Replace `YOUR-APPLICATION-ID-HERE` with your Application (client) ID
5. Save file

**Deliverable**: `data/outlook_credentials.json` created with valid client ID

**Time**: 5 minutes

---

### Step 1.5: Enable IMAP on Test Account

**Action**: Enable IMAP on your Outlook.com test account

**Key Steps**:
1. Go to https://outlook.live.com/mail/
2. Settings (gear icon) > View all Outlook settings
3. Mail > Sync email > POP and IMAP
4. Set "Let devices and apps use IMAP" to Yes
5. Save

**Deliverable**: IMAP enabled on test account

**Time**: 5 minutes

---

### Step 1.6: Test Azure Setup

**Action**: Verify setup is complete

**Checklist**:
- [ ] Azure app registration created
- [ ] Application (client) ID copied
- [ ] API permissions configured (`IMAP.AccessAsUser.All`, `offline_access`)
- [ ] Public client flows enabled
- [ ] `data/outlook_credentials.json` created with client ID
- [ ] IMAP enabled on test Outlook account

**Deliverable**: All external setup complete

**Time**: 5 minutes (verification)

**Total Phase 1 Time**: 2-4 hours

---

## Phase 2: Core Implementation (2-3 weeks)

### Step 2.1: Install Dependencies

**Action**: Update `requirements.txt` and install MSAL

**File**: `requirements.txt`

**Changes**:
```python
# Add this line:
msal>=1.24.0
```

**Command**:
```bash
pip install msal>=1.24.0
```

**Deliverable**: MSAL library installed

**Time**: 5 minutes

---

### Step 2.2: Update Database Schema

**Action**: Add `provider` column to `oauth_tokens` table

**File**: `src/database/schema.sql`

**Changes**:
```sql
-- Modify oauth_tokens table definition:
CREATE TABLE IF NOT EXISTS oauth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expiry TEXT,
    provider TEXT DEFAULT 'gmail',  -- NEW COLUMN
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Add index for provider (add at bottom):
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_provider ON oauth_tokens(provider);
```

**Migration** (if database already exists):
```sql
-- Run this SQL against existing database:
ALTER TABLE oauth_tokens ADD COLUMN provider TEXT DEFAULT 'gmail';
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_provider ON oauth_tokens(provider);
```

**Deliverable**: Database schema updated

**Time**: 30 minutes

---

### Step 2.3: Create OutlookOAuthManager

**Action**: Implement Outlook OAuth manager

**File**: `src/email_client/outlook_oauth.py` (NEW)

**Reference**: See **[OUTLOOK_OAUTH_INTEGRATION_STRATEGY.md](OUTLOOK_OAUTH_INTEGRATION_STRATEGY.md)** Phase 2

**Template Structure**:
```python
import msal
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class OutlookOAuthManager:
    """Manages Outlook/Hotmail OAuth 2.0 authentication."""
    
    SCOPES = [
        'https://outlook.office.com/IMAP.AccessAsUser.All',
        'offline_access'
    ]
    
    def __init__(self, credentials_file: str = 'data/outlook_credentials.json'):
        # Load configuration and create MSAL app
        pass
    
    def authorize_user(self) -> Optional[Dict[str, Any]]:
        """Run OAuth authorization flow for a new user."""
        pass
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh an expired access token."""
        pass
    
    def is_token_expired(self, token_expiry: Optional[str]) -> bool:
        """Check if an access token is expired or will expire soon."""
        pass
    
    def generate_oauth2_string(self, email: str, access_token: str) -> bytes:
        """Generate OAuth2 authentication string for IMAP XOAUTH2."""
        pass
```

**Implementation Guide**: Follow **[OAUTH_PROVIDER_COMPARISON.md](OAUTH_PROVIDER_COMPARISON.md)** Section 4 and 5

**Key Methods**:
1. `__init__()` - Load config, create `PublicClientApplication`
2. `authorize_user()` - Call `acquire_token_interactive()`
3. `refresh_token()` - Call `acquire_token_silent()`
4. `is_token_expired()` - Check expiry with 5-minute buffer
5. `generate_oauth2_string()` - Create XOAUTH2 auth string

**Deliverable**: `src/email_client/outlook_oauth.py` implemented

**Time**: 1-2 days

---

### Step 2.4: Update OAuthCredentialManager

**Action**: Add provider support to OAuth credential manager

**File**: `src/email_client/gmail_oauth.py`

**Changes to `OAuthCredentialManager` class**:

```python
def store_oauth_tokens(self, email: str, access_token: str, 
                      refresh_token: str, token_expiry: Optional[str] = None,
                      provider: str = 'gmail'):  # ADD PARAMETER
    """Store OAuth tokens in encrypted form."""
    try:
        encrypted_access = self.cred.encrypt_password(access_token)
        encrypted_refresh = self.cred.encrypt_password(refresh_token)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO oauth_tokens 
                (email, access_token, refresh_token, token_expiry, provider, updated_date)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (email, encrypted_access, encrypted_refresh, token_expiry, provider))
        
        self.logger.info(f"OAuth tokens stored for {email} (provider: {provider})")
    except Exception as e:
        self.logger.error(f"Failed to store OAuth tokens for {email}: {e}")
        raise

def get_oauth_tokens(self, email: str) -> Optional[Dict[str, str]]:
    """Retrieve and decrypt OAuth tokens for an email."""
    try:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT access_token, refresh_token, token_expiry, provider
                FROM oauth_tokens WHERE email = ?
            """, (email,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            access_token = self.cred.decrypt_password(row[0])
            refresh_token = self.cred.decrypt_password(row[1])
            token_expiry = row[2]
            provider = row[3] if len(row) > 3 else 'gmail'  # HANDLE OLD RECORDS
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_expiry': token_expiry,
                'provider': provider  # ADD PROVIDER TO RETURN
            }
    except Exception as e:
        self.logger.error(f"Failed to retrieve OAuth tokens for {email}: {e}")
        return None
```

**Deliverable**: `OAuthCredentialManager` supports multiple providers

**Time**: 2-3 hours

---

### Step 2.5: Create OutlookOAuthStrategy

**Action**: Implement Outlook OAuth authentication strategy

**File**: `src/email_client/auth/outlook_oauth_auth.py` (NEW)

**Reference**: See **[OAUTH_PROVIDER_COMPARISON.md](OAUTH_PROVIDER_COMPARISON.md)** Section 6

**Template Structure** (similar to `GmailOAuthStrategy`):
```python
import imaplib
import logging
import base64
from typing import Optional, Dict, Any
from .auth_strategy import IMAPAuthStrategy
from ..outlook_oauth import OutlookOAuthManager

class OutlookOAuthStrategy(IMAPAuthStrategy):
    """Outlook OAuth 2.0 IMAP authentication strategy."""
    
    def __init__(self, oauth_manager):
        super().__init__()
        self.oauth_manager = oauth_manager
        self.outlook_oauth = OutlookOAuthManager()
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self, imap_connection: imaplib.IMAP4_SSL, email: str) -> bool:
        """Authenticate using OAuth 2.0 tokens."""
        # Similar to GmailOAuthStrategy but using OutlookOAuthManager
        pass
```

**Key Differences from Gmail**:
- Import `OutlookOAuthManager` instead of `GmailOAuthManager`
- IMAP server will be `outlook.office365.com` (handled in connection)
- Token refresh uses MSAL instead of google-auth

**Deliverable**: `src/email_client/auth/outlook_oauth_auth.py` implemented

**Time**: 1 day

---

### Step 2.6: Update AuthStrategyFactory

**Action**: Add Outlook OAuth strategy creation

**File**: `src/email_client/auth/auth_factory.py`

**Changes**:

```python
# Add import at top:
from .outlook_oauth_auth import OutlookOAuthStrategy

# Modify create_strategy method:
def create_strategy(self, email: str, provider: str, 
                   encrypted_password: Optional[str] = None) -> IMAPAuthStrategy:
    """Create appropriate authentication strategy for the given email."""
    self.logger.debug(f"Creating auth strategy for {email} (provider: {provider})")
    
    # For Gmail, prefer OAuth if tokens are available
    if provider == 'gmail':
        oauth_tokens = self.oauth_manager.get_oauth_tokens(email)
        if oauth_tokens:
            self.logger.info(f"Using Gmail OAuth authentication for {email}")
            return GmailOAuthStrategy(self.oauth_manager)
    
    # For Outlook, prefer OAuth if tokens are available (NEW)
    if provider == 'outlook':
        oauth_tokens = self.oauth_manager.get_oauth_tokens(email)
        if oauth_tokens:
            self.logger.info(f"Using Outlook OAuth authentication for {email}")
            return OutlookOAuthStrategy(self.oauth_manager)
    
    # Fall back to password authentication if available
    if encrypted_password:
        try:
            password = self.cred_manager.decrypt_password(encrypted_password)
            self.logger.info(f"Using password authentication for {email}")
            return PasswordAuthStrategy(password)
        except Exception as e:
            self.logger.error(f"Failed to decrypt password for {email}: {e}")
            raise ValueError(f"Failed to decrypt password: {e}")
    
    # No authentication method available
    error_msg = f"No authentication method available for {email}"
    self.logger.error(error_msg)
    raise ValueError(error_msg)
```

**Deliverable**: `AuthStrategyFactory` supports Outlook OAuth

**Time**: 30 minutes

---

### Step 2.7: Update IMAP Connection Settings

**Action**: Add Outlook IMAP server configuration

**File**: `src/email_client/imap_connection.py`

**Changes**:

```python
def get_imap_server(provider: str) -> tuple[str, int]:
    """Get IMAP server and port for provider."""
    servers = {
        'gmail': ('imap.gmail.com', 993),
        'outlook': ('outlook.office365.com', 993),  # ADD THIS
        'yahoo': ('imap.mail.yahoo.com', 993),
        'generic': ('imap.gmail.com', 993),  # default
    }
    return servers.get(provider.lower(), servers['generic'])
```

**Deliverable**: IMAP connections support Outlook server

**Time**: 15 minutes

**Total Phase 2 Core Time**: 1-2 weeks

---

## Phase 3: UI Integration (1 week)

### Step 3.1: Create OutlookOAuthDialog

**Action**: Implement Outlook OAuth authorization dialog

**File**: `src/ui/outlook_oauth_dialog.py` (NEW)

**Reference**: Copy and modify `src/ui/oauth_dialog.py` (GmailOAuthDialog)

**Key Changes**:
1. Import `OutlookOAuthManager` instead of `GmailOAuthManager`
2. Update dialog title: "Outlook OAuth Authorization"
3. Update instructions to mention Microsoft/Outlook
4. Update branding (colors, text)

**Template Structure**:
```python
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from src.email_client.outlook_oauth import OutlookOAuthManager, OAuthCredentialManager

class OutlookOAuthDialog(tk.Toplevel):
    """Dialog for Outlook OAuth 2.0 authorization."""
    
    def __init__(self, parent, email: str, db_manager, cred_manager):
        super().__init__(parent)
        self.email = email
        self.db = db_manager
        self.cred = cred_manager
        self.oauth_manager = OAuthCredentialManager(db_manager, cred_manager)
        self.outlook_oauth = OutlookOAuthManager()
        self.success = False
        self.logger = logging.getLogger(__name__)
        
        self.title(f"Outlook OAuth Authorization - {email}")
        # ... rest similar to GmailOAuthDialog
```

**Deliverable**: `src/ui/outlook_oauth_dialog.py` implemented

**Time**: 1 day

---

### Step 3.2: Update AccountDialog

**Action**: Add Outlook OAuth support to account setup dialog

**File**: `src/ui/settings_dialog.py`

**Changes in `AccountDialog` class**:

```python
def _detect_provider(self, event=None):
    """Auto-detect provider from email."""
    email = self.email_entry.get().lower()
    
    if '@gmail.com' in email or '@googlemail.com' in email:
        provider = "Gmail"
        self.is_gmail = True
        self.is_outlook = False  # ADD
        self.oauth_frame.grid()
        self._update_info_text()
    elif '@outlook.com' in email or '@hotmail.com' in email or '@live.com' in email:
        provider = "Outlook"
        self.is_gmail = False
        self.is_outlook = True  # ADD
        self.oauth_frame.grid()  # SHOW OAuth for Outlook too
        self._update_info_text()
    # ... rest of providers
    
    self.provider_label.config(text=provider)
    self.logger.debug(f"Detected provider: {provider} for email: {email}")

def _update_info_text(self):
    """Update info text based on provider and auth method."""
    if self.is_gmail and self.use_oauth_var.get():
        info_text = (
            "OAuth 2.0 is the recommended authentication method for Gmail.\n"
            "Click 'Start OAuth Authorization' to begin the authorization process."
        )
    elif self.is_gmail:
        info_text = (
            "Gmail no longer supports regular passwords.\n"
            "You can use OAuth 2.0 (recommended) or generate an App Password."
        )
    elif self.is_outlook and self.use_oauth_var.get():  # ADD THIS BLOCK
        info_text = (
            "OAuth 2.0 is the recommended authentication method for Outlook.\n"
            "Click 'Start OAuth Authorization' to begin the authorization process."
        )
    elif self.is_outlook:  # ADD THIS BLOCK
        info_text = (
            "Outlook supports OAuth 2.0 (recommended) or App Passwords.\n"
            "Note: IMAP must be enabled in your Outlook settings."
        )
    else:
        info_text = (
            "Note: For most providers, you must generate an App Password\n"
            "from your account security settings."
        )
    self.info_label.config(text=info_text)

def _start_oauth(self):
    """Start OAuth authorization process."""
    email = self.email_entry.get().strip()
    
    # Validate email
    if not email or not self._validate_email(email):
        messagebox.showerror("Error", "Please enter a valid email address")
        return
    
    # Determine provider and launch appropriate OAuth dialog
    if self.is_gmail:
        from src.ui.oauth_dialog import GmailOAuthDialog
        oauth_dialog = GmailOAuthDialog(self, email, self.db, self.cred)
    elif self.is_outlook:  # ADD THIS BLOCK
        from src.ui.outlook_oauth_dialog import OutlookOAuthDialog
        oauth_dialog = OutlookOAuthDialog(self, email, self.db, self.cred)
    else:
        messagebox.showerror("Error", "OAuth is only supported for Gmail and Outlook accounts")
        return
    
    self.wait_window(oauth_dialog)
    
    # Check if authorization was successful
    if oauth_dialog.was_successful():
        self.connection_tested = True
        self.save_btn.config(state=tk.NORMAL)
        self.status_label.config(
            text="✓ OAuth authorization successful!",
            foreground='green'
        )
        self.logger.info(f"OAuth authorization successful for {email}")
        
        # Automatically save the account
        self._save_oauth_account()

def _save_oauth_account(self):
    """Save OAuth account (called automatically after successful authorization)."""
    email = self.email_entry.get().strip()
    
    try:
        self.logger.info(f"Saving OAuth account: {email}")
        
        # For OAuth accounts, use a placeholder for encrypted_password
        oauth_placeholder = "OAUTH_TOKEN_AUTH"
        
        # Determine provider
        provider = "gmail" if self.is_gmail else "outlook"  # UPDATE THIS LINE
        
        # Save to accounts database
        if self.db.add_account(email, oauth_placeholder, provider):
            provider_name = "Gmail" if self.is_gmail else "Outlook"  # UPDATE THIS LINE
            messagebox.showinfo(
                "Success", 
                f"{provider_name} account {email} saved successfully!\n\n"
                f"OAuth authorization is complete and the account is ready to use."
            )
            self.logger.info(f"OAuth account saved successfully: {email}")
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save OAuth account to database.")
            self.logger.error(f"Failed to save OAuth account to database: {email}")
    except Exception as e:
        error_msg = str(e)
        messagebox.showerror("Error", f"Failed to save OAuth account: {error_msg}")
        self.logger.error(f"Error saving OAuth account {email}: {error_msg}")
```

**Deliverable**: Account dialog supports Outlook OAuth

**Time**: 1-2 days

---

### Step 3.3: Update Client Factory

**Action**: Ensure client factory creates appropriate clients for Outlook OAuth

**File**: `src/email_client/client_factory.py`

**Verify/Update**:
```python
def create_email_client(account: dict, auth_factory: AuthStrategyFactory, 
                       oauth_manager) -> Union[GmailAPIClient, IMAPClient]:
    """Create appropriate email client based on account provider."""
    logger = logging.getLogger(__name__)
    
    email = account.get('email')
    provider = account.get('provider', '').lower()
    encrypted_password = account.get('encrypted_password')
    
    # ... provider detection ...
    
    # Use Gmail API for Gmail accounts with OAuth tokens
    if provider == 'gmail':
        oauth_tokens = oauth_manager.get_oauth_tokens(email)
        if oauth_tokens:
            logger.info(f"Using Gmail API for {email}")
            return GmailAPIClient(email, oauth_manager)
    
    # For Outlook, always use IMAP (no Graph API client yet)
    # OAuth will be handled by OutlookOAuthStrategy in IMAPClient
    
    # Use IMAP for all other cases
    logger.info(f"Using IMAP for {email}")
    auth_strategy = auth_factory.create_strategy(email, provider, encrypted_password)
    return IMAPClient(email, auth_strategy, provider)
```

**Deliverable**: Client factory properly routes Outlook OAuth to IMAP

**Time**: 30 minutes

**Total Phase 3 Time**: 1 week

---

## Phase 4: Testing (1 week)

### Step 4.1: Unit Tests

**Action**: Write unit tests for new components

**Files to Create**:
1. `tests/unit/email_client/test_outlook_oauth.py`
2. `tests/unit/email_client/auth/test_outlook_oauth_auth.py`
3. `tests/unit/ui/test_outlook_oauth_dialog.py`

**Test Cases**:

**OutlookOAuthManager**:
- `test_authorize_user_success()` - Mock MSAL interactive flow
- `test_authorize_user_failure()` - Mock authorization failure
- `test_refresh_token_success()` - Mock silent token acquisition
- `test_refresh_token_failure()` - Mock refresh failure
- `test_is_token_expired()` - Test expiry logic
- `test_generate_oauth2_string()` - Test XOAUTH2 string generation

**OutlookOAuthStrategy**:
- `test_authenticate_success()` - Mock IMAP auth success
- `test_authenticate_with_token_refresh()` - Mock expired token scenario
- `test_authenticate_failure()` - Mock auth failure
- `test_retry_with_token_refresh()` - Mock retry logic

**OutlookOAuthDialog**:
- `test_dialog_creation()` - Test UI creation
- `test_start_authorization()` - Mock authorization flow
- `test_authorization_success()` - Test success handling
- `test_authorization_failure()` - Test error handling

**Deliverable**: Unit tests passing for all new components

**Time**: 2-3 days

---

### Step 4.2: Integration Tests

**Action**: Write integration tests for OAuth flow

**Files to Create**:
1. `tests/integration/test_outlook_oauth_flow.py`
2. `tests/integration/test_outlook_imap_connection.py`

**Test Cases**:
- `test_outlook_oauth_flow_end_to_end()` - Test full flow (may need mocking)
- `test_outlook_imap_with_oauth()` - Test IMAP connection with OAuth
- `test_token_refresh_cycle()` - Test token refresh
- `test_multi_account_gmail_and_outlook()` - Test mixed accounts

**Deliverable**: Integration tests passing

**Time**: 1-2 days

---

### Step 4.3: Manual Testing

**Action**: Manually test with real Outlook accounts

**Test Checklist**:

**Setup**:
- [ ] Azure app registration completed successfully
- [ ] IMAP enabled on test Outlook.com account
- [ ] IMAP enabled on test Hotmail.com account  
- [ ] IMAP enabled on test Live.com account
- [ ] `data/outlook_credentials.json` created with valid client ID

**Authorization Flow**:
- [ ] Open application
- [ ] Click File > Add Account
- [ ] Enter outlook.com email address
- [ ] OAuth option appears
- [ ] Check "Use OAuth 2.0"
- [ ] Click "Start OAuth Authorization"
- [ ] Browser opens to Microsoft login
- [ ] Sign in with Outlook account
- [ ] Consent screen shows correct permissions
- [ ] Click "Accept"
- [ ] Return to application
- [ ] Application shows "Authorization successful!"
- [ ] Account saved to database

**IMAP Connection**:
- [ ] Account appears in Settings > Accounts
- [ ] Click "Scan Inbox" with Outlook account
- [ ] Scan completes successfully
- [ ] Senders table populated with results
- [ ] No IMAP errors in logs

**Token Refresh**:
- [ ] Wait for token to expire (or manually expire in database)
- [ ] Attempt to scan inbox again
- [ ] Token automatically refreshes
- [ ] Scan completes successfully
- [ ] No re-authorization required

**Multiple Accounts**:
- [ ] Add both Gmail and Outlook accounts
- [ ] Both accounts scan successfully
- [ ] Both accounts use correct OAuth tokens
- [ ] No cross-contamination of tokens

**Error Scenarios**:
- [ ] Test with invalid client ID (should show error)
- [ ] Test with IMAP disabled (should show error)
- [ ] Test with cancelled authorization (should handle gracefully)
- [ ] Test with network error (should handle gracefully)

**UI/UX**:
- [ ] OAuth dialog shows correct branding (Microsoft/Outlook)
- [ ] Instructions are clear
- [ ] Progress indicators work
- [ ] Error messages are helpful
- [ ] Success messages are clear

**Deliverable**: All manual tests pass

**Time**: 2 days

**Total Phase 4 Time**: 1 week

---

## Phase 5: Documentation (3-5 days)

### Step 5.1: User Documentation

**Action**: Update user-facing documentation

**Files to Update**:

1. **README.md** - Add Outlook OAuth section:
```markdown
### Outlook/Hotmail (OAuth 2.0 - Recommended)

Outlook now supports OAuth 2.0 for secure authentication:

1. **Set up OAuth credentials** (one-time setup):
   - Follow the [detailed Outlook OAuth setup guide](AZURE_APP_SETUP_GUIDE.md)
   - Create an Azure app registration
   - Download OAuth credentials and save as `data/outlook_credentials.json`

2. **Enable IMAP**:
   - Go to Outlook.com settings
   - Navigate to Mail > Sync email > POP and IMAP
   - Enable IMAP access

3. **Add account in application**:
   - Click `File > Add Account`
   - Enter your Outlook/Hotmail address
   - Check "Use OAuth 2.0 (Recommended)"
   - Click "Start OAuth Authorization"
   - Browser will open for you to authorize
   - Grant permissions and return to the application

4. **That's it!**:
   - You only need to authorize once
   - Tokens are automatically refreshed
   - No passwords needed or stored
```

2. **CHANGELOG.md** - Add entry:
```markdown
### Version X.X.0 (Current)
- **NEW**: Outlook/Hotmail OAuth 2.0 authentication support
- **NEW**: Automatic token refresh for Outlook accounts
- **NEW**: Support for outlook.com, hotmail.com, and live.com addresses
- **NEW**: MSAL integration for Microsoft OAuth
- **IMPROVED**: Multi-provider OAuth architecture
- **IMPROVED**: Enhanced account setup dialog with provider detection
```

**Deliverable**: User documentation updated

**Time**: 1 day

---

### Step 5.2: Developer Documentation

**Action**: Finalize developer documentation

**Files to Review/Update**:
1. **OUTLOOK_OAUTH_INTEGRATION_STRATEGY.md** - Already created
2. **AZURE_APP_SETUP_GUIDE.md** - Already created
3. **OAUTH_PROVIDER_COMPARISON.md** - Already created
4. **OUTLOOK_INTEGRATION_ACTION_PLAN.md** - This document

**Additional Files to Create**:

**OUTLOOK_OAUTH_GUIDE.md** - Technical guide similar to GMAIL_OAUTH_GUIDE.md:
- Architecture overview
- MSAL integration details
- Token management
- Error handling
- Testing procedures

**Deliverable**: Complete developer documentation

**Time**: 2 days

**Total Phase 5 Time**: 3-5 days

---

## Phase 6: Release (1-2 days)

### Step 6.1: Final Testing

**Action**: Complete final testing round

**Checklist**:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Manual testing complete with multiple accounts
- [ ] No regressions in Gmail OAuth
- [ ] No regressions in password-based auth
- [ ] Error scenarios handled gracefully
- [ ] Documentation reviewed and accurate

**Deliverable**: Application ready for release

**Time**: 1 day

---

### Step 6.2: Prepare Release

**Action**: Prepare release artifacts

**Tasks**:
1. Update version number in `main.py` or version file
2. Update `CHANGELOG.md` with final changes
3. Create release notes
4. Tag release in git (if using version control)
5. Build executable (if applicable)

**Release Notes Template**:
```markdown
# Email Unsubscriber v[X.X.0] - Outlook OAuth Support

## 🎉 New Features

### Outlook/Hotmail OAuth 2.0 Authentication
- Added support for OAuth 2.0 authentication with Outlook.com, Hotmail.com, and Live.com accounts
- Users can now securely connect their Microsoft accounts without storing passwords
- Automatic token refresh for seamless access
- No app passwords required

## 📚 New Documentation
- Complete Azure app registration guide
- Outlook OAuth setup instructions  
- Provider comparison guide for developers

## 🔧 Technical Improvements
- Integrated Microsoft Authentication Library (MSAL)
- Extended OAuth infrastructure to support multiple providers
- Enhanced database schema for multi-provider token storage
- Improved account setup dialog with provider-specific OAuth options

## 📦 Dependencies
- Added `msal>=1.24.0` for Microsoft OAuth support

## 🐛 Bug Fixes
- No bugs fixed in this release (new feature only)

## 📖 Documentation
- See AZURE_APP_SETUP_GUIDE.md for setup instructions
- See OUTLOOK_OAUTH_INTEGRATION_STRATEGY.md for technical details

## ⚠️ Breaking Changes
- None - fully backward compatible with existing Gmail OAuth and password-based authentication
```

**Deliverable**: Release prepared

**Time**: 1 day

**Total Phase 6 Time**: 1-2 days

---

## Complete Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **1. External Setup** | 2-4 hours | Azure app registration, config file |
| **2. Core Implementation** | 2-3 weeks | OAuth manager, strategy, database |
| **3. UI Integration** | 1 week | OAuth dialog, account setup updates |
| **4. Testing** | 1 week | Unit tests, integration tests, manual tests |
| **5. Documentation** | 3-5 days | User docs, developer docs |
| **6. Release** | 1-2 days | Final testing, release prep |
| **Total** | **4-5 weeks** | Complete Outlook OAuth integration |

---

## Risk Mitigation

### Potential Risks and Mitigation Strategies

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| MSAL library compatibility issues | High | Low | Test thoroughly, use stable version |
| Azure app registration complexity | Medium | Medium | Follow detailed guide, test early |
| IMAP not enabled by users | Medium | Medium | Clear documentation, helpful error messages |
| Token refresh failures | High | Low | Robust error handling, prompt re-auth |
| Breaking existing Gmail OAuth | Critical | Low | Thorough testing, backward compatibility |
| MSAL conflicts with google-auth | Medium | Low | Test with both libraries, use virtual env |

---

## Success Criteria

### Minimum Viable Product (MVP)

- [ ] Users can authorize Outlook.com accounts via OAuth 2.0
- [ ] Users can authorize Hotmail.com accounts via OAuth 2.0
- [ ] Users can authorize Live.com accounts via OAuth 2.0
- [ ] Tokens are securely stored and encrypted
- [ ] Tokens automatically refresh before expiry
- [ ] IMAP connections work with OAuth tokens
- [ ] Account setup dialog shows OAuth option for Outlook accounts
- [ ] Existing Gmail OAuth functionality unchanged
- [ ] Existing password-based auth unchanged
- [ ] Basic error handling for common scenarios

### Nice to Have (Future Enhancements)

- [ ] Microsoft Graph API support (alternative to IMAP)
- [ ] Batch token refresh for multiple accounts
- [ ] OAuth token dashboard in UI
- [ ] Publisher verification for Azure app (removes "unverified" warning)
- [ ] Yahoo Mail OAuth support

---

## Getting Help

### Resources

1. **Microsoft Documentation**:
   - MSAL Python: https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-v2-python-desktop
   - IMAP OAuth: https://docs.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth
   - Azure AD: https://docs.microsoft.com/en-us/azure/active-directory/develop/

2. **Code Examples**:
   - Existing Gmail implementation in codebase
   - MSAL samples: https://github.com/AzureAD/microsoft-authentication-library-for-python

3. **Community Support**:
   - Stack Overflow: `[msal] [python] [oauth2]` tags
   - Microsoft Q&A: https://docs.microsoft.com/en-us/answers/

---

## Next Steps

### Immediate Actions (Today)

1. **Read All Documentation**:
   - [ ] Read OUTLOOK_OAUTH_INTEGRATION_STRATEGY.md
   - [ ] Read AZURE_APP_SETUP_GUIDE.md
   - [ ] Read OAUTH_PROVIDER_COMPARISON.md
   - [ ] Read this action plan completely

2. **Complete External Setup**:
   - [ ] Follow AZURE_APP_SETUP_GUIDE.md step by step
   - [ ] Create Azure app registration
   - [ ] Save Application (client) ID
   - [ ] Create `data/outlook_credentials.json`
   - [ ] Enable IMAP on test account

3. **Verify Setup**:
   - [ ] Review setup checklist in Phase 1
   - [ ] Ensure all external setup is complete
   - [ ] Test Azure app registration (try logging in)

### Short-term Actions (This Week)

1. **Install Dependencies**:
   - [ ] Install MSAL: `pip install msal>=1.24.0`
   - [ ] Update requirements.txt

2. **Start Implementation**:
   - [ ] Update database schema
   - [ ] Create `OutlookOAuthManager` class
   - [ ] Test basic MSAL flow with sample code

3. **Review Existing Code**:
   - [ ] Study `GmailOAuthManager` implementation
   - [ ] Study `GmailOAuthStrategy` implementation
   - [ ] Study `GmailOAuthDialog` implementation

### Medium-term Actions (Next 2-3 Weeks)

1. **Complete Core Implementation** (Phase 2)
2. **Complete UI Integration** (Phase 3)
3. **Begin Testing** (Phase 4)

### Long-term Actions (Weeks 4-5)

1. **Complete Testing** (Phase 4)
2. **Complete Documentation** (Phase 5)
3. **Release** (Phase 6)

---

## Questions Checklist

Before starting implementation, ensure you can answer these questions:

### Strategy Questions
- [ ] Do I understand the difference between Gmail and Outlook OAuth?
- [ ] Do I understand MSAL vs google-auth libraries?
- [ ] Do I understand the XOAUTH2 SASL authentication mechanism?
- [ ] Do I know where tokens are stored and how they're encrypted?

### Setup Questions
- [ ] Have I completed Azure app registration?
- [ ] Do I have the Application (client) ID?
- [ ] Have I configured all required API permissions?
- [ ] Have I enabled public client flows?
- [ ] Have I created `data/outlook_credentials.json` with correct client ID?
- [ ] Have I enabled IMAP on my test Outlook account?

### Implementation Questions
- [ ] Do I know which files to create?
- [ ] Do I know which files to modify?
- [ ] Do I understand how the OAuth flow works?
- [ ] Do I understand how token refresh works?
- [ ] Do I understand how IMAP authentication works?

### Testing Questions
- [ ] Do I know how to test the OAuth flow?
- [ ] Do I have test Outlook accounts ready?
- [ ] Do I know how to test token refresh?
- [ ] Do I know how to test error scenarios?

If you answered "No" to any question, review the relevant documentation before proceeding.

---

## Conclusion

You now have a complete action plan for integrating Outlook/Hotmail OAuth 2.0 into the Email Unsubscriber application. The integration mirrors the existing Gmail OAuth implementation and should take approximately 4-5 weeks to complete.

**Key Success Factors**:
1. Follow the action plan step by step
2. Complete external setup first (Azure)
3. Test early and often
4. Maintain backward compatibility
5. Document as you go

**Remember**:
- The Gmail OAuth implementation is your best reference
- MSAL is similar to google-auth but with different method names
- XOAUTH2 SASL authentication is identical for both providers
- Take it one phase at a time

Good luck with the implementation! 🚀
