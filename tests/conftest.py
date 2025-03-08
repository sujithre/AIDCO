"""
tests/conftest.py - Test configuration and shared fixtures
"""

import os
import pytest

@pytest.fixture
def sample_markdown():
    """Fixture providing sample markdown content for testing"""
    return """# Test Document
    
**08.03.2024**

## Section 1
Some content here

## Section 2
More content here
"""

@pytest.fixture
def ensure_output_dir():
    """Fixture to ensure output directory exists"""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir