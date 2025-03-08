"""
plugins/compliance_plugin.py - Plugin for storing and managing compliance validation results

This plugin stores validation results from document compliance checks and provides
methods to access and manage this data.
"""

import json
from typing import Annotated, Dict, List, Union
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class CompliancePlugin:
    """Plugin that stores validation results from compliance checks."""
    
    def __init__(self):
        """Initialize with empty validation results."""
        self.compliance_items = []  # List of validation items checked
        self.is_complete = False  # Flag to track if validation is complete
        
    def reset(self):
        """Reset the stored data."""
        self.compliance_items = []
        self.is_complete = False
    
    @kernel_function(
        name="save_validation_result",
        description="Save a single validation check result"
    )
    def save_validation_result(
        self,
        validation_data: Annotated[str, "JSON string with validation data {section, item, status, details}"]
    ) -> str:
        """
        Save a single validation check result.
        Expected format: JSON string with validation details
        Returns: Success message or error
        """
        try:
            # Ensure validation_data is a string
            if not isinstance(validation_data, str):
                return f"Error: validation_data must be a JSON string, got {type(validation_data)}"
            
            # Parse the JSON input
            try:
                data = json.loads(validation_data)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON data: {str(e)}. Input was: {validation_data}"
            
            # Validate required fields
            required = ["section", "item", "status"]
            if not all(field in data for field in required):
                missing = [f for f in required if f not in data]
                return f"Error: Missing required fields {missing}"
            
            # Validate status value
            if data["status"] not in ["passed", "failed"]:
                return f"Error: status must be 'passed' or 'failed', got {data['status']}"
            
            # Add optional details field if not present
            if "details" not in data:
                data["details"] = None
            
            # Add to results list
            self.compliance_items.append(data)
            return f"Successfully saved validation result for {data['section']}: {data['item']}"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    @kernel_function(
        name="mark_validation_complete",
        description="Mark the validation process as complete"
    )
    def mark_validation_complete(self) -> str:
        """Mark the validation process as complete."""
        self.is_complete = True
        return "Validation process marked as complete"
    
    def get_validation_results(self) -> List[Dict]:
        """
        Return the list of validation results.
        Returns:
            List of validation result dictionaries
        """
        return self.compliance_items
    
    def get_validation_summary(self) -> Dict[str, List[Dict]]:
        """
        Get a summary of validation results grouped by section.
        Returns:
            Dict mapping section names to lists of validation items
        """
        summary = {}
        for item in self.compliance_items:
            section = item["section"]
            if section not in summary:
                summary[section] = []
            summary[section].append(item)
        return summary
    
    def format_markdown_report(self) -> str:
        """
        Format validation results as a Markdown checklist.
        Returns:
            Markdown formatted validation report
        """
        if not self.compliance_items:
            return "Keine Validierungsergebnisse vorhanden."
            
        summary = self.get_validation_summary()
        lines = []
        
        for section, items in summary.items():
            lines.append(f"\n### {section}")
            for item in items:
                checkbox = "✅" if item["status"] == "passed" else "❌"
                lines.append(f"{checkbox} {item['item']}")
                if "details" in item and item["details"]:
                    lines.append(f"   - {item['details']}")
                    
        return "\n".join(lines)