"""
No-Reply Table Widget for Email Unsubscriber.

This module contains the NoReplyTable widget that displays senders
whose email addresses contain no-reply-type patterns (e.g., noreply@, donotreply@).
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict
import logging
from src.ui.filterable_treeview import FilterableTreeview


class NoReplyTable(FilterableTreeview):
    """Table widget for displaying no-reply type senders."""
    
    def __init__(self, parent):
        """
        Initialize the no-reply table.
        
        Args:
            parent: Parent tkinter widget
        """
        # Initialize FilterableTreeview
        FilterableTreeview.__init__(self)
        
        self.parent = parent
        self.sender_data = {}  # Store full data by item ID
        self.logger = logging.getLogger(__name__)
        
        # Create frame with scrollbar
        self.frame = ttk.Frame(parent)
        
        # Define columns
        self.columns_def = {
            'sender': ('Sender', 400),
            'count': ('Email Count', 100),
            'unread': ('Unread', 100),
            'score': ('Score', 80)
        }
        
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL)
        
        # Create Treeview
        self.tree = ttk.Treeview(
            self.frame,
            columns=('sender', 'count', 'unread', 'score'),
            show='headings',
            selectmode='extended',
            yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.tree.yview)
        
        # Setup columns
        self._setup_columns()
        
        # Configure color tags
        self.tree.tag_configure('noreply', background='#FFE4E1')  # Light red
        
        # Create filter row
        self.create_filter_row(self.frame, self.tree, self.columns_def)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.logger.debug("NoReplyTable initialized")
    
    def _setup_columns(self):
        """Define column headers and properties."""
        columns = {
            'sender': ('Sender', 400),
            'count': ('Email Count', 100),
            'unread': ('Unread', 100),
            'score': ('Score', 80)
        }
        
        for col, (heading, width) in columns.items():
            self.tree.heading(col, text=heading,
                            command=lambda c=col: self._sort_by_column(c, False))
            self.tree.column(col, width=width)
    
    def populate(self, senders: List[Dict]):
        """
        Populate table with no-reply sender data.
        
        Args:
            senders: List of sender dictionaries with keys: sender, total_count, unread_count, total_score
        """
        self.clear()
        
        if not senders:
            self.logger.debug("No no-reply senders to populate")
            return
        
        for sender in senders:
            # Format values
            email = sender.get('sender', 'Unknown')
            count = sender.get('total_count', 0)
            unread = sender.get('unread_count', 0)
            score = sender.get('total_score', 0)
            
            values = (
                email,
                f"{count:,}",
                f"{unread:,}",
                f"{score:.1f}" if score >= 0 else "N/A"
            )
            
            # Insert item with colored background
            item_id = self.tree.insert('', tk.END, values=values, tags=('noreply',))
            self.sender_data[item_id] = sender
        
        # Store all items for filtering
        self.store_all_items()
        
        self.logger.info(f"Populated no-reply table with {len(senders)} senders")
    
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
    
    def _sort_by_column(self, col, reverse):
        """
        Sort table by column.
        
        Args:
            col: Column name to sort by
            reverse: Whether to sort in reverse order
        """
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Try numeric sort for count columns
        try:
            items.sort(key=lambda t: float(t[0].replace(',', '')), reverse=reverse)
        except (ValueError, AttributeError):
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
    
    def _data_to_values(self, data: Dict) -> tuple:
        """Convert sender data to display values tuple."""
        email = data.get('sender', 'Unknown')
        count = data.get('total_count', 0)
        unread = data.get('unread_count', 0)
        score = data.get('total_score', 0)
        
        return (
            email,
            f"{count:,}",
            f"{unread:,}",
            f"{score:.1f}" if score >= 0 else "N/A"
        )
    
    def _get_item_tags(self, data: Dict) -> tuple:
        """Get tags for an item."""
        return ('noreply',)

