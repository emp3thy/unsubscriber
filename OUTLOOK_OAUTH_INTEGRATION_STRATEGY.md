# Outlook/Hotmail OAuth 2.0 Integration Strategy

## Executive Summary

This document outlines the strategy for integrating Outlook.com and Hotmail.com email accounts into the Email Unsubscriber application using OAuth 2.0 authentication, mirroring the existing Gmail OAuth implementation.

**Goal**: Enable users to register outlook.com or hotmail.com email addresses using OAuth 2.0 in the same way they currently register Gmail accounts, allowing the application to scan and manage emails from these accounts.

---

## Current Gmail Integration Overview

### Architecture Components

The Gmail integration uses the following components:

1. **GmailOAuthManager** (`src/email_client/gmail_oauth.py`)
   - Handles OAuth authorization flow using Google's `InstalledAppFlow`
   - Manages token refresh operations
   - Generates IMAP XOAUTH2 authentication strings
   - Scopes: `https://www.googleapis.com/auth/gmail.modify`

2. **OAuthCredentialManager** (`src/email_client/gmail_oauth.py`)
   - Encrypts and stores OAuth tokens in database
   - Retrieves and decrypts tokens for use
   - Database table: `oauth_tokens`

3. **GmailOAuthStrategy** (`src/email_client/auth/gmail_oauth_auth.py`)
   - Implements `IMAPAuthStrategy` interface
   - Handles XOAUTH2 SASL authentication for IMAP
   - Automatically refreshes expired tokens

4. **GmailOAuthDialog** (`src/ui/oauth_dialog.py`)
   - User interface for OAuth authorization
   - Manages browser-based authorization flow
   - Provides user feedback during authorization

5. **Database Schema** (`oauth_tokens` table)
   ```sql
   CREATE TABLE oauth_tokens (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       email TEXT UNIQUE NOT NULL,
       access_token TEXT NOT NULL,      -- Encrypted
       refresh_token TEXT NOT NULL,     -- Encrypted
       token_expiry TEXT,              -- ISO datetime string
       updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
   );
   ```

### OAuth Flow

1. User initiates OAuth from Account Setup dialog
2. Browser opens to Google's OAuth endpoint
3. User grants permissions
4. Tokens (access + refresh) are received and encrypted
5. Tokens stored in database
6. On subsequent connections:
   - Tokens retrieved and decrypted
   - Access token checked for expiry (5-minute buffer)
   - If expired, refresh token used to get new access token
   - XOAUTH2 SASL authentication with IMAP

---

## Microsoft OAuth 2.0 for Outlook/Hotmail

### Microsoft Identity Platform Overview

Microsoft uses the **Microsoft Authentication Library (MSAL)** for OAuth 2.0 authentication. For Outlook/Hotmail integration, we'll use:

- **MSAL for Python** (`msal` library)
- **Microsoft Graph API** for email operations (optional, for API-based access)
- **IMAP with OAuth 2.0** (XOAUTH2 SASL) for IMAP-based access

### Key Differences from Gmail

| Aspect | Gmail | Outlook/Hotmail |
|--------|-------|-----------------|
| **OAuth Library** | `google-auth-oauthlib` | `msal` |
| **OAuth Endpoint** | Google Cloud Console | Azure AD / Microsoft Entra |
| **App Registration** | Google Cloud Project | Azure App Registration |
| **Scopes** | `https://mail.google.com/` | `https://outlook.office.com/IMAP.AccessAsUser.All`<br>`offline_access` |
| **Token Endpoint** | `https://oauth2.googleapis.com/token` | `https://login.microsoftonline.com/common/oauth2/v2.0/token` |
| **Authorization Endpoint** | `https://accounts.google.com/o/oauth2/auth` | `https://login.microsoftonline.com/common/oauth2/v2.0/authorize` |
| **IMAP Server** | `imap.gmail.com:993` | `outlook.office365.com:993` |
| **IMAP Auth** | XOAUTH2 SASL | XOAUTH2 SASL |
| **API Alternative** | Gmail API | Microsoft Graph API |

### Required Scopes

For IMAP access to Outlook/Hotmail:
- `https://outlook.office.com/IMAP.AccessAsUser.All` - Full IMAP access
- `offline_access` - Allows refresh token to be issued

For Microsoft Graph API access (alternative to IMAP):
- `https://graph.microsoft.com/Mail.ReadWrite` - Read and write access to mail
- `offline_access` - Allows refresh token to be issued

### MSAL Public Client Application

Unlike Gmail's `InstalledAppFlow`, MSAL uses `PublicClientApplication`:

```python
from msal import PublicClientApplication

app = PublicClientApplication(
    client_id="your-application-id",
    authority="https://login.microsoftonline.com/common"
)

# Interactive authorization
result = app.acquire_token_interactive(
    scopes=["https://outlook.office.com/IMAP.AccessAsUser.All", "offline_access"]
)

# Token refresh
result = app.acquire_token_silent(
    scopes=["https://outlook.office.com/IMAP.AccessAsUser.All"],
    account=account
)
```

---

## Proposed Architecture

### New Components to Create

1. **OutlookOAuthManager** (`src/email_client/outlook_oauth.py`)
   - Similar to `GmailOAuthManager`
   - Uses MSAL `PublicClientApplication`
   - Handles authorization and token refresh
   - Generates XOAUTH2 authentication strings

2. **OutlookOAuthStrategy** (`src/email_client/auth/outlook_oauth_auth.py`)
   - Similar to `GmailOAuthStrategy`
   - Implements `IMAPAuthStrategy` interface
   - Handles XOAUTH2 SASL authentication
   - Automatically refreshes expired tokens

3. **OutlookOAuthDialog** (`src/ui/outlook_oauth_dialog.py`)
   - Similar to `GmailOAuthDialog`
   - User interface for Outlook OAuth authorization
   - Manages browser-based authorization flow

4. **Unified OAuth Credentials Storage**
   - Extend existing `oauth_tokens` table with a `provider` column:
   ```sql
   ALTER TABLE oauth_tokens ADD COLUMN provider TEXT DEFAULT 'gmail';
   CREATE INDEX idx_oauth_tokens_provider ON oauth_tokens(provider);
   ```
   - This allows storing both Gmail and Outlook tokens in the same table

### Modified Components

1. **OAuthCredentialManager** (`src/email_client/gmail_oauth.py`)
   - Rename to more generic name or keep as-is but add provider support
   - Modify methods to support multiple providers
   - Add `provider` parameter to all methods

2. **AuthStrategyFactory** (`src/email_client/auth/auth_factory.py`)
   - Extend to create `OutlookOAuthStrategy` for Outlook accounts
   - Check for OAuth tokens for both Gmail and Outlook providers

3. **AccountDialog** (`src/ui/settings_dialog.py`)
   - Show OAuth option for Outlook/Hotmail addresses
   - Allow user to choose OAuth or app password
   - Launch appropriate OAuth dialog based on provider

4. **Client Factory** (`src/email_client/client_factory.py`)
   - Support Outlook OAuth in provider detection
   - Create appropriate client based on provider and auth method

### Code Structure Comparison

**Current Gmail Structure:**
```
src/email_client/
├── gmail_oauth.py (GmailOAuthManager, OAuthCredentialManager)
├── auth/
│   ├── gmail_oauth_auth.py (GmailOAuthStrategy)
│   └── auth_factory.py (creates strategies)
src/ui/
└── oauth_dialog.py (GmailOAuthDialog)
```

**Proposed Multi-Provider Structure:**
```
src/email_client/
├── gmail_oauth.py (GmailOAuthManager)
├── outlook_oauth.py (OutlookOAuthManager) [NEW]
├── oauth_manager.py (Unified OAuthCredentialManager) [REFACTORED]
├── auth/
│   ├── gmail_oauth_auth.py (GmailOAuthStrategy)
│   ├── outlook_oauth_auth.py (OutlookOAuthStrategy) [NEW]
│   └── auth_factory.py (creates strategies for both)
src/ui/
├── oauth_dialog.py (GmailOAuthDialog)
└── outlook_oauth_dialog.py (OutlookOAuthDialog) [NEW]
```

---

## External Setup Requirements

### Azure App Registration (One-Time Setup)

To use OAuth 2.0 with Outlook/Hotmail, you need to register an application in the Microsoft Azure portal.

#### Step 1: Create Azure Account and Register Application

1. **Sign in to Azure Portal**
   - Go to https://portal.azure.com/
   - Sign in with a Microsoft account (can be any Microsoft account)

2. **Navigate to App Registrations**
   - In the Azure portal, search for "App registrations"
   - Click "New registration"

3. **Configure Application**
   - **Name**: `Email Unsubscriber` (or any name)
   - **Supported account types**: 
     - Select "Accounts in any organizational directory and personal Microsoft accounts"
     - This allows both Outlook.com personal accounts and organizational accounts
   - **Redirect URI**: 
     - Select "Public client/native (mobile & desktop)"
     - Enter: `http://localhost` (MSAL will handle the redirect)
   - Click "Register"

4. **Note the Application (client) ID**
   - After registration, you'll see the "Application (client) ID"
   - **Save this ID** - you'll need it in your application
   - Example: `12345678-1234-1234-1234-123456789abc`

#### Step 2: Configure API Permissions

1. **Go to API Permissions**
   - In your app registration, click "API permissions" in the left sidebar

2. **Add Permissions**
   - Click "Add a permission"
   - Select "Microsoft Graph"
   - Choose "Delegated permissions"
   - Add these permissions:
     - `IMAP.AccessAsUser.All` (for IMAP access)
     - `offline_access` (for refresh tokens)
   - Alternatively, if using Microsoft Graph API instead of IMAP:
     - `Mail.ReadWrite`
     - `offline_access`

3. **Grant Admin Consent** (Optional)
   - If you're the admin of your tenant, you can grant consent
   - For personal Microsoft accounts, user consent is sufficient

#### Step 3: Configure Authentication Settings

1. **Go to Authentication**
   - In your app registration, click "Authentication" in the left sidebar

2. **Configure Platform**
   - Under "Platform configurations", ensure "Mobile and desktop applications" is configured
   - Add redirect URI: `http://localhost`
   - Under "Advanced settings", enable "Allow public client flows" = Yes

3. **Save Changes**

#### Step 4: Enable IMAP on User Accounts

Users must enable IMAP on their Outlook.com accounts:

1. Go to https://outlook.live.com/mail/
2. Click Settings (gear icon) > View all Outlook settings
3. Go to Mail > Sync email
4. Under "POP and IMAP", ensure IMAP is enabled

#### Step 5: Create Configuration File

Create a configuration file `data/outlook_credentials.json`:

```json
{
  "client_id": "your-application-id-here",
  "authority": "https://login.microsoftonline.com/common",
  "scope": [
    "https://outlook.office.com/IMAP.AccessAsUser.All",
    "offline_access"
  ],
  "redirect_uri": "http://localhost"
}
```

**Note**: Unlike Gmail, Outlook OAuth for public clients doesn't require a client secret.

---

## Implementation Steps

### Phase 1: Setup and Dependencies

1. **Install MSAL**
   - Add to `requirements.txt`:
   ```
   msal>=1.24.0
   ```

2. **Create Configuration Files**
   - Add `data/outlook_credentials.json` with Azure app registration details
   - Update `.gitignore` to exclude this file

3. **Database Schema Update**
   - Add migration to add `provider` column to `oauth_tokens` table
   - Update indexes as needed

### Phase 2: Core OAuth Manager

1. **Create `OutlookOAuthManager`**
   - Implement in `src/email_client/outlook_oauth.py`
   - Methods:
     - `authorize_user()` - Run MSAL interactive flow
     - `refresh_token()` - Use MSAL silent token acquisition
     - `is_token_expired()` - Check token expiry
     - `generate_oauth2_string()` - Create XOAUTH2 auth string

2. **Example Implementation**:

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
        self.credentials_file = credentials_file
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(credentials_file, 'r') as f:
            config = json.load(f)
        
        self.client_id = config['client_id']
        self.authority = config.get('authority', 'https://login.microsoftonline.com/common')
        
        # Create MSAL application
        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority
        )
    
    def authorize_user(self) -> Optional[Dict[str, Any]]:
        """Run OAuth authorization flow for a new user."""
        try:
            # Acquire token interactively
            result = self.app.acquire_token_interactive(
                scopes=self.SCOPES
            )
            
            if "access_token" in result:
                tokens = {
                    'access_token': result['access_token'],
                    'refresh_token': result.get('refresh_token'),
                    'token_expiry': self._calculate_expiry(result.get('expires_in', 3600))
                }
                self.logger.info("OAuth authorization completed successfully")
                return tokens
            else:
                error = result.get("error_description", "Unknown error")
                self.logger.error(f"OAuth authorization failed: {error}")
                return None
                
        except Exception as e:
            self.logger.error(f"OAuth authorization failed: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh an expired access token."""
        try:
            # Get accounts (should have cached account from previous auth)
            accounts = self.app.get_accounts()
            
            if accounts:
                # Try silent token acquisition
                result = self.app.acquire_token_silent(
                    scopes=self.SCOPES,
                    account=accounts[0]
                )
                
                if "access_token" in result:
                    tokens = {
                        'access_token': result['access_token'],
                        'refresh_token': result.get('refresh_token', refresh_token),
                        'token_expiry': self._calculate_expiry(result.get('expires_in', 3600))
                    }
                    self.logger.info("OAuth token refreshed successfully")
                    return tokens
            
            # If silent acquisition fails, need to re-authenticate
            self.logger.warning("Silent token acquisition failed, need to re-authenticate")
            return None
            
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
            return None
    
    def is_token_expired(self, token_expiry: Optional[str]) -> bool:
        """Check if an access token is expired or will expire soon."""
        if not token_expiry:
            return True
        
        try:
            expiry_time = datetime.fromisoformat(token_expiry.replace('Z', '+00:00'))
            buffer_time = datetime.now(expiry_time.tzinfo) + timedelta(minutes=5)
            return expiry_time <= buffer_time
        except Exception:
            return True
    
    def generate_oauth2_string(self, email: str, access_token: str) -> bytes:
        """Generate OAuth2 authentication string for IMAP XOAUTH2."""
        auth_string = f'user={email}\x01auth=Bearer {access_token}\x01\x01'
        return auth_string.encode('utf-8')
    
    def _calculate_expiry(self, expires_in: int) -> str:
        """Calculate token expiry time."""
        expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)
        return expiry_time.isoformat()
```

### Phase 3: Authentication Strategy

1. **Create `OutlookOAuthStrategy`**
   - Implement in `src/email_client/auth/outlook_oauth_auth.py`
   - Similar structure to `GmailOAuthStrategy`
   - Use Outlook IMAP server settings: `outlook.office365.com:993`

2. **Update `AuthStrategyFactory`**
   - Add logic to detect Outlook OAuth
   - Create `OutlookOAuthStrategy` when appropriate

### Phase 4: UI Integration

1. **Create `OutlookOAuthDialog`**
   - Implement in `src/ui/outlook_oauth_dialog.py`
   - Similar to `GmailOAuthDialog`
   - Update branding and instructions for Microsoft

2. **Update `AccountDialog`**
   - Show OAuth option for Outlook/Hotmail addresses
   - Launch `OutlookOAuthDialog` for Outlook accounts
   - Handle provider-specific logic

3. **Update Provider Detection**
   - Detect `@outlook.com`, `@hotmail.com`, `@live.com` addresses
   - Show OAuth option for these addresses

### Phase 5: Database and Credential Management

1. **Extend `OAuthCredentialManager`**
   - Add `provider` parameter to all methods
   - Support storing/retrieving tokens for multiple providers
   - Maintain backward compatibility with existing Gmail tokens

2. **Database Migration**
   - Add `provider` column to `oauth_tokens` table
   - Set default to 'gmail' for existing records

### Phase 6: Testing

1. **Unit Tests**
   - Test `OutlookOAuthManager` methods
   - Test `OutlookOAuthStrategy` authentication
   - Mock MSAL calls and IMAP connections

2. **Integration Tests**
   - Test full OAuth flow with test Microsoft account
   - Test token refresh functionality
   - Test IMAP connection with OAuth

3. **Manual Testing**
   - Test with real Outlook.com account
   - Test with real Hotmail.com account
   - Test with real Live.com account
   - Verify token refresh after expiry

---

## IMAP Configuration for Outlook

### Connection Settings

- **Server**: `outlook.office365.com`
- **Port**: `993`
- **Encryption**: SSL/TLS
- **Authentication**: XOAUTH2 (OAuth 2.0)

### XOAUTH2 SASL Authentication

The XOAUTH2 SASL mechanism is the same for both Gmail and Outlook:

```python
# Generate authentication string
auth_string = f'user={email}\x01auth=Bearer {access_token}\x01\x01'
auth_bytes = base64.b64encode(auth_string.encode('utf-8'))

# Authenticate with IMAP
imap_connection.authenticate('XOAUTH2', lambda x: auth_bytes)
```

### Important Notes

1. **IMAP Must Be Enabled**: Users must enable IMAP in their Outlook settings
2. **OAuth Scopes**: Ensure `IMAP.AccessAsUser.All` scope is granted
3. **Token Refresh**: Outlook tokens typically expire after 1 hour, similar to Gmail
4. **Error Handling**: Handle authentication failures gracefully, prompt for re-authorization

---

## Alternative Approach: Microsoft Graph API

Instead of using IMAP with OAuth, you could use the **Microsoft Graph API** for more reliable and feature-rich email access.

### Advantages of Graph API

1. **More Reliable**: Official Microsoft API with better support
2. **Richer Features**: Access to more email metadata and operations
3. **Better Performance**: Optimized for cloud-based access
4. **No IMAP Setup**: Users don't need to enable IMAP

### Disadvantages

1. **More Complex**: Requires learning Graph API
2. **Different Architecture**: Would need to create a new client type
3. **API-Specific Code**: Less portable than IMAP

### Graph API Implementation Outline

If you choose the Graph API route:

1. **Scopes**: Use `Mail.ReadWrite` instead of `IMAP.AccessAsUser.All`
2. **Client**: Create `OutlookGraphClient` similar to `GmailAPIClient`
3. **Endpoints**:
   - List messages: `GET /me/messages`
   - Delete message: `DELETE /me/messages/{id}`
   - Get message: `GET /me/messages/{id}`
4. **Pagination**: Handle `@odata.nextLink` for large result sets

**Recommendation**: Start with IMAP OAuth (easier to implement, consistent with current architecture) and consider Graph API as a future enhancement if IMAP proves unreliable.

---

## Migration Path and Backward Compatibility

### Ensuring Backward Compatibility

1. **Existing Gmail OAuth Users**
   - Existing Gmail tokens continue to work
   - No re-authorization needed
   - Provider column defaults to 'gmail' for existing tokens

2. **Existing Password-Based Users**
   - Both Gmail and Outlook password-based auth continues to work
   - Users can upgrade to OAuth at any time

3. **Mixed Authentication**
   - Users can have multiple accounts with different auth methods
   - Each account independently chooses auth method

### User Migration Strategy

1. **Announcement**: Inform users about new Outlook OAuth support
2. **Optional Upgrade**: Allow existing Outlook users to switch to OAuth
3. **Gradual Rollout**: Test with early adopters before full release
4. **Documentation**: Update user guides with Outlook OAuth instructions

---

## Documentation Requirements

### User-Facing Documentation

1. **Outlook OAuth Setup Guide** (`OUTLOOK_OAUTH_SETUP_INSTRUCTIONS.md`)
   - Step-by-step Azure app registration
   - How to enable IMAP in Outlook
   - How to authorize in the application
   - Troubleshooting common issues

2. **Update Existing Documentation**
   - Update `README.md` with Outlook OAuth support
   - Update `OAUTH_SETUP_INSTRUCTIONS.md` to mention both providers
   - Add Outlook OAuth troubleshooting section

### Developer-Facing Documentation

1. **Outlook OAuth Technical Guide** (`OUTLOOK_OAUTH_GUIDE.md`)
   - Architecture overview
   - MSAL integration details
   - Token management
   - Error handling
   - Testing procedures

2. **Multi-Provider OAuth Guide**
   - How to add new OAuth providers in the future
   - Common OAuth patterns in the codebase
   - Testing strategies for OAuth flows

---

## Security Considerations

### Token Storage

- **Encryption**: Use same Fernet encryption as Gmail tokens
- **Separation**: Store provider type to avoid token confusion
- **Revocation**: Provide UI to revoke OAuth access

### Scopes and Permissions

- **Minimal Scopes**: Only request `IMAP.AccessAsUser.All` and `offline_access`
- **User Consent**: Clearly explain what permissions are being requested
- **Scope Verification**: Verify granted scopes match requested scopes

### Error Handling

- **Invalid Tokens**: Prompt for re-authorization
- **Expired Tokens**: Automatically refresh with fallback to re-auth
- **Network Errors**: Graceful degradation and retry logic

---

## Testing Strategy

### Unit Tests

```python
# Test OutlookOAuthManager
- test_authorize_user_success()
- test_authorize_user_failure()
- test_refresh_token_success()
- test_refresh_token_failure()
- test_is_token_expired()
- test_generate_oauth2_string()

# Test OutlookOAuthStrategy
- test_authenticate_success()
- test_authenticate_with_token_refresh()
- test_authenticate_failure()
- test_retry_with_token_refresh()
```

### Integration Tests

```python
# Test full OAuth flow
- test_outlook_oauth_flow_end_to_end()
- test_outlook_imap_connection_with_oauth()
- test_token_refresh_cycle()
- test_multi_account_with_different_providers()
```

### Manual Testing Checklist

- [ ] Azure app registration completed successfully
- [ ] IMAP enabled on test Outlook account
- [ ] OAuth authorization flow completes
- [ ] Tokens stored in database correctly
- [ ] IMAP connection successful with OAuth
- [ ] Email scanning works correctly
- [ ] Token refresh works automatically
- [ ] Re-authorization works when token refresh fails
- [ ] UI shows appropriate messages and errors
- [ ] Multiple accounts (Gmail + Outlook) work together

---

## Rollout Plan

### Phase 1: Setup (Week 1)
- [ ] Azure app registration
- [ ] Documentation created
- [ ] Dependencies installed

### Phase 2: Core Implementation (Week 2-3)
- [ ] `OutlookOAuthManager` implemented
- [ ] `OutlookOAuthStrategy` implemented
- [ ] Database schema updated
- [ ] Unit tests written

### Phase 3: UI Integration (Week 4)
- [ ] `OutlookOAuthDialog` implemented
- [ ] `AccountDialog` updated
- [ ] Provider detection updated
- [ ] Integration tests written

### Phase 4: Testing (Week 5)
- [ ] Manual testing completed
- [ ] Bug fixes
- [ ] Documentation reviewed

### Phase 5: Release (Week 6)
- [ ] User documentation finalized
- [ ] Changelog updated
- [ ] Release notes prepared
- [ ] Application deployed

---

## Future Enhancements

1. **Yahoo Mail OAuth**: Add support for Yahoo Mail using OAuth 2.0
2. **Microsoft Graph API**: Migrate from IMAP to Graph API for better reliability
3. **Batch Token Refresh**: Refresh multiple tokens in parallel
4. **OAuth Token Dashboard**: UI for managing all OAuth tokens
5. **Automatic Provider Detection**: Auto-detect OAuth availability and recommend best auth method

---

## Summary

### Key Takeaways

1. **Outlook OAuth is very similar to Gmail OAuth** - Same XOAUTH2 SASL mechanism, similar token flow
2. **Main difference is MSAL vs google-auth** - Different libraries, but same concepts
3. **Azure App Registration required** - One-time setup in Azure portal
4. **IMAP with OAuth** - Same IMAP protocol, just different authentication
5. **Backward Compatible** - Existing Gmail OAuth and password auth continue to work

### Next Steps

1. **Complete Azure app registration** following the detailed steps above
2. **Install MSAL** and create configuration files
3. **Implement `OutlookOAuthManager`** following the Gmail pattern
4. **Create Outlook-specific UI components**
5. **Test thoroughly** with real Outlook/Hotmail accounts
6. **Update documentation** for end users

### Estimated Effort

- **Setup**: 2-4 hours (Azure registration, configuration)
- **Implementation**: 2-3 weeks (core OAuth, strategy, UI)
- **Testing**: 1 week (unit, integration, manual)
- **Documentation**: 3-5 days (user guides, technical docs)
- **Total**: 4-5 weeks for complete implementation and testing

---

## Questions?

For questions about this strategy or implementation details:
1. Review the existing Gmail OAuth implementation
2. Consult Microsoft's MSAL documentation: https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-overview
3. Check Microsoft Graph API documentation: https://docs.microsoft.com/en-us/graph/
4. Review IMAP OAuth documentation: https://docs.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth
