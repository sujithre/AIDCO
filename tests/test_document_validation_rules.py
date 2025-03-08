"""
tests/test_document_validation_rules.py - Tests for document validation rules
"""

import pytest
from models.core import Person, PersonType, DocumentContext

def test_gemeinde_validation():
    """Test gemeinde validation rules"""
    # Valid gemeinde
    valid = DocumentContext(
        requestor=Person(firstname="John", lastname="Doe", type=PersonType.REQUESTOR),
        requested_people=[],
        gemeinde="Zürich",
        zweck="Test"
    )
    assert valid.gemeinde == "Zürich"
    
    # Empty gemeinde should raise ValueError
    with pytest.raises(ValueError):
        DocumentContext(
            requestor=Person(firstname="John", lastname="Doe", type=PersonType.REQUESTOR),
            requested_people=[],
            gemeinde="",
            zweck="Test"
        )
    
    # Whitespace gemeinde should raise ValueError
    with pytest.raises(ValueError):
        DocumentContext(
            requestor=Person(firstname="John", lastname="Doe", type=PersonType.REQUESTOR),
            requested_people=[],
            gemeinde="   ",
            zweck="Test"
        )

def test_zweck_validation():
    """Test zweck validation rules"""
    # Valid zweck
    valid = DocumentContext(
        requestor=Person(firstname="John", lastname="Doe", type=PersonType.REQUESTOR),
        requested_people=[],
        gemeinde="Test",
        zweck="Nachbarschaftliche Kontaktaufnahme"
    )
    assert valid.zweck == "Nachbarschaftliche Kontaktaufnahme"
    
    # Empty zweck should raise ValueError
    with pytest.raises(ValueError):
        DocumentContext(
            requestor=Person(firstname="John", lastname="Doe", type=PersonType.REQUESTOR),
            requested_people=[],
            gemeinde="Test",
            zweck=""
        )

def test_requestor_validation():
    """Test requestor validation rules"""
    # Valid requestor
    valid_requestor = Person(
        firstname="John",
        lastname="Doe",
        type=PersonType.REQUESTOR
    )
    
    context = DocumentContext(
        requestor=valid_requestor,
        requested_people=[],
        gemeinde="Test",
        zweck="Test"
    )
    assert context.requestor.type == PersonType.REQUESTOR
    
    # Wrong type should raise ValueError
    invalid_requestor = Person(
        firstname="John",
        lastname="Doe",
        type=PersonType.REQUESTED  # Wrong type
    )
    
    with pytest.raises(ValueError):
        DocumentContext(
            requestor=invalid_requestor,
            requested_people=[],
            gemeinde="Test",
            zweck="Test"
        )