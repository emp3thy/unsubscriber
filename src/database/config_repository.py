"""Repository for configuration operations.

Handles key-value storage for application settings.
"""

from typing import Any, Dict, Optional
from .base_repository import BaseRepository


class ConfigRepository(BaseRepository):
    """Repository for managing application configuration.
    
    Provides simple key-value storage for application settings.
    All values stored as strings.
    """
    
    def get_config(self, key: str, default: Any = None) -> Optional[str]:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value as string, or default if not found
            
        Example:
            >>> repo.get_config('max_emails', '1000')
            '500'
        """
        sql = "SELECT value FROM config WHERE key = ?"
        result = self._fetch_one(sql, (key,))
        return result[0] if result else default
    
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Uses INSERT OR REPLACE to update existing keys.
        Values are converted to strings for storage.
        
        Args:
            key: Configuration key
            value: Configuration value (will be converted to string)
            
        Example:
            >>> repo.set_config('max_emails', 500)
            >>> repo.set_config('debug_mode', 'true')
        """
        sql = "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)"
        self._execute_query(sql, (key, str(value)))
        self.logger.debug(f"Set config: {key}={value}")
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean configuration value.
        
        Parses string values as booleans.
        Treats 'true', '1', 'yes', 'on' as True (case-insensitive).
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Boolean value
            
        Example:
            >>> repo.set_config('debug_mode', 'true')
            >>> repo.get_bool('debug_mode')
            True
        """
        value = self.get_config(key)
        if value is None:
            return default
        
        # Parse string to boolean
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found or invalid
            
        Returns:
            Integer value
            
        Example:
            >>> repo.set_config('max_emails', '500')
            >>> repo.get_int('max_emails')
            500
        """
        value = self.get_config(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid integer config value for '{key}': {value}")
            return default
    
    def get_all_config(self) -> Dict[str, str]:
        """Get all configuration as dictionary.
        
        Returns:
            Dictionary mapping all config keys to values
            
        Example:
            >>> config = repo.get_all_config()
            >>> config['max_emails']
            '500'
        """
        sql = "SELECT key, value FROM config"
        rows = self._fetch_all(sql)
        
        return {row[0]: row[1] for row in rows}

