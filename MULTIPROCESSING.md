# Multiprocessing Implementation

## Overview

The system now uses **8 parallel processes** to process media files, with **cross-process file locking** for the shared cache.

## Key Changes

### 1. File Locking (`processors/summary.py`)
- **Replaced**: `threading.Lock()` → `FileLock()` from `filelock` library
- **Lock file**: `.cache/summaries.json.lock`
- **Scope**: Works across processes (not just threads)
- **Behavior**: Blocks until lock is acquired, ensures only one process reads/writes cache at a time

### 2. Multiprocessing (`process_desktop_media.py`)
- **Uses**: `multiprocessing.Pool` with 8 worker processes
- **Worker function**: `process_single_file(file_path_str)`
- **Each process creates**:
  - Its own `ollama.Client()`
  - Its own `ImageProcessor` or `VideoTranscriber`
  - Its own EasyOCR reader and Whisper model

### 3. Process Isolation
```python
def process_single_file(file_path_str: str) -> dict:
    # Each process gets its own instances
    llm_client = ollama.Client()
    processor = ImageProcessor(llm_client=llm_client)
    result = processor.process(file_path)
    return result
```

## Benefits

✅ **True parallelism** - Not limited by Python GIL  
✅ **Process isolation** - No shared state conflicts  
✅ **Shared cache** - File locking prevents race conditions  
✅ **Memory efficiency** - OS manages process memory  
✅ **Fault tolerance** - One process crash doesn't affect others

## Performance Characteristics

### Memory Usage
- **Per process**: ~1-2GB (EasyOCR + Whisper model)
- **Total**: ~8-16GB for 8 processes
- **Cache**: Shared, single copy

### Speed
- **Best case**: ~8x speedup for CPU-bound tasks
- **Typical**: ~4-6x speedup (due to I/O, model loading, cache hits)
- **Cache hits**: Near-instant across all processes

### Bottlenecks
1. **Model loading**: First file in each process is slower
2. **File I/O**: Reading large video files
3. **LLM calls**: Ollama server throughput
4. **Cache lock**: Minimal (fast JSON operations)

## Installation

Install the new dependency:
```bash
pip install filelock>=3.12.0
```

Or:
```bash
pip install -r requirements.txt
```

## Usage

Same as before - just run:
```bash
python process_desktop_media.py
```

The script automatically:
1. Scans Desktop for media files
2. Spawns 8 worker processes
3. Distributes files across workers
4. Collects results
5. Writes summary log

## File Locking Details

### Lock Acquisition
```python
with FileLock(str(self.lock_file)):
    # Read or write cache
    # Lock automatically released on exit
```

### Lock File Location
`.cache/summaries.json.lock`

### Timeout
Default: Waits indefinitely (safe for our use case)

### Platform Support
- ✅ macOS (fcntl)
- ✅ Linux (fcntl)
- ✅ Windows (msvcrt)

## Troubleshooting

### "Too many open files"
Increase system limit:
```bash
ulimit -n 4096
```

### Processes hanging
Check for stale lock file:
```bash
rm .cache/summaries.json.lock
```

### Out of memory
Reduce process count in `process_desktop_media.py`:
```python
with Pool(processes=4) as pool:  # Changed from 8 to 4
```
