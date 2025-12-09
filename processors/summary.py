"""
Summary generation with caching support.
"""
# Import fix must be first - enables running as both module and script
try:
    from . import _import_fix
except ImportError:
    import _import_fix

import hashlib
import json
import sys
from pathlib import Path
from typing import Optional, Dict

from filelock import FileLock

from utils import find_project_root


class SummaryGenerator:
    """Generate summaries using LLM with caching."""
    
    def __init__(self, llm_client=None):
        """
        Initialize the summary generator.
        
        Args:
            llm_client: Ollama client for generating summaries
        """
        self.llm_client = llm_client
        
        # Set up cache file path
        cache_dir = find_project_root() / '.cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_dir / 'summaries.json'
        self.lock_file = cache_dir / 'summaries.json.lock'
        print('using cache file:', self.cache_file)
        
        # Initialize cache file if it doesn't exist
        if not self.cache_file.exists():
            with FileLock(str(self.lock_file)):
                # Double-check after acquiring lock
                if not self.cache_file.exists():
                    with open(self.cache_file, 'w', encoding='utf-8') as f:
                        json.dump({}, f)
    
    def _get_cache_key(self, prompt: str) -> str:
        """
        Generate a cache key from the prompt.
        
        Args:
            prompt: The LLM prompt to hash
            
        Returns:
            MD5 hash of the prompt
        """
        return hashlib.md5(prompt.encode('utf-8')).hexdigest()
    
    def _read_cache(self, cache_key: str) -> Optional[str]:
        """
        Read summary from cache (process-safe with file locking).
        
        Args:
            cache_key: Cache key to look up
            
        Returns:
            Cached summary or None if not found
        """
        with FileLock(str(self.lock_file)):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    return cache_data.get(cache_key)
            except Exception as e:
                print(f"  Warning: Could not read cache: {str(e)}")
                return None
    
    def _write_cache(self, cache_key: str, summary: str):
        """
        Write summary to cache (process-safe with file locking).
        
        Args:
            cache_key: Cache key
            summary: Summary to cache
        """
        with FileLock(str(self.lock_file)):
            try:
                # Read existing cache
                cache_data = {}
                if self.cache_file.exists():
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                
                # Update cache
                cache_data[cache_key] = summary
                
                # Write back
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"  Warning: Could not write cache: {str(e)}")
    
    def generate(self, prompt: str) -> str:
        """
        Generate a summary using LLM with caching.
        
        Args:
            prompt: The complete prompt to send to the LLM
            
        Returns:
            Generated summary text
        """
        if not self.llm_client:
            return ""
        
        if not prompt or not prompt.strip():
            return ""
        
        try:
            # Step 1: Generate cache key from the complete prompt
            cache_key = self._get_cache_key(prompt)
            
            # Step 2: Check cache - if exists, return and exit early
            cached_summary = self._read_cache(cache_key)
            if cached_summary is not None:
                print(f"  ✓ Using cached summary")
                return cached_summary
            
            # Step 3: Run the LLM to generate output
            response = self.llm_client.generate(
                model='llama3.2:3b',
                prompt=prompt
            )
            
            summary = response['response'].strip()
            
            # Step 4: Store in cache
            self._write_cache(cache_key, summary)
            
            return summary
            
        except Exception as e:
            print(f"  Warning: Could not generate summary: {str(e)}")
            return ""


if __name__ == '__main__':
    """Test the summary generator with caching."""
    import tempfile
    
    # Create a mock LLM client for testing
    class MockLLMClient:
        def __init__(self):
            self.call_count = 0
        
        def generate(self, model, prompt):
            self.call_count += 1
            return {
                'response': f"This is a test summary (call #{self.call_count})"
            }
    
    # Use a temporary directory for cache
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir) / 'test_cache'
        
        print("Testing SummaryGenerator with caching...")
        print("=" * 70)
        
        # Create mock client and generator
        mock_client = MockLLMClient()
        generator = SummaryGenerator(llm_client=mock_client)
        
        test_prompt = "Summarize this: The quick brown fox jumps over the lazy dog."
        
        # First call - should generate and cache
        print("\n1. First call (should generate new summary):")
        summary1 = generator.generate(test_prompt)
        print(f"   Result: {summary1}")
        print(f"   LLM calls so far: {mock_client.call_count}")
        
        # Second call with same prompt - should use cache
        print("\n2. Second call with same prompt (should use cache):")
        summary2 = generator.generate(test_prompt)
        print(f"   Result: {summary2}")
        print(f"   LLM calls so far: {mock_client.call_count}")
        
        # Third call with different prompt - should generate new
        print("\n3. Third call with different prompt (should generate new):")
        different_prompt = "Summarize this: A different piece of text entirely."
        summary3 = generator.generate(different_prompt)
        print(f"   Result: {summary3}")
        print(f"   LLM calls so far: {mock_client.call_count}")
        
        # Verify caching worked
        print("\n" + "=" * 70)
        print("Test Results:")
        print(f"  ✓ Cache hit: {summary1 == summary2}")
        print(f"  ✓ Cache miss for different prompt: {summary1 != summary3}")
        print(f"  ✓ LLM called only twice (not three times): {mock_client.call_count == 2}")
        print(f"  ✓ Cache file exists: {generator.cache_file.exists()}")
        
        # Check cache file contents
        with open(generator.cache_file, 'r') as f:
            cache_contents = json.load(f)
            print(f"  ✓ Cache entries: {len(cache_contents)} entries")
            print(f"  ✓ Cache is a dictionary: {isinstance(cache_contents, dict)}")
        
        if summary1 == summary2 and mock_client.call_count == 2 and len(cache_contents) == 2:
            print("\n✅ All tests passed! Caching is working correctly.")
        else:
            print("\n❌ Tests failed! Check the implementation.")
