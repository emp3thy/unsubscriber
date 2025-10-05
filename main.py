"""
Email Unsubscriber - Main Application Entry Point

This application helps users manage unwanted emails by identifying senders
with high email volume and providing automated unsubscribe functionality.
"""
import sys
import os
import tkinter as tk

# Add the current directory to Python path so we can import src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.utils.logger import setup_logger
from src.database.db_manager import DBManager
from src.ui.main_window import MainWindow


def main():
    """Initialize and run the Email Unsubscriber application."""
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Email Unsubscriber application")
    
    # Initialize database
    db = DBManager('data/emailunsubscriber.db')
    db.initialize_db('src/database/schema.sql')
    logger.info("Database initialized")
    
    # Create main window
    root = tk.Tk()
    app = MainWindow(root, db)
    
    logger.info("Application window created, starting main loop")
    root.mainloop()
    
    logger.info("Application closed")


if __name__ == '__main__':
    main()

