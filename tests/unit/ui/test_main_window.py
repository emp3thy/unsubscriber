"""
Unit tests for MainWindow service factory injection.

Tests the service factory dependency injection without creating actual UI components.
Note: Full UI testing requires integration tests with real Tkinter root.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.service_factory import ServiceFactory


class TestMainWindowServiceFactoryInjection:
    """
    Test suite for MainWindow service factory injection logic.
    
    These tests verify the factory injection mechanism works correctly
    without creating actual UI components (which require real Tkinter root).
    """
    
    @patch('src.ui.main_window.MainWindow._create_menu_bar')
    @patch('src.ui.main_window.MainWindow._create_main_content')
    @patch('src.ui.main_window.MainWindow._create_status_bar')
    @patch('src.ui.main_window.MainWindow._center_window')
    def test_init_with_default_service_factory(self, mock_center, mock_status, mock_content, mock_menu):
        """Test MainWindow creates default ServiceFactory when not provided."""
        from src.ui.main_window import MainWindow
        
        mock_root = Mock()
        mock_db = Mock()
        
        # Create MainWindow without service_factory parameter (backward compatible)
        window = MainWindow(mock_root, mock_db)
        
        # Verify service factory was created automatically
        assert window.service_factory is not None
        assert isinstance(window.service_factory, ServiceFactory)
        assert window.service_factory.db is mock_db
    
    @patch('src.ui.main_window.MainWindow._create_menu_bar')
    @patch('src.ui.main_window.MainWindow._create_main_content')
    @patch('src.ui.main_window.MainWindow._create_status_bar')
    @patch('src.ui.main_window.MainWindow._center_window')
    def test_init_with_provided_service_factory(self, mock_center, mock_status, mock_content, mock_menu):
        """Test MainWindow uses provided ServiceFactory."""
        from src.ui.main_window import MainWindow
        
        mock_root = Mock()
        mock_db = Mock()
        custom_factory = ServiceFactory(mock_db)
        
        # Create MainWindow with custom factory
        window = MainWindow(mock_root, mock_db, service_factory=custom_factory)
        
        # Verify the provided factory is used
        assert window.service_factory is custom_factory
    
    @patch('src.ui.main_window.MainWindow._create_menu_bar')
    @patch('src.ui.main_window.MainWindow._create_main_content')
    @patch('src.ui.main_window.MainWindow._create_status_bar')
    @patch('src.ui.main_window.MainWindow._center_window')
    def test_service_factory_has_correct_db_reference(self, mock_center, mock_status, mock_content, mock_menu):
        """Test that created ServiceFactory has correct database reference."""
        from src.ui.main_window import MainWindow
        
        mock_root = Mock()
        mock_db = Mock()
        
        window = MainWindow(mock_root, mock_db)
        
        # Verify factory's db reference matches MainWindow's db
        assert window.service_factory.db is window.db
        assert window.service_factory.db is mock_db

