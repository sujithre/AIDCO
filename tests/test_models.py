"""
tests/test_models.py - Tests for core domain models
"""

from models.core import Person, PersonType, DocumentContext

def test_person_full_name():
    """Test that Person.full_name property works correctly"""
    person = Person(firstname="John", lastname="Doe")
    assert person.full_name == "John Doe"

def test_person_full_address():
    """Test that Person.full_address property works correctly"""
    # Test with both address and city
    person = Person(
        firstname="John",
        lastname="Doe",
        address="Main Street 1",
        city="8000 Zurich"
    )
    assert person.full_address == "Main Street 1, 8000 Zurich"
    
    # Test with only address
    person = Person(
        firstname="John",
        lastname="Doe",
        address="Main Street 1"
    )
    assert person.full_address == "Main Street 1"
    
    # Test with no address
    person = Person(firstname="John", lastname="Doe")
    assert person.full_address is None

def test_document_context_addresses_dict():
    """Test that DocumentContext.get_addresses_dict works correctly"""
    requestor = Person(
        firstname="John",
        lastname="Doe",
        address="Main Street 1",
        city="8000 Zurich",
        type=PersonType.REQUESTOR
    )
    
    requested_people = [
        Person(
            firstname="Jane",
            lastname="Smith",
            address="Side Street 2",
            city="8000 Zurich"
        ),
        Person(
            firstname="Bob",
            lastname="Brown"  # No address
        )
    ]
    
    context = DocumentContext(
        requestor=requestor,
        requested_people=requested_people,
        gemeinde="Zurich",
        zweck="Test Purpose"
    )
    
    addresses = context.get_addresses_dict()
    assert addresses["John Doe"] == "Main Street 1, 8000 Zurich"
    assert addresses["Jane Smith"] == "Side Street 2, 8000 Zurich"
    assert "Bob Brown" not in addresses  # Should not include people without addresses