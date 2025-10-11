"""
Whitelist Table Widget for Email Unsubscriber.

This module contains the WhitelistTable widget that displays protected
email addresses and domains that should never be marked as unwanted.
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict
from src.ui.filterable_treeview import FilterableTreeview


class WhitelistTable(FilterableTreeview):
    """Table widget for displaying whitelisted entries."""
    
    def __init__(self, parent):
        """
        Initialize the whitelist table.
        
        Args:
            parent: Parent tkinter widget
        """
        # Initialize FilterableTreeview
        FilterableTreeview.__init__(self)
        
        self.parent = parent
        self.sender_data = {}  # Store full data by item ID (using sender_data for consistency)
        self.entry_data = self.sender_data  # Alias for backward compatibility
        
        # Create frame with scrollbar
        self.frame = ttk.Frame(parent)
        
        # Define columns
        self.columns_def = {
            'entry': ('Entry', 300),
            'type': ('Type', 100),
            'notes': ('Notes', 250),
            'date': ('Date Added', 150)
        }
        
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL)
        
        # Create Treeview
        self.tree = ttk.Treeview(
            self.frame,
            columns=('entry', 'type', 'notes', 'date'),
            show='headings',
            selectmode='extended',
            yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.tree.yview)
        
        # Setup columns
        self._setup_columns()
        
        # Configure color tags
        self.tree.tag_configure('protected', background='#E0FFE0')  # Light green
        
        # Create filter row
        self.create_filter_row(self.frame, self.tree, self.columns_def)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _setup_columns(self):
        """Define column headers and properties."""
        columns = {
            'entry': ('Entry', 300),
            'type': ('Type', 100),
            'notes': ('Notes', 250),
            'date': ('Date Added', 150)
        }
        
        for col, (heading, width) in columns.items():
            self.tree.heading(col, text=heading,
                            command=lambda c=col: self._sort_by_column(c, False))
            self.tree.column(col, width=width)
    
    def populate(self, entries: List[Dict]):
        """
        Populate table with whitelist entry data.
        
        Args:
            entries: List of entry dictionaries with keys: entry, type, notes, added_date
        """
        self.clear()
        
        if not entries:
            # Show empty state
            return
        
        for entry_dict in entries:
            # Format values
            entry = entry_dict.get('entry', 'Unknown')
            entry_type = entry_dict.get('type', 'email').capitalize()
            notes = entry_dict.get('notes', '')
            date = entry_dict.get('added_date', '')
            
            # Shorten date to just date part (not time)
            if ' ' in date:
                date = date.split(' ')[0]
            
            values = (
                entry,
                entry_type,
                notes[:40] + '...' if len(notes) > 40 else notes,  # Truncate long notes
                date
            )
            
            # Insert item with green background
            item_id = self.tree.insert('', tk.END, values=values, tags=('protected',))
            self.sender_data[item_id] = entry_dict
        
        # Store all items for filtering
        self.store_all_items()
    
    def get_selected(self) -> List[Dict]:
        """
        Get selected entry data.
        
        Returns:
            List of selected entry dictionaries
        """
        selected_ids = self.tree.selection()
        return [self.entry_data[item_id] for item_id in selected_ids
                if item_id in self.entry_data]
    
    def get_all(self) -> List[Dict]:
        """
        Get all entry data in the table.
        
        Returns:
            List of all entry dictionaries
        """
        return list(self.entry_data.values())
    
    def clear(self):
        """Clear all items from the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.entry_data.clear()
    
    def remove_selected(self):
        """Remove selected items from the table."""
        selected_ids = self.tree.selection()
        for item_id in selected_ids:
            self.tree.delete(item_id)
            if item_id in self.entry_data:
                del self.entry_data[item_id]
    
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
    
    def _data_to_values(self, data: Dict) -> tuple:
        """Convert entry data to display values tuple."""
        entry = data.get('entry', 'Unknown')
        entry_type = data.get('type', 'email').capitalize()
        notes = data.get('notes', '')
        date = data.get('added_date', '')
        
        # Shorten date to just date part (not time)
        if ' ' in date:
            date = date.split(' ')[0]
        
        return (
            entry,
            entry_type,
            notes[:40] + '...' if len(notes) > 40 else notes,
            date
        )
    
    def _get_item_tags(self, data: Dict) -> tuple:
        """Get tags for an item."""
        return ('protected',)

