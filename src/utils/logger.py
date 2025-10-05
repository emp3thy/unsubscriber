"""Logging configuration for Email Unsubscriber

Provides centralized logging setup with both console and rotating file handlers.
Logs are written to console (INFO and above) and to rotating log files (DEBUG and above).
"""

import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(log_dir: str = 'data/logs', log_file: str = 'app.log', 
                level: int = logging.DEBUG):
    """Configure application-wide logging.
    
    Sets up logging with two handlers:
    - Console handler: INFO and above
    - Rotating file handler: DEBUG and above (max 10MB per file, 30 backups)
    
    Args:
        log_dir: Directory for log files (default: 'data/logs')
        log_file: Name of the log file (default: 'app.log')
        level: Root logger level (default: DEBUG)
        
    Returns:
        logging.Logger: Configured root logger
    """
    
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)
    
    # Define log format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers (makes function idempotent)
    logger.handlers = []
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation (DEBUG and above)
    # Max 10MB per file, keep 30 backup files (approximately 30 days of logs)
    file_handler = RotatingFileHandler(
        log_path, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=30
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized. Log file: {log_path}")
    
    return logger

