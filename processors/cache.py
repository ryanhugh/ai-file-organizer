"""
Generic file-based caching with process-safe locking.
"""
# Import fix must be first - enables running as both module and script
try:
    from . import _import_fix
except ImportError:
    import _import_fix

import hashlib
import json
from pathlib import Path
from typing import Optional

from filelock import FileLock

from utils import find_project_root


class FileCache:
    """Generic file-based cache with process-safe locking."""
    
    def __init__(self, cache_name: str):
        """
        Initialize cache.
        
        Args:
            cache_name: Name of the cache file (e.g., 'ocr', 'transcription')
        """
        cache_dir = find_project_root() / '.cache'
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = cache_dir / f'{cache_name}.json'
        self.lock_file = cache_dir / f'{cache_name}.json.lock'
        
        # Initialize cache file if it doesn't exist
        if not self.cache_file.exists():
            with FileLock(str(self.lock_file)):
                if not self.cache_file.exists():
                    with open(self.cache_file, 'w', encoding='utf-8') as f:
                        json.dump({}, f)
    
    def get_file_hash(self, file_path: Path) -> str:
        """
        Generate MD5 hash of file contents.
        
        Args:
            file_path: Path to file
            
        Returns:
            MD5 hash of file contents
        """
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        with FileLock(str(self.lock_file)):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    return cache_data.get(key)
            except Exception as e:
                print(f"  Warning: Could not read cache: {str(e)}")
                return None
    
    def set(self, key: str, value: str):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with FileLock(str(self.lock_file)):
            try:
                # Read existing cache
                cache_data = {}
                if self.cache_file.exists():
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                
                # Update cache
                cache_data[key] = value
                
                # Write back
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"  Warning: Could not write cache: {str(e)}")


def cleanup_cache_locks():
    """Clean up all stale cache lock files."""
    cache_dir = find_project_root() / '.cache'
    
    if not cache_dir.exists():
        return
    
    lock_files = list(cache_dir.glob('*.lock'))
    
    if lock_files:
        for lock_file in lock_files:
            try:
                lock_file.unlink()
                print(f"✓ Cleaned up stale lock file: {lock_file.name}")
            except Exception as e:
                print(f"⚠ Warning: Could not remove {lock_file.name}: {e}")
