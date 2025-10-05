# Gmail OAuth Setup Instructions

This guide will help you set up OAuth 2.0 authentication for Gmail in the Email Unsubscriber application.

## Why OAuth?

Gmail has deprecated password-based authentication for third-party applications. OAuth 2.0 is now the required authentication method, offering:
- **Better security**: No need to share your actual password
- **Granular permissions**: Control exactly what the app can access
- **Easy revocation**: Revoke access anytime from your Google Account settings
- **Seamless experience**: Authenticate once and the app remembers

## Setup Steps

### Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "New Project"
4. Enter a project name (e.g., "Email Unsubscriber")
5. Click "Create"

### Step 2: Enable Gmail API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "Enable"

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type
3. Click "Create"
4. Fill in the required fields:
   - App name: Email Unsubscriber
   - User support email: Your email
   - Developer contact: Your email
5. Click "Save and Continue"
6. On the "Scopes" page:
   - Click "Add or Remove Scopes"
   - Search for "https://mail.google.com/"
   - Select this scope (Full mail access)
   - Click "Update"
   - Click "Save and Continue"
7. On the "Test users" page:
   - Click "Add Users"
   - Add your Gmail address(es)
   - Click "Save and Continue"
8. Review the summary and click "Back to Dashboard"

### Step 4: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Desktop app" as the application type
4. Enter a name (e.g., "Email Unsubscriber Desktop")
5. Click "Create"
6. A dialog will appear with your credentials
7. Click "Download JSON"

### Step 5: Install the Credentials File

1. Save the downloaded JSON file
2. Rename it to `gmail_credentials.json`
3. Place it in the `data/` folder of the Email Unsubscriber application
   - Create the `data/` folder if it doesn't exist
   - Full path should be: `data/gmail_credentials.json`

### Step 6: Authorize the Application

1. Launch the Email Unsubscriber application
2. Go to Settings > Accounts
3. Click "Add Account"
4. Enter your Gmail address
5. Check "Use OAuth 2.0 (Recommended for Gmail)"
6. Click "Start OAuth Authorization"
7. A browser window will open
8. Log in to your Google account if not already logged in
9. Review the permissions requested
10. Click "Allow"
11. You'll see a success message
12. Close the browser window and return to the application

## Troubleshooting

### Error: Credentials file not found

- Make sure `gmail_credentials.json` is in the `data/` folder
- Check that the file name is exactly `gmail_credentials.json`

### Error: Access blocked

- Make sure you've added your Gmail address as a test user in the OAuth consent screen
- If your app is in "Testing" mode, only test users can access it

### Error: Invalid scope

- Make sure you've added the `https://mail.google.com/` scope in the OAuth consent screen
- This scope is required for full mail access (read, send, delete)

### Token expired

- The application automatically refreshes tokens
- If you see this error, try removing and re-adding your account

### Need to revoke access?

1. Go to your [Google Account](https://myaccount.google.com/)
2. Navigate to "Security" > "Third-party apps with account access"
3. Find "Email Unsubscriber" and click "Remove Access"

## Security Notes

- Your OAuth tokens are encrypted and stored locally
- Never share your `gmail_credentials.json` file
- You can revoke access at any time from your Google Account settings
- The application only requests the permissions it needs

## For Production Use

If you want to publish the application for others to use:

1. Complete the OAuth consent screen verification process
2. Submit your app for verification by Google
3. Once verified, users won't need to be added as test users
4. The "Unverified app" warning will be removed

For personal use, the test mode is sufficient and works perfectly well.
