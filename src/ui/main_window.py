"""
Main application window for Email Unsubscriber.

This module contains the MainWindow class which creates and manages
the primary user interface including menu bar, content area, and status bar.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from src.ui.settings_dialog import AccountDialog, SettingsDialog
from src.ui.sender_table import SenderTable
from src.ui.must_delete_table import MustDeleteTable
from src.ui.whitelist_table import WhitelistTable
from src.ui.progress_dialog import ProgressDialog
from src.utils.threading_utils import BackgroundTask
from src.email_client.credentials import CredentialManager
from src.email_client.imap_client import IMAPClient
from src.email_client.email_parser import EmailParser
from src.scoring.scorer import EmailScorer
from src.scoring.email_grouper import EmailGrouper
from src.unsubscribe.strategy_chain import StrategyChain
from src.unsubscribe.list_unsubscribe import ListUnsubscribeStrategy
from src.unsubscribe.http_strategy import HTTPStrategy


class MainWindow:
    """Main application window."""
    
    def __init__(self, root, db_manager):
        """
        Initialize the main application window.
        
        Args:
            root: Tkinter root window
            db_manager: DBManager instance for database operations
        """
        self.root = root
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
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
        """Delete emails from selected must-delete senders."""
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
        progress.set_cancel_callback(bg_task.cancel)
        
        def delete_task(progress_callback):
            """Delete emails in background thread."""
            # Get account and connect
            account = self.db.get_primary_account()
            if not account:
                raise Exception("No account configured")
            
            cred_manager = CredentialManager()
            password = cred_manager.decrypt_password(account['encrypted_password'])
            
            client = IMAPClient(account['email'], password)
            if not client.connect():
                error_msg = client.get_error_message() or "Failed to connect to email server"
                raise Exception(error_msg)
            
            results = {
                'deleted_senders': 0,
                'failed_senders': 0,
                'total_emails_deleted': 0,
                'removed_from_list': []
            }
            
            try:
                for i, sender_info in enumerate(selected):
                    if bg_task.is_cancelled:
                        break
                    
                    sender = sender_info['email']
                    progress_callback(i, sender_count, f"Deleting emails from {sender}")
                    
                    # Delete emails from this sender
                    deleted, message = client.delete_emails_from_sender(sender, self.db)
                    
                    if deleted > 0:
                        results['deleted_senders'] += 1
                        results['total_emails_deleted'] += deleted
                        results['removed_from_list'].append(sender)
                        self.logger.info(f"Deleted {deleted} emails from {sender}")
                        
                        # Remove from must-delete list in database
                        self.db.remove_from_must_delete(sender)
                    else:
                        results['failed_senders'] += 1
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
            self.delete_selected_btn.config(state=tk.NORMAL)
            
            if error:
                self.status_bar.config(text="Deletion failed")
                messagebox.showerror("Error", "Failed to delete some emails. Please check your internet connection and try again.")
                self.logger.error(f"Must-delete deletion failed: {error}")
            elif results:
                deleted_senders = results['deleted_senders']
                total_emails = results['total_emails_deleted']
                failed_senders = results['failed_senders']
                
                # Show summary
                msg = f"Deletion complete:\n\n"
                msg += f"  Senders processed: {deleted_senders}\n"
                msg += f"  Total emails deleted: {total_emails:,}\n"
                if failed_senders > 0:
                    msg += f"  Failed: {failed_senders}\n"
                
                messagebox.showinfo("Deletion Complete", msg)
                self.logger.info(f"Must-delete deletion complete: {total_emails} emails from {deleted_senders} senders")
                
                # Refresh the must-delete list
                self._refresh_must_delete_list()
                
                # Update statistics
                current_senders = self.sender_table.get_all() if hasattr(self.sender_table, 'get_all') else []
                self.update_statistics(current_senders)
                
                # Update status bar
                self.status_bar.config(
                    text=f"Deleted {total_emails:,} emails from {deleted_senders} senders"
                )
            else:
                self.status_bar.config(text="Deletion cancelled")
                self.logger.info("Must-delete deletion cancelled by user")
        
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
        """Scan inbox for emails."""
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
        progress.set_cancel_callback(bg_task.cancel)
        
        def scan_task(progress_callback):
            """Scan task to run in background."""
            # Decrypt password
            cred = CredentialManager()
            password = cred.decrypt_password(account['encrypted_password'])
            
            # Connect to IMAP
            self.logger.info(f"Connecting to IMAP for {account['email']}")
            client = IMAPClient(account['email'], password)
            if not client.connect():
                error_msg = client.get_error_message() or "Failed to connect to email server"
                raise Exception(error_msg)
            
            # Fetch email IDs
            progress_callback(0, 100, "Fetching email list...")
            email_ids = client.fetch_email_ids()
            total = len(email_ids)
            self.logger.info(f"Found {total} emails to process")
            
            if total == 0:
                client.disconnect()
                return []
            
            # Parse emails
            parser = EmailParser()
            emails = []
            
            for i, email_id in enumerate(email_ids):
                if bg_task.is_cancelled:
                    self.logger.info("Scan cancelled by user")
                    break
                
                # Fetch and parse
                try:
                    headers = client.fetch_headers([email_id])
                    if headers:
                        email_data = parser.parse_email(headers[0])
                        emails.append(email_data)
                except Exception as e:
                    self.logger.warning(f"Error parsing email {email_id}: {str(e)}")
                    continue
                
                # Update progress every 50 emails
                if i % 50 == 0 or i == total - 1:
                    progress_callback(
                        i + 1, 
                        total, 
                        f"Processing email {i+1:,} of {total:,}"
                    )
            
            client.disconnect()
            
            # Score and group
            if not bg_task.is_cancelled and emails:
                progress_callback(total, total, "Analyzing senders...")
                scorer = EmailScorer(self.db)
                grouper = EmailGrouper(scorer)
                senders = grouper.group_by_sender(emails)
                self.logger.info(f"Grouped into {len(senders)} unique senders")
                return senders
            
            return []
        
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
                self.status_bar.config(text=f"Scan complete: {len(result)} senders found")
                self.logger.info(f"Scan complete: {len(result)} senders found")
            else:
                self.status_bar.config(text="Scan cancelled")
                self.logger.info("Scan cancelled by user")
        
        # Start scan
        bg_task.run(scan_task, on_progress, on_complete)
    
    def _on_sender_selection_changed(self, event=None):
        """Enable/disable unsubscribe button based on selection."""
        selected = self.sender_table.get_selected()
        self.unsub_btn.config(state=tk.NORMAL if selected else tk.DISABLED)
    
    def unsubscribe_selected(self):
        """Unsubscribe from selected senders."""
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
        
        # Disable button during operation
        self.unsub_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="Starting unsubscribe...")
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Unsubscribing")
        
        # Create background task
        bg_task = BackgroundTask(self.root)
        progress.set_cancel_callback(bg_task.cancel)
        
        def unsubscribe_task(progress_callback):
            """Unsubscribe task to run in background."""
            # Create strategy chain
            chain = StrategyChain(self.db)
            chain.add_strategy(ListUnsubscribeStrategy())
            chain.add_strategy(HTTPStrategy())
            
            results = {
                'success': 0, 
                'failed': 0, 
                'details': [],
                'successful_senders': []  # Track successful senders for deletion option
            }
            
            for i, sender_data in enumerate(selected):
                if bg_task.is_cancelled:
                    self.logger.info("Unsubscribe cancelled by user")
                    break
                
                sender = sender_data.get('sender', 'unknown')
                progress_callback(i, count, f"Processing {sender}")
                
                try:
                    # Execute unsubscribe
                    success, message, strategy = chain.execute(sender_data)
                    
                    if success:
                        results['success'] += 1
                        results['successful_senders'].append({
                            'sender': sender,
                            'email_count': sender_data.get('total_count', 0)
                        })
                        sender_data['status'] = f'Unsubscribed ({strategy})'
                        self.sender_table.update_sender_status(sender, f'Unsubscribed ({strategy})')
                        results['details'].append(f"✓ {sender}: {message}")
                        self.logger.info(f"Unsubscribe succeeded for {sender}: {strategy}")
                    else:
                        results['failed'] += 1
                        short_msg = message[:30] + "..." if len(message) > 30 else message
                        sender_data['status'] = f'Failed: {short_msg}'
                        self.sender_table.update_sender_status(sender, f'Failed: {short_msg}')
                        results['details'].append(f"✗ {sender}: {message}")
                        self.logger.warning(f"Unsubscribe failed for {sender}: {message}")
                
                except Exception as e:
                    results['failed'] += 1
                    sender_data['status'] = 'Unsubscribe failed'
                    self.sender_table.update_sender_status(sender, 'Unsubscribe failed')
                    results['details'].append(f"✗ {sender}: Unsubscribe failed")
                    self.logger.error(f"Unsubscribe error for {sender}: {e}")
            
            return results
        
        def on_progress(current, total, message):
            """Update progress dialog."""
            progress.update_progress(current, total, message)
        
        def on_complete(results, error=None):
            """Handle completion."""
            progress.destroy()
            self.unsub_btn.config(state=tk.NORMAL)
            
            if error:
                self.status_bar.config(text="Unsubscribe failed")
                messagebox.showerror("Error", "Failed to unsubscribe from some senders. Please check your internet connection and try again.")
                self.logger.error(f"Unsubscribe operation failed: {error}")
            elif results:
                # Show summary
                success_count = results.get('success', 0)
                failed_count = results.get('failed', 0)
                successful_senders = results.get('successful_senders', [])
                
                msg = f"Unsubscribe complete:\n\n"
                msg += f"  Successful: {success_count}\n"
                msg += f"  Failed: {failed_count}\n\n"
                
                if success_count > 0:
                    msg += "Successful unsubscribes will no longer send you emails."
                
                messagebox.showinfo("Unsubscribe Complete", msg)
                
                # Update statistics
                self.status_bar.config(
                    text=f"Unsubscribe complete: {success_count} succeeded, {failed_count} failed"
                )
                self.logger.info(f"Unsubscribe complete: {success_count} succeeded, {failed_count} failed")
                
                # Offer to delete emails from successfully unsubscribed senders
                if successful_senders:
                    self._offer_bulk_delete_after_unsubscribe(successful_senders)
            else:
                self.status_bar.config(text="Unsubscribe cancelled")
                self.logger.info("Unsubscribe cancelled by user")
        
        # Start unsubscribe
        bg_task.run(unsubscribe_task, on_progress, on_complete)
    
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
            
            cred_manager = CredentialManager()
            password = cred_manager.decrypt_password(account['encrypted_password'])
            
            client = IMAPClient(account['email'], password)
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
                
                msg = f"Deletion complete:\n\n"
                msg += f"  Senders processed: {deleted_count}\n"
                msg += f"  Total emails deleted: {total_emails:,}\n"
                if failed_count > 0:
                    msg += f"  Failed: {failed_count}\n"
                
                messagebox.showinfo("Deletion Complete", msg)
                self.logger.info(f"Bulk deletion complete: {total_emails} emails from {deleted_count} senders")
                
                # Update status bar
                self.status_bar.config(text=f"Deleted {total_emails:,} emails from {deleted_count} senders")
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
                messagebox.showinfo("Success", f"Added {sender_email} to whitelist")
                self.logger.info(f"Quick-added {sender_email} to whitelist")
                
                # Refresh sender table to show new whitelisted status
                # (In a real implementation, we'd need to rescan or mark the sender)
                self.status_bar.config(text=f"Added {sender_email} to whitelist")
            else:
                messagebox.showinfo("Already Whitelisted", 
                                  f"{sender_email} is already in the whitelist")
        except Exception as e:
            self.logger.error(f"Error adding to whitelist: {e}")
            messagebox.showerror("Error", "Failed to add to whitelist. Please try again.")
    
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
                    messagebox.showinfo("Success", f"Added {entry} to whitelist")
                    self._refresh_whitelist()
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
        
        # Show result
        if removed_count > 0:
            messagebox.showinfo("Success", f"Removed {removed_count} {'entry' if removed_count == 1 else 'entries'} from whitelist")
        else:
            messagebox.showwarning("Failed", "No entries were removed")

