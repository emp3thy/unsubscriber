"""
Progress dialog for Email Unsubscriber.

This module provides a modal dialog for showing progress of long-running
operations with cancellation support.
"""
import tkinter as tk
from tkinter import ttk
import logging


class ProgressDialog(tk.Toplevel):
    """Dialog showing progress of long-running operations."""
    
    def __init__(self, parent, title="Processing"):
        """
        Initialize the progress dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("450x180")
        self.resizable(False, False)
        self.logger = logging.getLogger(__name__)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self._center_on_parent(parent)
        
        # Create widgets
        self._create_widgets()
        
        self.cancel_callback = None
        self.cancelled = False
        
        self.logger.info(f"Progress dialog opened: {title}")
    
    def _center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.update_idletasks()
        
        # Get parent position and size
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        
        self.geometry(f'+{x}+{y}')
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame, 
            length=400, 
            mode='determinate',
            maximum=100
        )
        self.progress.pack(pady=(10, 15))
        
        # Progress percentage label
        self.progress_label = ttk.Label(
            main_frame, 
            text="0%", 
            font=('', 10, 'bold')
        )
        self.progress_label.pack()
        
        # Status message label
        self.status_label = ttk.Label(
            main_frame, 
            text="Initializing...",
            font=('', 9),
            wraplength=380
        )
        self.status_label.pack(pady=10)
        
        # Cancel button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        self.cancel_btn = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self._on_cancel
        )
        self.cancel_btn.pack()
    
    def update_progress(self, current: int, total: int, message: str = ""):
        """
        Update progress bar and message.
        
        Args:
            current: Current progress value
            total: Total expected value  
            message: Optional status message
        """
        if total > 0:
            percent = (current / total) * 100
            self.progress['value'] = percent
            self.progress_label.config(text=f"{percent:.1f}%")
        else:
            # Indeterminate mode
            self.progress['value'] = 0
            self.progress_label.config(text="Processing...")
        
        # Update status message
        if message:
            self.status_label.config(text=message)
        else:
            self.status_label.config(text=f"Processing {current:,} of {total:,}")
        
        # Force update
        self.update_idletasks()
    
    def set_cancel_callback(self, callback):
        """
        Set function to call when cancelled.
        
        Args:
            callback: Function to call on cancel
        """
        self.cancel_callback = callback
    
    def _on_cancel(self):
        """Handle cancel button click."""
        if self.cancel_callback and not self.cancelled:
            self.cancelled = True
            self.cancel_callback()
            self.status_label.config(text="Cancelling... Please wait.")
            self.cancel_btn.config(state=tk.DISABLED)
            self.logger.info("Progress dialog cancelled by user")

