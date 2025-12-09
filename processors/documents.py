"""
Document file processors (PDF, Word, Excel, etc.)
"""
from pathlib import Path
from typing import Dict, Any
import json

from docx import Document
from PyPDF2 import PdfReader
import openpyxl
import pandas as pd

from processors.base import MediaProcessor


class DocumentProcessor(MediaProcessor):
    """Process document files."""
    
    # Supported document file extensions
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.xlsx', '.xls'}
    
    def __init__(self):
        """Initialize document processor."""
        pass
    
    def process_pdf(self, file_path: Path) -> str:
        """Extract text from PDF files."""
        try:
            reader = PdfReader(str(file_path))
            text_parts = []
            
            # Extract from all pages
            for page in reader.pages:
                text_parts.append(page.extract_text())
                    
            return '\n'.join(text_parts)
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def process_docx(self, file_path: Path) -> str:
        """Extract text from DOCX files."""
        try:
            doc = Document(str(file_path))
            paragraphs = [p.text for p in doc.paragraphs]
            return '\n'.join(paragraphs)
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    def process_excel(self, file_path: Path) -> str:
        """Extract data from Excel files."""
        try:
            # Read entire Excel file
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Convert to readable format
            content = f"Excel file: {file_path.name}\n"
            content += f"Shape: {df.shape[0]} rows x {df.shape[1]} columns\n\n"
            content += "Columns:\n"
            content += ", ".join(df.columns) + "\n\n"
            content += "Data:\n"
            content += df.to_string()
            
            return content
        except Exception as e:
            return f"Error reading Excel: {str(e)}"
    
    def process_json(self, file_path: Path) -> str:
        """Extract and format JSON content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            formatted = json.dumps(data, indent=2)
            return formatted
        except Exception as e:
            return f"Error reading JSON: {str(e)}"
    
    def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a document file and extract its content.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with success status and summary (extracted text)
        """
        try:
            ext = file_path.suffix.lower()
            
            if ext == '.pdf':
                content = self.process_pdf(file_path)
            elif ext in ['.docx', '.doc']:
                content = self.process_docx(file_path)
            elif ext in ['.xlsx', '.xls']:
                content = self.process_excel(file_path)
            else:
                return {
                    'success': False,
                    'summary': '',
                    'error': f'Unsupported file type: {ext}'
                }
            
            # For documents, the "summary" is the full extracted text
            return {
                'success': True,
                'summary': content
            }
            
        except Exception as e:
            return {
                'success': False,
                'summary': '',
                'error': str(e)
            }


if __name__ == '__main__':
    # Test document processor
    import sys
    
    processor = DocumentProcessor()
    
    # Test with a file path from command line or use a default
    if len(sys.argv) > 1:
        test_file = Path(sys.argv[1])
    else:
        # Try to find any document file in Desktop for testing
        desktop = Path.home() / "Desktop"
        test_files = (
            list(desktop.glob("*.pdf")) +
            list(desktop.glob("*.docx")) +
            list(desktop.glob("*.xlsx"))
        )
        
        if test_files:
            test_file = test_files[0]
        else:
            print("No test files found on Desktop")
            print("Usage: python documents.py <file_path>")
            sys.exit(1)
    
    if not test_file.exists():
        print(f"Error: File not found: {test_file}")
        sys.exit(1)
    
    print(f"Testing DocumentProcessor with: {test_file.name}")
    print("=" * 80)
    
    # Process the file
    result = processor.process(test_file)
    
    if result['success']:
        content = result['summary']
        print(f"\n✓ Successfully processed {test_file.name}")
        print(f"\nExtracted content ({len(content)} characters):")
        print("-" * 80)
        print(content)
        print("-" * 80)
    else:
        print(f"\n✗ Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)
