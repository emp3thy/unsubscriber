# Gmail OAuth 2.0 Setup Instructions

This guide will walk you through setting up OAuth 2.0 authentication for Gmail in the Email Unsubscriber application.

## Why OAuth 2.0?

Gmail has deprecated password-based authentication for third-party applications. OAuth 2.0 is now the recommended and most secure method to access Gmail via IMAP. Benefits include:

- ✅ **More secure** - No passwords stored in the application
- ✅ **Better user experience** - Authorize once, use seamlessly
- ✅ **Automatic token refresh** - No need to re-authenticate
- ✅ **Granular permissions** - Only grant mail access, nothing else

## Prerequisites

- A Google account with Gmail
- Internet connection
- Web browser

## Step-by-Step Setup

### Step 1: Create a Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project**
   - Click "Select a project" at the top
   - Click "New Project"
   - Enter project name: `Email Unsubscriber` (or any name you prefer)
   - Click "Create"

3. **Select Your Project**
   - Make sure your new project is selected in the project dropdown

### Step 2: Enable Gmail API

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" > "Library"

2. **Search for Gmail API**
   - In the search box, type "Gmail API"
   - Click on "Gmail API" from the results

3. **Enable the API**
   - Click the "Enable" button
   - Wait for the API to be enabled

### Step 3: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen**
   - In the left sidebar, click "APIs & Services" > "OAuth consent screen"

2. **Choose User Type**
   - Select "External" (unless you have a Google Workspace account)
   - Click "Create"

3. **Fill App Information**
   - **App name**: `Email Unsubscriber`
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
   - Leave other fields as default
   - Click "Save and Continue"

4. **Scopes** (Step 2)
   - Click "Save and Continue" (no changes needed)

5. **Test Users** (Step 3)
   - Add your Gmail address as a test user
   - Click "Add Users" and enter your Gmail address
   - Click "Save and Continue"

6. **Summary** (Step 4)
   - Review your settings
   - Click "Back to Dashboard"

### Step 4: Create OAuth Credentials

1. **Go to Credentials**
   - In the left sidebar, click "APIs & Services" > "Credentials"

2. **Create Credentials**
   - Click "Create Credentials" > "OAuth client ID"

3. **Configure OAuth Client**
   - **Application type**: Select "Desktop application"
   - **Name**: `Email Unsubscriber Desktop`
   - Click "Create"

4. **Download Credentials**
   - A dialog will appear with your client ID and secret
   - Click "Download JSON"
   - Save the file as `gmail_credentials.json`

### Step 5: Install Credentials in Application

1. **Create Data Directory**
   - In your Email Unsubscriber folder, create a `data` folder if it doesn't exist

2. **Copy Credentials File**
   - Move the downloaded `gmail_credentials.json` file to the `data` folder
   - The path should be: `data/gmail_credentials.json`

3. **Verify File Structure**
   ```
   Email Unsubscriber/
   ├── data/
   │   └── gmail_credentials.json
   ├── src/
   ├── main.py
   └── ...
   ```

## Using OAuth in the Application

### First-Time Setup

1. **Open Email Unsubscriber**
   - Run `python main.py`

2. **Add Gmail Account**
   - Click `Settings` > `Accounts` > `Add Account`
   - Enter your Gmail address
   - Check "Use OAuth 2.0 (Recommended for Gmail)"
   - Click "Start OAuth Authorization"

3. **Authorize in Browser**
   - Your web browser will open automatically
   - Sign in to your Gmail account if prompted
   - Review the permissions requested
   - Click "Allow" to grant access

4. **Complete Setup**
   - Return to the application
   - You should see "Authorization successful!"
   - The account is now ready to use

### Daily Usage

After the initial setup:
- ✅ No need to enter passwords
- ✅ No need to re-authorize
- ✅ Tokens refresh automatically
- ✅ Seamless Gmail access

## Troubleshooting

### "Credentials file not found"
- Ensure `gmail_credentials.json` is in the `data` folder
- Check the file name is exactly `gmail_credentials.json`

### "This app isn't verified"
- This is normal for personal projects
- Click "Advanced" > "Go to Email Unsubscriber (unsafe)"
- This is safe since you created the OAuth app yourself

### "Access blocked"
- Make sure you added your email as a test user in Step 3
- Ensure Gmail API is enabled in your Google Cloud project

### "Authorization failed"
- Check your internet connection
- Try again - sometimes Google's servers are temporarily busy
- Ensure you clicked "Allow" in the browser

### "Token refresh failed"
- This is rare but can happen
- Simply re-authorize by going through the OAuth flow again

## Security Notes

- ✅ **Your credentials are secure** - Only stored encrypted on your local machine
- ✅ **No passwords stored** - OAuth tokens are used instead
- ✅ **Limited scope** - App only has access to Gmail, nothing else
- ✅ **Revocable access** - You can revoke access anytime in your Google Account settings

## Revoking Access

If you want to revoke the application's access to your Gmail:

1. Go to your Google Account settings: https://myaccount.google.com/
2. Click "Security" > "Third-party apps with account access"
3. Find "Email Unsubscriber" and click "Remove Access"

## Support

If you encounter issues:
1. Check this troubleshooting section
2. Ensure all steps were followed correctly
3. Try the authorization process again
4. Check the application logs in `data/logs/app.log`

The OAuth setup is a one-time process. Once completed, you'll have secure, seamless access to your Gmail account!