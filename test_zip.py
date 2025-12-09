#!/usr/bin/env python3
"""
Test zip file extraction.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from file_extractor import FileExtractor

# Test on the zip files
zip_files = [
    "/Users/ryanhughes/Desktop/file-organizer-test/a zip file.zip",
    "/Users/ryanhughes/Desktop/file-organizer-test/backup of todo.zip",
    "/Users/ryanhughes/Desktop/file-organizer-test/back up of company data.zip"
]

extractor = FileExtractor()

for zip_path in zip_files:
    path = Path(zip_path)
    if not path.exists():
        print(f"File not found: {zip_path}")
        continue
    
    print(f"\n{'='*70}")
    print(f"Extracting: {path.name}")
    print(f"{'='*70}")
    
    result = extractor.extract(path)
    print(result['content'])
    print()
