# Email Unsubscriber

A Python application that helps you manage unwanted emails by identifying senders with high email volume and providing automated unsubscribe functionality.

## Features

### Core Functionality
- **Smart Scanning**: Analyzes your inbox to identify problematic senders based on email frequency and content
- **Automatic Unsubscribe**: Attempts to unsubscribe from mailing lists using multiple strategies (RFC 2369 headers, direct HTTP links)
- **Manual Cleanup**: Delete all emails from senders where unsubscribe failed
- **Score-based Prioritization**: Senders are ranked by how "unwanted" they appear to be with detailed tooltips
- **Progress Tracking**: Visual progress indicators during long operations with cancellation support
- **OAuth 2.0 Support**: Secure Gmail authentication using OAuth 2.0 (recommended method)
- **Gmail API Support**: Fast and reliable email operations using Gmail's official API
- **Cross-platform**: Works on Windows, macOS, and Linux

### Advanced Features
- **Excel-style Filtering**: Filter senders by any column with real-time search across all tables
- **No-Reply Detection**: Automatically identifies and isolates no-reply email addresses
- **Must Delete List**: Dedicated management for senders that failed to unsubscribe
- **Auto Delete**: Bulk delete all emails from multiple senders with one click
- **Context Menu Actions**: Right-click any sender to quickly add to whitelist or must delete list
- **Whitelist Protection**: Protect important senders from accidental operations (supports individual emails and entire domains)
- **Dynamic Column Resizing**: All filters automatically adjust when window or columns are resized
- **Multi-tab Interface**: Organized tabs for Senders, Must Delete, Whitelist, and No-Reply Senders

## Installation

### Requirements

- Python 3.8 or higher
- Internet connection for email operations
- IMAP-enabled email account (Gmail, Outlook, etc.)

### Setup

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python main.py
   ```

### Building Standalone Executable (Optional)

For Windows users, you can build a standalone `.exe` file:

```bash
python build.py
```

This creates a single executable that doesn't require Python to be installed.

## User Interface Overview

The application features a clean 4-tab interface:

### Tabs

1. **Senders Tab**: Main view showing all detected senders with scores, counts, and status
   - Filter by any column using the filter row above headers
   - Right-click senders for quick actions
   - Click column headers to sort
   - Color-coded by score level

2. **Must Delete Tab**: Senders that failed to unsubscribe
   - Auto Delete button processes all senders at once
   - Delete Selected button for individual senders
   - Shows failure reason and date added

3. **Whitelist Tab**: Protected senders that won't be affected by operations
   - Add/Remove entries
   - Support for individual emails and domains
   - Shows entry type, notes, and date added

4. **No-Reply Senders Tab**: Automatically detected no-reply email addresses
   - Shows senders like noreply@, donotreply@, etc.
   - Delete All Emails button for bulk cleanup
   - Automatically populated during scanning

### Toolbar Buttons

- **Scan Inbox**: Analyze your inbox and populate all tabs
- **Unsubscribe Selected**: Attempt to unsubscribe from selected senders
- **Delete Selected**: Delete all emails from selected senders (use with caution!)

### Status Bar

Located at the bottom of the window:
- Shows operation progress and results
- Displays email counts and statistics
- No intrusive popup messages for routine operations

## Getting Started

### First Run

1. **Add Email Account**:
   - Click `File > Add Account`
   - Enter your email address and app password
   - Click "Test Connection" to verify
   - Click "Save" to store the account

2. **Scan Your Inbox**:
   - Click "Scan Inbox" in the toolbar
   - Wait for the scan to complete (may take several minutes for large inboxes)
   - Review the results in the sender table

3. **Review and Act**:
   - Review senders sorted by score (highest first)
   - Select senders you want to unsubscribe from
   - Click "Unsubscribe Selected"
   - Confirm the operation

### Understanding Scores

The application assigns scores to senders based on:

- **Unread emails** (+1 point): Unread emails suggest unwanted content
- **Email frequency** (+1 point per email beyond the first): High volume = more unwanted
- **Unsubscribe links** (+1 point): Presence suggests it's a mailing list
- **Historical data** (+5 points): Previously marked as unwanted

**Hover over any score value** in the Score column to see a detailed tooltip showing exactly how that score was calculated (e.g., "Score 42.0 = Unread: +6 + Frequency: +35 + Has unsubscribe: +1").

**Color coding:**
- **Green background**: Whitelisted (protected) senders
- **White background**: Low score (< 3 points)
- **Light yellow background**: Medium score (3-7 points)  
- **Light red background**: High score (7+ points)

## Email Provider Setup

### Gmail (OAuth 2.0 - Recommended)

Gmail now uses OAuth 2.0 for secure authentication. This is the recommended method:

1. **Set up OAuth credentials** (one-time setup):
   - Follow the [detailed OAuth setup guide](OAUTH_SETUP_INSTRUCTIONS.md)
   - Create a Google Cloud project and enable Gmail API
   - Download OAuth credentials and save as `data/gmail_credentials.json`

2. **Add account in application**:
   - Click `File > Add Account`
   - Enter your Gmail address
   - Check "Use OAuth 2.0 (Recommended for Gmail)"
   - Click "Start OAuth Authorization"
   - Browser will open for you to authorize
   - Grant permissions and return to the application

3. **That's it!**:
   - You only need to authorize once
   - Tokens are automatically refreshed
   - No passwords needed or stored

### Gmail (App Password - Alternative)

If you prefer not to use OAuth:

1. **Enable 2-Factor Authentication**:
   - Go to your Google Account settings
   - Navigate to Security > 2-Step Verification
   - Enable 2-factor authentication

2. **Generate App Password**:
   - In Google Account settings, go to Security > App passwords
   - Generate a new app password for "Mail"
   - Use this 16-character password in the application

3. **Enable IMAP** (if not already enabled):
   - Go to Gmail settings > See all settings > Forwarding and POP/IMAP
   - Enable IMAP access

### Outlook/Hotmail

1. **Enable IMAP**:
   - Go to Outlook.com settings
   - Navigate to Mail > Sync email > POP and IMAP
   - Under IMAP, select "Yes"

2. **Use Regular Password**:
   - Outlook doesn't require app passwords
   - Use your regular account password

## Usage Guide

### Scanning

- Click "Scan Inbox" to analyze your emails
- The application reads email headers only (no full message content)
- Scanning is safe and won't mark emails as read
- After scanning, senders are organized into multiple tabs
- No-reply senders are automatically detected and shown in a separate tab

### Using Filters

**All tables support Excel-style filtering:**
- Type in any filter box above columns to search
- Filters work across multiple columns simultaneously
- Right-click any filter box to clear that specific filter
- Press **Escape** in any filter box to clear all filters
- Filters automatically adjust when you resize the window or columns

### Unsubscribing

1. **Select senders** from the Senders tab (Ctrl+click for multiple)
2. **Click "Unsubscribe Selected"**
3. **Confirm** the operation
4. **Wait** for completion (may take several minutes)

The application tries multiple unsubscribe strategies:
1. **RFC 2369 List-Unsubscribe headers** (most reliable)
2. **Direct HTTP links** found in emails

**Results shown in status bar** - No popup notifications for completed operations

### Must Delete List

**For senders where unsubscribe fails:**

1. **Automatic Addition**: Failed unsubscribes are automatically added to the Must Delete tab
2. **Manual Addition**: Right-click any sender in the Senders tab and select "Add to Must Delete"
3. **View List**: Switch to the "Must Delete" tab to see all senders
4. **Delete Selected**: Select specific senders and click "Delete Selected"
5. **Auto Delete**: Click "Auto Delete" to process all senders in the list at once

**Auto Delete features:**
- Checks each sender for emails in your inbox
- Deletes all emails found
- Removes senders from the list after successful deletion
- Shows progress and summary in status bar

### No-Reply Senders

**Automatically detected senders with no-reply email patterns:**

1. **Automatic Detection**: Senders with emails containing at least 2 of these keywords are flagged: `no`, `not`, `do`, `reply`
2. **Examples**: `noreply@`, `donotreply@`, `no-reply@`, etc.
3. **View Tab**: Check the "No-Reply Senders" tab after scanning
4. **Bulk Delete**: Click "Delete All Emails" to remove all emails from these senders

### Whitelist Management

**To protect important senders:**

**Quick Add:**
1. **Right-click a sender** in the Senders tab
2. Select "Add to Whitelist"

**Manual Add:**
1. Go to the **Whitelist tab**
2. Click **"Add Entry"**
3. Choose Email or Domain type
4. Enter the email/domain and optional notes

**Whitelisted senders:**
- Are marked with green background and "Protected" score
- Cannot be selected for unsubscribe or delete operations
- Can be individual emails or entire domains (e.g., `@company.com`)

### Context Menu Actions

**Right-click any sender in the Senders tab for quick actions:**
- **Add to Whitelist**: Protect this sender from operations
- **Add to Must Delete**: Mark for bulk deletion

## Troubleshooting

### Connection Issues

**"Connection failed" errors:**
- Check your internet connection
- Verify email address and password
- For Gmail: Ensure you used an app password, not your regular password
- For Outlook: Make sure IMAP is enabled

**"Authentication failed" errors:**
- Double-check your email address spelling
- For Gmail: Regenerate your app password
- For Outlook: Try your regular password

### Scan Issues

**"Scan failed" errors:**
- Check your internet connection
- Verify your email account has IMAP enabled
- Try again later if the email server is busy

**No senders found:**
- Check if your inbox is empty
- Verify the account is configured correctly
- Try rescanning

### Unsubscribe Issues

**"Unsubscribe failed" errors:**
- Some senders may not support automatic unsubscribe
- The application will mark these for manual deletion
- Check the "Must Delete" tab for senders that need manual cleanup

## Privacy & Security

- **Read-only by default**: The application only reads email headers, never modifies emails without explicit confirmation
- **Local storage only**: All data is stored locally in an encrypted database
- **No data transmission**: Your emails and credentials never leave your computer
- **App passwords recommended**: Use app-specific passwords for enhanced security

## Advanced Configuration

### Settings

Access `Settings > Preferences` to configure:
- **Batch size**: Number of emails to process at once (default: 500)
- **Timeout**: Network timeout in seconds (default: 30)

### Logging

The application logs all operations to `data/logs/app.log` for troubleshooting. Enable debug logging by modifying the logging configuration if needed.

## Contributing

This is an open-source project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or feature requests:
- Check the troubleshooting section above
- Review existing issues on GitHub
- Create a new issue with detailed information

## Changelog

### Version 1.2.0 (Current)
- **NEW**: Excel-style filtering on all tables with real-time search
- **NEW**: No-Reply Senders tab - automatically detects and isolates no-reply email addresses
- **NEW**: Auto Delete button in Must Delete tab for bulk processing
- **NEW**: Context menu actions - right-click senders for quick operations
- **NEW**: Dynamic filter alignment - filters adjust automatically when resizing
- **NEW**: Score tooltips showing detailed breakdown on hover
- **IMPROVED**: Status bar messaging replaces many popup dialogs
- **IMPROVED**: Enhanced keyboard shortcuts (Escape to clear filters)
- **IMPROVED**: Better visual organization with 4-tab interface
- **IMPROVED**: Debounced filter updates for smoother performance

### Version 1.1.0
- **NEW**: Gmail OAuth 2.0 authentication support
- **NEW**: Automatic token refresh for seamless access
- **NEW**: Secure encrypted token storage
- **IMPROVED**: Better Gmail authentication experience

### Version 1.0.0
- Initial release
- Core unsubscribe functionality
- Gmail and Outlook support
- Whitelist protection
- Manual email deletion
- Score-based sender prioritization
