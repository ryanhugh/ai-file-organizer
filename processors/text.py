"""
Text file processor.
"""
from pathlib import Path
from typing import Dict, Any
import chardet

from processors.base import MediaProcessor


class TextProcessor(MediaProcessor):
    """Process text files with encoding detection."""
    
    # Comprehensive list of supported text file extensions
    SUPPORTED_EXTENSIONS = {
        # Programming languages
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
        
        # Web technologies
        '.html', '.htm', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
        
        # Data formats
        '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
        
        # Documentation
        '.md', '.markdown', '.rst', '.txt', '.text', '.log',
        
        # Shell scripts
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        
        # Config files
        '.env', '.gitignore', '.dockerignore', '.editorconfig',
        
        # SQL and databases
        '.sql', '.graphql', '.prisma',
        
        # Other common formats
        '.csv', '.tsv', '.properties', '.gradle', '.cmake',
    }
    
    def __init__(self, max_text_size: int = 10_000_000):
        """
        Initialize text processor.
        
        Args:
            max_text_size: Maximum characters to extract (default: 10MB worth of text)
        """
        self.max_text_size = max_text_size
    
    def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a text file and extract its content.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dictionary with success status and summary (extracted text)
        """
        try:
            # Detect encoding
            encoding = 'utf-8'
            with open(file_path, 'rb') as f:
                raw_data = f.read(min(100000, file_path.stat().st_size))
                detected = chardet.detect(raw_data)
                encoding = detected['encoding'] or 'utf-8'
            
            # Read file with detected encoding
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read(self.max_text_size)
            
            # For text files, the "summary" is the full extracted text
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
    # Test text processor
    import sys
    
    processor = TextProcessor()
    
    # Test with a file path from command line or use a default
    if len(sys.argv) > 1:
        test_file = Path(sys.argv[1])
    else:
        # Try to find any text file in Desktop for testing
        desktop = Path.home() / "Desktop"
        test_files = []
        
        # Search for common text file types
        for ext in ['.txt', '.md', '.py', '.js', '.json', '.log']:
            test_files.extend(desktop.glob(f'*{ext}'))
        
        if test_files:
            test_file = test_files[0]
        else:
            print("No test files found on Desktop")
            print("Usage: python text.py <file_path>")
            sys.exit(1)
    
    if not test_file.exists():
        print(f"Error: File not found: {test_file}")
        sys.exit(1)
    
    print(f"Testing TextProcessor with: {test_file.name}")
    print("=" * 80)
    
    # Process the file
    result = processor.process(test_file)
    
    if result['success']:
        content = result['summary']
        print(f"\n✓ Successfully processed {test_file.name}")
        print(f"\nExtracted content ({len(content)} characters):")
        print("-" * 80)
        # Show first 1000 chars for preview
        if len(content) > 1000:
            print(content[:1000])
            print(f"\n... (truncated, total {len(content)} characters)")
        else:
            print(content)
        print("-" * 80)
    else:
        print(f"\n✗ Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)
