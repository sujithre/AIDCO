"""
plugins/report_plugin.py - Plugin for storing and managing address verification data

This plugin stores person data collected during address verification
and provides methods to access and manage this data.
"""

import json
from typing import Annotated, Dict, List
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class ReportPlugin:
    """Plugin that stores people information during address verification."""
    
    def __init__(self):
        """Initialize with empty people list."""
        self.people = []  # List of persons with their information
        self.is_complete = False  # Flag to track if verification is complete
        
    def reset(self):
        """Reset the stored data."""
        self.people = []
        self.is_complete = False
    
    @kernel_function(
        name="save_people_data",
        description="Save verified person data including requestor and requested people"
    )
    def save_people_data(
        self,
        people_data: Annotated[str, "JSON string with people information [{firstname, lastname, address, city, type}]"]
    ) -> str:
        """
        Save a list of people with their verification data.
        Expected format: JSON array with person objects
        Returns: Success message or error
        """
        try:
            # Parse the JSON input
            data = json.loads(people_data)
            
            # Validate each person has the right format
            for person in data:
                required = ["firstname", "lastname", "type"]
                if not all(field in person for field in required):
                    missing = [f for f in required if f not in person]
                    return f"Error: Missing required fields {missing}"
            
            # Store the data
            self.people = data
            self.is_complete = True
            return f"Successfully saved data for {len(data)} people"
            
        except json.JSONDecodeError as e:
            return f"Error parsing JSON data: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @kernel_function(
        name="mark_complete",
        description="Mark the verification process as complete"
    )
    def mark_complete(self) -> str:
        """Mark the verification process as complete."""
        self.is_complete = True
        return "Verification process marked as complete"
    
    def get_addresses_dict(self) -> Dict[str, str]:
        """
        Return a dictionary with name -> address mapping.
        This is used by the app to generate the final document.
        
        Returns:
            Dict mapping full names to formatted addresses
        """
        result = {}
        
        for person in self.people:
            name = f"{person['firstname']} {person['lastname']}"
            
            # Format address if available
            if person.get('address') and person.get('city'):
                address = f"{person['address']}, {person['city']}"
            elif person.get('address'):
                address = person['address']
            else:
                address = None
                
            result[name] = address
            
        return result
    
    def get_requestor(self) -> dict:
        """
        Get the requestor's information.
        
        Returns:
            Dictionary with requestor details or None if not found
        """
        for person in self.people:
            if person.get('type') == 'requestor':
                return person
        return None
    
    def get_requested_people(self) -> List[dict]:
        """
        Get list of requested people (excluding the requestor).
        
        Returns:
            List of dictionaries with requested people details
        """
        return [p for p in self.people if p.get('type') == 'requested']