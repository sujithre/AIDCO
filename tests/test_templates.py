"""
tests/test_templates.py - Tests for template handling and validation
"""

import os

def test_validation_questions_exist():
    """Test that validation questions template exists and has content"""
    template_path = os.path.join('templates', 'validation_questions.md')
    assert os.path.exists(template_path)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert content.strip() != ""
        assert "Gesetzliche Grundlage" in content
        assert "Listenauskunft" in content
        assert "Verpflichtungserklärung" in content
        assert "Rechtsmittelbelehrung" in content

def test_verfuegung_template_structure():
    """Test that Verfügung template has required sections"""
    template_path = os.path.join('templates', 'verfuegung_template.md')
    assert os.path.exists(template_path)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Check for required sections
        assert "# Verfügung zur Bekanntgabe von Personendaten" in content
        assert "## Systematische Bekanntgabe" in content
        assert "### Verfügung:" in content
        assert "### Ort, Datum" in content
        assert "### Einverstanden:" in content

def test_reference_docx_exists():
    """Test that reference.docx template exists"""
    template_path = os.path.join('templates', 'reference.docx')
    assert os.path.exists(template_path)
    assert os.path.getsize(template_path) > 0  # Should not be empty