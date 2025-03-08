"""
tests/test_compliance_validations.py - Tests for compliance validation rules
"""

from plugins.compliance_plugin import CompliancePlugin

def test_validation_sections():
    """Test compliance validation sections are processed correctly"""
    plugin = CompliancePlugin()
    
    # Add validations for different sections
    sections = [
        ("Gesetzliche Grundlage", "Test Item 1", "passed"),
        ("Listenauskunft", "Test Item 2", "failed"),
        ("Verpflichtungserklärung", "Test Item 3", "passed"),
        ("Rechtsmittelbelehrung", "Test Item 4", "passed")
    ]
    
    for section, item, status in sections:
        plugin.save_validation_result(
            f'{{"section": "{section}", "item": "{item}", "status": "{status}"}}'
        )
    
    summary = plugin.get_validation_summary()
    
    # Check all sections are present
    assert len(summary) == 4
    assert all(section[0] in summary for section in sections)
    
    # Check items are in correct sections
    assert len(summary["Gesetzliche Grundlage"]) == 1
    assert len(summary["Listenauskunft"]) == 1
    assert summary["Listenauskunft"][0]["status"] == "failed"

def test_validation_status_counting():
    """Test counting of passed/failed validations"""
    plugin = CompliancePlugin()
    
    # Add mix of passed and failed validations
    validations = [
        ("Section 1", "Item 1", "passed"),
        ("Section 1", "Item 2", "failed"),
        ("Section 2", "Item 3", "passed"),
        ("Section 2", "Item 4", "passed")
    ]
    
    for section, item, status in validations:
        plugin.save_validation_result(
            f'{{"section": "{section}", "item": "{item}", "status": "{status}"}}'
        )
    
    # Count results
    all_results = plugin.get_validation_results()
    passed = sum(1 for r in all_results if r["status"] == "passed")
    failed = sum(1 for r in all_results if r["status"] == "failed")
    
    assert passed == 3
    assert failed == 1
    assert passed + failed == len(validations)

def test_validation_report_formatting():
    """Test validation report markdown formatting"""
    plugin = CompliancePlugin()
    
    # Add validations with details
    plugin.save_validation_result(
        '{"section": "Test Section", "item": "Item 1", "status": "passed", "details": "Test passed successfully"}'
    )
    plugin.save_validation_result(
        '{"section": "Test Section", "item": "Item 2", "status": "failed", "details": "Missing required field"}'
    )
    
    report = plugin.format_markdown_report()
    
    # Check markdown formatting
    assert "### Test Section" in report
    assert "✅" in report  # Check for success emoji
    assert "❌" in report  # Check for failure emoji
    assert "Test passed successfully" in report
    assert "Missing required field" in report
    
    # Check order (success should come before failure)
    success_pos = report.find("✅")
    failure_pos = report.find("❌")
    assert success_pos < failure_pos  # Success should be listed first