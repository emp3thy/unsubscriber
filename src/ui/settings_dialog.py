"""
Account setup dialog for Email Unsubscriber.

This module provides a dialog for adding and testing email account credentials
with built-in connection testing and provider auto-detection. Supports OAuth 2.0
for Gmail accounts.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import re
import logging
from src.email_client.imap_client import IMAPClient
from src.email_client.credentials import CredentialManager
from src.email_client.gmail_oauth import OAuthCredentialManager
from src.database.db_manager import DBManager
from src.ui.oauth_dialog import GmailOAuthDialog


class AccountDialog(tk.Toplevel):
    """Dialog for adding email accounts."""
    
    def __init__(self, parent, db_manager: DBManager, cred_manager: CredentialManager):
        """
        Initialize the account setup dialog.
        
        Args:
            parent: Parent window
            db_manager: DBManager instance for database operations
            cred_manager: CredentialManager instance for encryption
        """
        super().__init__(parent)
        self.db = db_manager
        self.cred = cred_manager
        self.oauth_manager = OAuthCredentialManager(db_manager, cred_manager)
        self.connection_tested = False
        self.is_gmail = False
        self.use_oauth = False
        self.logger = logging.getLogger(__name__)
        
        self.title("Add Email Account")
        self.geometry("450x450")
        self.resizable(False, False)
        
        self._create_form_fields()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.logger.info("Account dialog opened")
    
    def _create_form_fields(self):
        """Create form fields."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Email
        ttk.Label(main_frame, text="Email Address:", font=('', 10)).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=10
        )
        self.email_entry = ttk.Entry(main_frame, width=35)
        self.email_entry.grid(row=0, column=1, padx=5, pady=10)
        self.email_entry.bind('<FocusOut>', self._detect_provider)
        
        # Password
        ttk.Label(main_frame, text="App Password:", font=('', 10)).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=10
        )
        self.password_entry = ttk.Entry(main_frame, width=35, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=10)
        
        # Show/Hide password
        self.show_password = tk.BooleanVar()
        ttk.Checkbutton(
            main_frame, 
            text="Show password", 
            variable=self.show_password,
            command=self._toggle_password
        ).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Provider
        ttk.Label(main_frame, text="Provider:", font=('', 10)).grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=10
        )
        self.provider_label = ttk.Label(
            main_frame, 
            text="(auto-detect)", 
            font=('', 10, 'italic')
        )
        self.provider_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=10)
        
        # Gmail OAuth option
        self.oauth_frame = ttk.Frame(main_frame)
        self.oauth_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.use_oauth_var = tk.BooleanVar(value=False)
        self.oauth_checkbox = ttk.Checkbutton(
            self.oauth_frame,
            text="Use OAuth 2.0 (Recommended for Gmail)",
            variable=self.use_oauth_var,
            command=self._toggle_oauth
        )
        self.oauth_checkbox.pack()
        
        ttk.Button(
            self.oauth_frame,
            text="Start OAuth Authorization",
            command=self._start_oauth
        ).pack(pady=5)
        
        # Hide OAuth frame initially
        self.oauth_frame.grid_remove()
        
        # Info label
        self.info_label = ttk.Label(
            main_frame, 
            text="", 
            font=('', 8), 
            foreground='gray',
            wraplength=380,
            justify=tk.LEFT
        )
        self.info_label.grid(row=5, column=0, columnspan=2, pady=15)
        
        # Status label for connection feedback
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=('', 9),
            wraplength=380
        )
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        self.test_btn = ttk.Button(
            button_frame, 
            text="Test Connection", 
            command=self._test_connection
        )
        self.test_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(
            button_frame, 
            text="Save", 
            command=self._save_account, 
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def _detect_provider(self, event=None):
        """Auto-detect provider from email."""
        email = self.email_entry.get().lower()
        
        if '@gmail.com' in email or '@googlemail.com' in email:
            provider = "Gmail"
            self.is_gmail = True
            self.oauth_frame.grid()
            self._update_info_text()
        elif '@outlook.com' in email or '@hotmail.com' in email or '@live.com' in email:
            provider = "Outlook"
            self.is_gmail = False
            self.oauth_frame.grid_remove()
            self.use_oauth_var.set(False)
            self._update_info_text()
        elif '@yahoo.com' in email or '@ymail.com' in email:
            provider = "Yahoo"
            self.is_gmail = False
            self.oauth_frame.grid_remove()
            self.use_oauth_var.set(False)
            self._update_info_text()
        else:
            provider = "Unknown"
            self.is_gmail = False
            self.oauth_frame.grid_remove()
            self.use_oauth_var.set(False)
            self._update_info_text()
        
        self.provider_label.config(text=provider)
        self.logger.debug(f"Detected provider: {provider} for email: {email}")
    
    def _update_info_text(self):
        """Update info text based on provider and auth method."""
        if self.is_gmail and self.use_oauth_var.get():
            info_text = (
                "OAuth 2.0 is the recommended authentication method for Gmail.\n"
                "Click 'Start OAuth Authorization' to begin the authorization process."
            )
        elif self.is_gmail:
            info_text = (
                "Gmail no longer supports regular passwords.\n"
                "You can use OAuth 2.0 (recommended) or generate an App Password."
            )
        else:
            info_text = (
                "Note: For Outlook, you must generate an App Password\n"
                "from your account security settings. Do not use your regular password."
            )
        self.info_label.config(text=info_text)
    
    def _toggle_oauth(self):
        """Toggle OAuth authentication option."""
        self.use_oauth = self.use_oauth_var.get()
        self._update_info_text()
        
        # Update password field requirement
        if self.use_oauth:
            self.password_entry.config(state=tk.DISABLED)
        else:
            self.password_entry.config(state=tk.NORMAL)
    
    def _start_oauth(self):
        """Start OAuth authorization process."""
        email = self.email_entry.get().strip()
        
        # Validate email
        if not email or not self._validate_email(email):
            messagebox.showerror("Error", "Please enter a valid Gmail address")
            return
        
        # Open OAuth dialog
        oauth_dialog = GmailOAuthDialog(self, email, self.db, self.cred)
        self.wait_window(oauth_dialog)
        
        # Check if authorization was successful
        if oauth_dialog.was_successful():
            self.connection_tested = True
            self.save_btn.config(state=tk.NORMAL)
            self.status_label.config(
                text="✓ OAuth authorization successful!",
                foreground='green'
            )
            self.logger.info(f"OAuth authorization successful for {email}")
            
            # Automatically save the account
            self._save_oauth_account()
    
    def _toggle_password(self):
        """Toggle password visibility."""
        if self.show_password.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
    
    def _validate_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _test_connection(self):
        """Test IMAP connection."""
        email = self.email_entry.get().strip()
        
        # Check if using OAuth
        if self.use_oauth_var.get():
            messagebox.showinfo(
                "OAuth Mode",
                "For OAuth authentication, please use the 'Start OAuth Authorization' button."
            )
            return
        
        password = self.password_entry.get()
        
        # Validate inputs
        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password")
            return
        
        if not self._validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        # Show testing status
        self.status_label.config(text="Testing connection...", foreground='blue')
        self.config(cursor="watch")
        self.update()
        
        try:
            self.logger.info(f"Testing connection for {email}")
            client = IMAPClient(email, password)
            
            if client.connect():
                self.connection_tested = True
                self.save_btn.config(state=tk.NORMAL)
                self.status_label.config(
                    text="✓ Connection successful!", 
                    foreground='green'
                )
                messagebox.showinfo(
                    "Success", 
                    "Connection successful! You can now save the account."
                )
                client.disconnect()
                self.logger.info(f"Connection test successful for {email}")
            else:
                error_msg = client.get_error_message() or "Connection failed"
                self.status_label.config(
                    text="✗ Connection failed",
                    foreground='red'
                )
                messagebox.showerror("Error", error_msg)
                self.logger.warning(f"Connection test failed for {email}")
                
        except Exception as e:
            error_msg = str(e)
            # Try to get a more specific error message from the client if available
            client_error = client.get_error_message() if 'client' in locals() else ""
            display_error = client_error or "Connection failed. Please check your email address and app password."

            self.status_label.config(
                text="✗ Connection failed",
                foreground='red'
            )
            messagebox.showerror("Error", display_error)
            self.logger.error(f"Connection test error for {email}: {error_msg}")
            
        finally:
            self.config(cursor="")
    
    def _save_account(self):
        """Save account to database."""
        if not self.connection_tested:
            messagebox.showwarning(
                "Warning", 
                "Please test the connection first to verify your credentials."
            )
            return
        
        # Check if using OAuth - OAuth accounts are saved automatically
        if self.use_oauth_var.get():
            messagebox.showinfo(
                "OAuth Account",
                "OAuth account was already saved during authorization."
            )
            self.destroy()
            return
        
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        provider = self.provider_label.cget("text").lower()
        
        try:
            self.logger.info(f"Saving account: {email}")
            
            # Encrypt password
            encrypted = self.cred.encrypt_password(password)
            
            # Save to database
            if self.db.add_account(email, encrypted, provider):
                messagebox.showinfo("Success", "Account saved successfully!")
                self.logger.info(f"Account saved successfully: {email}")
                self.destroy()
            else:
                messagebox.showerror("Error", "Failed to save account. Please check your email address and try again.")
                self.logger.error(f"Failed to save account to database: {email}")
                
        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("Error", f"Failed to save account: {error_msg}")
            self.logger.error(f"Error saving account {email}: {error_msg}")
    
    def _save_oauth_account(self):
        """Save OAuth account (called automatically after successful authorization)."""
        # OAuth tokens are already saved by the OAuth dialog
        # Just close this dialog
        self.destroy()


class SettingsDialog(tk.Toplevel):
    """Comprehensive settings dialog with tabs."""
    
    def __init__(self, parent, db_manager: DBManager, cred_manager: CredentialManager):
        """
        Initialize the settings dialog.
        
        Args:
            parent: Parent window
            db_manager: DBManager instance
            cred_manager: CredentialManager instance
        """
        super().__init__(parent)
        self.db = db_manager
        self.cred = cred_manager
        self.logger = logging.getLogger(__name__)
        
        self.title("Settings")
        self.geometry("600x450")
        self.resizable(True, True)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_accounts_tab()
        self._create_preferences_tab()
        self._create_about_tab()
        
        # Close button
        close_btn = ttk.Button(self, text="Close", command=self.destroy)
        close_btn.pack(pady=10)
        
        self.logger.info("Settings dialog opened")
    
    def _create_accounts_tab(self):
        """Create Accounts tab."""
        accounts_tab = ttk.Frame(self.notebook)
        self.notebook.add(accounts_tab, text="Accounts")
        
        # Title
        ttk.Label(accounts_tab, text="Email Accounts", font=('', 12, 'bold')).pack(pady=(10, 5))
        
        # Accounts listbox with scrollbar
        list_frame = ttk.Frame(accounts_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.accounts_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
        scrollbar.config(command=self.accounts_listbox.yview)
        
        self.accounts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(accounts_tab)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Add Account", command=self._add_account).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected", command=self._remove_account).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_accounts).pack(side=tk.LEFT, padx=5)
        
        # Load accounts
        self._refresh_accounts()
    
    def _create_preferences_tab(self):
        """Create Preferences tab."""
        prefs_tab = ttk.Frame(self.notebook)
        self.notebook.add(prefs_tab, text="Preferences")
        
        # Title
        ttk.Label(prefs_tab, text="Application Preferences", font=('', 12, 'bold')).pack(pady=(20, 10))
        
        # Main frame for settings
        settings_frame = ttk.Frame(prefs_tab)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=40)
        
        # Batch size setting
        ttk.Label(settings_frame, text="Email Batch Size:", font=('', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=10
        )
        self.batch_size_var = tk.StringVar(value=self.db.get_config('batch_size', '500'))
        batch_spinbox = ttk.Spinbox(
            settings_frame, 
            from_=100, 
            to=2000, 
            increment=100,
            textvariable=self.batch_size_var,
            width=10
        )
        batch_spinbox.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Timeout setting
        ttk.Label(settings_frame, text="Connection Timeout (seconds):", font=('', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=10
        )
        self.timeout_var = tk.StringVar(value=self.db.get_config('timeout', '30'))
        timeout_spinbox = ttk.Spinbox(
            settings_frame, 
            from_=10, 
            to=120, 
            increment=5,
            textvariable=self.timeout_var,
            width=10
        )
        timeout_spinbox.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Save button
        ttk.Button(settings_frame, text="Save Preferences", 
                  command=self._save_preferences).grid(row=2, column=0, columnspan=2, pady=20)
    
    def _create_about_tab(self):
        """Create About tab."""
        about_tab = ttk.Frame(self.notebook)
        self.notebook.add(about_tab, text="About")
        
        # App info
        info_frame = ttk.Frame(about_tab)
        info_frame.pack(expand=True)
        
        ttk.Label(info_frame, text="Email Unsubscriber", font=('', 16, 'bold')).pack(pady=(20, 5))
        ttk.Label(info_frame, text="Version 1.0.0", font=('', 10)).pack(pady=5)
        ttk.Label(info_frame, text="A tool to manage unwanted email subscriptions", 
                 font=('', 10)).pack(pady=5)
        
        # Logs location
        ttk.Label(info_frame, text="\nLog Files Location:", font=('', 10, 'bold')).pack(pady=(20, 5))
        logs_path = "data/logs/app.log"
        ttk.Label(info_frame, text=logs_path, font=('', 9), foreground='blue').pack(pady=5)
        
        # Database location
        ttk.Label(info_frame, text="\nDatabase Location:", font=('', 10, 'bold')).pack(pady=(10, 5))
        db_path = self.db.db_path
        ttk.Label(info_frame, text=db_path, font=('', 9), foreground='blue').pack(pady=5)
    
    def _refresh_accounts(self):
        """Refresh accounts list."""
        self.accounts_listbox.delete(0, tk.END)
        accounts = self.db.list_accounts()
        for account in accounts:
            email = account.get('email', 'Unknown')
            provider = account.get('provider', '').capitalize()
            self.accounts_listbox.insert(tk.END, f"{email} ({provider})")
    
    def _add_account(self):
        """Open add account dialog."""
        dialog = AccountDialog(self, self.db, self.cred)
        self.wait_window(dialog)
        self._refresh_accounts()
    
    def _remove_account(self):
        """Remove selected account."""
        selection = self.accounts_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an account to remove")
            return
        
        # Get selected account email
        account_str = self.accounts_listbox.get(selection[0])
        email = account_str.split(' (')[0]  # Extract email from "email (provider)"
        
        # Confirm removal
        result = messagebox.askyesno(
            "Confirm Remove",
            f"Remove account {email}?\n\nThis will not delete any emails."
        )
        
        if result:
            if self.db.delete_account(email):
                messagebox.showinfo("Success", f"Account {email} removed")
                self._refresh_accounts()
            else:
                messagebox.showerror("Error", "Failed to remove account")
    
    def _save_preferences(self):
        """Save preferences to database."""
        try:
            batch_size = self.batch_size_var.get()
            timeout = self.timeout_var.get()
            
            self.db.set_config('batch_size', batch_size)
            self.db.set_config('timeout', timeout)
            
            messagebox.showinfo("Success", "Preferences saved successfully")
            self.logger.info(f"Preferences saved: batch_size={batch_size}, timeout={timeout}")
        except Exception as e:
            messagebox.showerror("Error", "Failed to save preferences. Please try again.")
            self.logger.error(f"Error saving preferences: {e}")
