"""
tests/test_address_formatting.py - Tests for address formatting and validation
"""

from models.core import Person, PersonType

def test_address_formatting():
    """Test different address format combinations"""
    test_cases = [
        # Full address
        {
            "address": "Main Street 1",
            "city": "8000 Zurich",
            "expected": "Main Street 1, 8000 Zurich"
        },
        # Only street
        {
            "address": "Side Street 2",
            "city": None,
            "expected": "Side Street 2"
        },
        # Only city
        {
            "address": None,
            "city": "8000 Zurich",
            "expected": None
        },
        # Both None
        {
            "address": None,
            "city": None,
            "expected": None
        }
    ]
    
    for case in test_cases:
        person = Person(
            firstname="Test",
            lastname="Person",
            address=case["address"],
            city=case["city"]
        )
        assert person.full_address == case["expected"]

def test_address_whitespace_handling():
    """Test that address whitespace is handled correctly"""
    test_cases = [
        # Extra spaces in address
        {
            "address": "  Main Street  1  ",
            "city": "8000  Zurich",
            "expected": "Main Street  1, 8000  Zurich"
        },
        # Tabs and newlines
        {
            "address": "\tSide Street\t2\n",
            "city": "\n8000\tZurich",
            "expected": "Side Street\t2, 8000\tZurich"
        }
    ]
    
    for case in test_cases:
        person = Person(
            firstname="Test",
            lastname="Person",
            address=case["address"],
            city=case["city"]
        )
        assert person.full_address == case["expected"]

def test_address_special_chars():
    """Test addresses with special characters"""
    test_cases = [
        # German characters
        {
            "address": "Mühlengasse 5",
            "city": "8000 Zürich",
            "expected": "Mühlengasse 5, 8000 Zürich"
        },
        # Special symbols
        {
            "address": "St. Johann's-Vorstadt 1",
            "city": "4056 Basel",
            "expected": "St. Johann's-Vorstadt 1, 4056 Basel"
        }
    ]
    
    for case in test_cases:
        person = Person(
            firstname="Test",
            lastname="Person",
            address=case["address"],
            city=case["city"]
        )
        assert person.full_address == case["expected"]