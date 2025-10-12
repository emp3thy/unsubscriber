"""Email Client Interface

Defines the common interface that all email clients (IMAP, Gmail API) must implement.
This allows polymorphic usage and easier testing with mock clients.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any


class EmailClientInterface(ABC):
    """Abstract base class for email clients.
    
    All email clients must implement this interface to ensure consistent
    behavior across different providers (IMAP, Gmail API, etc.).
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to email server and authenticate.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to email server.
        
        Should be safe to call multiple times and when not connected.
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to email server.
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    def fetch_email_ids(self, limit: int = 500) -> List[Any]:
        """Fetch email IDs from the server.
        
        Args:
            limit: Maximum number of IDs to fetch (default: 500)
            
        Returns:
            List of message IDs (type varies by implementation)
        """
        pass
    
    @abstractmethod
    def fetch_headers(self, message_ids: List[Any]) -> List[Dict]:
        """Fetch email headers for given message IDs.
        
        Args:
            message_ids: List of message IDs to fetch
            
        Returns:
            List of dictionaries containing email header information
        """
        pass
    
    @abstractmethod
    def delete_emails_from_sender(self, sender_email: str, db_manager=None) -> Tuple[int, str]:
        """Delete all emails from a specific sender.
        
        Args:
            sender_email: Email address of sender whose emails to delete
            db_manager: Optional DBManager for whitelist check (safety)
        
        Returns:
            Tuple of (count_deleted, message):
                - count_deleted: Number of emails deleted (0 if failed)
                - message: Descriptive result message
        """
        pass
    
    @abstractmethod
    def get_error_message(self) -> str:
        """Get the last error message from operations.
        
        Returns:
            Error message string, empty if no error
        """
        pass
    
    @abstractmethod
    def get_email_count(self) -> int:
        """Get total number of emails in mailbox.
        
        Returns:
            Email count, 0 on error
        """
        pass

