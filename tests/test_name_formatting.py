"""
tests/test_name_formatting.py - Tests for person name formatting and parsing
"""

from models.core import Person, PersonType

def test_name_formatting_variations():
    """Test different name format variations"""
    test_cases = [
        # Standard format
        ("John", "Doe", "John Doe"),
        # With middle name in lastname
        ("Maria", "von Schmidt", "Maria von Schmidt"),
        # With special characters
        ("André", "Müller", "André Müller"),
        # Single character names
        ("J", "Smith", "J Smith"),
        # Extra spaces
        ("Jane  ", "  Doe", "Jane Doe")
    ]
    
    for firstname, lastname, expected in test_cases:
        person = Person(firstname=firstname, lastname=lastname)
        assert person.full_name == expected

def test_name_component_trimming():
    """Test that name components are properly trimmed"""
    test_cases = [
        ("  John  ", "  Doe  ", "John", "Doe"),
        ("\tBob\t", "\nSmith\n", "Bob", "Smith"),
        ("Mary   Jane", "  O'Connor  ", "Mary   Jane", "O'Connor")
    ]
    
    for firstname, lastname, exp_first, exp_last in test_cases:
        person = Person(firstname=firstname, lastname=lastname)
        assert person.firstname == exp_first
        assert person.lastname == exp_last

def test_name_case_preservation():
    """Test that name casing is preserved"""
    test_cases = [
        ("John", "DOE", "John DOE"),
        ("JANE", "Smith", "JANE Smith"),
        ("von", "BERG", "von BERG"),
        ("Jean-Pierre", "D'ARCY", "Jean-Pierre D'ARCY")
    ]
    
    for firstname, lastname, expected in test_cases:
        person = Person(firstname=firstname, lastname=lastname)
        assert person.full_name == expected
        assert person.firstname == firstname  # Original case preserved
        assert person.lastname == lastname  # Original case preserved