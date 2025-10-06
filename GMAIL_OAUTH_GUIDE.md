# Gmail OAuth 2.0 Technical Guide

This document provides technical details about the Gmail OAuth 2.0 implementation in the Email Unsubscriber application.

## Overview

The OAuth 2.0 implementation replaces password-based authentication for Gmail accounts, providing a more secure and user-friendly authentication method. The system handles the complete OAuth flow, token management, and IMAP authentication.

## Architecture

### Components

1. **GmailOAuthManager** (`src/email_client/gmail_oauth.py`)
   - Handles OAuth authorization flow
   - Manages token refresh operations
   - Generates IMAP authentication strings

2. **OAuthCredentialManager** (`src/email_client/gmail_oauth.py`)
   - Encrypts and stores OAuth tokens in database
   - Retrieves and decrypts tokens for use
   - Manages token lifecycle

3. **GmailOAuthStrategy** (`src/email_client/auth/gmail_oauth_auth.py`)
   - Authentication strategy for OAuth-based IMAP connections
   - Handles token validation and refresh
   - Implements XOAUTH2 SASL authentication

4. **GmailOAuthDialog** (`src/ui/oauth_dialog.py`)
   - User interface for OAuth authorization
   - Manages browser-based authorization flow
   - Provides user feedback during authorization

### Database Schema

OAuth tokens are stored in the `oauth_tokens` table:

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

## OAuth 2.0 Flow

### Initial Authorization

1. **User Initiates**: User selects OAuth option in account setup
2. **Credentials Check**: System verifies `data/gmail_credentials.json` exists
3. **Browser Launch**: `InstalledAppFlow` opens browser to Google's OAuth endpoint
4. **User Authorization**: User signs in and grants permissions
5. **Token Receipt**: Google redirects with authorization code
6. **Token Exchange**: System exchanges code for access/refresh tokens
7. **Token Storage**: Tokens are encrypted and stored in database

### Daily Authentication

1. **Token Retrieval**: System gets encrypted tokens from database
2. **Token Decryption**: Tokens are decrypted using Fernet encryption
3. **Expiry Check**: System checks if access token will expire within 5 minutes
4. **Token Refresh**: If needed, refresh token is used to get new access token
5. **IMAP Authentication**: XOAUTH2 SASL mechanism authenticates with Gmail
6. **Connection Success**: IMAP connection is established

### Token Refresh Process

```python
# Check if token is expired or will expire soon
if self.gmail_oauth.is_token_expired(token_expiry):
    # Use refresh token to get new access token
    new_tokens = self.gmail_oauth.refresh_token(refresh_token)
    
    # Update stored tokens
    self.oauth_manager.store_oauth_tokens(
        email, new_tokens['access_token'], 
        new_tokens['refresh_token'], new_tokens['token_expiry']
    )
```

## IMAP Authentication

### XOAUTH2 SASL Mechanism

Gmail uses the XOAUTH2 SASL mechanism for OAuth authentication:

```python
# Generate authentication string
auth_string = f'user={email}\x01auth=Bearer {access_token}\x01\x01'
auth_bytes = base64.b64encode(auth_string.encode('utf-8'))

# Authenticate with IMAP
imap_connection.authenticate('XOAUTH2', lambda x: auth_bytes)
```

### Authentication Flow

1. **Connection**: Establish SSL connection to `imap.gmail.com:993`
2. **Capability Check**: IMAP server advertises XOAUTH2 support
3. **Authentication**: Send XOAUTH2 command with OAuth token
4. **Success**: Server responds with authentication success
5. **Ready**: IMAP connection is ready for mail operations

## Security Considerations

### Token Storage

- **Encryption**: All tokens encrypted using Fernet symmetric encryption
- **Key Management**: Encryption key stored in `data/key.key`
- **Database**: Tokens stored in local SQLite database
- **No Transmission**: Tokens never leave the local machine

### Scope Limitations

- **Minimal Scope**: Only `https://mail.google.com/` scope requested
- **Mail Only**: No access to other Google services
- **IMAP Operations**: Read, send, delete email operations only

### Token Lifecycle

- **Access Token**: Short-lived (typically 1 hour)
- **Refresh Token**: Long-lived (can be revoked by user)
- **Automatic Refresh**: Happens transparently before expiry
- **Expiry Buffer**: Tokens refreshed 5 minutes before expiry

## Error Handling

### Common Scenarios

1. **Missing Credentials File**
   ```python
   if not os.path.exists(self.credentials_file):
       raise FileNotFoundError("OAuth credentials file not found")
   ```

2. **Authorization Cancelled**
   ```python
   if not tokens:
       self.error_message = "Authorization was cancelled"
       return False
   ```

3. **Token Refresh Failure**
   ```python
   if not new_tokens:
       self.error_message = "Failed to refresh token. Please re-authorize."
       return False
   ```

4. **IMAP Authentication Failure**
   ```python
   except imaplib.IMAP4.error as e:
       if 'invalid credentials' in str(e).lower():
           # Attempt token refresh and retry
           return self._retry_with_token_refresh()
   ```

## Configuration

### OAuth Credentials

The `data/gmail_credentials.json` file contains:

```json
{
  "installed": {
    "client_id": "your-client-id.googleusercontent.com",
    "client_secret": "your-client-secret",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}
```

### Required Scopes

- `https://mail.google.com/` - Full mail access (read, send, delete)

## Integration Points

### Strategy Pattern Integration

The OAuth authentication integrates with the strategy pattern:

```python
# Factory creates appropriate strategy
if provider == 'gmail' and oauth_tokens_available:
    return GmailOAuthStrategy(oauth_manager)
else:
    return PasswordAuthStrategy(password)

# IMAPClient uses strategy
client = IMAPClient(email, auth_strategy, provider)
```

### UI Integration

OAuth is integrated into the account setup dialog:

1. **Provider Detection**: Gmail addresses show OAuth option
2. **OAuth Toggle**: Checkbox enables OAuth mode
3. **Authorization Button**: Launches OAuth flow
4. **Status Updates**: Real-time feedback during authorization

## Testing Considerations

### Unit Testing

- Mock `InstalledAppFlow` for authorization testing
- Mock database operations for token storage testing
- Mock IMAP connections for authentication testing

### Integration Testing

- Test complete OAuth flow with test Google account
- Verify token refresh functionality
- Test error handling scenarios

### Manual Testing

- Test initial authorization with real Gmail account
- Verify seamless re-authentication after token refresh
- Test error scenarios (network issues, cancelled authorization)

## Performance Considerations

### Token Caching

- Tokens cached in memory during application session
- Database queries minimized through caching
- Token validation happens before each IMAP connection

### Background Refresh

- Token refresh happens automatically before expiry
- No user interaction required for refresh
- Refresh failures trigger re-authorization prompt

## Future Enhancements

### Potential Improvements

1. **Multiple OAuth Providers**: Support Outlook OAuth, Yahoo OAuth
2. **Token Revocation**: UI for revoking OAuth access
3. **Batch Authorization**: Authorize multiple accounts at once
4. **Advanced Scopes**: Request additional permissions if needed

### Scalability

- Current implementation supports multiple Gmail accounts
- Database schema supports multiple OAuth providers
- Strategy pattern allows easy addition of new auth methods

## Debugging

### Log Messages

The system logs OAuth operations at various levels:

```python
self.logger.info("Starting OAuth authorization flow...")
self.logger.info("OAuth token refreshed successfully")
self.logger.error(f"OAuth authorization failed: {e}")
```

### Common Issues

1. **"This app isn't verified"**: Normal for development apps
2. **"Access blocked"**: User not added as test user
3. **"Invalid credentials"**: Token expired and refresh failed
4. **"Connection refused"**: Network connectivity issues

This implementation provides a robust, secure, and user-friendly OAuth 2.0 authentication system for Gmail accounts in the Email Unsubscriber application.