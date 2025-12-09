#!/usr/bin/env python3
"""
Test zip file extraction with LLM summary.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from file_extractor import FileExtractor
from llm_categorizer import LLMCategorizer

# Initialize components
categorizer = LLMCategorizer(model='llama3.2:3b')
extractor = FileExtractor()

# Test on one zip file
zip_path = Path("/Users/ryanhughes/Desktop/file-organizer-test/a zip file.zip")

print(f"{'='*70}")
print(f"Processing: {zip_path.name}")
print(f"{'='*70}\n")

# Extract archive info
result = extractor.extract(zip_path)
print("Archive Contents:")
print(result['content'])
print()

# Generate summary using LLM
print(f"{'='*70}")
print("Generating Summary with LLM...")
print(f"{'='*70}\n")

prompt = f"""Based on the following archive file information, write a single concise paragraph (2-3 sentences) describing what this archive contains and what it might be used for.

{result['content']}

Summary:"""

response = categorizer.client.generate(
    model='llama3.2:3b',
    prompt=prompt
)

summary = response['response'].strip()

print("📋 Summary:")
print(f"{'-'*70}")
print(summary)
print(f"{'-'*70}")
