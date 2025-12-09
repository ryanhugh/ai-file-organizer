#!/usr/bin/env python3
"""
Test all zip files with intelligent processing.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from file_extractor import FileExtractor
from llm_categorizer import LLMCategorizer

# Initialize components
print("Initializing LLM categorizer...")
categorizer = LLMCategorizer(model='llama3.2:3b')
extractor = FileExtractor(llm_client=categorizer.client)

# Test on all zip files
zip_files = [
    "/Users/ryanhughes/Desktop/file-organizer-test/a zip file.zip",
    "/Users/ryanhughes/Desktop/file-organizer-test/backup of todo.zip",
    "/Users/ryanhughes/Desktop/file-organizer-test/back up of company data.zip",
]

for zip_path in zip_files:
    path = Path(zip_path)
    if not path.exists():
        print(f"File not found: {zip_path}")
        continue
    
    print(f"\n{'='*70}")
    print(f"Processing: {path.name}")
    print(f"{'='*70}\n")
    
    result = extractor.extract(path)
    
    # Print just the first 2000 characters to keep it readable
    content = result['content']
    if len(content) > 2000:
        print(content[:2000])
        print(f"\n... (truncated, total length: {len(content)} chars)")
    else:
        print(content)
    
    print()
