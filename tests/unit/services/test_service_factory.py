"""
Unit tests for ServiceFactory.

Tests the service factory to verify proper dependency injection,
service caching, and client management.
"""

import pytest
from unittest.mock import Mock
from src.services.service_factory import ServiceFactory
from src.services.email_scan_service import EmailScanService
from src.services.unsubscribe_service import UnsubscribeService
from src.services.email_deletion_service import EmailDeletionService


class TestServiceFactory:
    """Test suite for ServiceFactory."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database manager."""
        return Mock()
    
    @pytest.fixture
    def mock_client(self):
        """Create mock email client."""
        client = Mock()
        client.__class__.__name__ = "MockClient"
        return client
    
    @pytest.fixture
    def factory(self, mock_db, mock_client):
        """Create ServiceFactory with mocked dependencies."""
        return ServiceFactory(mock_db, mock_client)
    
    @pytest.fixture
    def factory_no_client(self, mock_db):
        """Create ServiceFactory without email client."""
        return ServiceFactory(mock_db)
    
    def test_factory_initialization_with_client(self, factory, mock_db, mock_client):
        """Test factory initializes correctly with all dependencies."""
        assert factory.db is mock_db
        assert factory.email_client is mock_client
        assert factory._services == {}
    
    def test_factory_initialization_without_client(self, factory_no_client, mock_db):
        """Test factory can be initialized without client."""
        assert factory_no_client.db is mock_db
        assert factory_no_client.email_client is None
    
    def test_create_scan_service(self, factory):
        """Test creating EmailScanService."""
        service = factory.create_scan_service()
        
        assert isinstance(service, EmailScanService)
        assert service.email_client is factory.email_client
        assert service.db is factory.db
    
    def test_create_unsubscribe_service(self, factory):
        """Test creating UnsubscribeService."""
        service = factory.create_unsubscribe_service()
        
        assert isinstance(service, UnsubscribeService)
        assert service.db is factory.db
        assert service.strategy_chain is not None
    
    def test_create_deletion_service(self, factory):
        """Test creating EmailDeletionService."""
        service = factory.create_deletion_service()
        
        assert isinstance(service, EmailDeletionService)
        assert service.email_client is factory.email_client
        assert service.db is factory.db
    
    def test_service_caching(self, factory):
        """Test that services are cached and reused."""
        service1 = factory.create_scan_service()
        service2 = factory.create_scan_service()
        
        assert service1 is service2
    
    def test_all_services_cached_independently(self, factory):
        """Test that each service type is cached independently."""
        scan = factory.create_scan_service()
        unsub = factory.create_unsubscribe_service()
        delete = factory.create_deletion_service()
        
        scan2 = factory.create_scan_service()
        unsub2 = factory.create_unsubscribe_service()
        delete2 = factory.create_deletion_service()
        
        assert scan is scan2
        assert unsub is unsub2
        assert delete is delete2
    
    def test_services_share_same_db(self, factory):
        """Test that all services share the same DB instance."""
        scan = factory.create_scan_service()
        unsub = factory.create_unsubscribe_service()
        delete = factory.create_deletion_service()
        
        assert scan.db is factory.db
        assert unsub.db is factory.db
        assert delete.db is factory.db
        assert scan.db is unsub.db is delete.db
    
    def test_services_share_same_client(self, factory):
        """Test that scan and deletion services share the same client."""
        scan = factory.create_scan_service()
        delete = factory.create_deletion_service()
        
        assert scan.email_client is factory.email_client
        assert delete.email_client is factory.email_client
        assert scan.email_client is delete.email_client
    
    def test_set_email_client(self, factory_no_client):
        """Test setting email client after factory creation."""
        new_client = Mock()
        new_client.__class__.__name__ = "NewClient"
        
        factory_no_client.set_email_client(new_client)
        
        assert factory_no_client.email_client is new_client
    
    def test_set_email_client_updates_existing_services(self, factory):
        """Test that setting client updates already-created services."""
        # Create services with initial client
        scan = factory.create_scan_service()
        delete = factory.create_deletion_service()
        
        # Change client
        new_client = Mock()
        new_client.__class__.__name__ = "NewClient"
        factory.set_email_client(new_client)
        
        # Services should have new client
        assert scan.email_client is new_client
        assert delete.email_client is new_client
    
    def test_create_scan_service_without_client_raises_error(self, factory_no_client):
        """Test that creating scan service without client raises error."""
        with pytest.raises(ValueError) as exc_info:
            factory_no_client.create_scan_service()
        
        assert "Email client must be set" in str(exc_info.value)
    
    def test_create_deletion_service_without_client_raises_error(self, factory_no_client):
        """Test that creating deletion service without client raises error."""
        with pytest.raises(ValueError) as exc_info:
            factory_no_client.create_deletion_service()
        
        assert "Email client must be set" in str(exc_info.value)
    
    def test_create_unsubscribe_service_without_client(self, factory_no_client):
        """Test that unsubscribe service can be created without client."""
        # Should not raise
        service = factory_no_client.create_unsubscribe_service()
        
        assert isinstance(service, UnsubscribeService)
    
    def test_deferred_client_creation(self, factory_no_client):
        """Test that client can be set after factory creation."""
        # Create unsubscribe service (doesn't need client)
        unsub = factory_no_client.create_unsubscribe_service()
        
        # Set client
        client = Mock()
        factory_no_client.set_email_client(client)
        
        # Now can create services that need client
        scan = factory_no_client.create_scan_service()
        delete = factory_no_client.create_deletion_service()
        
        assert scan.email_client is client
        assert delete.email_client is client
    
    def test_get_email_client(self, factory, mock_client):
        """Test getting current email client."""
        assert factory.get_email_client() is mock_client
    
    def test_get_email_client_when_none(self, factory_no_client):
        """Test getting email client when not set."""
        assert factory_no_client.get_email_client() is None
    
    def test_clear_cache(self, factory):
        """Test clearing service cache."""
        # Create services
        service1 = factory.create_scan_service()
        
        # Clear cache
        factory.clear_cache()
        
        # New service should be different instance
        service2 = factory.create_scan_service()
        
        assert service1 is not service2
    
    def test_get_cached_services(self, factory):
        """Test getting list of cached service names."""
        assert factory.get_cached_services() == []
        
        factory.create_scan_service()
        assert 'scan' in factory.get_cached_services()
        
        factory.create_unsubscribe_service()
        assert 'scan' in factory.get_cached_services()
        assert 'unsubscribe' in factory.get_cached_services()
        assert len(factory.get_cached_services()) == 2
        
        factory.create_deletion_service()
        assert len(factory.get_cached_services()) == 3
    
    def test_clear_cache_empties_cached_services_list(self, factory):
        """Test that clear_cache empties the cached services list."""
        factory.create_scan_service()
        factory.create_unsubscribe_service()
        assert len(factory.get_cached_services()) == 2
        
        factory.clear_cache()
        
        assert factory.get_cached_services() == []
    
    def test_set_email_client_doesnt_update_unsubscribe_service(self, factory):
        """Test that unsubscribe service is not affected by client updates."""
        unsub = factory.create_unsubscribe_service()
        
        new_client = Mock()
        factory.set_email_client(new_client)
        
        # Unsubscribe service doesn't use client, so nothing to update
        # Just verify it doesn't error
        assert unsub is not None
    
    def test_multiple_client_updates(self, factory):
        """Test that client can be updated multiple times."""
        scan = factory.create_scan_service()
        
        client1 = Mock()
        client1.__class__.__name__ = "Client1"
        factory.set_email_client(client1)
        assert scan.email_client is client1
        
        client2 = Mock()
        client2.__class__.__name__ = "Client2"
        factory.set_email_client(client2)
        assert scan.email_client is client2
        
        client3 = Mock()
        client3.__class__.__name__ = "Client3"
        factory.set_email_client(client3)
        assert scan.email_client is client3
    
    def test_factory_creates_intermediate_dependencies(self, factory):
        """Test that factory creates all intermediate dependencies."""
        service = factory.create_scan_service()
        
        # Should have parser, scorer, grouper
        assert service.parser is not None
        assert service.scorer is not None
        assert service.grouper is not None
    
    def test_unsubscribe_service_has_strategy_chain(self, factory):
        """Test that unsubscribe service is created with strategy chain."""
        service = factory.create_unsubscribe_service()
        
        assert service.strategy_chain is not None
        # Should have strategies added
        strategies = service.strategy_chain.get_strategies()
        assert len(strategies) >= 2  # ListUnsubscribe and HTTP strategies
    
    def test_factory_with_none_client_explicitly(self, mock_db):
        """Test factory with None client explicitly passed."""
        factory = ServiceFactory(mock_db, None)
        
        assert factory.email_client is None
    
    def test_factory_db_required(self):
        """Test that factory requires db_manager."""
        # This should work as long as we pass something for db
        # Python doesn't enforce types, so we just verify it's stored
        db = Mock()
        factory = ServiceFactory(db)
        
        assert factory.db is db

