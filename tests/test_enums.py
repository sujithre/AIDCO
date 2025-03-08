"""
tests/test_enums.py - Tests for enumerations and constants
"""

from models.core import PersonType

def test_person_type_values():
    """Test PersonType enum has correct values"""
    assert PersonType.REQUESTOR.value == "requestor"
    assert PersonType.REQUESTED.value == "requested"

def test_person_type_comparisons():
    """Test PersonType enum comparisons work correctly"""
    assert PersonType.REQUESTOR != PersonType.REQUESTED
    assert PersonType.REQUESTOR == PersonType.REQUESTOR
    
    # Test string comparisons
    assert PersonType.REQUESTOR.value == "requestor"
    assert PersonType.REQUESTED.value == "requested"

def test_person_type_string_representation():
    """Test string representation of PersonType"""
    assert str(PersonType.REQUESTOR) == "PersonType.REQUESTOR"
    assert str(PersonType.REQUESTED) == "PersonType.REQUESTED"

def test_person_type_membership():
    """Test membership checking in PersonType"""
    assert PersonType.REQUESTOR in PersonType
    assert PersonType.REQUESTED in PersonType
    assert "invalid" not in [pt.value for pt in PersonType]