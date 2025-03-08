"""
models/core.py - Core domain models for the document generation system

This module defines the core entities used throughout the application,
including Person and DocumentContext classes.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional

class PersonType(Enum):
    """Type of person in the document context"""
    REQUESTOR = "requestor"
    REQUESTED = "requested"

@dataclass
class Person:
    """
    Represents a person in the system, either a requestor or someone being looked up.
    """
    firstname: str
    lastname: str
    address: Optional[str] = None
    city: Optional[str] = None
    type: PersonType = PersonType.REQUESTED

    def __post_init__(self):
        """Clean up whitespace in name components"""
        self.firstname = self.firstname.strip()
        self.lastname = self.lastname.strip()
        if self.address:
            self.address = self.address.strip()
        if self.city:
            self.city = self.city.strip()

    @property
    def full_name(self) -> str:
        """Get the person's full name"""
        return f"{self.firstname} {self.lastname}"

    @property
    def full_address(self) -> Optional[str]:
        """Get the person's formatted full address if available"""
        if not self.address:
            return None
        
        parts = [self.address.strip()]
        if self.city:
            parts.append(self.city.strip())
            
        return ", ".join(parts)

@dataclass
class DocumentContext:
    """
    Context object containing all information needed to generate a document.
    """
    requestor: Person
    requested_people: List[Person]
    gemeinde: str
    zweck: str

    def __post_init__(self):
        """Validate document context data"""
        if not self.gemeinde or not self.gemeinde.strip():
            raise ValueError("Municipality (gemeinde) cannot be empty")
            
        if not self.zweck or not self.zweck.strip():
            raise ValueError("Purpose (zweck) cannot be empty")
            
        if self.requestor.type != PersonType.REQUESTOR:
            raise ValueError("Requestor must have type PersonType.REQUESTOR")
            
        self.gemeinde = self.gemeinde.strip()
        self.zweck = self.zweck.strip()

    def get_addresses_dict(self) -> Dict[str, str]:
        """
        Get a dictionary mapping names to addresses for all people.
        
        Returns:
            Dict mapping full names to full addresses
        """
        result = {}
        
        # Add requestor
        if self.requestor.full_address:
            result[self.requestor.full_name] = self.requestor.full_address
            
        # Add requested people
        for person in self.requested_people:
            if person.full_address:
                result[person.full_name] = person.full_address
                
        return result

# Constants used across the application
MAX_MESSAGE_COUNT = 20  # Maximum number of messages in agent chat
COMPLETION_MARKER = "COMPLETE"  # Marker used by agents to signal completion