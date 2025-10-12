# Azure App Registration Setup Guide for Outlook/Hotmail OAuth

## Overview

This guide provides step-by-step instructions for registering an application in Microsoft Azure to enable OAuth 2.0 authentication for Outlook.com and Hotmail.com accounts in the Email Unsubscriber application.

**Time Required**: 15-30 minutes  
**Prerequisites**: 
- A Microsoft account (any outlook.com, hotmail.com, or live.com account)
- Web browser
- Internet connection

---

## Part 1: Azure Portal Setup

### Step 1: Access Azure Portal

1. **Open your web browser** and navigate to:
   ```
   https://portal.azure.com/
   ```

2. **Sign in** with your Microsoft account
   - You can use any Microsoft account (outlook.com, hotmail.com, live.com)
   - You don't need an Azure subscription or credit card
   - Personal Microsoft accounts can create app registrations for free

3. **Accept any terms** if prompted

### Step 2: Navigate to App Registrations

1. **Find App Registrations**:
   - Click the **search bar** at the top of the Azure portal
   - Type: `App registrations`
   - Click on **App registrations** in the results

   ![Azure Search](https://docs.microsoft.com/en-us/azure/includes/media/active-directory-develop-guidedsetup-portal/portal-01-app-reg.png)

2. **Alternative navigation**:
   - Click the menu icon (≡) in the top-left
   - Expand **Azure Active Directory** (or **Microsoft Entra ID**)
   - Click **App registrations**

### Step 3: Create New App Registration

1. **Start Registration**:
   - Click **+ New registration** button at the top
   
2. **Configure Application Details**:
   
   **Name**:
   ```
   Email Unsubscriber
   ```
   - Or any descriptive name you prefer
   - This name is shown to users during authorization

   **Supported account types**:
   - Select: **"Accounts in any organizational directory (Any Azure AD directory - Multitenant) and personal Microsoft accounts (e.g. Skype, Xbox)"**
   - ⚠️ This option is REQUIRED to support personal Outlook.com and Hotmail.com accounts
   
   **Redirect URI**:
   - Platform dropdown: Select **"Public client/native (mobile & desktop)"**
   - Redirect URI field: Enter `http://localhost`
   - ℹ️ This URI is used by MSAL to capture the authorization response

3. **Register the Application**:
   - Click the **Register** button at the bottom
   - Wait for the registration to complete (usually a few seconds)

### Step 4: Save Application (Client) ID

1. **Copy the Application ID**:
   - After registration, you'll see the **Overview** page
   - Find **Application (client) ID** (it looks like: `12345678-1234-1234-1234-123456789abc`)
   - Click the **copy icon** next to the ID
   - **SAVE THIS ID** - you'll need it later

   Example:
   ```
   Application (client) ID: a1b2c3d4-e5f6-1234-5678-9abcdef01234
   ```

2. **Note the Directory (tenant) ID** (optional):
   - You'll also see **Directory (tenant) ID**
   - For personal accounts, this is typically not needed
   - We'll use the "common" endpoint instead

---

## Part 2: Configure API Permissions

### Step 5: Add Required Permissions

1. **Navigate to API Permissions**:
   - In the left sidebar, click **API permissions**
   - You should see one default permission: "Microsoft Graph > User.Read"

2. **Add IMAP Permission**:
   - Click **+ Add a permission**
   - In the **Request API permissions** panel:
     - Click **APIs my organization uses** tab
     - In the search box, type: `Office 365 Exchange Online`
     - Click on **Office 365 Exchange Online** in the results
   
   - Select **Delegated permissions** (not Application permissions)
   - In the permissions list, find and check:
     - ☑️ **IMAP.AccessAsUser.All**
   - Click **Add permissions** at the bottom

3. **Add Offline Access Permission**:
   - Click **+ Add a permission** again
   - Click **Microsoft Graph**
   - Select **Delegated permissions**
   - Expand **OpenId permissions** section
   - Find and check:
     - ☑️ **offline_access** (This allows refresh tokens)
   - Click **Add permissions**

4. **Verify Permissions**:
   Your permissions list should now show:
   ```
   ✓ Microsoft Graph > User.Read (default)
   ✓ Microsoft Graph > offline_access
   ✓ Office 365 Exchange Online > IMAP.AccessAsUser.All
   ```

### Step 6: Grant Admin Consent (Optional)

**For Personal Accounts**:
- Skip this step - personal accounts provide consent during first login
- Each user will consent when they first authorize the app

**For Organizational Accounts** (if you're an admin):
- Click **Grant admin consent for [Your Organization]**
- Confirm the consent
- This pre-approves the app for all users in your organization

---

## Part 3: Configure Authentication Settings

### Step 7: Enable Public Client Flow

1. **Navigate to Authentication**:
   - In the left sidebar, click **Authentication**

2. **Verify Redirect URI**:
   - Under **Platform configurations**, you should see:
     - **Mobile and desktop applications**
     - Redirect URI: `http://localhost`
   
   - If not present, click **+ Add a platform** and add it

3. **Enable Public Client Flows**:
   - Scroll down to **Advanced settings** section
   - Find **Allow public client flows**
   - Set the toggle to **Yes**
   - ℹ️ This is REQUIRED for desktop applications using MSAL

4. **Save Changes**:
   - Click **Save** at the top if you made any changes

---

## Part 4: Create Configuration File

### Step 8: Create Application Configuration

1. **Navigate to Application Directory**:
   - Open your Email Unsubscriber application folder
   - Create a `data` folder if it doesn't exist

2. **Create Configuration File**:
   - Create a new file: `data/outlook_credentials.json`
   - Use the following template:

   ```json
   {
     "client_id": "PASTE-YOUR-APPLICATION-ID-HERE",
     "authority": "https://login.microsoftonline.com/common",
     "scope": [
       "https://outlook.office.com/IMAP.AccessAsUser.All",
       "offline_access"
     ],
     "redirect_uri": "http://localhost"
   }
   ```

3. **Replace the client_id**:
   - Paste the **Application (client) ID** you copied in Step 4
   - The file should look like:

   ```json
   {
     "client_id": "a1b2c3d4-e5f6-1234-5678-9abcdef01234",
     "authority": "https://login.microsoftonline.com/common",
     "scope": [
       "https://outlook.office.com/IMAP.AccessAsUser.All",
       "offline_access"
     ],
     "redirect_uri": "http://localhost"
   }
   ```

4. **Save the File**:
   - Save `data/outlook_credentials.json`
   - Verify the file is in the correct location:
     ```
     Email Unsubscriber/
     ├── data/
     │   └── outlook_credentials.json  ← Should be here
     ├── src/
     ├── main.py
     └── ...
     ```

---

## Part 5: Enable IMAP in Outlook Account

### Step 9: Enable IMAP for Your Account

**This step must be completed by each user** who wants to use OAuth with their Outlook/Hotmail account.

1. **Sign in to Outlook.com**:
   - Go to: https://outlook.live.com/mail/
   - Sign in with the account you want to use

2. **Open Settings**:
   - Click the **gear icon** (⚙️) in the top-right
   - Click **View all Outlook settings** at the bottom of the panel

3. **Navigate to Sync Email**:
   - In the Settings panel, click **Mail** in the left sidebar
   - Click **Sync email** in the expanded menu

4. **Enable IMAP**:
   - Scroll down to **POP and IMAP** section
   - Find **Let devices and apps use IMAP**
   - Ensure it's set to **Yes**
   - If it was set to No, change it to Yes and click **Save**

5. **Note the Settings**:
   - IMAP Server: `outlook.office365.com`
   - IMAP Port: `993`
   - Encryption: TLS

---

## Part 6: Security and Best Practices

### Step 10: Security Considerations

1. **Keep Application ID Private**:
   - Treat your application ID as sensitive
   - Don't share it publicly
   - Add `data/outlook_credentials.json` to `.gitignore`

2. **Review Permissions Regularly**:
   - Periodically review your app registration
   - Ensure only necessary permissions are granted
   - Remove any unused or excessive permissions

3. **Monitor Usage** (Optional):
   - In Azure portal, you can view sign-in logs
   - Navigate to **Azure Active Directory** > **Sign-in logs**
   - Monitor for unusual activity

### Step 11: User Privacy and Revocation

**Users can revoke access at any time**:

1. **Via Microsoft Account Settings**:
   - Go to: https://account.microsoft.com/privacy/
   - Click **Apps and services**
   - Find "Email Unsubscriber"
   - Click **Remove these permissions**

2. **Via Azure Portal** (for admins):
   - Enterprise applications > Find app > Delete consent

---

## Part 7: Testing

### Step 12: Test the Setup

1. **Run the Application**:
   ```bash
   python main.py
   ```

2. **Add an Account**:
   - Click `File > Add Account`
   - Enter an Outlook.com or Hotmail.com email address
   - The OAuth option should appear
   - Click "Start OAuth Authorization"

3. **Complete Authorization**:
   - Browser opens to Microsoft login
   - Sign in with your Outlook/Hotmail account
   - Review requested permissions:
     - Read, write, send, and permanently delete your mail using IMAP
     - Maintain access to data you have given it access to
   - Click **Accept**
   - Return to application

4. **Verify Success**:
   - Application should show "Authorization successful!"
   - Account should be saved
   - Try scanning inbox to verify IMAP connection works

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "App is not verified"

**Problem**: Microsoft shows a warning that the app is not verified.

**Solution**:
1. This is normal for personal projects
2. Click **Advanced** link
3. Click **Go to Email Unsubscriber (unsafe)**
4. This is safe because you created the app yourself
5. To remove this warning, you would need to complete Microsoft's publisher verification process (not required for personal use)

#### Issue: "AADSTS700016: Application not found"

**Problem**: The client ID is incorrect or the app was deleted.

**Solution**:
1. Verify the Application (client) ID in `outlook_credentials.json`
2. Check that you copied the ID correctly from Azure portal
3. Ensure the app registration still exists in Azure

#### Issue: "AADSTS650053: The app needs access to a service"

**Problem**: Required API permissions are missing.

**Solution**:
1. Go back to Azure portal > App registrations > Your app
2. Click **API permissions**
3. Verify `IMAP.AccessAsUser.All` and `offline_access` are listed
4. Try re-adding the permissions if they're missing

#### Issue: "IMAP not available"

**Problem**: IMAP is not enabled on the user's Outlook account.

**Solution**:
1. Follow Step 9 to enable IMAP in Outlook settings
2. Wait a few minutes for the change to take effect
3. Try authorizing again

#### Issue: "Invalid redirect URI"

**Problem**: The redirect URI in the app doesn't match Azure configuration.

**Solution**:
1. Verify `outlook_credentials.json` has: `"redirect_uri": "http://localhost"`
2. Verify Azure app registration has the same redirect URI
3. Ensure the platform is set to "Public client/native"

#### Issue: "Public client flows not allowed"

**Problem**: Public client flows are not enabled in Azure.

**Solution**:
1. Go to Azure portal > Your app > Authentication
2. Scroll to **Advanced settings**
3. Set **Allow public client flows** to **Yes**
4. Save changes

---

## Summary Checklist

Use this checklist to ensure all steps are completed:

### Azure Portal Setup
- [ ] Signed in to Azure portal
- [ ] Created app registration with name "Email Unsubscriber"
- [ ] Selected multi-tenant + personal accounts
- [ ] Set redirect URI to `http://localhost` (Public client/native)
- [ ] Copied Application (client) ID

### API Permissions
- [ ] Added `IMAP.AccessAsUser.All` permission
- [ ] Added `offline_access` permission
- [ ] Verified all permissions are listed

### Authentication Settings
- [ ] Verified redirect URI is configured
- [ ] Enabled "Allow public client flows" to Yes

### Configuration File
- [ ] Created `data` folder
- [ ] Created `outlook_credentials.json`
- [ ] Pasted Application (client) ID into config
- [ ] Saved file in correct location

### User Account Setup
- [ ] Signed in to Outlook.com
- [ ] Enabled IMAP in Outlook settings

### Testing
- [ ] Tested authorization flow in application
- [ ] Successfully connected to Outlook account
- [ ] Verified IMAP scanning works

---

## Next Steps

After completing this setup:

1. **Implement OAuth in Application**: Use the implementation guide to add Outlook OAuth to your code
2. **Test with Multiple Accounts**: Test with different Outlook.com and Hotmail.com accounts
3. **Document for Users**: Create user-facing documentation for the OAuth process
4. **Monitor and Maintain**: Keep the app registration active and monitor for issues

---

## Additional Resources

### Microsoft Documentation
- **Azure App Registration**: https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app
- **MSAL Python**: https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-v2-python-desktop
- **IMAP with OAuth**: https://docs.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth
- **Microsoft Graph Permissions**: https://docs.microsoft.com/en-us/graph/permissions-reference

### Tools
- **Azure Portal**: https://portal.azure.com/
- **Microsoft Account Privacy**: https://account.microsoft.com/privacy/
- **MSAL Python GitHub**: https://github.com/AzureAD/microsoft-authentication-library-for-python

---

## Support

If you encounter issues:

1. **Check Troubleshooting Section**: Review common issues above
2. **Azure Portal Logs**: Check Azure AD sign-in logs for errors
3. **Application Logs**: Check `data/logs/app.log` in your application
4. **Microsoft Support**: For Azure-specific issues, consult Microsoft documentation

---

**Congratulations!** You've completed the Azure app registration setup. Your application is now ready to authenticate Outlook and Hotmail users via OAuth 2.0.
