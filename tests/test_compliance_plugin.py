"""
tests/test_compliance_plugin.py - Tests for the compliance validation plugin
"""

from plugins.compliance_plugin import CompliancePlugin

def test_compliance_plugin_init():
    """Test CompliancePlugin initialization"""
    plugin = CompliancePlugin()
    assert plugin.compliance_items == []
    assert plugin.is_complete is False

def test_save_validation_result():
    """Test saving validation results"""
    plugin = CompliancePlugin()
    
    # Test valid result
    result = plugin.save_validation_result(
        '{"section": "Test Section", "item": "Test Item", "status": "passed", "details": "Test passed"}'
    )
    assert "Successfully saved" in result
    assert len(plugin.compliance_items) == 1
    assert plugin.compliance_items[0]["section"] == "Test Section"
    
    # Test invalid JSON
    result = plugin.save_validation_result("invalid json")
    assert "Error parsing JSON" in result
    
    # Test missing required field
    result = plugin.save_validation_result('{"section": "Test", "status": "passed"}')
    assert "Missing required fields" in result
    
    # Test invalid status
    result = plugin.save_validation_result(
        '{"section": "Test", "item": "Test", "status": "invalid"}'
    )
    assert "status must be 'passed' or 'failed'" in result

def test_format_markdown_report():
    """Test markdown report formatting"""
    plugin = CompliancePlugin()
    
    # Empty report
    assert "Keine Validierungsergebnisse" in plugin.format_markdown_report()
    
    # Add some test results
    plugin.save_validation_result(
        '{"section": "Section 1", "item": "Item 1", "status": "passed", "details": null}'
    )
    plugin.save_validation_result(
        '{"section": "Section 1", "item": "Item 2", "status": "failed", "details": "Failed check"}'
    )
    plugin.save_validation_result(
        '{"section": "Section 2", "item": "Item 3", "status": "passed", "details": "Good"}'
    )
    
    report = plugin.format_markdown_report()
    assert "### Section 1" in report
    assert "### Section 2" in report
    assert "✅ Item 1" in report
    assert "❌ Item 2" in report
    assert "Failed check" in report
    assert "✅ Item 3" in report
    assert "Good" in report

def test_get_validation_summary():
    """Test getting validation summary by section"""
    plugin = CompliancePlugin()
    
    # Add test results
    plugin.save_validation_result(
        '{"section": "Section A", "item": "Item 1", "status": "passed"}'
    )
    plugin.save_validation_result(
        '{"section": "Section A", "item": "Item 2", "status": "failed"}'
    )
    plugin.save_validation_result(
        '{"section": "Section B", "item": "Item 3", "status": "passed"}'
    )
    
    summary = plugin.get_validation_summary()
    assert len(summary["Section A"]) == 2
    assert len(summary["Section B"]) == 1
    assert summary["Section A"][0]["item"] == "Item 1"
    assert summary["Section B"][0]["status"] == "passed"