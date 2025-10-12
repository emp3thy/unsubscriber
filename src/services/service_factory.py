"""
Service Factory for Email Unsubscriber.

This factory creates service instances with proper dependency injection,
handling all the complexity of wiring dependencies together.
"""

import logging
from typing import Optional
from src.services.email_scan_service import EmailScanService
from src.services.unsubscribe_service import UnsubscribeService
from src.services.email_deletion_service import EmailDeletionService
from src.email_client.email_parser import EmailParser
from src.scoring.scorer import EmailScorer
from src.scoring.email_grouper import EmailGrouper
from src.unsubscribe.strategy_chain import StrategyChain
from src.unsubscribe.list_unsubscribe import ListUnsubscribeStrategy
from src.unsubscribe.http_strategy import HTTPStrategy


class ServiceFactory:
    """
    Factory for creating service instances with proper dependency injection.
    
    This factory encapsulates the complexity of wiring services with their
    dependencies, providing a simple interface for creating fully configured
    service instances. Services are cached to ensure the same instance is
    returned on subsequent calls.
    
    Example:
        >>> from src.database.db_manager import DBManager
        >>> db = DBManager('data/emailunsubscriber.db')
        >>> factory = ServiceFactory(db)
        >>> 
        >>> # Create services
        >>> scan_service = factory.create_scan_service()
        >>> unsub_service = factory.create_unsubscribe_service()
        >>> delete_service = factory.create_deletion_service()
        >>> 
        >>> # Update email client for all services
        >>> factory.set_email_client(new_client)
    """
    
    def __init__(self, db_manager, email_client=None):
        """
        Initialize ServiceFactory with root dependencies.
        
        Args:
            db_manager: Database manager instance (required)
            email_client: Email client instance (optional, can be set later)
        """
        self.db = db_manager
        self.email_client = email_client
        self._services = {}
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("ServiceFactory initialized")
    
    def create_scan_service(self) -> EmailScanService:
        """
        Create or return cached EmailScanService.
        
        Creates an EmailScanService with all required dependencies:
        - EmailParser for parsing emails
        - EmailScorer for scoring
        - EmailGrouper for grouping by sender
        
        Returns:
            EmailScanService instance (cached on subsequent calls)
        
        Raises:
            ValueError: If email_client is not set
        """
        if 'scan' not in self._services:
            if self.email_client is None:
                raise ValueError(
                    "Email client must be set before creating scan service. "
                    "Use set_email_client() first."
                )
            
            self.logger.info("Creating EmailScanService")
            
            # Create dependencies
            parser = EmailParser()
            scorer = EmailScorer(self.db)
            grouper = EmailGrouper(scorer)
            
            # Create service
            self._services['scan'] = EmailScanService(
                self.email_client,
                self.db,
                parser,
                scorer,
                grouper
            )
            
            self.logger.info("EmailScanService created successfully")
        
        return self._services['scan']
    
    def create_unsubscribe_service(self) -> UnsubscribeService:
        """
        Create or return cached UnsubscribeService.
        
        Creates an UnsubscribeService with a configured strategy chain:
        - ListUnsubscribeStrategy (tries List-Unsubscribe header)
        - HTTPStrategy (tries common unsubscribe URL patterns)
        
        Returns:
            UnsubscribeService instance (cached on subsequent calls)
        """
        if 'unsubscribe' not in self._services:
            self.logger.info("Creating UnsubscribeService")
            
            # Create strategy chain
            chain = StrategyChain(self.db)
            chain.add_strategy(ListUnsubscribeStrategy())
            chain.add_strategy(HTTPStrategy())
            
            # Create service
            self._services['unsubscribe'] = UnsubscribeService(chain, self.db)
            
            self.logger.info("UnsubscribeService created successfully")
        
        return self._services['unsubscribe']
    
    def create_deletion_service(self) -> EmailDeletionService:
        """
        Create or return cached EmailDeletionService.
        
        Creates an EmailDeletionService with email client and database access.
        
        Returns:
            EmailDeletionService instance (cached on subsequent calls)
        
        Raises:
            ValueError: If email_client is not set
        """
        if 'deletion' not in self._services:
            if self.email_client is None:
                raise ValueError(
                    "Email client must be set before creating deletion service. "
                    "Use set_email_client() first."
                )
            
            self.logger.info("Creating EmailDeletionService")
            
            # Create service
            self._services['deletion'] = EmailDeletionService(
                self.email_client,
                self.db
            )
            
            self.logger.info("EmailDeletionService created successfully")
        
        return self._services['deletion']
    
    def set_email_client(self, client):
        """
        Set or update the email client for all services.
        
        Updates the email client and propagates the change to any
        already-created services that depend on it (scan and deletion services).
        
        Args:
            client: Email client instance (IMAP or Gmail API)
        """
        self.logger.info(f"Setting email client: {client.__class__.__name__}")
        self.email_client = client
        
        # Update existing services that use email client
        if 'scan' in self._services:
            self._services['scan'].email_client = client
            self.logger.debug("Updated email client for EmailScanService")
        
        if 'deletion' in self._services:
            self._services['deletion'].email_client = client
            self.logger.debug("Updated email client for EmailDeletionService")
    
    def get_email_client(self):
        """
        Get the current email client.
        
        Returns:
            Current email client instance or None
        """
        return self.email_client
    
    def clear_cache(self):
        """
        Clear all cached service instances.
        
        Forces recreation of services on next call to create_*_service().
        Useful for testing or when services need to be reset.
        """
        self.logger.info("Clearing service cache")
        self._services.clear()
    
    def get_cached_services(self):
        """
        Get list of currently cached service names.
        
        Returns:
            List of service names that are currently cached
        """
        return list(self._services.keys())

