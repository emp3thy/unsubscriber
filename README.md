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

Hover over score values to see the breakdown of how each score was calculated.

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

### Unsubscribing

1. **Select senders** from the table (Ctrl+click for multiple)
2. **Click "Unsubscribe Selected"**
3. **Confirm** the operation
4. **Wait** for completion (may take several minutes)

The application tries multiple unsubscribe strategies:
1. **RFC 2369 List-Unsubscribe headers** (most reliable)
2. **Direct HTTP links** found in emails

### Manual Deletion

For senders where unsubscribe fails:
1. **Go to "Must Delete" tab**
2. **Select senders** you want to delete emails from
3. **Click "Delete All Must-Delete"**
4. **Confirm** the operation

### Whitelist Management

To protect important senders:
1. **Right-click a sender** in the table and select "Add to Whitelist"
2. **Or use the Whitelist tab** to manually add entries

Whitelisted senders:
- Won't appear in scan results
- Are protected from deletion operations
- Can be individual emails or entire domains (e.g., `@company.com`)

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
