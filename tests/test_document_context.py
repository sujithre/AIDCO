"""
tests/test_document_context.py - Tests for document context validation
"""

from models.core import Person, PersonType, DocumentContext

def test_empty_document_context():
    """Test document context with minimal data"""
    context = DocumentContext(
        requestor=Person(firstname="John", lastname="Doe", type=PersonType.REQUESTOR),
        requested_people=[],
        gemeinde="Test City",
        zweck="Test Purpose"
    )
    
    assert context.requestor.full_name == "John Doe"
    assert len(context.requested_people) == 0
    assert context.gemeinde == "Test City"
    assert context.zweck == "Test Purpose"

def test_document_context_with_multiple_people():
    """Test document context with multiple requested people"""
    requestor = Person(
        firstname="John",
        lastname="Doe",
        type=PersonType.REQUESTOR
    )
    
    requested_people = [
        Person(firstname="Jane", lastname="Smith"),
        Person(firstname="Bob", lastname="Brown"),
        Person(firstname="Alice", lastname="White")
    ]
    
    context = DocumentContext(
        requestor=requestor,
        requested_people=requested_people,
        gemeinde="Test City",
        zweck="Test Purpose"
    )
    
    assert len(context.requested_people) == 3
    assert all(p.type == PersonType.REQUESTED for p in context.requested_people)
    assert [p.full_name for p in context.requested_people] == [
        "Jane Smith", "Bob Brown", "Alice White"
    ]

def test_document_context_addresses():
    """Test document context address handling"""
    requestor = Person(
        firstname="John",
        lastname="Doe",
        address="Main St 1",
        city="8000 Zurich",
        type=PersonType.REQUESTOR
    )
    
    requested_people = [
        Person(
            firstname="Jane",
            lastname="Smith",
            address="Side St 2",
            city="8000 Zurich"
        ),
        Person(  # Person with no address
            firstname="Bob",
            lastname="Brown"
        ),
        Person(  # Person with partial address
            firstname="Alice",
            lastname="White",
            address="Back St 3"
        )
    ]
    
    context = DocumentContext(
        requestor=requestor,
        requested_people=requested_people,
        gemeinde="Zurich",
        zweck="Test Purpose"
    )
    
    addresses = context.get_addresses_dict()
    assert addresses["John Doe"] == "Main St 1, 8000 Zurich"
    assert addresses["Jane Smith"] == "Side St 2, 8000 Zurich"
    assert "Bob Brown" not in addresses
    assert addresses["Alice White"] == "Back St 3"