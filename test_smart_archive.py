#!/usr/bin/env python3
"""
Test intelligent archive processing.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from file_extractor import FileExtractor
from llm_categorizer import LLMCategorizer

# Initialize components
categorizer = LLMCategorizer(model='llama3.2:3b')
extractor = FileExtractor(llm_client=categorizer.client)

# Test on zip files
zip_files = [
    "/Users/ryanhughes/Desktop/file-organizer-test/a zip file.zip",
    "/Users/ryanhughes/Desktop/file-organizer-test/backup of todo.zip",
]

for zip_path in zip_files:
    path = Path(zip_path)
    if not path.exists():
        continue
    
    print(f"\n{'='*70}")
    print(f"Processing: {path.name}")
    print(f"{'='*70}\n")
    
    result = extractor.extract(path)
    print(result['content'])
    print()
