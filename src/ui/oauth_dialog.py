"""
OAuth authorization dialog for Gmail accounts.

Provides a user interface for the OAuth 2.0 authorization flow,
including browser-based authorization and token storage.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from src.email_client.gmail_oauth import GmailOAuthManager, OAuthCredentialManager


class GmailOAuthDialog(tk.Toplevel):
    """Dialog for Gmail OAuth 2.0 authorization."""
    
    def __init__(self, parent, email: str, db_manager, cred_manager):
        """Initialize OAuth authorization dialog.
        
        Args:
            parent: Parent window
            email: Gmail address to authorize
            db_manager: DBManager instance
            cred_manager: CredentialManager instance
        """
        super().__init__(parent)
        self.email = email
        self.db = db_manager
        self.cred = cred_manager
        self.oauth_manager = OAuthCredentialManager(db_manager, cred_manager)
        self.gmail_oauth = GmailOAuthManager()
        self.success = False
        self.logger = logging.getLogger(__name__)
        
        self.title(f"Gmail OAuth Authorization - {email}")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
        self.logger.info(f"OAuth dialog opened for {email}")
    
    def _create_ui(self):
        """Create the OAuth authorization UI."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Gmail OAuth 2.0 Authorization",
            font=('', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Email info
        email_label = ttk.Label(
            main_frame,
            text=f"Authorizing access for: {self.email}",
            font=('', 10)
        )
        email_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = (
            "To authorize Gmail access:\n\n"
            "1. Click 'Start Authorization' below\n"
            "2. Your web browser will open to Google's authorization page\n"
            "3. Sign in to your Gmail account if prompted\n"
            "4. Review and grant the requested permissions\n"
            "5. Return to this application\n\n"
            "The authorization is secure and handled entirely by Google.\n"
            "Your credentials are never stored by this application."
        )
        
        instructions_label = ttk.Label(
            main_frame,
            text=instructions,
            font=('', 9),
            justify=tk.LEFT,
            wraplength=450
        )
        instructions_label.pack(pady=(0, 20))
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Ready to start authorization",
            font=('', 9),
            foreground='blue'
        )
        self.status_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=400
        )
        self.progress.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.auth_btn = tk.Button(
            button_frame,
            text="Start Authorization",
            command=self._start_authorization,
            width=20,
            height=2,
            bg='#0078d4',
            fg='white',
            font=('Arial', 9, 'bold'),
            relief='raised',
            bd=2
        )
        self.auth_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel,
            width=15,
            height=2,
            bg='#f0f0f0',
            fg='black',
            font=('Arial', 9),
            relief='raised',
            bd=2
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def _start_authorization(self):
        """Start the OAuth authorization process."""
        self.auth_btn.config(state=tk.DISABLED, bg='#cccccc')
        self.status_label.config(text="Starting authorization...", foreground='blue')
        self.progress.start()
        
        # Run authorization in background thread
        auth_thread = threading.Thread(target=self._run_authorization, daemon=True)
        auth_thread.start()
    
    def _run_authorization(self):
        """Run OAuth authorization in background thread."""
        try:
            self.logger.info(f"Starting OAuth flow for {self.email}")
            
            # Update status on main thread
            self.after(0, lambda: self.status_label.config(
                text="Opening browser for authorization...", foreground='blue'
            ))
            
            # Run OAuth flow
            tokens = self.gmail_oauth.authorize_user()
            
            if tokens:
                # Store tokens
                self.oauth_manager.store_oauth_tokens(
                    self.email,
                    tokens['access_token'],
                    tokens['refresh_token'],
                    tokens.get('token_expiry')
                )
                
                # Update UI on main thread
                self.after(0, self._authorization_success)
                self.logger.info(f"OAuth authorization successful for {self.email}")
            else:
                # Update UI on main thread
                self.after(0, self._authorization_failed, "Authorization was cancelled or failed")
                self.logger.warning(f"OAuth authorization failed for {self.email}")
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"OAuth authorization error for {self.email}: {error_msg}")
            # Update UI on main thread
            self.after(0, self._authorization_failed, f"Authorization error: {error_msg}")
    
    def _authorization_success(self):
        """Handle successful authorization."""
        self.progress.stop()
        self.status_label.config(
            text="✓ Authorization successful! Gmail access granted.",
            foreground='green'
        )
        self.success = True
        
        # Update buttons
        self.auth_btn.config(text="Done", state=tk.NORMAL, command=self.destroy, bg='#28a745')
        self.cancel_btn.config(text="Close", command=self.destroy)
        
        messagebox.showinfo(
            "Success",
            f"Gmail authorization successful!\n\n"
            f"Account {self.email} is now configured for OAuth access."
        )
    
    def _authorization_failed(self, error_message: str):
        """Handle failed authorization.
        
        Args:
            error_message: Error message to display
        """
        self.progress.stop()
        self.status_label.config(
            text="✗ Authorization failed",
            foreground='red'
        )
        
        # Re-enable auth button
        self.auth_btn.config(state=tk.NORMAL, bg='#0078d4')
        
        messagebox.showerror(
            "Authorization Failed",
            f"Gmail authorization failed:\n\n{error_message}\n\n"
            f"Please try again or check your internet connection."
        )
    
    def _cancel(self):
        """Cancel the authorization process."""
        self.destroy()
    
    def was_successful(self) -> bool:
        """Check if authorization was successful.
        
        Returns:
            True if authorization completed successfully, False otherwise
        """
        return self.success