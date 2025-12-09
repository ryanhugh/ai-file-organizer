# Architecture Overview

## Base Class Pattern

All media processors inherit from `MediaProcessor` base class:

```python
class MediaProcessor(ABC):
    """Abstract base class for media file processors."""
    
    @property
    @abstractmethod
    def SUPPORTED_EXTENSIONS(self) -> Set[str]:
        """Return set of supported file extensions."""
        pass
    
    @abstractmethod
    def process(self, file_path: Path) -> Dict[str, Any]:
        """Process a media file and return results."""
        pass
```

## Processor Implementations

### ImageProcessor
- **Inherits from**: `MediaProcessor`
- **Main method**: `process(file_path)` 
- **Returns**: `{'success': bool, 'summary': str, 'error': str (optional)}`
- **Summary format**: One paragraph + metadata (dimensions, format, EXIF)

### VideoTranscriber
- **Inherits from**: `MediaProcessor`
- **Main method**: `process(file_path, max_duration=300)`
- **Returns**: `{'success': bool, 'summary': str, 'error': str (optional)}`
- **Summary format**: One paragraph + metadata (duration, format)

## File-Type Agnostic Processing

`process_desktop_media.py` is completely agnostic to file types:

1. **Processor registration**: Builds `ext_to_processor` mapping from `SUPPORTED_EXTENSIONS`
2. **File discovery**: Finds all files matching any registered extension
3. **Processing**: Calls `processor.process(file_path)` for each file
4. **Result handling**: Treats all results uniformly (just filename + summary text)

### Benefits

- **Extensibility**: Add new processor types without changing main script
- **Consistency**: All processors follow same interface
- **Simplicity**: Main script doesn't need to know about images vs videos
- **Maintainability**: File-type specific logic stays in processor classes

## Adding New Processor Types

To add a new media type (e.g., audio, documents):

1. Create new processor class inheriting from `MediaProcessor`
2. Define `SUPPORTED_EXTENSIONS` class attribute
3. Implement `process(file_path)` method returning standard format
4. Add instance to `processors` list in `process_desktop_media.py`

That's it! No other changes needed

This document explains how the file organizer works internally.

## System Components

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│              (CLI & Orchestration)                      │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│file_extractor│  │llm_categorizer│  │project_manager│
│    .py       │  │     .py       │  │     .py       │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
   File System        Ollama API        File System
```

## Module Responsibilities

### 1. `main.py` - Orchestration
- CLI argument parsing
- Workflow coordination
- Progress reporting
- Error handling

**Key Class:** `FileOrganizer`

### 2. `file_extractor.py` - Content Extraction
- Detects file types
- Extracts text content from various formats
- Handles binary files gracefully
- Extracts metadata (EXIF, etc.)

**Key Class:** `FileExtractor`

**Supported Formats:**
- Text: TXT, MD, RST, LOG
- Documents: PDF, DOCX, DOC
- Spreadsheets: XLSX, XLS, CSV
- Code: PY, JS, TS, JAVA, CPP, etc.
- Images: JPG, PNG, GIF, etc. (metadata only)
- Videos/Audio: MP4, MP3, etc. (metadata only)

### 3. `llm_categorizer.py` - AI Categorization
- Interfaces with Ollama
- Matches files to projects
- Generates category names
- Handles LLM responses

**Key Class:** `LLMCategorizer`

**Methods:**
- `match_to_project()` - Match file to existing project
- `categorize_file()` - Generate category for unmatched file
- `batch_categorize()` - Process multiple files efficiently

### 4. `project_manager.py` - File Organization
- Loads existing projects
- Creates directory structure
- Moves/copies files
- Generates README files
- Creates reports

**Key Class:** `ProjectManager`

## Workflow

### Phase 1: Discovery
```
1. Scan source directory
2. Filter out system files (.DS_Store, etc.)
3. Load existing project READMEs (if provided)
```

### Phase 2: Extraction
```
For each file:
  1. Detect file type
  2. Extract content (up to 50KB)
  3. Extract metadata
  4. Store in file_info dict
```

### Phase 3: Categorization
```
For each file:
  1. Try to match to existing project
     - Build prompt with file content + project descriptions
     - Ask LLM for best match
     - Parse response
  
  2. If no project match:
     - Build categorization prompt
     - Ask LLM for category name
     - Sanitize category name
  
  3. Add to categorized dict
```

### Phase 4: Organization
```
For each category:
  1. Create category directory
  2. Create files subdirectory
  3. Generate README.md
  4. Copy/move files to files/
  5. Handle name conflicts
```

### Phase 5: Reporting
```
1. Generate ORGANIZATION_REPORT.md
2. Print summary statistics
3. Show output location
```

## LLM Prompting Strategy

### Project Matching Prompt
```
Input:
  - File name, type, extension
  - First 1000 chars of content
  - List of projects with descriptions

Output:
  - Project number (1-N) or "NONE"

Temperature: 0.1 (low for consistency)
```

### Categorization Prompt
```
Input:
  - File name, type, extension
  - First 800 chars of content

Output:
  - Short category name (1-3 words)

Temperature: 0.1 (low for consistency)
```

## File Organization Structure

### Output Directory Layout
```
output_dir/
├── ORGANIZATION_REPORT.md
├── ProjectA/                    # Matched project
│   ├── README.md               # From projects_dir
│   └── files/                  # Created by organizer
│       ├── file1.py
│       └── file2.txt
├── Documents/                   # AI category
│   ├── README.md               # Generated
│   └── files/
│       └── report.pdf
└── Images/                      # AI category
    ├── README.md               # Generated
    └── files/
        └── photo.jpg
```

## Performance Considerations

### File Extraction
- Limits text extraction to 50KB per file
- Reads only first 10 pages of PDFs
- Handles large files gracefully
- Uses encoding detection for text files

### LLM Processing
- Processes files sequentially (one at a time)
- Uses low temperature for consistent results
- Limits prompt size to prevent token overflow
- Caches project descriptions

### Optimization Opportunities
1. **Batch LLM requests** - Could process multiple files in one prompt
2. **Parallel extraction** - Could extract file content in parallel
3. **Smart caching** - Could cache similar file categorizations
4. **Progressive processing** - Could show results as they complete

## Error Handling

### File Extraction Errors
- Gracefully degrades to filename-only analysis
- Logs errors but continues processing
- Returns error message in content field

### LLM Errors
- Falls back to "Uncategorized" category
- Retries not implemented (could be added)
- Logs errors for debugging

### File System Errors
- Handles name conflicts with numbering
- Validates paths before operations
- Creates directories as needed

## Extension Points

### Adding New File Types
1. Add extension to `FileExtractor._extract()` switch
2. Implement extraction method
3. Add to supported types in README

### Custom Categorization Logic
1. Modify `LLMCategorizer._build_categorization_prompt()`
2. Adjust temperature/parameters
3. Add post-processing rules

### Alternative LLM Backends
1. Create new class implementing same interface
2. Replace `LLMCategorizer` initialization
3. Maintain same method signatures

## Testing Strategy

### Unit Tests (Not Implemented)
- Test file extraction for each type
- Test LLM prompt building
- Test path sanitization
- Test conflict resolution

### Integration Tests (Not Implemented)
- Test full workflow with sample files
- Test project matching accuracy
- Test error handling

### Manual Testing
- Use `--dry-run` for safe testing
- Use `--max-files` for quick tests
- Use `example_usage.py` for demos

## Security Considerations

### Privacy
- All processing is local
- No data sent to external servers
- Ollama runs on localhost

### File Safety
- Default mode is COPY (not move)
- Dry run available for preview
- No file deletion
- Handles conflicts safely

### Input Validation
- Validates directory paths
- Prevents source == output
- Sanitizes folder names
- Filters system files

## Future Enhancements

### Potential Features
1. **Undo functionality** - Track operations for rollback
2. **Watch mode** - Continuously organize new files
3. **Custom rules** - User-defined categorization rules
4. **Web UI** - Browser-based interface
5. **Duplicate detection** - Find and handle duplicates
6. **Compression** - Automatically compress old files
7. **Cloud sync** - Optional cloud backup
8. **Smart search** - Search organized files by content

### Performance Improvements
1. Parallel processing
2. Incremental organization
3. Smart caching
4. Batch LLM requests

### Quality Improvements
1. Comprehensive test suite
2. Better error messages
3. Progress bars
4. Logging system
5. Configuration files
