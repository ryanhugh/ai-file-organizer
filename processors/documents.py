"""
Document file processors (PDF, Word, Excel, etc.)
"""
from pathlib import Path
from typing import Dict, Any
import json

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import openpyxl
    import pandas as pd
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class DocumentProcessor:
    """Process document files."""
    
    def __init__(self, max_text_size: int = 50000):
        """
        Initialize document processor.
        
        Args:
            max_text_size: Maximum characters to extract
        """
        self.max_text_size = max_text_size
    
    def process_pdf(self, file_path: Path) -> str:
        """Extract text from PDF files."""
        if not PDF_AVAILABLE:
            return f"PDF file: {file_path.name} (PyPDF2 not available)"
        
        try:
            reader = PdfReader(str(file_path))
            text_parts = []
            
            # Extract from first few pages
            for page_num, page in enumerate(reader.pages[:10]):  # First 10 pages
                text_parts.append(page.extract_text())
                if len(''.join(text_parts)) > self.max_text_size:
                    break
                    
            return '\n'.join(text_parts)[:self.max_text_size]
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    def process_docx(self, file_path: Path) -> str:
        """Extract text from DOCX files."""
        if not DOCX_AVAILABLE:
            return f"Word document: {file_path.name} (python-docx not available)"
        
        try:
            doc = Document(str(file_path))
            paragraphs = [p.text for p in doc.paragraphs]
            return '\n'.join(paragraphs)[:self.max_text_size]
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    def process_excel(self, file_path: Path) -> str:
        """Extract data from Excel files."""
        if not EXCEL_AVAILABLE:
            return f"Excel file: {file_path.name} (openpyxl/pandas not available)"
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=0, nrows=100)
            
            # Convert to readable format
            content = f"Excel file: {file_path.name}\n"
            content += f"Shape: {df.shape[0]} rows x {df.shape[1]} columns\n\n"
            content += "Columns:\n"
            content += ", ".join(df.columns) + "\n\n"
            content += "Sample data:\n"
            content += df.head(20).to_string()
            
            return content[:self.max_text_size]
        except Exception as e:
            return f"Error reading Excel: {str(e)}"
    
    def process_json(self, file_path: Path) -> str:
        """Extract and format JSON content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            formatted = json.dumps(data, indent=2)
            return formatted[:self.max_text_size]
        except Exception as e:
            return f"Error reading JSON: {str(e)}"
