"""
Services package for Email Unsubscriber.

This package contains business logic services that coordinate between
the UI layer and lower-level components (repositories, email clients, etc.).

Services are designed for dependency injection and testability.
"""

from src.services.email_scan_service import EmailScanService
from src.services.unsubscribe_service import UnsubscribeService

__all__ = [
    'EmailScanService',
    'UnsubscribeService',
]

