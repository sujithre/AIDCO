"""
tests/test_export_service.py - Tests for document export functionality
"""

import os
from services.export_service import ExportService

def test_export_service_init():
    """Test that ExportService initializes correctly"""
    service = ExportService()
    assert service is not None
    assert hasattr(service, 'reference_template_path')
    assert os.path.exists(service.reference_template_path)

def test_markdown_to_docx_date_substitution():
    """Test that date substitution in markdown works correctly"""
    service = ExportService()
    
    # Simple markdown with a date
    markdown = """# Test Document
**01.01.2024**
Some content"""
    
    new_date = "15.03.2024"
    result_md, _ = service.markdown_to_docx(markdown, date=new_date)
    
    assert "**15.03.2024**" in result_md
    assert "**01.01.2024**" not in result_md

def test_markdown_to_docx_multiple_dates(sample_markdown):
    """Test handling multiple dates in markdown"""
    service = ExportService()
    
    # Add another date to test multiple date handling
    markdown_multiple = sample_markdown + "\n**10.03.2024**\n"
    
    new_date = "15.03.2024"
    result_md, _ = service.markdown_to_docx(markdown_multiple, date=new_date)
    
    assert "**15.03.2024**" in result_md
    assert "**08.03.2024**" not in result_md
    assert "**10.03.2024**" not in result_md
    assert result_md.count("**15.03.2024**") == 2  # Should replace both dates

def test_markdown_to_docx_output_path(ensure_output_dir):
    """Test that output file is created in correct location"""
    service = ExportService()
    markdown = "# Test Document\n**01.01.2024**"
    
    _, output_path = service.markdown_to_docx(markdown)
    
    assert output_path.startswith(ensure_output_dir)
    assert output_path.endswith(".docx")
    assert "verfuegung_" in output_path
    assert os.path.exists(output_path)

def test_markdown_to_docx_no_date():
    """Test markdown conversion without date substitution"""
    service = ExportService()
    markdown = "# Test Document\nNo date here\nJust regular content"
    
    result_md, _ = service.markdown_to_docx(markdown)
    assert result_md == markdown  # Should return unchanged if no date to substitute