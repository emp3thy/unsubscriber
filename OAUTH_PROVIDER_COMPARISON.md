# OAuth Provider Comparison: Gmail vs Outlook

## Quick Reference Guide

This document provides a side-by-side comparison of Gmail and Outlook OAuth implementations for the Email Unsubscriber application.

---

## Overview Comparison

| Aspect | Gmail | Outlook/Hotmail |
|--------|-------|-----------------|
| **Provider** | Google | Microsoft |
| **OAuth Library** | `google-auth-oauthlib` | `msal` (Microsoft Authentication Library) |
| **Registration Portal** | Google Cloud Console | Azure Portal |
| **Personal Accounts** | @gmail.com, @googlemail.com | @outlook.com, @hotmail.com, @live.com |
| **Setup Complexity** | Medium | Medium |
| **Setup Time** | 20-30 minutes | 20-30 minutes |
| **Cost** | Free | Free |

---

## 1. OAuth Registration Setup

### Gmail (Google Cloud Console)

```
Portal: https://console.cloud.google.com/
Steps:
1. Create new project
2. Enable Gmail API
3. Configure OAuth consent screen
4. Create OAuth client ID (Desktop application)
5. Download credentials JSON
```

**Credentials File Structure**:
```json
{
  "installed": {
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxx",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}
```

**File Location**: `data/gmail_credentials.json`

---

### Outlook (Azure Portal)

```
Portal: https://portal.azure.com/
Steps:
1. Navigate to App Registrations
2. Create new app registration
3. Configure API permissions
4. Enable public client flows
5. Copy Application (client) ID
```

**Credentials File Structure**:
```json
{
  "client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "authority": "https://login.microsoftonline.com/common",
  "scope": [
    "https://outlook.office.com/IMAP.AccessAsUser.All",
    "offline_access"
  ],
  "redirect_uri": "http://localhost"
}
```

**File Location**: `data/outlook_credentials.json`

**Key Difference**: 
- Gmail uses client secret (confidential client)
- Outlook uses public client (no client secret)

---

## 2. OAuth Scopes

### Gmail

```python
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
```

**Permissions Granted**:
- Read all email (IMAP)
- Send email
- Delete email
- Modify labels
- Full Gmail API access

**Scope URL Format**: googleapis.com (uses Google's unified OAuth scope)

---

### Outlook

```python
SCOPES = [
    'https://outlook.office.com/IMAP.AccessAsUser.All',
    'offline_access'
]
```

**Permissions Granted**:
- Read email (IMAP)
- Send email (IMAP)
- Delete email (IMAP)
- IMAP access only

**Alternative (Graph API)**:
```python
SCOPES = [
    'https://graph.microsoft.com/Mail.ReadWrite',
    'offline_access'
]
```

**Scope URL Format**: outlook.office.com or graph.microsoft.com

**Key Difference**:
- Gmail: Single scope for full access
- Outlook: Separate scopes for IMAP vs Graph API
- Outlook: `offline_access` required for refresh tokens

---

## 3. Python Libraries

### Gmail

**Installation**:
```bash
pip install google-auth>=2.23.0
pip install google-auth-oauthlib>=1.1.0
pip install google-auth-httplib2>=0.1.1
pip install google-api-python-client>=2.100.0
```

**Import Statements**:
```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
```

---

### Outlook

**Installation**:
```bash
pip install msal>=1.24.0
```

**Import Statements**:
```python
from msal import PublicClientApplication
```

**Key Difference**: 
- Gmail: Multiple packages, more complex
- Outlook: Single package (msal), simpler

---

## 4. Authorization Flow Code

### Gmail

```python
from google_auth_oauthlib.flow import InstalledAppFlow

def authorize_user(self):
    flow = InstalledAppFlow.from_client_secrets_file(
        'data/gmail_credentials.json',
        scopes=['https://www.googleapis.com/auth/gmail.modify']
    )
    
    credentials = flow.run_local_server(port=0)
    
    return {
        'access_token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_expiry': credentials.expiry.isoformat()
    }
```

**Flow Type**: `InstalledAppFlow` - Starts local HTTP server, opens browser

---

### Outlook

```python
from msal import PublicClientApplication

def authorize_user(self):
    app = PublicClientApplication(
        client_id="your-client-id",
        authority="https://login.microsoftonline.com/common"
    )
    
    result = app.acquire_token_interactive(
        scopes=[
            "https://outlook.office.com/IMAP.AccessAsUser.All",
            "offline_access"
        ]
    )
    
    if "access_token" in result:
        return {
            'access_token': result['access_token'],
            'refresh_token': result.get('refresh_token'),
            'token_expiry': self._calculate_expiry(result.get('expires_in', 3600))
        }
    return None
```

**Flow Type**: `PublicClientApplication` - Interactive browser-based flow

**Key Difference**:
- Gmail: `run_local_server()` - automatic
- Outlook: `acquire_token_interactive()` - more explicit
- Gmail: Returns `Credentials` object
- Outlook: Returns dictionary with token info

---

## 5. Token Refresh Code

### Gmail

```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def refresh_token(self, refresh_token: str):
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=self._get_client_id(),
        client_secret=self._get_client_secret()
    )
    
    request = Request()
    credentials.refresh(request)
    
    return {
        'access_token': credentials.token,
        'refresh_token': credentials.refresh_token or refresh_token,
        'token_expiry': credentials.expiry.isoformat()
    }
```

**Method**: Create `Credentials` object, call `refresh()`

---

### Outlook

```python
def refresh_token(self, refresh_token: str):
    # Get cached accounts
    accounts = self.app.get_accounts()
    
    if accounts:
        # Silent token acquisition
        result = self.app.acquire_token_silent(
            scopes=[
                "https://outlook.office.com/IMAP.AccessAsUser.All",
                "offline_access"
            ],
            account=accounts[0]
        )
        
        if "access_token" in result:
            return {
                'access_token': result['access_token'],
                'refresh_token': result.get('refresh_token', refresh_token),
                'token_expiry': self._calculate_expiry(result.get('expires_in', 3600))
            }
    
    return None
```

**Method**: Use cached account, call `acquire_token_silent()`

**Key Difference**:
- Gmail: Manual `Credentials` object creation
- Outlook: Uses MSAL's account cache
- Gmail: Requires client ID and secret
- Outlook: No client secret needed

---

## 6. IMAP Configuration

### Gmail

```python
# Connection settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# Authentication
auth_string = f'user={email}\x01auth=Bearer {access_token}\x01\x01'
auth_bytes = base64.b64encode(auth_string.encode('utf-8'))
imap.authenticate('XOAUTH2', lambda x: auth_bytes)
```

**IMAP Server**: `imap.gmail.com`  
**Port**: `993`  
**Encryption**: SSL/TLS  
**Auth Mechanism**: XOAUTH2 SASL

---

### Outlook

```python
# Connection settings
IMAP_SERVER = 'outlook.office365.com'
IMAP_PORT = 993

# Authentication (same as Gmail)
auth_string = f'user={email}\x01auth=Bearer {access_token}\x01\x01'
auth_bytes = base64.b64encode(auth_string.encode('utf-8'))
imap.authenticate('XOAUTH2', lambda x: auth_bytes)
```

**IMAP Server**: `outlook.office365.com`  
**Port**: `993`  
**Encryption**: SSL/TLS  
**Auth Mechanism**: XOAUTH2 SASL (same as Gmail)

**Key Difference**:
- Only the IMAP server hostname differs
- Authentication mechanism is identical

---

## 7. Token Expiry

### Gmail

```python
def is_token_expired(self, token_expiry: Optional[str]) -> bool:
    if not token_expiry:
        return True
    
    expiry_time = datetime.fromisoformat(token_expiry.replace('Z', '+00:00'))
    buffer_time = datetime.now(expiry_time.tzinfo) + timedelta(minutes=5)
    return expiry_time <= buffer_time
```

**Token Lifetime**: ~1 hour  
**Refresh Buffer**: 5 minutes before expiry  
**Refresh Token**: Long-lived (can be revoked)

---

### Outlook

```python
def is_token_expired(self, token_expiry: Optional[str]) -> bool:
    if not token_expiry:
        return True
    
    expiry_time = datetime.fromisoformat(token_expiry.replace('Z', '+00:00'))
    buffer_time = datetime.now(expiry_time.tzinfo) + timedelta(minutes=5)
    return expiry_time <= buffer_time
```

**Token Lifetime**: ~1 hour  
**Refresh Buffer**: 5 minutes before expiry  
**Refresh Token**: Long-lived (can be revoked)

**Key Difference**: None - identical logic

---

## 8. Error Handling

### Gmail

**Common Errors**:
```python
# Missing credentials file
FileNotFoundError: "OAuth credentials file not found"

# Authorization cancelled
Exception: "Authorization was cancelled"

# Invalid token
google.auth.exceptions.RefreshError: "invalid_grant"

# IMAP authentication failure
imaplib.IMAP4.error: "b'[AUTHENTICATIONFAILED] Invalid credentials'"
```

---

### Outlook

**Common Errors**:
```python
# Missing configuration
FileNotFoundError: "Outlook credentials file not found"

# Authorization cancelled
Exception: "User cancelled authorization"

# Invalid token
msal.exceptions.MsalServiceError: "invalid_grant"

# IMAP authentication failure
imaplib.IMAP4.error: "b'[AUTHENTICATIONFAILED] Invalid credentials'"

# IMAP not enabled
Exception: "IMAP not available for this account"
```

**Key Difference**:
- Gmail: `google.auth.exceptions`
- Outlook: `msal.exceptions`
- Outlook: Additional "IMAP not enabled" error

---

## 9. Database Schema

### Shared Schema

Both providers use the same `oauth_tokens` table:

```sql
CREATE TABLE oauth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    access_token TEXT NOT NULL,      -- Encrypted
    refresh_token TEXT NOT NULL,     -- Encrypted
    token_expiry TEXT,              -- ISO datetime string
    provider TEXT DEFAULT 'gmail',  -- 'gmail' or 'outlook'
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Addition**: `provider` column to distinguish token types

---

## 10. User Experience

### Gmail OAuth Flow

```
1. User clicks "Start OAuth Authorization"
2. Browser opens to Google sign-in
3. User signs in (if not already)
4. Google shows consent screen:
   - "Email Unsubscriber wants to access your Gmail"
   - "Read, compose, send, and permanently delete email"
5. User clicks "Allow"
6. Browser shows "You may close this window"
7. Application shows "Authorization successful!"
```

**Consent Screen**: Shows app name, requested permissions  
**Warning**: May show "App isn't verified" for unverified apps  
**Duration**: ~30-60 seconds

---

### Outlook OAuth Flow

```
1. User clicks "Start OAuth Authorization"
2. Browser opens to Microsoft sign-in
3. User signs in (if not already)
4. Microsoft shows consent screen:
   - "Email Unsubscriber wants to access your email via IMAP"
   - Permissions listed
5. User clicks "Accept"
6. Browser redirects to localhost
7. Application shows "Authorization successful!"
```

**Consent Screen**: Shows app name, requested permissions  
**Warning**: May show "App isn't verified" for unverified apps  
**Duration**: ~30-60 seconds

**Key Difference**:
- Gmail: "You may close this window" message
- Outlook: Automatic redirect to localhost
- Similar overall experience

---

## 11. File Structure Comparison

### Gmail Files

```
src/email_client/
├── gmail_oauth.py
│   ├── GmailOAuthManager
│   └── OAuthCredentialManager
└── auth/
    └── gmail_oauth_auth.py
        └── GmailOAuthStrategy

src/ui/
└── oauth_dialog.py
    └── GmailOAuthDialog

data/
└── gmail_credentials.json
```

---

### Outlook Files (Proposed)

```
src/email_client/
├── outlook_oauth.py [NEW]
│   └── OutlookOAuthManager
├── oauth_manager.py [REFACTORED]
│   └── OAuthCredentialManager (provider-agnostic)
└── auth/
    └── outlook_oauth_auth.py [NEW]
        └── OutlookOAuthStrategy

src/ui/
└── outlook_oauth_dialog.py [NEW]
    └── OutlookOAuthDialog

data/
├── gmail_credentials.json
└── outlook_credentials.json [NEW]
```

---

## 12. Testing Requirements

### Gmail Tests

```python
# Unit tests
test_gmail_oauth_manager.py
test_gmail_oauth_strategy.py
test_gmail_oauth_dialog.py

# Integration tests
test_gmail_oauth_flow_end_to_end.py
test_gmail_imap_with_oauth.py

# Manual tests
- Test with personal Gmail account
- Test token refresh
- Test re-authorization
```

---

### Outlook Tests

```python
# Unit tests
test_outlook_oauth_manager.py [NEW]
test_outlook_oauth_strategy.py [NEW]
test_outlook_oauth_dialog.py [NEW]

# Integration tests
test_outlook_oauth_flow_end_to_end.py [NEW]
test_outlook_imap_with_oauth.py [NEW]

# Manual tests
- Test with Outlook.com account [NEW]
- Test with Hotmail.com account [NEW]
- Test with Live.com account [NEW]
- Test token refresh [NEW]
- Test re-authorization [NEW]
```

---

## 13. Dependencies

### Gmail Dependencies

```python
# requirements.txt
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.100.0
```

**Total Packages**: 4  
**Total Size**: ~15-20 MB

---

### Outlook Dependencies

```python
# requirements.txt (addition)
msal>=1.24.0
```

**Total Packages**: 1 (plus dependencies)  
**Total Size**: ~5-10 MB

**Key Difference**:
- Gmail: 4 packages, larger
- Outlook: 1 package, smaller

---

## 14. Security Comparison

### Gmail Security

- ✅ Client secret required (confidential client)
- ✅ Tokens encrypted with Fernet
- ✅ Tokens stored in local SQLite database
- ✅ Automatic token refresh
- ✅ User can revoke access via Google Account settings
- ✅ Scope limitation to mail only

---

### Outlook Security

- ✅ No client secret needed (public client)
- ✅ Tokens encrypted with Fernet
- ✅ Tokens stored in local SQLite database
- ✅ Automatic token refresh
- ✅ User can revoke access via Microsoft Account settings
- ✅ Scope limitation to IMAP or Graph API

**Key Difference**:
- Gmail: Uses client secret
- Outlook: Public client (no secret)
- Outlook: Considered more secure for desktop apps (no secret to steal)

---

## 15. Advantages and Disadvantages

### Gmail OAuth

**Advantages**:
- ✅ Well-documented
- ✅ Widely used (lots of examples online)
- ✅ Gmail API provides rich features
- ✅ Mature library ecosystem

**Disadvantages**:
- ❌ Multiple dependencies
- ❌ Google Cloud Console can be complex
- ❌ "App isn't verified" warning for unverified apps
- ❌ Requires client secret (potential security concern)

---

### Outlook OAuth

**Advantages**:
- ✅ Single dependency (MSAL)
- ✅ Public client (no client secret)
- ✅ Azure portal is user-friendly
- ✅ Supports personal and organizational accounts
- ✅ Microsoft Graph API available (powerful alternative)

**Disadvantages**:
- ❌ Less familiar to many developers
- ❌ IMAP must be explicitly enabled by users
- ❌ "App isn't verified" warning for unverified apps
- ❌ Documentation can be scattered

---

## Summary

### Similarities

1. **OAuth 2.0 Flow**: Both use standard OAuth 2.0 authorization code flow
2. **XOAUTH2 SASL**: Both use same IMAP authentication mechanism
3. **Token Lifecycle**: Both have ~1 hour access tokens, long-lived refresh tokens
4. **User Experience**: Both open browser for authorization, similar consent screens
5. **Security**: Both encrypt and store tokens locally
6. **Architecture**: Both follow similar patterns (Manager, Strategy, Dialog)

### Differences

1. **Libraries**: Google libraries vs MSAL
2. **Client Type**: Confidential (Gmail) vs Public (Outlook)
3. **Registration**: Google Cloud Console vs Azure Portal
4. **Scopes**: Single scope (Gmail) vs multiple scopes (Outlook)
5. **IMAP Server**: Different hostnames
6. **User Setup**: Gmail works out of box, Outlook requires IMAP enablement

### Recommendation

**For Implementation**:
1. Follow Gmail implementation pattern closely
2. Use MSAL for Outlook instead of google-auth libraries
3. Reuse shared components (OAuthCredentialManager, database schema)
4. Keep similar user experience for both providers
5. Start with IMAP (easier), consider Graph API later

**Expected Implementation Time**:
- **Setup**: 2-4 hours (Azure registration)
- **Core Implementation**: 1-2 weeks (OAuth manager, strategy, UI)
- **Testing**: 1 week
- **Total**: 3-4 weeks

---

## Quick Reference: Code Snippets

### Creating OAuth Manager

**Gmail**:
```python
from src.email_client.gmail_oauth import GmailOAuthManager
manager = GmailOAuthManager('data/gmail_credentials.json')
```

**Outlook**:
```python
from src.email_client.outlook_oauth import OutlookOAuthManager
manager = OutlookOAuthManager('data/outlook_credentials.json')
```

### Authorizing User

**Gmail**:
```python
tokens = gmail_manager.authorize_user()
```

**Outlook**:
```python
tokens = outlook_manager.authorize_user()
```

### Refreshing Token

**Gmail**:
```python
new_tokens = gmail_manager.refresh_token(refresh_token)
```

**Outlook**:
```python
new_tokens = outlook_manager.refresh_token(refresh_token)
```

### Creating Auth Strategy

**Gmail**:
```python
strategy = GmailOAuthStrategy(oauth_credential_manager)
```

**Outlook**:
```python
strategy = OutlookOAuthStrategy(oauth_credential_manager)
```

### Connecting to IMAP

**Gmail**:
```python
client = IMAPClient(email, gmail_oauth_strategy, 'gmail')
client.connect()
```

**Outlook**:
```python
client = IMAPClient(email, outlook_oauth_strategy, 'outlook')
client.connect()
```

---

**End of Comparison**

This document should be updated as implementation progresses and new differences are discovered.
