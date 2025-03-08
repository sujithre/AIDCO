"""
tests/test_document_validation.py - Tests for document validation edge cases
"""

from plugins.compliance_plugin import CompliancePlugin
import json

def test_validation_empty_document():
    """Test validation of empty document"""
    plugin = CompliancePlugin()
    
    # Test with empty content
    result = plugin.save_validation_result(json.dumps({
        "section": "Gesetzliche Grundlage",
        "item": "Document content check",
        "status": "failed",
        "details": "Document is empty"
    }))
    
    assert "Successfully saved" in result
    report = plugin.format_markdown_report()
    assert "❌" in report
    assert "Document is empty" in report

def test_validation_special_chars():
    """Test validation with special characters"""
    plugin = CompliancePlugin()
    
    # Test with various special characters
    special_chars = "äöüÄÖÜß@€$%&*()[]"
    result = plugin.save_validation_result(json.dumps({
        "section": f"Section with {special_chars}",
        "item": f"Item with {special_chars}",
        "status": "passed",
        "details": f"Details with {special_chars}"
    }))
    
    assert "Successfully saved" in result
    report = plugin.format_markdown_report()
    assert special_chars in report
    
def test_validation_duplicate_items():
    """Test handling of duplicate validation items"""
    plugin = CompliancePlugin()
    
    # Add same validation twice
    validation = {
        "section": "Test Section",
        "item": "Duplicate Item",
        "status": "passed"
    }
    
    plugin.save_validation_result(json.dumps(validation))
    plugin.save_validation_result(json.dumps(validation))
    
    results = plugin.get_validation_results()
    assert len(results) == 2  # Should keep both validations
    
    summary = plugin.get_validation_summary()
    assert len(summary["Test Section"]) == 2