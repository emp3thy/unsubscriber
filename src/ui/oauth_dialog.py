"""
OAuth authentication dialog for Gmail accounts.

This module provides a dialog that guides users through the OAuth 2.0
authorization process for Gmail accounts.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
from src.email_client.gmail_oauth import GmailOAuthManager, OAuthCredentialManager
from src.email_client.credentials import CredentialManager
from src.database.db_manager import DBManager


class GmailOAuthDialog(tk.Toplevel):
    """Dialog for Gmail OAuth 2.0 authentication."""
    
    def __init__(self, parent, email: str, db_manager: DBManager, cred_manager: CredentialManager):
        """
        Initialize the Gmail OAuth dialog.
        
        Args:
            parent: Parent window
            email: Gmail address to authorize
            db_manager: DBManager instance for database operations
            cred_manager: CredentialManager instance for encryption
        """
        super().__init__(parent)
        self.email = email
        self.db = db_manager
        self.cred = cred_manager
        self.oauth_manager = GmailOAuthManager()
        self.oauth_cred_manager = OAuthCredentialManager(db_manager, cred_manager)
        self.authorization_success = False
        self.logger = logging.getLogger(__name__)
        
        self.title("Gmail OAuth Authorization")
        self.geometry("500x400")
        self.resizable(False, False)
        
        self._create_ui()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.logger.info(f"OAuth dialog opened for {email}")
    
    def _create_ui(self):
        """Create the UI elements."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Gmail OAuth Authorization",
            font=('', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Email label
        email_label = ttk.Label(
            main_frame,
            text=f"Account: {self.email}",
            font=('', 11)
        )
        email_label.pack(pady=(0, 20))
        
        # Instructions
        instructions_text = (
            "To connect your Gmail account, you need to authorize this application "
            "using Google's OAuth 2.0 process.\n\n"
            "Steps:\n"
            "1. Click 'Start Authorization' below\n"
            "2. A browser window will open\n"
            "3. Log in to your Google account\n"
            "4. Grant the requested permissions\n"
            "5. Return to this application\n\n"
            "Required permissions:\n"
            "• Full mail access (read, send, delete)\n\n"
            "Note: You only need to do this once. The application will "
            "remember your authorization."
        )
        
        instructions_label = ttk.Label(
            main_frame,
            text=instructions_text,
            font=('', 9),
            wraplength=450,
            justify=tk.LEFT
        )
        instructions_label.pack(pady=(0, 20))
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=('', 10),
            wraplength=450
        )
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.auth_btn = ttk.Button(
            button_frame,
            text="Start Authorization",
            command=self._start_authorization
        )
        self.auth_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Setup instructions button
        ttk.Button(
            main_frame,
            text="Setup Instructions",
            command=self._show_setup_instructions
        ).pack(pady=(10, 0))
    
    def _show_setup_instructions(self):
        """Show setup instructions for OAuth credentials."""
        instructions = (
            "Before using Gmail OAuth, you need to set up OAuth credentials:\n\n"
            "1. Go to Google Cloud Console:\n"
            "   https://console.cloud.google.com/\n\n"
            "2. Create a new project or select existing one\n\n"
            "3. Enable Gmail API for your project\n\n"
            "4. Configure OAuth consent screen:\n"
            "   - User type: External\n"
            "   - Add scope: https://mail.google.com/\n\n"
            "5. Create OAuth 2.0 credentials:\n"
            "   - Application type: Desktop application\n"
            "   - Download credentials JSON file\n\n"
            "6. Save the JSON file as:\n"
            "   data/gmail_credentials.json\n\n"
            "For detailed instructions, see GMAIL_OAUTH_GUIDE.md"
        )
        
        messagebox.showinfo("OAuth Setup Instructions", instructions)
    
    def _start_authorization(self):
        """Start the OAuth authorization process."""
        # Check if credentials file exists
        if not self.oauth_manager.has_credentials_file():
            messagebox.showerror(
                "Credentials Not Found",
                "OAuth credentials file not found.\n\n"
                "Please set up OAuth credentials first.\n"
                "Click 'Setup Instructions' for details."
            )
            return
        
        # Disable buttons
        self.auth_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)
        
        # Show status
        self.status_label.config(text="Opening browser for authorization...", foreground='blue')
        self.progress.start()
        
        # Run authorization in thread to avoid blocking UI
        auth_thread = threading.Thread(target=self._authorize_in_thread)
        auth_thread.daemon = True
        auth_thread.start()
    
    def _authorize_in_thread(self):
        """Run OAuth authorization in a separate thread."""
        try:
            self.logger.info(f"Starting OAuth authorization for {self.email}")
            
            # Start OAuth flow
            tokens = self.oauth_manager.authorize(self.email)
            
            if tokens:
                # Store tokens in database
                success = self.oauth_cred_manager.store_oauth_tokens(
                    self.email,
                    tokens['access_token'],
                    tokens['refresh_token'],
                    tokens.get('token_expiry')
                )
                
                if success:
                    # Update UI on success
                    self.after(0, self._authorization_complete, True)
                else:
                    self.after(0, self._authorization_complete, False, "Failed to store tokens")
            else:
                self.after(0, self._authorization_complete, False, "Authorization failed")
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"OAuth authorization error: {error_msg}")
            self.after(0, self._authorization_complete, False, error_msg)
    
    def _authorization_complete(self, success: bool, error_msg: str = ""):
        """Handle completion of authorization process.
        
        Args:
            success: Whether authorization succeeded
            error_msg: Error message if failed
        """
        # Stop progress bar
        self.progress.stop()
        
        # Re-enable buttons
        self.auth_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.NORMAL)
        
        if success:
            self.status_label.config(
                text="✓ Authorization successful!",
                foreground='green'
            )
            self.authorization_success = True
            
            # Add account to database
            self.db.add_account(self.email, "", "gmail")
            
            messagebox.showinfo(
                "Success",
                "Gmail account authorized successfully!\n\n"
                "You can now use this account to access your emails."
            )
            
            self.logger.info(f"OAuth authorization successful for {self.email}")
            
            # Close dialog after short delay
            self.after(1000, self.destroy)
        else:
            self.status_label.config(
                text=f"✗ Authorization failed: {error_msg}",
                foreground='red'
            )
            messagebox.showerror(
                "Authorization Failed",
                f"Failed to authorize Gmail account:\n\n{error_msg}\n\n"
                "Please try again or check the setup instructions."
            )
            self.logger.error(f"OAuth authorization failed for {self.email}: {error_msg}")
    
    def _cancel(self):
        """Cancel the OAuth process."""
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel authorization?"):
            self.destroy()
    
    def was_successful(self) -> bool:
        """Check if authorization was successful.
        
        Returns:
            True if authorization succeeded, False otherwise
        """
        return self.authorization_success
