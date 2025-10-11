"""
Filterable Treeview widget with Excel-style column filtering.

This module provides a mixin that adds filtering capabilities to ttk.Treeview widgets,
allowing users to filter data by typing in entry boxes above each column.
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional
import logging


class FilterableTreeview:
    """Mixin class that adds Excel-style filtering to Treeview widgets."""
    
    def __init__(self):
        """Initialize filtering components."""
        self.filter_frame = None
        self.filter_entries = {}
        self.filter_vars = {}
        self.all_items = []  # Store all data for filtering
        self.filter_logger = logging.getLogger(__name__)
        self._resize_timer = None  # For debouncing resize events
        
    def create_filter_row(self, parent, tree, columns):
        """
        Create filter entry boxes aligned with treeview columns.
        
        Args:
            parent: Parent widget to contain the filter frame
            tree: The ttk.Treeview widget to filter
            columns: Dictionary of column identifiers to (heading, width) tuples
        """
        # Create main container frame
        self.filter_frame = ttk.Frame(parent, height=28)
        self.filter_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 0))
        self.filter_frame.pack_propagate(False)
        
        # Store tree reference for alignment updates
        self.tree_ref = tree
        
        # Get column list to maintain order
        column_ids = list(tree['columns'])
        
        # Create a sub-frame that will hold the entries and can be positioned
        entry_container = ttk.Frame(self.filter_frame)
        entry_container.place(x=0, y=0, relwidth=1.0, height=28)
        
        # Calculate cumulative x positions based on column widths
        x_offset = 0
        
        for col_id in column_ids:
            if col_id in columns:
                heading, width = columns[col_id]
                
                # Create StringVar for this column
                var = tk.StringVar()
                var.trace_add('write', lambda *args, c=col_id: self._on_filter_change(c))
                self.filter_vars[col_id] = var
                
                # Create entry widget
                entry = ttk.Entry(
                    entry_container, 
                    textvariable=var,
                    font=('TkDefaultFont', 9)
                )
                
                # Use place geometry for precise positioning
                entry.place(x=x_offset, y=2, width=width-1, height=24)
                self.filter_entries[col_id] = entry
                
                # Bind right-click to clear this filter
                entry.bind('<Button-3>', lambda e, v=var: self._clear_single_filter(v))
                
                # Bind Escape to clear all filters
                entry.bind('<Escape>', lambda e: self.clear_filters())
                
                # Move x offset for next column
                x_offset += width
        
        # Store the container reference
        self.entry_container = entry_container
        
        # Schedule initial position update after widget is rendered
        tree.after(100, self._update_filter_positions)
        
        # Bind tree column resize events to update filter positions
        tree.bind('<Configure>', self._update_filter_positions)
        
        # Also bind to the parent frame to catch window resizes
        parent.bind('<Configure>', self._update_filter_positions, add='+')
        
        # Bind to the filter frame itself
        self.filter_frame.bind('<Configure>', self._update_filter_positions, add='+')
        
        self.filter_logger.debug("Filter row created with place layout")
    
    def _update_filter_positions(self, event=None):
        """Update filter positions when tree columns are resized (debounced)."""
        if not hasattr(self, 'tree_ref') or not hasattr(self, 'filter_entries'):
            return
        
        # Cancel any pending update
        if self._resize_timer:
            try:
                self.tree_ref.after_cancel(self._resize_timer)
            except:
                pass
        
        # Schedule update after a short delay to debounce rapid resize events
        self._resize_timer = self.tree_ref.after(50, self._do_update_filter_positions)
    
    def _do_update_filter_positions(self):
        """Actually perform the filter position update."""
        try:
            if not hasattr(self, 'tree_ref') or not hasattr(self, 'filter_entries'):
                return
            
            column_ids = list(self.tree_ref['columns'])
            x_offset = 0
            
            for col_id in column_ids:
                if col_id in self.filter_entries:
                    # Get current column width from tree
                    width = self.tree_ref.column(col_id, 'width')
                    entry = self.filter_entries[col_id]
                    
                    # Update entry position and width (subtract 1 for visual spacing)
                    entry.place(x=x_offset, width=width-1)
                    x_offset += width
            
            self.filter_logger.debug(f"Updated filter positions, total width: {x_offset}")
        except Exception as e:
            self.filter_logger.error(f"Error updating filter positions: {e}")
    
    def _clear_single_filter(self, var):
        """Clear a single filter entry (right-click action)."""
        var.set('')
    
    def _on_filter_change(self, column_id):
        """Handle filter text change for a column."""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply all active filters to the treeview."""
        if not hasattr(self, 'tree') or not hasattr(self, 'sender_data'):
            self.filter_logger.warning("Tree or sender_data not initialized")
            return
        
        if not hasattr(self, 'all_items') or not self.all_items:
            self.filter_logger.warning("No items stored for filtering")
            return
        
        # Get filter values
        filters = {}
        for col_id, var in self.filter_vars.items():
            filter_text = var.get().strip().lower()
            if filter_text:
                filters[col_id] = filter_text
        
        self.filter_logger.debug(f"Applying filters: {filters}")
        
        # Clear current tree items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear sender_data before repopulating
        self.sender_data.clear()
        
        # If no filters, restore all items
        if not filters:
            self._restore_all_items()
            self.filter_logger.debug(f"Restored all {len(self.all_items)} items")
            return
        
        # Apply filters to stored data
        filtered_count = 0
        for data in self.all_items:
            try:
                if self._item_matches_filters(data, filters):
                    # Re-insert matching item
                    values = self._data_to_values(data)
                    if values:
                        tags = self._get_item_tags(data)
                        new_id = self.tree.insert('', tk.END, values=values, tags=tags)
                        self.sender_data[new_id] = data
                        filtered_count += 1
            except Exception as e:
                self.filter_logger.error(f"Error filtering item: {e}")
                continue
        
        self.filter_logger.debug(f"Applied filters: {filtered_count} of {len(self.all_items)} items match")
    
    def _item_matches_filters(self, data, filters: Dict[str, str]) -> bool:
        """
        Check if an item matches all active filters.
        
        Args:
            data: Item data dictionary
            filters: Dictionary of column_id -> filter_text
            
        Returns:
            True if item matches all filters
        """
        # Get column values
        values = self._data_to_values(data)
        if not values:
            return False
        
        # Map column IDs to their position
        columns = list(self.tree['columns'])
        
        # Check each filter
        for col_id, filter_text in filters.items():
            try:
                col_index = columns.index(col_id)
                if col_index < len(values):
                    cell_value = str(values[col_index]).lower()
                    if filter_text not in cell_value:
                        return False
            except (ValueError, IndexError):
                continue
        
        return True
    
    def _data_to_values(self, data: Dict) -> tuple:
        """
        Convert data dictionary to tuple of values for display.
        Must be implemented by subclass.
        
        Args:
            data: Data dictionary
            
        Returns:
            Tuple of display values
        """
        # Default implementation - subclasses should override
        return tuple()
    
    def _get_item_tags(self, data: Dict) -> tuple:
        """
        Get tags for an item based on its data.
        Must be implemented by subclass.
        
        Args:
            data: Data dictionary
            
        Returns:
            Tuple of tag names
        """
        # Default implementation - subclasses should override
        return tuple()
    
    def _restore_all_items(self):
        """Restore all items to the treeview."""
        if not hasattr(self, 'sender_data'):
            return
            
        self.sender_data.clear()
        
        for data in self.all_items:
            values = self._data_to_values(data)
            tags = self._get_item_tags(data)
            new_id = self.tree.insert('', tk.END, values=values, tags=tags)
            self.sender_data[new_id] = data
    
    def store_all_items(self):
        """Store current tree items for filtering."""
        self.all_items = []
        
        if not hasattr(self, 'tree') or not hasattr(self, 'sender_data'):
            return
        
        # Store just the data, not the item IDs (which become invalid after tree clear)
        for item_id in self.tree.get_children():
            if item_id in self.sender_data:
                self.all_items.append(self.sender_data[item_id].copy())
        
        self.filter_logger.debug(f"Stored {len(self.all_items)} items for filtering")
    
    def clear_filters(self):
        """Clear all filter entries and show all data."""
        for var in self.filter_vars.values():
            var.set('')
        
        # Restore all items
        self._restore_all_items()
        
        self.filter_logger.debug("All filters cleared")

