"""
services/export_service.py - Service for converting documents to Word format

This service handles the conversion of Markdown documents to properly formatted
Word documents using pandoc with custom styling.
"""

import os
import tempfile
import pypandoc
from datetime import datetime
from utils.create_reference_template import create_reference_template

class ExportService:
    """Service for exporting documents to Word format."""
    
    def __init__(self, reference_template_path: str = None):
        """
        Initialize the export service.
        
        Args:
            reference_template_path: Optional path to custom reference template.
                                   If not provided, uses default template.
        """
        if reference_template_path is None:
            reference_template_path = os.path.join("templates", "reference.docx")
            
        # Ensure reference template exists
        if not os.path.exists(reference_template_path):
            reference_template_path = create_reference_template(reference_template_path)
            
        self.reference_template_path = reference_template_path
    
    def markdown_to_docx(self, markdown_text: str, date: str = None) -> tuple[str, str]:
        """
        Convert markdown text to a Word document.
        
        Args:
            markdown_text: The markdown text to convert
            date: Optional date to insert in the document
            
        Returns:
            Tuple of (markdown with substituted date, path to generated docx)
        """
        # Replace date if provided
        if date:
            # Find the date in the markdown (assuming it's bold with **)
            import re
            date_pattern = r"\*\*\d{2}\.\d{2}\.\d{4}\*\*"
            markdown_text = re.sub(date_pattern, f"**{date}**", markdown_text)
        
        # Create temp file for markdown
        with tempfile.NamedTemporaryFile(mode='w', 
                                       suffix='.md', 
                                       encoding='utf-8',
                                       delete=False) as md_file:
            md_file.write(markdown_text)
            md_path = md_file.name
            
        # Create output path
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"verfuegung_{timestamp}.docx")
        
        try:
            # First try with reference doc
            self._convert_with_pandoc(md_path, output_path, use_reference=True)
        except Exception as e:
            print(f"Warning: Failed conversion with reference doc: {e}")
            print("Trying without reference doc...")
            self._convert_with_pandoc(md_path, output_path, use_reference=False)
            
        # Clean up temp file
        os.unlink(md_path)
        
        return markdown_text, output_path
    
    def _convert_with_pandoc(self, input_path: str, output_path: str, use_reference: bool = True):
        """
        Convert markdown to docx using pandoc with optional reference doc.
        
        Args:
            input_path: Path to input markdown file
            output_path: Path where docx should be saved
            use_reference: Whether to use reference doc for styling
        """
        # Base arguments
        args = [
            "--from", "markdown",
            "--to", "docx",
            "-o", output_path,
            "--standalone"
        ]
        
        # Add reference doc if requested
        if use_reference:
            args.extend(["--reference-doc", self.reference_template_path])
        
        # Convert using pandoc
        pypandoc.convert_file(
            input_path,
            "docx",
            outputfile=output_path,
            extra_args=args
        )