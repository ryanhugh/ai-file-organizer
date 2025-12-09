# Caching System

## Overview

The system implements **three-level caching** for expensive operations:

1. **OCR Cache** - Image text extraction results
2. **Transcription Cache** - Video audio transcription + OCR results  
3. **Summary Cache** - LLM-generated summaries

All caches use **MD5 file hashing** and **process-safe file locking**.

## Cache Architecture

### Cache Files Location
```
.cache/
├── ocr.json              # Image OCR results
├── ocr.json.lock         # Lock file for OCR cache
├── transcription.json    # Video transcription results
├── transcription.json.lock
├── summaries.json        # LLM summaries
└── summaries.json.lock
```

### Cache Keys

**OCR & Transcription**: MD5 hash of file contents
- Same file → Same hash → Cache hit
- Modified file → Different hash → Cache miss

**Summaries**: MD5 hash of complete LLM prompt
- Same prompt → Cache hit
- Different prompt → Cache miss (even for same file)

## What Gets Cached

### 1. OCR Cache (`ocr.json`)
**Key**: MD5 hash of image file  
**Value**: Extracted text string  
**Why**: EasyOCR is computationally expensive (~2-5 seconds per image)

### 2. Transcription Cache (`transcription.json`)
**Key**: MD5 hash of video file  
**Value**: JSON object with:
```json
{
  "audio_transcription": "...",
  "ocr_text": "...",
  "language": "en",
  "segments": 42
}
```
**Why**: Whisper transcription is very expensive (~30-60 seconds per video)

### 3. Summary Cache (`summaries.json`)
**Key**: MD5 hash of LLM prompt  
**Value**: Generated summary text  
**Why**: LLM calls take 5-15 seconds and cost API credits

## Cache Behavior

### Cache Hits
```
Image Processing:
1. Hash image file → Check OCR cache
2. If hit: Use cached text (instant)
3. Generate summary (may also hit summary cache)

Video Processing:
1. Hash video file → Check transcription cache
2. If hit: Use cached transcription + OCR (instant)
3. Generate summary (may also hit summary cache)
```

### Cache Misses
```
1. Perform expensive operation (OCR/transcription)
2. Store result in cache
3. Continue processing
```

### Cache Invalidation
- **File modified**: New hash → Automatic cache miss
- **Prompt changed**: New hash → Automatic cache miss  
- **Manual**: Delete `.cache/*.json` files

## Process Safety

### File Locking
```python
with FileLock(str(self.lock_file)):
    # Read or write cache
    # Lock automatically released
```

### Benefits
- ✅ Multiple processes can safely access cache
- ✅ No race conditions
- ✅ No data corruption
- ✅ Automatic lock cleanup on process exit

### Lock Cleanup
At startup, `cleanup_cache_locks()` removes stale locks from crashed processes.

## Performance Impact

### Without Cache
- Image: ~3-8 seconds (OCR + LLM)
- Video: ~40-90 seconds (Whisper + OCR + LLM)

### With Cache (Hit)
- Image: ~0.1-2 seconds (just LLM, or instant if summary cached)
- Video: ~0.1-2 seconds (just LLM, or instant if summary cached)

### Speedup
- **First run**: No speedup (building cache)
- **Subsequent runs**: ~10-50x faster for unchanged files
- **Multiprocessing**: Shared cache across all 8 processes

## Cache Management

### View Cache Stats
```bash
# Check cache sizes
ls -lh .cache/

# Count cached items
cat .cache/ocr.json | jq 'length'
cat .cache/transcription.json | jq 'length'
cat .cache/summaries.json | jq 'length'
```

### Clear Cache
```bash
# Clear all caches
rm .cache/*.json

# Clear specific cache
rm .cache/ocr.json
rm .cache/transcription.json
rm .cache/summaries.json
```

### Clear Lock Files
```bash
# Remove stale locks
rm .cache/*.lock
```

Or use the built-in function:
```python
from processors.cache import cleanup_cache_locks
cleanup_cache_locks()
```

## Implementation Details

### FileCache Class
```python
from processors.cache import FileCache

# Create cache instance
cache = FileCache('my_cache_name')

# Get file hash
file_hash = cache.get_file_hash(Path('/path/to/file'))

# Check cache
result = cache.get(file_hash)
if result is not None:
    # Cache hit
    use_cached_result(result)
else:
    # Cache miss
    result = expensive_operation()
    cache.set(file_hash, result)
```

### Cache Storage Format
All caches use JSON with UTF-8 encoding:
```json
{
  "abc123def456...": "cached value 1",
  "789ghi012jkl...": "cached value 2"
}
```

## Best Practices

1. **Don't cache fast operations** (< 0.5 seconds)
2. **Cache expensive operations** (> 2 seconds)
3. **Use file hashing for file-based operations**
4. **Use prompt hashing for LLM operations**
5. **Clean up locks at startup**
6. **Monitor cache sizes** (can grow large over time)

## Troubleshooting

### "Could not read cache"
- Cache file corrupted → Delete and rebuild
- Permission issues → Check file permissions

### "Could not write cache"
- Disk full → Free up space
- Permission issues → Check directory permissions

### Processes hanging
- Stale lock file → Run `cleanup_cache_locks()`
- Or manually: `rm .cache/*.lock`

### Cache not working
- Check `.cache/` directory exists
- Check cache files are valid JSON
- Check file permissions
