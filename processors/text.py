"""
Text file processor.
"""
from pathlib import Path

try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False


class TextProcessor:
    """Process text files."""
    
    def __init__(self, max_text_size: int = 50000):
        """
        Initialize text processor.
        
        Args:
            max_text_size: Maximum characters to extract
        """
        self.max_text_size = max_text_size
    
    def process(self, file_path: Path) -> str:
        """Extract text from text files with encoding detection."""
        try:
            # Detect encoding
            encoding = 'utf-8'
            if CHARDET_AVAILABLE:
                with open(file_path, 'rb') as f:
                    raw_data = f.read(min(100000, file_path.stat().st_size))
                    detected = chardet.detect(raw_data)
                    encoding = detected['encoding'] or 'utf-8'
            
            # Read file
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read(self.max_text_size)
                
            return content
        except Exception as e:
            return f"Error reading text file: {str(e)}"
