"""
Email pattern detection utilities.

This module provides functions to detect patterns in email addresses,
such as no-reply type addresses.
"""
import re
from typing import List


def is_noreply_email(email: str) -> bool:
    """
    Check if an email address contains at least two of the no-reply keywords
    before the "@" symbol.
    
    Keywords checked: "no", "not", "do", "reply"
    
    Args:
        email: Email address to check
        
    Returns:
        True if email contains at least 2 of the keywords before @, False otherwise
        
    Examples:
        >>> is_noreply_email("noreply@example.com")
        True
        >>> is_noreply_email("donotreply@example.com")
        True
        >>> is_noreply_email("no-reply@example.com")
        True
        >>> is_noreply_email("support@example.com")
        False
    """
    if not email or '@' not in email:
        return False
    
    # Get the part before the @ symbol
    local_part = email.split('@')[0].lower()
    
    # Keywords to search for (order matters - check longer words first to avoid double-counting)
    keywords = ['reply', 'not', 'no', 'do']
    
    # Track which keywords we've found to avoid counting overlaps
    found_keywords = []
    remaining_text = local_part
    
    for keyword in keywords:
        if keyword in remaining_text:
            found_keywords.append(keyword)
            # Remove the found keyword to avoid double-counting overlapping patterns
            remaining_text = remaining_text.replace(keyword, '', 1)
    
    return len(found_keywords) >= 2


def get_noreply_senders(senders: List[dict]) -> List[dict]:
    """
    Filter a list of senders to only those with no-reply type email addresses.
    
    Args:
        senders: List of sender dictionaries (must have 'sender' key with email)
        
    Returns:
        Filtered list of sender dictionaries with no-reply emails
    """
    return [
        sender for sender in senders
        if is_noreply_email(sender.get('sender', ''))
    ]

