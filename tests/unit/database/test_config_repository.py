"""Tests for ConfigRepository class."""

import pytest
import tempfile
import os
import sqlite3
from src.database.config_repository import ConfigRepository


@pytest.fixture
def temp_db():
    """Create a temporary database with config table."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Initialize with config table
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def config_repo(temp_db):
    """Create a ConfigRepository instance."""
    return ConfigRepository(temp_db)


class TestConfigRepository:
    """Tests for ConfigRepository class."""
    
    def test_init(self, temp_db):
        """Test repository initialization."""
        repo = ConfigRepository(temp_db)
        
        assert repo.db_path == temp_db
        assert repo.logger is not None
    
    def test_set_and_get_config(self, config_repo):
        """Test setting and getting config value."""
        config_repo.set_config('test_key', 'test_value')
        
        value = config_repo.get_config('test_key')
        
        assert value == 'test_value'
    
    def test_get_config_not_found_returns_default(self, config_repo):
        """Test getting non-existent config returns default."""
        value = config_repo.get_config('nonexistent', 'default_value')
        
        assert value == 'default_value'
    
    def test_get_config_not_found_returns_none(self, config_repo):
        """Test getting non-existent config without default returns None."""
        value = config_repo.get_config('nonexistent')
        
        assert value is None
    
    def test_set_config_updates_existing(self, config_repo):
        """Test setting existing config key updates value."""
        # Set first time
        config_repo.set_config('test_key', 'value1')
        assert config_repo.get_config('test_key') == 'value1'
        
        # Update
        config_repo.set_config('test_key', 'value2')
        assert config_repo.get_config('test_key') == 'value2'
    
    def test_set_config_converts_to_string(self, config_repo):
        """Test set_config converts values to strings."""
        # Set integer
        config_repo.set_config('number', 42)
        assert config_repo.get_config('number') == '42'
        
        # Set boolean
        config_repo.set_config('flag', True)
        assert config_repo.get_config('flag') == 'True'
    
    def test_get_bool_true_values(self, config_repo):
        """Test get_bool recognizes true values."""
        true_values = ['true', 'True', 'TRUE', '1', 'yes', 'YES', 'on', 'ON']
        
        for i, value in enumerate(true_values):
            config_repo.set_config(f'bool_{i}', value)
            assert config_repo.get_bool(f'bool_{i}') is True
    
    def test_get_bool_false_values(self, config_repo):
        """Test get_bool recognizes false values."""
        false_values = ['false', 'False', 'FALSE', '0', 'no', 'NO', 'off', 'OFF', 'anything']
        
        for i, value in enumerate(false_values):
            config_repo.set_config(f'bool_{i}', value)
            assert config_repo.get_bool(f'bool_{i}') is False
    
    def test_get_bool_default(self, config_repo):
        """Test get_bool returns default when key not found."""
        assert config_repo.get_bool('nonexistent', default=True) is True
        assert config_repo.get_bool('nonexistent', default=False) is False
    
    def test_get_int_valid(self, config_repo):
        """Test get_int with valid integer strings."""
        config_repo.set_config('number', '42')
        
        value = config_repo.get_int('number')
        
        assert value == 42
        assert isinstance(value, int)
    
    def test_get_int_negative(self, config_repo):
        """Test get_int with negative number."""
        config_repo.set_config('negative', '-10')
        
        assert config_repo.get_int('negative') == -10
    
    def test_get_int_invalid_returns_default(self, config_repo):
        """Test get_int with invalid value returns default."""
        config_repo.set_config('invalid', 'not_a_number')
        
        value = config_repo.get_int('invalid', default=100)
        
        assert value == 100
    
    def test_get_int_not_found_returns_default(self, config_repo):
        """Test get_int for non-existent key returns default."""
        value = config_repo.get_int('nonexistent', default=50)
        
        assert value == 50
    
    def test_get_int_default_zero(self, config_repo):
        """Test get_int returns 0 by default."""
        value = config_repo.get_int('nonexistent')
        
        assert value == 0
    
    def test_get_all_config_empty(self, config_repo):
        """Test getting all config when empty."""
        config = config_repo.get_all_config()
        
        assert config == {}
    
    def test_get_all_config_multiple(self, config_repo):
        """Test getting all config with multiple entries."""
        config_repo.set_config('key1', 'value1')
        config_repo.set_config('key2', 'value2')
        config_repo.set_config('key3', 'value3')
        
        config = config_repo.get_all_config()
        
        assert len(config) == 3
        assert config['key1'] == 'value1'
        assert config['key2'] == 'value2'
        assert config['key3'] == 'value3'
    
    def test_get_all_config_returns_dict(self, config_repo):
        """Test get_all_config returns dictionary."""
        config_repo.set_config('test', 'value')
        
        config = config_repo.get_all_config()
        
        assert isinstance(config, dict)
    
    def test_multiple_config_values(self, config_repo):
        """Test setting multiple different types of config."""
        config_repo.set_config('max_emails', '1000')
        config_repo.set_config('debug_mode', 'true')
        config_repo.set_config('app_version', '1.0.0')
        config_repo.set_config('timeout', '30')
        
        assert config_repo.get_config('max_emails') == '1000'
        assert config_repo.get_int('max_emails') == 1000
        assert config_repo.get_bool('debug_mode') is True
        assert config_repo.get_config('app_version') == '1.0.0'
        assert config_repo.get_int('timeout') == 30
    
    def test_config_persistence(self, temp_db):
        """Test config values persist across repository instances."""
        # Create first instance and set config
        repo1 = ConfigRepository(temp_db)
        repo1.set_config('persistent', 'value')
        
        # Create second instance and read config
        repo2 = ConfigRepository(temp_db)
        value = repo2.get_config('persistent')
        
        assert value == 'value'

