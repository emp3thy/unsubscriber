# Gmail OAuth Implementation Guide

## Overview

Gmail has deprecated password-based authentication for IMAP access. This document describes the OAuth 2.0 authentication process we've implemented for the Email Unsubscriber application.

## Gmail OAuth Process

### 1. OAuth Flow Overview

The OAuth 2.0 authorization flow follows these steps:

1. **Application Registration**: Register the application in Google Cloud Console
2. **User Authorization**: User grants permission to the application
3. **Token Exchange**: Exchange authorization code for access and refresh tokens
4. **IMAP Authentication**: Use access token for IMAP authentication
5. **Token Refresh**: Automatically refresh expired access tokens

### 2. Setting Up Google Cloud Project

To use Gmail OAuth, you need to:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API for your project
4. Configure the OAuth consent screen:
   - Choose "External" user type (for testing)
   - Add required scopes: `https://mail.google.com/`
5. Create OAuth 2.0 credentials:
   - Application type: Desktop application
   - Download the credentials JSON file

### 3. Required OAuth Scopes

For read and write access (including delete), we use:
- `https://mail.google.com/` - Full mail access (read, write, delete)

Alternative scopes (if full access is not needed):
- `https://www.googleapis.com/auth/gmail.readonly` - Read-only access
- `https://www.googleapis.com/auth/gmail.modify` - Read and modify (but not delete)

### 4. Token Management

**Access Token:**
- Short-lived (typically 1 hour)
- Used for IMAP authentication
- Format: Bearer token

**Refresh Token:**
- Long-lived (persists until revoked)
- Used to obtain new access tokens
- Stored securely in encrypted form

### 5. IMAP Authentication with OAuth

Gmail IMAP with OAuth uses SASL XOAUTH2 mechanism:

```
Authenticate XOAUTH2 user={email} auth=Bearer {access_token}
```

The access token must be valid and have the correct scope.

### 6. Token Refresh Process

When an access token expires:
1. Detect authentication failure (invalid credentials error)
2. Use refresh token to request a new access token
3. Retry the IMAP connection with the new access token
4. Update stored token in database

### 7. Security Considerations

- Refresh tokens are encrypted using Fernet symmetric encryption
- Access tokens are stored in memory only (not persisted)
- User can revoke access at any time via Google Account settings
- Tokens are specific to the application and user

### 8. User Experience

**First-Time Setup:**
1. User clicks "Add Gmail Account"
2. Browser opens to Google login page
3. User authenticates and grants permissions
4. Application receives tokens and stores them securely
5. User is redirected back to the application

**Subsequent Use:**
- Application uses stored refresh token to obtain access tokens
- No user interaction needed
- Seamless background authentication

### 9. Error Handling

Common scenarios:
- **Token expired**: Automatically refresh and retry
- **Token revoked**: Prompt user to re-authenticate
- **Invalid scope**: Show error and request re-authorization
- **Network error**: Retry with exponential backoff

## Implementation Files

- `src/email_client/gmail_oauth.py` - OAuth token management
- `src/email_client/imap_client.py` - Modified for OAuth support
- `src/database/schema.sql` - Added oauth_tokens table
- `src/ui/oauth_dialog.py` - OAuth authorization UI

## Testing

To test OAuth implementation:
1. Use test credentials from Google Cloud Console
2. Test users must be added to the OAuth consent screen
3. Verify token refresh works correctly
4. Test revocation and re-authorization flows

## References

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [IMAP XOAUTH2 Protocol](https://developers.google.com/gmail/imap/xoauth2-protocol)
