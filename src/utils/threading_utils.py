"""
Threading utilities for Email Unsubscriber.

This module provides thread-safe infrastructure for running background tasks
with progress updates in Tkinter applications.
"""
import threading
import queue
from typing import Callable, Any
import tkinter as tk
import logging


class BackgroundTask:
    """Manages background tasks with progress updates for Tkinter UI."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the background task manager.
        
        Args:
            root: Tkinter root window for UI updates
        """
        self.root = root
        self.queue = queue.Queue()
        self.is_cancelled = False
        self.thread = None
        self.logger = logging.getLogger(__name__)
    
    def run(self, task_func: Callable, on_progress: Callable, on_complete: Callable):
        """
        Run task in background thread with progress updates.
        
        Args:
            task_func: Function to run. Must accept progress_callback parameter.
            on_progress: Called with (current, total, message) for updates.
            on_complete: Called with result on completion or error.
        """
        self.is_cancelled = False
        self.logger.info("Starting background task")
        
        def wrapper():
            """Wrapper function that runs in the background thread."""
            try:
                result = task_func(self.progress_callback)
                if not self.is_cancelled:
                    self.queue.put(('complete', result))
                    self.logger.info("Background task completed successfully")
            except Exception as e:
                error_msg = str(e)
                self.queue.put(('error', error_msg))
                self.logger.error(f"Background task error: {error_msg}")
        
        # Start daemon thread (won't block app exit)
        self.thread = threading.Thread(target=wrapper, daemon=True)
        self.thread.start()
        
        # Start checking queue for updates
        self._check_queue(on_progress, on_complete)
    
    def progress_callback(self, current: int, total: int, message: str = ""):
        """
        Called by task to report progress (thread-safe).
        
        Args:
            current: Current progress value
            total: Total expected value
            message: Optional status message
        """
        if not self.is_cancelled:
            self.queue.put(('progress', (current, total, message)))
    
    def _check_queue(self, on_progress: Callable, on_complete: Callable):
        """
        Check queue for updates and schedule next check.
        
        This method runs in the main UI thread and processes messages
        from the background thread safely.
        
        Args:
            on_progress: Progress callback function
            on_complete: Completion callback function
        """
        try:
            # Process all available messages
            while True:
                msg_type, data = self.queue.get_nowait()
                
                if msg_type == 'progress':
                    on_progress(*data)
                elif msg_type == 'complete':
                    on_complete(data)
                    return  # Task complete, stop checking
                elif msg_type == 'error':
                    on_complete(None, error=data)
                    return  # Task failed, stop checking
                    
        except queue.Empty:
            pass  # No messages available yet
        
        # Schedule next check in 100ms (Tkinter-safe)
        if not self.is_cancelled:
            self.root.after(100, lambda: self._check_queue(on_progress, on_complete))
    
    def cancel(self):
        """Cancel the running task."""
        self.is_cancelled = True
        self.logger.info("Background task cancelled")

