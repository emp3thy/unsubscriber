"""
Must Delete Table Widget for Email Unsubscriber.

This module contains the MustDeleteTable widget that displays senders
whose unsubscribe attempts failed and need manual email deletion.
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict


class MustDeleteTable:
    """Table widget for displaying must-delete senders."""
    
    def __init__(self, parent):
        """
        Initialize the must-delete table.
        
        Args:
            parent: Parent tkinter widget
        """
        self.parent = parent
        self.sender_data = {}  # Store full data by item ID
        
        # Create frame with scrollbar
        self.frame = ttk.Frame(parent)
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL)
        
        # Create Treeview
        self.tree = ttk.Treeview(
            self.frame,
            columns=('sender', 'reason', 'date', 'status'),
            show='headings',
            selectmode='extended',
            yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.tree.yview)
        
        # Setup columns
        self._setup_columns()
        
        # Configure color tags
        self.tree.tag_configure('failed', background='#FFE4E1')  # Light red
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _setup_columns(self):
        """Define column headers and properties."""
        columns = {
            'sender': ('Sender', 350),
            'reason': ('Failure Reason', 300),
            'date': ('Date Added', 150),
            'status': ('Status', 120)
        }
        
        for col, (heading, width) in columns.items():
            self.tree.heading(col, text=heading,
                            command=lambda c=col: self._sort_by_column(c, False))
            self.tree.column(col, width=width)
    
    def populate(self, senders: List[Dict]):
        """
        Populate table with must-delete sender data.
        
        Args:
            senders: List of sender dictionaries with keys: email, reason, added_date
        """
        self.clear()
        
        if not senders:
            # Show "No must-delete senders" message
            return
        
        for sender in senders:
            # Format values
            email = sender.get('email', 'Unknown')
            reason = sender.get('reason', 'Unknown')
            date = sender.get('added_date', '')
            
            # Shorten date to just date part (not time)
            if ' ' in date:
                date = date.split(' ')[0]
            
            values = (
                email,
                reason[:50] + '...' if len(reason) > 50 else reason,  # Truncate long reasons
                date,
                'Pending Deletion'
            )
            
            # Insert item with red background
            item_id = self.tree.insert('', tk.END, values=values, tags=('failed',))
            self.sender_data[item_id] = sender
    
    def get_selected(self) -> List[Dict]:
        """
        Get selected sender data.
        
        Returns:
            List of selected sender dictionaries
        """
        selected_ids = self.tree.selection()
        return [self.sender_data[item_id] for item_id in selected_ids
                if item_id in self.sender_data]
    
    def get_all(self) -> List[Dict]:
        """
        Get all sender data in the table.
        
        Returns:
            List of all sender dictionaries
        """
        return list(self.sender_data.values())
    
    def clear(self):
        """Clear all items from the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.sender_data.clear()
    
    def remove_selected(self):
        """Remove selected items from the table."""
        selected_ids = self.tree.selection()
        for item_id in selected_ids:
            self.tree.delete(item_id)
            if item_id in self.sender_data:
                del self.sender_data[item_id]
    
    def update_status(self, email: str, status: str):
        """
        Update the status column for a specific sender.
        
        Args:
            email: Email address to update
            status: New status text
        """
        for item_id, data in self.sender_data.items():
            if data.get('email') == email:
                values = list(self.tree.item(item_id, 'values'))
                values[3] = status  # Update status column
                self.tree.item(item_id, values=values)
                break
    
    def _sort_by_column(self, col, reverse):
        """
        Sort table by column.
        
        Args:
            col: Column name to sort by
            reverse: Whether to sort in reverse order
        """
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Sort items
        items.sort(reverse=reverse)
        
        # Rearrange items in tree
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Toggle sort direction for next click
        self.tree.heading(col, command=lambda: self._sort_by_column(col, not reverse))
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame."""
        self.frame.grid(**kwargs)

