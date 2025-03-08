"""
tests/test_report_plugin.py - Tests for the report data management plugin
"""

from plugins.report_plugin import ReportPlugin

def test_report_plugin_init():
    """Test ReportPlugin initialization"""
    plugin = ReportPlugin()
    assert plugin.people == []
    assert plugin.is_complete is False

def test_save_people_data():
    """Test saving people data"""
    plugin = ReportPlugin()
    
    # Test valid data
    valid_data = '[{"firstname": "John", "lastname": "Doe", "type": "requestor", "address": "Main St 1", "city": "Zurich"}]'
    result = plugin.save_people_data(valid_data)
    assert "Successfully saved data" in result
    assert len(plugin.people) == 1
    
    # Test invalid JSON
    result = plugin.save_people_data("invalid json")
    assert "Error parsing JSON" in result
    
    # Test missing required fields
    result = plugin.save_people_data('[{"firstname": "John", "type": "requestor"}]')
    assert "Missing required fields" in result

def test_get_addresses_dict():
    """Test getting formatted addresses dictionary"""
    plugin = ReportPlugin()
    
    # Add test data
    plugin.save_people_data("""[
        {"firstname": "John", "lastname": "Doe", "type": "requestor", "address": "Main St 1", "city": "Zurich"},
        {"firstname": "Jane", "lastname": "Smith", "type": "requested", "address": "Side St 2", "city": "Zurich"},
        {"firstname": "Bob", "lastname": "Brown", "type": "requested"}
    ]""")
    
    addresses = plugin.get_addresses_dict()
    assert addresses["John Doe"] == "Main St 1, Zurich"
    assert addresses["Jane Smith"] == "Side St 2, Zurich"
    assert addresses["Bob Brown"] is None  # Person exists in dict but has no address

def test_get_requestor():
    """Test getting requestor information"""
    plugin = ReportPlugin()
    
    # Add test data with one requestor and multiple requested people
    plugin.save_people_data("""[
        {"firstname": "John", "lastname": "Doe", "type": "requestor", "address": "Main St"},
        {"firstname": "Jane", "lastname": "Smith", "type": "requested"},
        {"firstname": "Bob", "lastname": "Brown", "type": "requested"}
    ]""")
    
    requestor = plugin.get_requestor()
    assert requestor is not None
    assert requestor["firstname"] == "John"
    assert requestor["lastname"] == "Doe"
    assert requestor["type"] == "requestor"

def test_get_requested_people():
    """Test getting list of requested people"""
    plugin = ReportPlugin()
    
    # Add test data
    plugin.save_people_data("""[
        {"firstname": "John", "lastname": "Doe", "type": "requestor"},
        {"firstname": "Jane", "lastname": "Smith", "type": "requested"},
        {"firstname": "Bob", "lastname": "Brown", "type": "requested"}
    ]""")
    
    requested = plugin.get_requested_people()
    assert len(requested) == 2
    assert requested[0]["firstname"] == "Jane"
    assert requested[1]["firstname"] == "Bob"
    assert all(p["type"] == "requested" for p in requested)