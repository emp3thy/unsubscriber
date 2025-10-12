"""
Main application window for Email Unsubscriber.

This module contains the MainWindow class which creates and manages
the primary user interface including menu bar, content area, and status bar.
Supports OAuth 2.0 for Gmail accounts.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from src.ui.settings_dialog import AccountDialog, SettingsDialog
from src.ui.sender_table import SenderTable
from src.ui.must_delete_table import MustDeleteTable
from src.ui.whitelist_table import WhitelistTable
from src.ui.noreply_table import NoReplyTable
from src.ui.progress_dialog import ProgressDialog
from src.utils.threading_utils import BackgroundTask
from src.utils.email_patterns import get_noreply_senders
from src.email_client.credentials import CredentialManager
from src.email_client.gmail_oauth import OAuthCredentialManager
from src.email_client.auth import AuthStrategyFactory
from src.email_client.client_factory import create_email_client
from src.services.service_factory import ServiceFactory


class MainWindow:
    """Main application window."""
    
    def __init__(self, root, db_manager, service_factory=None):
        """
        Initialize the main application window.
        
        Args:
            root: Tkinter root window
            db_manager: DBManager instance for database operations
            service_factory: ServiceFactory instance (optional, creates default if not provided)
        """
        self.root = root
        self.db = db_manager
        self.cred_manager = CredentialManager()
        self.oauth_manager = OAuthCredentialManager(db_manager, self.cred_manager)
        self.auth_factory = AuthStrategyFactory(self.cred_manager, self.oauth_manager)
        self.logger = logging.getLogger(__name__)
        
        # Initialize service factory (for backward compatibility, create if not provided)
        if service_factory is None:
            self.logger.info("Creating default ServiceFactory")
            self.service_factory = ServiceFactory(db_manager)
        else:
            self.service_factory = service_factory
            self.logger.info("Using provided ServiceFactory")
        
        # Configure window
        self.root.title("Email Unsubscriber")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self._center_window()
        
        # Create UI components
        self._create_menu_bar()
        self._create_main_content()
        self._create_status_bar()
        
        self.logger.info("Main window initialized")
    
    def _create_email_client(self, account: dict):
        """Create email client (Gmail API or IMAP) based on account.
        
        Args:
            account: Account dictionary from database with 'email', 'provider', etc.
            
        Returns:
            Email client instance implementing EmailClientInterface
        """
        return create_email_client(
            account=account,
            auth_factory=self.auth_factory,
            oauth_manager=self.oauth_manager
        )
    
    def _center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.logger.debug(f"Window centered at {x},{y} with size {width}x{height}")
    
    def _create_menu_bar(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Account", command=self._add_account)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences", command=self._open_settings)
        settings_menu.add_command(label="View Logs", state=tk.DISABLED)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Generate App Password", command=self._show_app_password_help)
        
        self.logger.debug("Menu bar created")
    
    def _create_main_content(self):
        """Create main content area with tabs."""
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create toolbar
        self._create_toolbar()
        
        # Create statistics frame
        self._create_statistics_frame()
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create Senders tab
        self.senders_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.senders_tab, text="Senders")
        
        # Create sender table in senders tab
        self.sender_table = SenderTable(self.senders_tab)
        self.sender_table.pack(fill=tk.BOTH, expand=True)

        # Bind selection change to enable/disable unsubscribe button
        self.sender_table.tree.bind('<<TreeviewSelect>>', self._on_sender_selection_changed)

        # Set whitelist callback for right-click context menu
        self.sender_table.set_whitelist_callback(self._quick_add_to_whitelist)
        
        # Set must delete callback for right-click context menu
        self.sender_table.set_must_delete_callback(self._quick_add_to_must_delete)
        
        # Create Must Delete tab
        self.must_delete_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.must_delete_tab, text="Must Delete")

        # Create must-delete table first (main content)
        self.must_delete_table = MustDeleteTable(self.must_delete_tab)
        self.must_delete_table.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Create toolbar for must-delete tab (can now bind to existing table)
        self._create_must_delete_toolbar()
        
        # Create Whitelist tab
        self.whitelist_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.whitelist_tab, text="Whitelist")

        # Create whitelist table first (main content)
        self.whitelist_table = WhitelistTable(self.whitelist_tab)
        self.whitelist_table.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Create toolbar for whitelist tab (can now bind to existing table)
        self._create_whitelist_toolbar()
        
        # Create No-Reply Senders tab
        self.noreply_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.noreply_tab, text="No-Reply Senders")
        
        # Create no-reply table first (main content)
        self.noreply_table = NoReplyTable(self.noreply_tab)
        self.noreply_table.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create toolbar for no-reply tab
        self._create_noreply_toolbar()

        # Bind tab change event to refresh tables
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        
        self.logger.debug("Main content frame with tabs created")
    
    def _create_status_bar(self):
        """Create status bar at bottom."""
        self.status_bar = ttk.Label(
            self.root, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.logger.debug("Status bar created")
    
    def _create_toolbar(self):
        """Create toolbar with action buttons."""
        toolbar = ttk.Frame(self.content_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # Scan Inbox button
        self.scan_btn = ttk.Button(
            toolbar, 
            text="Scan Inbox", 
            command=self.scan_inbox
        )
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        # Unsubscribe Selected button
        self.unsub_btn = ttk.Button(
            toolbar,
            text="Unsubscribe Selected",
            command=self.unsubscribe_selected,
            state=tk.DISABLED
        )
        self.unsub_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete Selected button
        self.delete_btn = ttk.Button(
            toolbar,
            text="Delete Selected",
            command=self.delete_selected,
            state=tk.DISABLED
        )
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Note: sender_table binding will be added after sender_table is created
        
        self.logger.debug("Toolbar created")
    
    def _create_statistics_frame(self):
        """Create statistics display above sender table."""
        self.stats_frame = ttk.LabelFrame(
            self.content_frame, 
            text="Summary", 
            padding=15
        )
        self.stats_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # Create statistics grid
        stats_grid = ttk.Frame(self.stats_frame)
        stats_grid.pack()
        
        # Total Senders
        ttk.Label(
            stats_grid, 
            text="Total Senders:", 
            font=('', 10, 'bold')
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.stat_total_senders = ttk.Label(
            stats_grid, 
            text="0", 
            font=('', 14)
        )
        self.stat_total_senders.grid(row=0, column=1, padx=10, pady=5)
        
        # Can Unsubscribe
        ttk.Label(
            stats_grid, 
            text="Can Unsubscribe:", 
            font=('', 10, 'bold')
        ).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.stat_can_unsub = ttk.Label(
            stats_grid, 
            text="0", 
            font=('', 14),
            foreground='green'
        )
        self.stat_can_unsub.grid(row=0, column=3, padx=10, pady=5)
        
        # Must Delete
        ttk.Label(
            stats_grid, 
            text="Must Delete:", 
            font=('', 10, 'bold')
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.stat_must_delete = ttk.Label(
            stats_grid, 
            text="0", 
            font=('', 14),
            foreground='black'
        )
        self.stat_must_delete.grid(row=1, column=1, padx=10, pady=5)
        
        # Total Emails
        ttk.Label(
            stats_grid, 
            text="Total Emails:", 
            font=('', 10, 'bold')
        ).grid(row=1, column=2, sticky=tk.W, padx=10, pady=5)
        self.stat_total_emails = ttk.Label(
            stats_grid, 
            text="0", 
            font=('', 14)
        )
        self.stat_total_emails.grid(row=1, column=3, padx=10, pady=5)
        
        self.logger.debug("Statistics frame created")
    
    def update_statistics(self, senders):
        """
        Update statistics from sender data.
        
        Args:
            senders: List of sender dictionaries
        """
        if not senders:
            # Reset to zeros
            self.stat_total_senders.config(text="0")
            self.stat_can_unsub.config(text="0")
            self.stat_must_delete.config(text="0")
            self.stat_total_emails.config(text="0")
            return
        
        # Calculate statistics
        total_senders = len(senders)
        can_unsubscribe = sum(1 for s in senders if s.get('has_unsubscribe'))
        total_emails = sum(s.get('total_count', 0) for s in senders)
        
        # Query must-delete from database
        must_delete = self.db.get_must_delete_count()
        
        # Update labels with formatting
        self.stat_total_senders.config(text=f"{total_senders:,}")
        self.stat_can_unsub.config(text=f"{can_unsubscribe:,}")
        self.stat_total_emails.config(text=f"{total_emails:,}")
        
        # Must delete with color coding
        self.stat_must_delete.config(
            text=f"{must_delete:,}",
            foreground='red' if must_delete > 0 else 'black'
        )
        
        self.logger.info(
            f"Statistics updated: {total_senders} senders, "
            f"{can_unsubscribe} with unsubscribe, {total_emails} total emails"
        )
    
    def _create_must_delete_toolbar(self):
        """Create toolbar for must-delete tab."""
        toolbar = ttk.Frame(self.must_delete_tab)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        # Auto Delete button
        self.auto_delete_btn = ttk.Button(
            toolbar,
            text="Auto Delete",
            command=self.auto_delete_must_delete
        )
        self.auto_delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete Selected button
        self.delete_selected_btn = ttk.Button(
            toolbar,
            text="Delete Selected",
            command=self.delete_selected_must_delete,
            state=tk.DISABLED
        )
        self.delete_selected_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind selection change to enable/disable button
        self.must_delete_table.tree.bind('<<TreeviewSelect>>',
                                         self._on_must_delete_selection_changed)
        
        self.logger.debug("Must-delete toolbar created")
    
    def _create_whitelist_toolbar(self):
        """Create toolbar for whitelist tab."""
        toolbar = ttk.Frame(self.whitelist_tab)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        # Add Entry button
        self.add_whitelist_btn = ttk.Button(
            toolbar,
            text="Add Entry",
            command=self.add_whitelist_entry
        )
        self.add_whitelist_btn.pack(side=tk.LEFT, padx=5)
        
        # Remove Selected button
        self.remove_whitelist_btn = ttk.Button(
            toolbar,
            text="Remove Selected",
            command=self.remove_whitelist_entry,
            state=tk.DISABLED
        )
        self.remove_whitelist_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind selection change to enable/disable button
        self.whitelist_table.tree.bind('<<TreeviewSelect>>',
                                      self._on_whitelist_selection_changed)
        
        self.logger.debug("Whitelist toolbar created")
    
    def _create_noreply_toolbar(self):
        """Create toolbar for no-reply senders tab."""
        toolbar = ttk.Frame(self.noreply_tab)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        # Delete All button
        self.delete_all_noreply_btn = ttk.Button(
            toolbar,
            text="Delete All Emails",
            command=self.delete_all_noreply
        )
        self.delete_all_noreply_btn.pack(side=tk.LEFT, padx=5)
        
        self.logger.debug("No-reply toolbar created")
    
    def _on_tab_changed(self, event):
        """Handle tab change event to refresh tables."""
        current_tab = self.notebook.index(self.notebook.select())
        
        # If switched to Must Delete tab (index 1), refresh the list
        if current_tab == 1:
            self._refresh_must_delete_list()
        # If switched to Whitelist tab (index 2), refresh the list
        elif current_tab == 2:
            self._refresh_whitelist()
    
    def _refresh_must_delete_list(self):
        """Refresh the must-delete sender list from database."""
        try:
            senders = self.db.get_must_delete_senders()
            self.must_delete_table.populate(senders)
            
            if not senders:
                self.logger.info("No senders in must-delete list")
            else:
                self.logger.info(f"Loaded {len(senders)} senders in must-delete list")
        except Exception as e:
            self.logger.error(f"Error refreshing must-delete list: {e}")
            messagebox.showerror("Error", "Failed to load must-delete list. Please try again.")
    
    def _on_must_delete_selection_changed(self, event=None):
        """Enable/disable delete button based on must-delete table selection."""
        selected = self.must_delete_table.get_selected()
        self.delete_selected_btn.config(state=tk.NORMAL if selected else tk.DISABLED)
    
    def delete_selected_must_delete(self):
        """Delete emails from selected must-delete senders using EmailDeletionService."""
        selected = self.must_delete_table.get_selected()
        if not selected:
            return
        
        # Calculate total count
        sender_count = len(selected)
        
        # Build confirmation message
        msg = f"Delete all emails from {sender_count} sender(s) in the must-delete list?\n\n"
        msg += "This will permanently delete all emails from these senders.\n"
        msg += "After deletion, these senders will be removed from the must-delete list.\n\n"
        msg += "⚠️ This action cannot be undone!"
        
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Confirm Deletion",
            msg,
            icon='warning'
        )
        
        if not result:
            return
        
        self.logger.info(f"Starting must-delete deletion for {sender_count} senders")
        
        # Disable button during operation
        self.delete_selected_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="Starting deletion...")
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Deleting Emails")
        
        # Create background task
        bg_task = BackgroundTask(self.root)
        
        def delete_task(progress_callback):
            """Delete emails in background thread using EmailDeletionService."""
            # Get account and connect
            account = self.db.get_primary_account()
            if not account:
                raise Exception("No account configured")
            
            client = self._create_email_client(account)
            if not client.connect():
                error_msg = client.get_error_message() or "Failed to connect to email server"
                raise Exception(error_msg)
            
            try:
                # Set email client in service factory
                self.service_factory.set_email_client(client)
                
                # Get deletion service from factory
                deletion_service = self.service_factory.create_deletion_service()
                
                # Set cancel callback to cancel the service
                progress.set_cancel_callback(deletion_service.cancel)
                
                # Convert selected format ('email' key) to service format ('sender' key)
                senders = [{'sender': s['email']} for s in selected]
                
                # Run deletion using service (service handles must-delete list removal)
                results = deletion_service.delete_from_senders(
                    senders,
                    progress_callback=progress_callback
                )
                
                return results
            finally:
                # Always disconnect client
                client.disconnect()
        
        def on_progress(current, total, message):
            """Update progress dialog."""
            progress.update_progress(current, total, message)
        
        def on_complete(results, error=None):
            """Handle completion."""
            progress.destroy()
            self.delete_selected_btn.config(state=tk.NORMAL)
            
            if error:
                self.status_bar.config(text="Deletion failed")
                messagebox.showerror("Error", "Failed to delete some emails. Please check your internet connection and try again.")
                self.logger.error(f"Must-delete deletion failed: {error}")
            elif results:
                deleted_senders = results['deleted_senders']
                total_emails = results['total_emails_deleted']
                failed_senders = results['failed_senders']
                deleted_emails = results.get('deleted_sender_emails', [])
                
                # Show summary
                self.logger.info(f"Must-delete deletion complete: {total_emails} emails from {deleted_senders} senders")
                
                # Remove deleted senders from sender table
                if deleted_emails:
                    self.sender_table.remove_senders(deleted_emails)
                    self.logger.debug(f"Removed {len(deleted_emails)} sender(s) from sender table after must-delete")
                
                # Refresh the must-delete list
                self._refresh_must_delete_list()
                
                # Update statistics
                current_senders = []
                if hasattr(self.sender_table, 'sender_data'):
                    current_senders = list(self.sender_table.sender_data.values())
                self.update_statistics(current_senders)
                
                # Show status in status bar
                status_msg = f"Deleted {total_emails:,} emails from {deleted_senders} senders"
                if failed_senders > 0:
                    status_msg += f" ({failed_senders} failed)"
                self.status_bar.config(text=status_msg)
            else:
                self.status_bar.config(text="Deletion cancelled")
                self.logger.info("Must-delete deletion cancelled by user")
        
        # Start deletion
        bg_task.run(delete_task, on_progress, on_complete)
    
    def auto_delete_must_delete(self):
        """Auto-delete all emails from all senders in the must delete list using EmailDeletionService."""
        # Get all senders from must delete list
        all_senders = self.db.get_must_delete_senders()
        
        if not all_senders:
            self.status_bar.config(text="Must delete list is empty")
            self.logger.info("Auto-delete: must delete list is empty")
            return
        
        # Calculate total count
        sender_count = len(all_senders)
        
        # Build confirmation message
        msg = f"Delete all emails from {sender_count} sender(s) in the must-delete list?\n\n"
        msg += "This will check each sender for emails in your inbox and delete them all.\n"
        msg += "After deletion, these senders will be removed from the must-delete list.\n\n"
        msg += "⚠️ This action cannot be undone!"
        
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Confirm Auto Delete",
            msg,
            icon='warning'
        )
        
        if not result:
            return
        
        self.logger.info(f"Starting auto-delete for {sender_count} must-delete senders")
        
        # Disable button during operation
        self.auto_delete_btn.config(state=tk.DISABLED)
        self.delete_selected_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="Starting auto-delete...")
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Auto-Deleting Emails")
        
        # Create background task
        bg_task = BackgroundTask(self.root)
        
        def delete_task(progress_callback):
            """Delete emails in background thread using EmailDeletionService."""
            # Get account and connect
            account = self.db.get_primary_account()
            if not account:
                raise Exception("No account configured")
            
            client = self._create_email_client(account)
            if not client.connect():
                error_msg = client.get_error_message() or "Failed to connect to email server"
                raise Exception(error_msg)
            
            try:
                # Set email client in service factory
                self.service_factory.set_email_client(client)
                
                # Get deletion service from factory
                deletion_service = self.service_factory.create_deletion_service()
                
                # Set cancel callback to cancel the service
                progress.set_cancel_callback(deletion_service.cancel)
                
                # Run deletion using service (service handles must-delete list automatically)
                results = deletion_service.delete_from_must_delete_list(
                    progress_callback=progress_callback
                )
                
                return results
            finally:
                # Always disconnect client
                client.disconnect()
        
        def on_progress(current, total, message):
            """Update progress dialog."""
            progress.update_progress(current, total, message)
        
        def on_complete(results, error=None):
            """Handle completion."""
            progress.destroy()
            self.auto_delete_btn.config(state=tk.NORMAL)
            self.delete_selected_btn.config(state=tk.NORMAL)
            
            if error:
                self.status_bar.config(text="Auto-delete failed")
                messagebox.showerror("Error", f"Failed to auto-delete emails: {error}")
                self.logger.error(f"Auto-delete failed: {error}")
            elif results:
                deleted_senders = results['deleted_senders']
                total_emails = results['total_emails_deleted']
                failed_senders = results['failed_senders']
                skipped_senders = results['skipped_senders']
                deleted_emails = results.get('deleted_sender_emails', [])
                
                self.logger.info(f"Auto-delete complete: {total_emails} emails from {deleted_senders} senders")
                
                # Remove deleted senders from sender table
                if deleted_emails:
                    self.sender_table.remove_senders(deleted_emails)
                    self.logger.debug(f"Removed {len(deleted_emails)} sender(s) from sender table after auto-delete")
                
                # Refresh the must-delete list
                self._refresh_must_delete_list()
                
                # Update statistics
                current_senders = []
                if hasattr(self.sender_table, 'sender_data'):
                    current_senders = list(self.sender_table.sender_data.values())
                self.update_statistics(current_senders)
                
                # Show status in status bar
                status_msg = f"Auto-deleted {total_emails:,} emails from {deleted_senders} senders"
                if skipped_senders > 0:
                    status_msg += f" ({skipped_senders} had no emails)"
                if failed_senders > 0:
                    status_msg += f" ({failed_senders} failed)"
                self.status_bar.config(text=status_msg)
            else:
                self.status_bar.config(text="Auto-delete cancelled")
                self.logger.info("Auto-delete cancelled by user")
        
        # Start deletion
        bg_task.run(delete_task, on_progress, on_complete)
    
    def delete_all_noreply(self):
        """Delete all emails from all no-reply senders in the table using EmailDeletionService."""
        # Get all senders from no-reply table
        all_senders = self.noreply_table.get_all()
        
        if not all_senders:
            self.status_bar.config(text="No no-reply senders to delete")
            self.logger.info("Delete all no-reply: table is empty")
            return
        
        # Calculate total count
        sender_count = len(all_senders)
        total_email_count = sum(s.get('total_count', 0) for s in all_senders)
        
        # Build confirmation message
        msg = f"Delete all emails from {sender_count} no-reply sender(s)?\n\n"
        msg += f"This will permanently delete approximately {total_email_count:,} email(s) from senders like:\n"
        msg += f"  • noreply@...\n"
        msg += f"  • donotreply@...\n"
        msg += f"  • no-reply@...\n\n"
        msg += "⚠️ This action cannot be undone!"
        
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Confirm Delete All No-Reply",
            msg,
            icon='warning'
        )
        
        if not result:
            return
        
        self.logger.info(f"Starting delete all for {sender_count} no-reply senders")
        
        # Disable button during operation
        self.delete_all_noreply_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="Starting deletion...")
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Deleting No-Reply Emails")
        
        # Create background task
        bg_task = BackgroundTask(self.root)
        
        def delete_task(progress_callback):
            """Delete emails in background thread using EmailDeletionService."""
            # Get account and connect
            account = self.db.get_primary_account()
            if not account:
                raise Exception("No account configured")
            
            client = self._create_email_client(account)
            if not client.connect():
                error_msg = client.get_error_message() or "Failed to connect to email server"
                raise Exception(error_msg)
            
            try:
                # Set email client in service factory
                self.service_factory.set_email_client(client)
                
                # Get deletion service from factory
                deletion_service = self.service_factory.create_deletion_service()
                
                # Set cancel callback to cancel the service
                progress.set_cancel_callback(deletion_service.cancel)
                
                # Run deletion using service
                results = deletion_service.delete_from_senders(
                    all_senders,
                    progress_callback=progress_callback
                )
                
                return results
            finally:
                # Always disconnect client
                client.disconnect()
        
        def on_progress(current, total, message):
            """Update progress dialog."""
            progress.update_progress(current, total, message)
        
        def on_complete(results, error=None):
            """Handle completion."""
            progress.destroy()
            self.delete_all_noreply_btn.config(state=tk.NORMAL)
            
            if error:
                self.status_bar.config(text="Delete all no-reply failed")
                messagebox.showerror("Error", f"Failed to delete emails: {error}")
                self.logger.error(f"Delete all no-reply failed: {error}")
            elif results:
                deleted_senders = results['deleted_senders']
                total_emails = results['total_emails_deleted']
                failed_senders = results['failed_senders']
                skipped_senders = results['skipped_senders']
                deleted_emails = results.get('deleted_sender_emails', [])
                
                self.logger.info(f"Delete all no-reply complete: {total_emails} emails from {deleted_senders} senders")
                
                # Remove deleted senders from both tables
                if deleted_emails:
                    self.sender_table.remove_senders(deleted_emails)
                    self.logger.debug(f"Removed {len(deleted_emails)} no-reply sender(s) from sender table")
                
                # Clear the no-reply table since emails are deleted
                self.noreply_table.clear()
                
                # Update statistics
                current_senders = []
                if hasattr(self.sender_table, 'sender_data'):
                    current_senders = list(self.sender_table.sender_data.values())
                self.update_statistics(current_senders)
                
                # Show status in status bar
                status_msg = f"Deleted {total_emails:,} emails from {deleted_senders} no-reply senders"
                if skipped_senders > 0:
                    status_msg += f" ({skipped_senders} had no emails)"
                if failed_senders > 0:
                    status_msg += f" ({failed_senders} failed)"
                self.status_bar.config(text=status_msg)
            else:
                self.status_bar.config(text="Delete all no-reply cancelled")
                self.logger.info("Delete all no-reply cancelled by user")
        
        # Start deletion
        bg_task.run(delete_task, on_progress, on_complete)
    
    def _add_account(self):
        """Show add account dialog."""
        self.logger.info("Add account clicked")
        self.status_bar.config(text="Opening account setup dialog...")
        
        # Create credential manager
        cred_manager = CredentialManager()
        
        # Open account dialog
        dialog = AccountDialog(self.root, self.db, cred_manager)
        self.root.wait_window(dialog)
        
        self.status_bar.config(text="Ready")
    
    def _open_settings(self):
        """Open settings dialog."""
        self.logger.info("Settings dialog opened")
        self.status_bar.config(text="Opening settings...")
        
        # Create credential manager
        cred_manager = CredentialManager()
        
        # Open settings dialog
        dialog = SettingsDialog(self.root, self.db, cred_manager)
        self.root.wait_window(dialog)

        self.status_bar.config(text="Ready")

    def _show_about(self):
        """Show about dialog with application information."""
        about_text = """Email Unsubscriber

A tool to help manage unwanted emails by identifying senders with high email volume and providing automated unsubscribe functionality.

Features:
• Scan inbox for unwanted email patterns
• Automatic unsubscribe from mailing lists
• Manual deletion of emails from failed unsubscribe attempts
• Whitelist protection for important senders
• Score-based prioritization of problematic senders

Version: 1.0.0
Author: Email Unsubscriber Team

This application is designed to be read-only and will not modify your emails without explicit user confirmation."""

        messagebox.showinfo("About Email Unsubscriber", about_text)

    def _show_app_password_help(self):
        """Show help for generating app passwords."""
        help_text = """App Password Setup

To use this application with Gmail or Outlook, you need to generate an "App Password" instead of using your regular password.

Gmail:
1. Enable 2-factor authentication on your Google account
2. Go to Google Account settings > Security > App passwords
3. Generate a new app password for "Mail"
4. Use this 16-character password in the application

Outlook/Hotmail:
1. Go to Outlook.com > Settings > View all Outlook settings
2. Navigate to Mail > Sync email > POP and IMAP
3. Under "IMAP", select "Yes" to enable IMAP access
4. Use your regular password (no app password needed for Outlook)

Note: App passwords are more secure than regular passwords for applications like this one."""

        messagebox.showinfo("App Password Setup", help_text)
    
    def scan_inbox(self):
        """Scan inbox for emails using EmailScanService."""
        self.logger.info("Scan inbox clicked")
        
        # Get account
        account = self.db.get_primary_account()
        if not account:
            messagebox.showerror(
                "Error", 
                "No account configured. Please add an account first using File > Add Account."
            )
            return
        
        # Disable scan button during scan
        self.scan_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="Starting scan...")
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Scanning Inbox")
        
        # Create background task
        bg_task = BackgroundTask(self.root)
        
        def scan_task(progress_callback):
            """Scan task to run in background using EmailScanService."""
            # Connect to email server (Gmail API or IMAP)
            self.logger.info(f"Connecting to email server for {account['email']}")
            client = self._create_email_client(account)
            if not client.connect():
                error_msg = client.get_error_message() or "Failed to connect to email server"
                raise Exception(error_msg)
            
            try:
                # Set email client in service factory
                self.service_factory.set_email_client(client)
                
                # Get scan service from factory
                scan_service = self.service_factory.create_scan_service()
                
                # Set cancel callback to cancel the service
                progress.set_cancel_callback(scan_service.cancel)
                
                # Run scan using service
                senders = scan_service.scan_inbox(progress_callback=progress_callback)
                
                return senders
            finally:
                # Always disconnect client
                client.disconnect()
        
        def on_progress(current, total, message):
            """Update progress dialog."""
            progress.update_progress(current, total, message)
        
        def on_complete(result, error=None):
            """Handle completion."""
            progress.destroy()
            self.scan_btn.config(state=tk.NORMAL)
            
            if error:
                self.status_bar.config(text="Scan failed")
                messagebox.showerror("Error", "Failed to scan inbox. Please check your internet connection and email account settings.")
                self.logger.error(f"Scan failed: {error}")
            elif result:
                self.sender_table.populate(result)
                self.update_statistics(result)
                
                # Filter and populate no-reply senders table
                noreply_senders = get_noreply_senders(result)
                self.noreply_table.populate(noreply_senders)
                
                self.status_bar.config(text=f"Scan complete: {len(result)} senders found ({len(noreply_senders)} no-reply)")
                self.logger.info(f"Scan complete: {len(result)} senders found, {len(noreply_senders)} no-reply senders")
            else:
                self.status_bar.config(text="Scan cancelled")
                self.logger.info("Scan cancelled by user")
        
        # Start scan
        bg_task.run(scan_task, on_progress, on_complete)
    
    def _on_sender_selection_changed(self, event=None):
        """Enable/disable unsubscribe and delete buttons based on selection."""
        selected = self.sender_table.get_selected()
        self.unsub_btn.config(state=tk.NORMAL if selected else tk.DISABLED)
        self.delete_btn.config(state=tk.NORMAL if selected else tk.DISABLED)
    
    def unsubscribe_selected(self):
        """Unsubscribe from selected senders using UnsubscribeService."""
        selected = self.sender_table.get_selected()
        if not selected:
            return
        
        # Confirmation dialog
        count = len(selected)
        result = messagebox.askyesno(
            "Confirm Unsubscribe",
            f"Unsubscribe from {count} sender(s)?\n\n"
            "This will attempt to unsubscribe using available methods:\n"
            "1. List-Unsubscribe header (if present)\n"
            "2. Unsubscribe links from email body\n\n"
            "Do you want to proceed?"
        )
        if not result:
            return
        
        self.logger.info(f"Starting unsubscribe for {count} senders")
        
        # Disable buttons during operation
        self.unsub_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="Starting unsubscribe...")
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Unsubscribing")
        
        # Create background task
        bg_task = BackgroundTask(self.root)
        
        def unsubscribe_task(progress_callback):
            """Unsubscribe task to run in background using UnsubscribeService."""
            # Get unsubscribe service from factory
            unsubscribe_service = self.service_factory.create_unsubscribe_service()
            
            # Set cancel callback to cancel the service
            progress.set_cancel_callback(unsubscribe_service.cancel)
            
            # Convert sender data format for service (map sample_links to unsubscribe_links)
            senders_for_service = []
            for sender_data in selected:
                service_format = sender_data.copy()
                # Service expects 'unsubscribe_links' but EmailGrouper provides 'sample_links'
                if 'sample_links' in sender_data and sender_data['sample_links']:
                    service_format['unsubscribe_links'] = sender_data['sample_links']
                senders_for_service.append(service_format)
            
            # Run unsubscribe using service
            service_results = unsubscribe_service.unsubscribe_from_senders(
                senders_for_service, 
                progress_callback=progress_callback
            )
            
            # Convert service result format to UI format and update sender table statuses
            results = {
                'success': service_results['success_count'],
                'failed': service_results['failed_count'],
                'skipped': service_results['skipped_count'],
                'details': service_results['details'],
                'successful_senders': []  # Build UI-specific format
            }
            
            # Update sender table statuses based on results
            for detail in service_results['details']:
                # Parse detail format: "sender@example.com: Result message"
                if ': ' in detail:
                    sender_email, message = detail.split(': ', 1)
                    sender_email = sender_email.strip()
                    
                    if 'Success' in message:
                        status = f'Unsubscribed ({message})'
                        self.sender_table.update_sender_status(sender_email, status)
                    elif 'Skipped' in message or 'No unsubscribe method' in message:
                        self.sender_table.update_sender_status(sender_email, 'Skipped (no unsubscribe link)')
                    elif 'Failed' in message or 'Error' in message:
                        short_msg = message[:30] + "..." if len(message) > 30 else message
                        self.sender_table.update_sender_status(sender_email, f'Failed: {short_msg}')
            
            # Build successful_senders list for deletion offer
            for sender_email in service_results['successful_senders']:
                # Find corresponding sender_data to get email_count
                for sender_data in selected:
                    if sender_data.get('sender') == sender_email:
                        results['successful_senders'].append({
                            'sender': sender_email,
                            'email_count': sender_data.get('total_count', 0)
                        })
                        break
            
            return results
        
        def on_progress(current, total, message):
            """Update progress dialog."""
            progress.update_progress(current, total, message)
        
        def on_complete(results, error=None):
            """Handle completion."""
            progress.destroy()
            self.unsub_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
            
            if error:
                self.status_bar.config(text="Unsubscribe failed")
                messagebox.showerror("Error", "Failed to unsubscribe from some senders. Please check your internet connection and try again.")
                self.logger.error(f"Unsubscribe operation failed: {error}")
            elif results:
                # Show summary
                success_count = results.get('success', 0)
                failed_count = results.get('failed', 0)
                skipped_count = results.get('skipped', 0)
                successful_senders = results.get('successful_senders', [])
                
                msg = f"Unsubscribe complete:\n\n"
                msg += f"  Successful: {success_count}\n"
                msg += f"  Failed: {failed_count}\n"
                if skipped_count > 0:
                    msg += f"  Skipped (no unsubscribe link): {skipped_count}\n"
                msg += "\n"
                
                if success_count > 0:
                    msg += "Successful unsubscribes will no longer send you emails."
                if skipped_count > 0:
                    msg += "\nSkipped senders can still be deleted using 'Delete Selected'."
                
                # Update statistics and show in status bar
                status_msg = f"Unsubscribe complete: {success_count} succeeded, {failed_count} failed"
                if skipped_count > 0:
                    status_msg += f", {skipped_count} skipped"
                self.status_bar.config(text=status_msg)
                self.logger.info(f"Unsubscribe complete: {success_count} succeeded, {failed_count} failed, {skipped_count} skipped")
                
                # Offer to delete emails from successfully unsubscribed senders
                if successful_senders:
                    self._offer_bulk_delete_after_unsubscribe(successful_senders)
            else:
                self.status_bar.config(text="Unsubscribe cancelled")
                self.logger.info("Unsubscribe cancelled by user")
        
        # Start unsubscribe
        bg_task.run(unsubscribe_task, on_progress, on_complete)
    
    def delete_selected(self):
        """Delete emails from selected senders using EmailDeletionService."""
        selected = self.sender_table.get_selected()
        if not selected:
            return
        
        # Calculate total count
        sender_count = len(selected)
        total_email_count = sum(s.get('total_count', 0) for s in selected)
        
        # Build confirmation message
        msg = f"Delete all emails from {sender_count} selected sender(s)?\n\n"
        msg += f"This will permanently delete approximately {total_email_count:,} email(s).\n\n"
        msg += "⚠️ This action cannot be undone!"
        
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Confirm Deletion",
            msg,
            icon='warning'
        )
        
        if not result:
            return
        
        self.logger.info(f"Starting deletion for {sender_count} selected senders")
        
        # Disable buttons during operation
        self.unsub_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="Starting deletion...")
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Deleting Emails")
        
        # Create background task
        bg_task = BackgroundTask(self.root)
        
        def delete_task(progress_callback):
            """Delete emails in background thread using EmailDeletionService."""
            # Get account and connect
            account = self.db.get_primary_account()
            if not account:
                raise Exception("No account configured")
            
            client = self._create_email_client(account)
            if not client.connect():
                error_msg = client.get_error_message() or "Failed to connect to email server"
                raise Exception(error_msg)
            
            try:
                # Set email client in service factory
                self.service_factory.set_email_client(client)
                
                # Get deletion service from factory
                deletion_service = self.service_factory.create_deletion_service()
                
                # Set cancel callback to cancel the service
                progress.set_cancel_callback(deletion_service.cancel)
                
                # Run deletion using service
                results = deletion_service.delete_from_senders(
                    selected,
                    progress_callback=progress_callback
                )
                
                return results
            finally:
                # Always disconnect client
                client.disconnect()
        
        def on_progress(current, total, message):
            """Update progress dialog."""
            progress.update_progress(current, total, message)
        
        def on_complete(results, error=None):
            """Handle completion."""
            progress.destroy()
            self.unsub_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
            
            if error:
                self.status_bar.config(text="Deletion failed")
                messagebox.showerror("Error", f"Failed to delete emails: {error}")
                self.logger.error(f"Deletion operation failed: {error}")
            elif results:
                deleted_senders = results['deleted_senders']
                total_emails = results['total_emails_deleted']
                failed_senders = results['failed_senders']
                deleted_emails = results.get('deleted_sender_emails', [])
                
                self.logger.info(f"Deletion complete: {total_emails} emails from {deleted_senders} senders")
                
                # Remove deleted senders from the table
                if deleted_emails:
                    self.sender_table.remove_senders(deleted_emails)
                    self.logger.debug(f"Removed {len(deleted_emails)} sender(s) from UI table")
                
                # Update statistics
                current_senders = []
                if hasattr(self.sender_table, 'sender_data'):
                    current_senders = list(self.sender_table.sender_data.values())
                self.update_statistics(current_senders)
                
                # Update status bar
                status_msg = f"Deleted {total_emails:,} emails from {deleted_senders} senders"
                if failed_senders > 0:
                    status_msg += f" ({failed_senders} failed)"
                self.status_bar.config(text=status_msg)
            else:
                self.status_bar.config(text="Deletion cancelled")
                self.logger.info("Deletion cancelled by user")
        
        # Start deletion
        bg_task.run(delete_task, on_progress, on_complete)
    
    def _offer_bulk_delete_after_unsubscribe(self, successful_senders):
        """
        Offer to delete emails from successfully unsubscribed senders.
        
        Args:
            successful_senders: List of dicts with 'sender' and 'email_count' keys
        """
        # Calculate total email count
        total_emails = sum(s['email_count'] for s in successful_senders)
        sender_count = len(successful_senders)
        
        # Build confirmation message
        msg = f"You successfully unsubscribed from {sender_count} sender(s).\n\n"
        msg += f"Would you like to delete all {total_emails:,} emails from "
        msg += f"{'this sender' if sender_count == 1 else 'these senders'}?\n\n"
        msg += "This will permanently delete the emails from your inbox.\n"
        msg += "This action cannot be undone."
        
        # Show confirmation dialog with three options
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Emails?")
        dialog.geometry("450x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Message label
        msg_label = ttk.Label(dialog, text=msg, wraplength=400, justify=tk.LEFT)
        msg_label.pack(padx=20, pady=20)
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        user_choice = {'delete': False}
        
        def delete_emails():
            user_choice['delete'] = True
            dialog.destroy()
        
        def keep_emails():
            user_choice['delete'] = False
            dialog.destroy()
        
        # Buttons
        ttk.Button(button_frame, text="Delete Emails", 
                  command=delete_emails).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Keep Emails", 
                  command=keep_emails).pack(side=tk.LEFT, padx=5)
        
        # Wait for user choice
        self.root.wait_window(dialog)
        
        # If user chose to delete, start deletion process
        if user_choice['delete']:
            self._delete_emails_from_senders(successful_senders)
    
    def _delete_emails_from_senders(self, senders_to_delete):
        """
        Delete all emails from the specified senders.
        
        Args:
            senders_to_delete: List of dicts with 'sender' and 'email_count' keys
        """
        count = len(senders_to_delete)
        self.logger.info(f"Starting bulk deletion for {count} senders")
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Deleting Emails")
        
        # Create background task
        bg_task = BackgroundTask(self.root)
        progress.set_cancel_callback(bg_task.cancel)
        
        def delete_task(progress_callback):
            """Delete emails in background thread."""
            # Get account and connect
            account = self.db.get_primary_account()
            if not account:
                raise Exception("No account configured")
            
            client = self._create_email_client(account)
            if not client.connect():
                error_msg = client.get_error_message() or "Failed to connect to email server"
                raise Exception(error_msg)
            
            results = {'deleted_count': 0, 'failed_count': 0, 'total_emails': 0}
            
            try:
                for i, sender_info in enumerate(senders_to_delete):
                    if bg_task.is_cancelled:
                        break
                    
                    sender = sender_info['sender']
                    progress_callback(i, count, f"Deleting emails from {sender}")
                    
                    # Delete emails from this sender
                    deleted, message = client.delete_emails_from_sender(sender, self.db)
                    
                    if deleted > 0:
                        results['deleted_count'] += 1
                        results['total_emails'] += deleted
                        self.logger.info(f"Deleted {deleted} emails from {sender}")
                    else:
                        results['failed_count'] += 1
                        self.logger.warning(f"Failed to delete emails from {sender}: {message}")
                
            finally:
                client.disconnect()
            
            return results
        
        def on_progress(current, total, message):
            """Update progress dialog."""
            progress.update_progress(current, total, message)
        
        def on_complete(results, error=None):
            """Handle completion."""
            progress.destroy()
            
            if error:
                messagebox.showerror("Error", "Failed to delete emails. Please check your internet connection and email account permissions.")
                self.logger.error(f"Bulk deletion failed: {error}")
            elif results:
                deleted_count = results['deleted_count']
                total_emails = results['total_emails']
                failed_count = results['failed_count']
                
                self.logger.info(f"Bulk deletion complete: {total_emails} emails from {deleted_count} senders")
                
                # Update status bar
                status_msg = f"Deleted {total_emails:,} emails from {deleted_count} senders"
                if failed_count > 0:
                    status_msg += f" ({failed_count} failed)"
                self.status_bar.config(text=status_msg)
            else:
                self.status_bar.config(text="Deletion cancelled")
        
        # Start deletion
        bg_task.run(delete_task, on_progress, on_complete)
    
    def _refresh_whitelist(self):
        """Refresh the whitelist from database."""
        try:
            entries = self.db.get_whitelist()
            self.whitelist_table.populate(entries)
            self.logger.info(f"Whitelist refreshed: {len(entries)} entries")
        except Exception as e:
            self.logger.error(f"Error refreshing whitelist: {e}")
            messagebox.showerror("Error", "Failed to refresh whitelist. Please try again.")
    
    def _on_whitelist_selection_changed(self, event=None):
        """Handle whitelist selection change to enable/disable remove button."""
        selected = self.whitelist_table.get_selected()
        if selected:
            self.remove_whitelist_btn.config(state=tk.NORMAL)
        else:
            self.remove_whitelist_btn.config(state=tk.DISABLED)
    
    def _quick_add_to_whitelist(self, sender_email):
        """Quick add sender to whitelist from context menu.
        
        Args:
            sender_email: Email address to add to whitelist
        """
        # Confirm action
        result = messagebox.askyesno(
            "Add to Whitelist",
            f"Add {sender_email} to whitelist?\n\n"
            "This sender will be protected from unsubscribe/delete operations."
        )
        
        if not result:
            return
        
        # Add to database
        try:
            success = self.db.add_to_whitelist(sender_email, is_domain=False, 
                                              notes="Added from sender table")
            if success:
                self.logger.info(f"Quick-added {sender_email} to whitelist")
                self.status_bar.config(text=f"Added {sender_email} to whitelist")
            else:
                self.logger.info(f"{sender_email} already in whitelist")
                self.status_bar.config(text=f"{sender_email} is already whitelisted")
        except Exception as e:
            self.logger.error(f"Error adding to whitelist: {e}")
            messagebox.showerror("Error", "Failed to add to whitelist. Please try again.")
    
    def _quick_add_to_must_delete(self, sender_email):
        """Quick add sender to must delete list from context menu.
        
        Args:
            sender_email: Email address to add to must delete list
        """
        # Confirm action
        result = messagebox.askyesno(
            "Add to Must Delete",
            f"Add {sender_email} to must delete list?\n\n"
            "This sender will appear in the Must Delete tab for bulk deletion."
        )
        
        if not result:
            return
        
        # Add to database
        try:
            self.db.add_to_must_delete(sender_email, reason="Manually added from sender table")
            self.logger.info(f"Quick-added {sender_email} to must delete list")
            
            # Update statistics
            current_senders = []
            if hasattr(self.sender_table, 'sender_data'):
                current_senders = list(self.sender_table.sender_data.values())
            self.update_statistics(current_senders)
            
            self.status_bar.config(text=f"Added {sender_email} to must delete list")
        except Exception as e:
            self.logger.error(f"Error adding to must delete list: {e}")
            messagebox.showerror("Error", "Failed to add to must delete list. Please try again.")
    
    def add_whitelist_entry(self):
        """Show dialog to add new whitelist entry."""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add to Whitelist")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Entry type selection
        ttk.Label(dialog, text="Entry Type:", font=('', 10, 'bold')).pack(pady=(20, 5))
        
        entry_type = tk.StringVar(value="email")
        ttk.Radiobutton(dialog, text="Email Address", variable=entry_type, 
                       value="email").pack(pady=2)
        ttk.Radiobutton(dialog, text="Domain (e.g., @company.com)", variable=entry_type, 
                       value="domain").pack(pady=2)
        
        # Entry field
        ttk.Label(dialog, text="Entry:", font=('', 10, 'bold')).pack(pady=(15, 5))
        entry_field = ttk.Entry(dialog, width=40)
        entry_field.pack(pady=5)
        
        # Notes field
        ttk.Label(dialog, text="Notes (optional):").pack(pady=(10, 5))
        notes_field = ttk.Entry(dialog, width=40)
        notes_field.pack(pady=5)
        
        # Status label
        status_label = ttk.Label(dialog, text="", foreground="red")
        status_label.pack(pady=10)
        
        def save_entry():
            """Save the whitelist entry."""
            entry = entry_field.get().strip()
            is_domain = entry_type.get() == "domain"
            notes = notes_field.get().strip()
            
            # Validation
            if not entry:
                status_label.config(text="Please enter an email or domain")
                return
            
            # Basic validation
            if is_domain and not entry.startswith('@'):
                status_label.config(text="Domain must start with @")
                return
            
            if not is_domain and '@' not in entry:
                status_label.config(text="Invalid email address")
                return
            
            # Add to database
            try:
                success = self.db.add_to_whitelist(entry, is_domain=is_domain, notes=notes)
                if success:
                    self._refresh_whitelist()
                    self.status_bar.config(text=f"Added {entry} to whitelist")
                    self.logger.info(f"Added {entry} to whitelist")
                    dialog.destroy()
                else:
                    status_label.config(text="Entry already exists in whitelist")
            except Exception as e:
                self.logger.error(f"Error adding to whitelist: {e}")
                status_label.config(text=f"Error: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Add", command=save_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def remove_whitelist_entry(self):
        """Remove selected whitelist entries."""
        selected = self.whitelist_table.get_selected()
        
        if not selected:
            return
        
        # Confirm removal
        count = len(selected)
        result = messagebox.askyesno(
            "Confirm Remove",
            f"Remove {count} {'entry' if count == 1 else 'entries'} from whitelist?\n\n"
            "These senders will no longer be protected."
        )
        
        if not result:
            return
        
        # Remove from database
        removed_count = 0
        for entry_dict in selected:
            entry = entry_dict.get('entry')
            try:
                if self.db.remove_from_whitelist(entry):
                    removed_count += 1
                    self.logger.info(f"Removed {entry} from whitelist")
            except Exception as e:
                self.logger.error(f"Error removing {entry} from whitelist: {e}")
        
        # Refresh display
        self._refresh_whitelist()
        
        # Show result in status bar
        if removed_count > 0:
            self.status_bar.config(text=f"Removed {removed_count} {'entry' if removed_count == 1 else 'entries'} from whitelist")
        else:
            self.status_bar.config(text="No entries were removed")
            messagebox.showwarning("Failed", "No entries were removed")

