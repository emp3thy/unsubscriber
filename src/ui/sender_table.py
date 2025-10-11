"""
Sender table widget for Email Unsubscriber.

This module provides a sortable Treeview-based table widget for displaying
grouped sender data with color coding based on sender score.
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict
import logging
from src.ui.filterable_treeview import FilterableTreeview


class SenderTable(FilterableTreeview):
    """Table widget for displaying sender data."""
    
    def __init__(self, parent):
        """
        Initialize the sender table widget.
        
        Args:
            parent: Parent frame to contain the table
        """
        # Initialize FilterableTreeview
        FilterableTreeview.__init__(self)
        
        self.parent = parent
        self.sender_data = {}  # Store full data by item ID
        self.logger = logging.getLogger(__name__)
        
        # Create frame with scrollbar
        self.frame = ttk.Frame(parent)
        
        # Add filter row first
        self.columns_def = {
            'sender': ('Sender', 300),
            'count': ('Count', 80),
            'unread': ('Unread', 80),
            'score': ('Score', 80),
            'has_unsub': ('Has Unsub', 100),
            'status': ('Status', 120)
        }
        
        self.scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL)
        
        # Create Treeview
        self.tree = ttk.Treeview(
            self.frame,
            columns=('sender', 'count', 'unread', 'score', 'has_unsub', 'status'),
            show='headings',
            selectmode='extended',
            yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.tree.yview)
        
        # Setup columns
        self._setup_columns()
        
        # Configure color tags
        self.tree.tag_configure('normal', background='white')
        self.tree.tag_configure('medium', background='#FFFACD')  # Light yellow
        self.tree.tag_configure('high', background='#FFB6C1')     # Light red
        self.tree.tag_configure('whitelisted', background='#90EE90')  # Light green
        
        # Create filter row
        self.create_filter_row(self.frame, self.tree, self.columns_def)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Add to Whitelist", command=self._add_to_whitelist)
        self.context_menu.add_command(label="Add to Must Delete", command=self._add_to_must_delete)
        
        # Bind right-click to show context menu
        self.tree.bind("<Button-3>", self._show_context_menu)  # Right-click

        # Bind hover events for tooltips
        self.tree.bind("<Motion>", self._on_mouse_move)
        self.tree.bind("<Leave>", self._on_mouse_leave)
        
        # Store callbacks
        self.on_whitelist_add = None
        self.on_must_delete_add = None
        
        self.logger.debug("SenderTable initialized")

        # Tooltip variables
        self.tooltip = None
        self.tooltip_label = None
        self.score_breakdowns = {}  # item_id -> score breakdown dict

    def _store_score_breakdown(self, item_id: str, sender: Dict):
        """Store score breakdown for tooltip display."""
        # Get score breakdown from sender data (aggregated from all emails)
        breakdown = sender.get('score_breakdown', {})
        if breakdown:
            self.score_breakdowns[item_id] = breakdown

    def _on_mouse_move(self, event):
        """Handle mouse movement for tooltip display."""
        # Get the region (column) where mouse is hovering
        region = self.tree.identify_region(event.x, event.y)

        if region == "cell":
            # Get column and item under mouse
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)

            if item and column == "#4":  # Score column (0-indexed, so #4 is the 4th column)
                if item in self.score_breakdowns:
                    self._show_tooltip(event, self._format_score_breakdown(self.score_breakdowns[item]))
                else:
                    self._hide_tooltip()
            else:
                self._hide_tooltip()
        else:
            self._hide_tooltip()

    def _on_mouse_leave(self, event):
        """Hide tooltip when mouse leaves tree."""
        self._hide_tooltip()

    def _show_tooltip(self, event, text: str):
        """Show tooltip at mouse position."""
        if self.tooltip:
            self.tooltip.destroy()

        # Create tooltip window
        self.tooltip = tk.Toplevel(self.tree)
        self.tooltip.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

        # Create label with tooltip text
        self.tooltip_label = tk.Label(
            self.tooltip,
            text=text,
            background="#FFFFE0",
            borderwidth=1,
            relief="solid",
            font=("Arial", 9)
        )
        self.tooltip_label.pack()

        # Make sure tooltip stays on top
        self.tooltip.lift()

    def _hide_tooltip(self):
        """Hide the tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
            self.tooltip_label = None

    def _format_score_breakdown(self, breakdown: Dict) -> str:
        """Format score breakdown for tooltip display."""
        if not breakdown or 'total' not in breakdown:
            return "Score details unavailable"

        parts = []
        total = breakdown.get('total', 0)

        # Show each component
        if 'unread' in breakdown and breakdown['unread'] > 0:
            parts.append(f"Unread: +{breakdown['unread']}")
        if 'frequency' in breakdown and breakdown['frequency'] > 0:
            parts.append(f"Frequency: +{breakdown['frequency']}")
        if 'has_unsubscribe' in breakdown and breakdown['has_unsubscribe'] > 0:
            parts.append(f"Has unsubscribe: +{breakdown['has_unsubscribe']}")
        if 'historical_unwanted' in breakdown and breakdown['historical_unwanted'] > 0:
            parts.append(f"Historical: +{breakdown['historical_unwanted']}")

        if not parts:
            return f"Score: {total}"

        return f"Score {total} = {' + '.join(parts)}"
    
    def _setup_columns(self):
        """Define column headers and properties."""
        columns = {
            'sender': ('Sender', 300),
            'count': ('Count', 80),
            'unread': ('Unread', 80),
            'score': ('Score', 80),
            'has_unsub': ('Has Unsub', 100),
            'status': ('Status', 120)
        }
        
        for col, (heading, width) in columns.items():
            self.tree.heading(
                col, 
                text=heading,
                command=lambda c=col: self._sort_by_column(c, False)
            )
            self.tree.column(col, width=width)
        
        self.logger.debug("Table columns configured")
    
    def populate(self, senders: List[Dict]):
        """
        Populate table with sender data.
        
        Args:
            senders: List of sender dictionaries from EmailGrouper
        """
        self.clear()
        
        if not senders:
            self.logger.debug("No senders to populate")
            return
        
        for sender in senders:
            # Determine color tag based on score
            score = sender.get('total_score', 0)
            
            # Score of -1 indicates whitelisted (protected) sender
            if score == -1:
                tag = 'whitelisted'
                status_text = 'Whitelisted'
            elif score < 3:
                tag = 'normal'
                status_text = sender.get('status', 'Ready')
            elif score < 7:
                tag = 'medium'
                status_text = sender.get('status', 'Ready')
            else:
                tag = 'high'
                status_text = sender.get('status', 'Ready')
            
            # Format values
            values = (
                sender.get('sender', ''),
                f"{sender.get('total_count', 0):,}",
                f"{sender.get('unread_count', 0):,}",
                f"{score:.1f}" if score >= 0 else "Protected",
                'Yes' if sender.get('has_unsubscribe') else 'No',
                status_text
            )
            
            # Insert item
            item_id = self.tree.insert('', tk.END, values=values, tags=(tag,))
            self.sender_data[item_id] = sender

            # Store score breakdown for tooltip
            self._store_score_breakdown(item_id, sender)
        
        # Store all items for filtering
        self.store_all_items()
        
        self.logger.info(f"Populated table with {len(senders)} senders")
    
    def get_selected(self) -> List[Dict]:
        """
        Get selected sender data.
        
        Automatically filters out whitelisted senders (score=-1) to prevent
        accidental operations on protected senders.
        
        Returns:
            List of sender dictionaries for selected rows (excluding whitelisted)
        """
        selected_ids = self.tree.selection()
        selected = [
            self.sender_data[item_id] 
            for item_id in selected_ids
            if item_id in self.sender_data and self.sender_data[item_id].get('total_score', 0) != -1
        ]
        
        total_selected = len([s for s in selected_ids if s in self.sender_data])
        filtered = total_selected - len(selected)
        if filtered > 0:
            self.logger.info(f"Filtered out {filtered} whitelisted sender(s) from selection")
        
        self.logger.debug(f"Retrieved {len(selected)} selected senders (excluding whitelisted)")
        return selected
    
    def clear(self):
        """Clear all items from the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.sender_data.clear()
        self.score_breakdowns.clear()
        self._hide_tooltip()
        
        self.logger.debug("Table cleared")
    
    def _sort_by_column(self, col, reverse):
        """
        Sort table by column.
        
        Args:
            col: Column identifier to sort by
            reverse: If True, sort in descending order
        """
        items = [
            (self.tree.set(item, col), item) 
            for item in self.tree.get_children('')
        ]
        
        # Try numeric sort, fall back to string sort
        try:
            # Remove commas and convert to float for numeric columns
            items.sort(
                key=lambda t: float(t[0].replace(',', '').replace('Yes', '1').replace('No', '0')), 
                reverse=reverse
            )
        except (ValueError, AttributeError):
            # Fall back to string sort
            items.sort(reverse=reverse)
        
        # Rearrange items in sorted order
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Toggle sort direction for next click
        self.tree.heading(
            col, 
            command=lambda: self._sort_by_column(col, not reverse)
        )
        
        self.logger.debug(f"Table sorted by {col}, reverse={reverse}")
    
    def update_sender_status(self, sender_email: str, status: str):
        """
        Update status of a specific sender in the table.
        
        Args:
            sender_email: Email address of sender to update
            status: New status text
        """
        for item_id, sender_data in self.sender_data.items():
            if sender_data.get('sender') == sender_email:
                # Update the tree item
                current_values = list(self.tree.item(item_id)['values'])
                current_values[5] = status  # Status is column index 5
                self.tree.item(item_id, values=current_values)
                
                # Update stored data
                sender_data['status'] = status
                
                self.logger.debug(f"Updated status for {sender_email} to {status}")
                break
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame."""
        self.frame.grid(**kwargs)
    
    def _show_context_menu(self, event):
        """Show context menu on right-click.
        
        Args:
            event: Tkinter event object
        """
        # Select the item under cursor
        item_id = self.tree.identify_row(event.y)
        if item_id:
            # Select the item
            self.tree.selection_set(item_id)
            # Show context menu
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
    
    def _add_to_whitelist(self):
        """Handle 'Add to Whitelist' context menu action."""
        selected = self.get_selected()
        if not selected or not self.on_whitelist_add:
            return
        
        # Get the first selected sender
        sender_data = selected[0]
        sender_email = sender_data.get('sender', '')
        
        # Call the callback if provided
        if self.on_whitelist_add:
            self.on_whitelist_add(sender_email)
    
    def set_whitelist_callback(self, callback):
        """Set callback function for whitelist addition.
        
        Args:
            callback: Function to call when user selects "Add to Whitelist"
                     Should accept sender email as parameter
        """
        self.on_whitelist_add = callback
    
    def set_must_delete_callback(self, callback):
        """Set callback function for must delete addition.
        
        Args:
            callback: Function to call when user selects "Add to Must Delete"
                     Should accept sender email as parameter
        """
        self.on_must_delete_add = callback
    
    def _add_to_must_delete(self):
        """Handle 'Add to Must Delete' context menu action."""
        selected = self.get_selected()
        if not selected or not self.on_must_delete_add:
            return
        
        # Get the first selected sender
        sender_data = selected[0]
        sender_email = sender_data.get('sender', '')
        
        # Call the callback if provided
        if self.on_must_delete_add:
            self.on_must_delete_add(sender_email)
    
    def _data_to_values(self, data: Dict) -> tuple:
        """Convert sender data to display values tuple."""
        score = data.get('total_score', 0)
        status_text = data.get('status', 'Ready')
        
        if score == -1:
            status_text = 'Whitelisted'
        
        return (
            data.get('sender', ''),
            f"{data.get('total_count', 0):,}",
            f"{data.get('unread_count', 0):,}",
            f"{score:.1f}" if score >= 0 else "Protected",
            'Yes' if data.get('has_unsubscribe') else 'No',
            status_text
        )
    
    def _get_item_tags(self, data: Dict) -> tuple:
        """Get tags for an item based on sender score."""
        score = data.get('total_score', 0)
        
        if score == -1:
            return ('whitelisted',)
        elif score < 3:
            return ('normal',)
        elif score < 7:
            return ('medium',)
        else:
            return ('high',)

