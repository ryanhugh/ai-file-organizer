# Project Summary

## What This Is

An intelligent file organization system that uses a **local LLM** (Large Language Model) running on your MacBook to automatically categorize and organize files. It reads file contents, understands context, and can match files to existing projects or create smart categories.

## Key Features

✅ **100% Local Processing** - No cloud, no API keys, complete privacy
✅ **Multi-Format Support** - PDFs, Word docs, Excel, images, videos, code, and more
✅ **Project Matching** - Automatically matches files to existing projects via README descriptions
✅ **Smart Categorization** - AI-powered grouping of unmatched files
✅ **Safe by Default** - Copy mode and dry-run options
✅ **Comprehensive Reports** - Auto-generated README files and organization reports

## Project Structure

```
ryan-file-organizer/
├── main.py                  # Main CLI application
├── file_extractor.py        # Content extraction for various file types
├── llm_categorizer.py       # LLM integration via Ollama
├── project_manager.py       # File organization logic
├── requirements.txt         # Python dependencies
├── setup.sh                 # Automated setup script
├── example_usage.py         # Example/demo script
├── .gitignore              # Git ignore rules
│
├── README.md               # Full documentation
├── QUICKSTART.md           # 5-minute getting started guide
├── ARCHITECTURE.md         # Technical architecture details
├── TROUBLESHOOTING.md      # Common issues and solutions
├── USAGE_EXAMPLES.md       # Real-world usage examples
└── PROJECT_SUMMARY.md      # This file
```

## Quick Start

```bash
# 1. Install Ollama
brew install ollama

# 2. Start Ollama and download model
ollama serve  # In one terminal
ollama pull llama3.2:3b  # In another terminal

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run organizer
python main.py ~/Downloads -o ~/Downloads/Organized --dry-run
```

## How It Works

1. **Scans** files in source directory
2. **Extracts** content from each file (text, metadata, etc.)
3. **Loads** existing project descriptions (if provided)
4. **Categorizes** using local LLM:
   - Matches files to projects based on content similarity
   - Creates categories for unmatched files
5. **Organizes** files into structured folders
6. **Generates** README files and reports

## Technology Stack

- **Python 3.8+** - Core language
- **Ollama** - Local LLM runtime
- **llama3.2:3b** - Default AI model (3 billion parameters)
- **PyPDF2** - PDF text extraction
- **python-docx** - Word document processing
- **Pillow** - Image metadata extraction
- **openpyxl** - Excel file processing
- **chardet** - Text encoding detection

## Supported File Types

### Documents
- PDF, DOCX, DOC, TXT, MD, RST, LOG
- XLSX, XLS, CSV, TSV
- JSON, XML, HTML

### Code
- Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, Ruby, PHP, Swift, Kotlin, and more

### Media
- Images: JPG, PNG, GIF, BMP, WebP, TIFF, SVG
- Videos: MP4, AVI, MOV, MKV, WebM
- Audio: MP3, WAV, FLAC, AAC, OGG

### Other
- Archives: ZIP, TAR, GZ, RAR, 7Z
- Any text-based file format

## Use Cases

1. **Clean up Downloads folder** - Organize random downloads
2. **Project file collection** - Match scattered files to projects
3. **Document organization** - Categorize work documents
4. **Media library** - Organize photos and videos
5. **Code repository cleanup** - Group code files by project
6. **Archive preparation** - Organize before archiving

## Privacy & Security

- ✅ All processing happens on your MacBook
- ✅ No internet connection required (after setup)
- ✅ No data sent to external servers
- ✅ No API keys or cloud services
- ✅ File contents never leave your machine

## Performance

- **Speed:** ~2-5 seconds per file (depends on model and file size)
- **Accuracy:** High for well-described projects and clear file types
- **Scalability:** Can handle thousands of files (process in batches)
- **Resource Usage:** Moderate CPU, low memory

## Model Options

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| llama3.2:1b | 1B params | Fast | Good | Large batches |
| llama3.2:3b | 3B params | Medium | Better | Default use |
| llama3.1:8b | 8B params | Slow | Best | High accuracy |

## Documentation

- **README.md** - Comprehensive documentation (7KB)
- **QUICKSTART.md** - Get started in 5 minutes (2.6KB)
- **ARCHITECTURE.md** - Technical details (7.9KB)
- **TROUBLESHOOTING.md** - Common issues (7.8KB)
- **USAGE_EXAMPLES.md** - Real-world examples (9.5KB)

## Command Examples

```bash
# Basic organization
python main.py ~/Downloads -o ~/Organized

# With existing projects
python main.py ~/Downloads -o ~/Organized -p ~/Projects

# Dry run (preview only)
python main.py ~/Downloads -o ~/Organized --dry-run

# Move instead of copy
python main.py ~/Downloads -o ~/Organized --move

# Recursive (include subdirectories)
python main.py ~/Documents -o ~/Organized -r

# Use different model
python main.py ~/Downloads -o ~/Organized --model llama3.2:1b

# Limit number of files
python main.py ~/Downloads -o ~/Organized --max-files 50
```

## Output Structure

```
Organized/
├── ORGANIZATION_REPORT.md       # Summary report
├── ProjectA/                    # Matched project
│   ├── README.md               # Project description
│   └── files/                  # Organized files
├── Documents/                   # AI category
│   ├── README.md               # Category description
│   └── files/                  # Organized files
└── Images/                      # AI category
    ├── README.md
    └── files/
```

## Development Status

✅ **Complete and Working**
- Core functionality implemented
- Multi-format file support
- LLM integration
- Project matching
- CLI interface
- Comprehensive documentation

🚀 **Potential Enhancements**
- Web UI
- Watch mode (continuous organization)
- Duplicate detection
- Custom categorization rules
- Undo functionality
- Progress bars
- Test suite

## Requirements

### System
- macOS (tested on macOS)
- Python 3.8 or higher
- 4GB+ RAM recommended
- 10GB+ disk space (for Ollama and models)

### Software
- Ollama (https://ollama.ai)
- Python packages (see requirements.txt)

## Installation Time

- **Ollama:** 5 minutes
- **Model download:** 5-10 minutes (depends on internet speed)
- **Python dependencies:** 1-2 minutes
- **Total:** ~15 minutes

## Usage Time

- **Setup per run:** < 1 second
- **Per file processing:** 2-5 seconds
- **100 files:** ~5-10 minutes
- **1000 files:** ~1-2 hours (can batch process)

## File Safety

- ✅ Default mode is **COPY** (originals untouched)
- ✅ Dry run available for preview
- ✅ No file deletion
- ✅ Automatic conflict resolution (numbered duplicates)
- ✅ Validates paths before operations

## Error Handling

- Graceful degradation for unsupported file types
- Continues processing if individual files fail
- Detailed error messages
- Logs errors without stopping

## Testing

```bash
# Run example script
python example_usage.py

# Test with dry run
python main.py ~/Downloads -o ~/test --dry-run --max-files 5

# Run setup script
./setup.sh
```

## License

MIT License - Free to use and modify

## Author Notes

This is a personal project built to solve the problem of messy file organization. It prioritizes:
- **Privacy** - Everything runs locally
- **Safety** - Copy mode by default, dry run available
- **Flexibility** - Multiple options and configurations
- **Usability** - Clear documentation and examples

## Getting Help

1. Read [QUICKSTART.md](QUICKSTART.md) for quick setup
2. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
3. Review [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for examples
4. Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details

## Success Metrics

After running the organizer, you should have:
- ✅ Files organized into logical categories
- ✅ README files describing each category
- ✅ Organization report summarizing the process
- ✅ Original files intact (if using copy mode)
- ✅ Clear folder structure

## Next Steps

1. **Install:** Run `./setup.sh`
2. **Test:** Try with `--dry-run` and `--max-files 5`
3. **Organize:** Run on your actual files
4. **Review:** Check the output and reports
5. **Adjust:** Modify settings as needed

---

**Ready to organize your files?** Start with [QUICKSTART.md](QUICKSTART.md)!
