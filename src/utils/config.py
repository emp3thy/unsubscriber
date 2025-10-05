"""Configuration management for Email Unsubscriber

Provides a type-safe API for storing and retrieving application settings
using the database as persistent storage. Handles serialization of complex
types (lists, dicts) to JSON automatically.
"""

import json
from typing import Any
import logging
from src.database.db_manager import DBManager


class Config:
    """Configuration management with database persistence.
    
    Wraps DBManager to provide type-safe access to configuration values
    with automatic JSON serialization for complex types.
    """
    
    def __init__(self, db_manager: DBManager):
        """Initialize configuration manager.
        
        Args:
            db_manager: Database manager instance for persistence
        """
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default.
        
        Automatically deserializes JSON for complex types.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default if not found
        """
        try:
            value = self.db.get_config(key)
            if value is None:
                return default
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Not JSON, return as-is
                return value
        except Exception as e:
            self.logger.error(f"Error getting config '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value.
        
        Automatically serializes complex types to JSON.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Raises:
            Exception: If setting config fails
        """
        try:
            # Serialize complex types to JSON
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value)
            elif isinstance(value, bool):
                # Booleans must be serialized as JSON to preserve type
                value = json.dumps(value)
            else:
                value = str(value)
            
            self.db.set_config(key, value)
        except Exception as e:
            self.logger.error(f"Error setting config '{key}': {e}")
            raise
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Boolean configuration value
        """
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        # Handle string representations of booleans
        return str(value).lower() in ('true', '1', 'yes')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Integer configuration value
        """
        try:
            return int(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_str(self, key: str, default: str = "") -> str:
        """Get string configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            String configuration value
        """
        return str(self.get(key, default))

