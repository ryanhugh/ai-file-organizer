# Intelligent File Organizer

An AI-powered file organization system that uses a **local LLM** (via Ollama) to intelligently categorize and organize files on your MacBook. The system reads file contents, understands context, and can match files to existing projects or create new categories.

## Features

- 🤖 **Local LLM Processing** - Uses Ollama for privacy-preserving AI categorization
- 📁 **Project Matching** - Automatically matches files to existing projects based on README descriptions
- 📄 **Multi-Format Support** - Handles text, code, PDFs, Word docs, Excel, images, videos, and more
- 🔍 **Content Analysis** - Opens and reads file contents for intelligent categorization
- 📊 **Automatic Reports** - Generates README files and organization reports
- 🎯 **Smart Categorization** - Groups unmatched files into logical categories
- 🔒 **Privacy First** - All processing happens locally on your machine

## Supported File Types

### Documents
- PDF (`.pdf`)
- Microsoft Word (`.docx`, `.doc`)
- Plain text (`.txt`, `.md`, `.rst`, `.log`)
- Excel (`.xlsx`, `.xls`)
- CSV/TSV (`.csv`, `.tsv`)

### Code
- Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, Ruby, PHP, Swift, Kotlin, and more

### Media
- Images: JPG, PNG, GIF, BMP, WebP, TIFF, SVG (with EXIF metadata extraction)
- Videos: MP4, AVI, MOV, MKV, WebM, etc.
- Audio: MP3, WAV, FLAC, AAC, OGG, etc.

### Other
- JSON, XML, HTML
- Archives (ZIP, TAR, etc.)
- And many more...

## Installation

### Prerequisites

1. **Install Ollama**
   ```bash
   # Visit https://ollama.ai and download for macOS
   # Or use Homebrew:
   brew install ollama
   ```

2. **Pull an LLM Model**
   ```bash
   # Recommended: Fast and efficient 3B parameter model
   ollama pull llama3.2:3b
   
   # Alternative: Smaller model for faster processing
   ollama pull llama3.2:1b
   
   # Alternative: Larger model for better accuracy
   ollama pull llama3.1:8b
   ```

3. **Start Ollama Service**
   ```bash
   ollama serve
   ```
   (Keep this running in a separate terminal)

### Install Python Dependencies

```bash
cd ryan-file-organizer
pip install -r requirements.txt
```

## Usage

### Basic Usage

Organize files in a directory:

```bash
python main.py /path/to/messy/folder -o /path/to/organized/output
```

### With Existing Projects

If you have existing projects with README files, the system will match files to them:

```bash
python main.py ~/Downloads -o ~/Organized -p ~/Projects
```

**Project Structure Expected:**
```
~/Projects/
├── ProjectA/
│   ├── README.md          # Description of ProjectA
│   └── files/             # Will be created
├── ProjectB/
│   ├── README.md          # Description of ProjectB
│   └── files/             # Will be created
```

### Advanced Options

```bash
# Dry run (see what would happen without moving files)
python main.py ~/Downloads -o ~/Organized --dry-run

# Move files instead of copying
python main.py ~/Downloads -o ~/Organized --move

# Organize recursively (include subdirectories)
python main.py ~/Documents -o ~/Organized -r

# Use a different model
python main.py ~/Downloads -o ~/Organized --model llama3.1:8b

# Limit number of files (useful for testing)
python main.py ~/Downloads -o ~/Organized --max-files 10
```

### Full Command Reference

```
usage: main.py [-h] -o OUTPUT [-p PROJECTS] [-m MODEL] [-r] [--move] 
               [--dry-run] [--max-files MAX_FILES] source

positional arguments:
  source                Source directory containing files to organize

options:
  -h, --help            Show help message
  -o, --output OUTPUT   Output directory for organized files
  -p, --projects PROJECTS
                        Directory containing existing projects with README files
  -m, --model MODEL     Ollama model to use (default: llama3.2:3b)
  -r, --recursive       Scan subdirectories recursively
  --move                Move files instead of copying them
  --dry-run             Simulate organization without moving/copying files
  --max-files MAX_FILES Maximum number of files to process
```

## How It Works

1. **Scan Files** - Discovers all files in the source directory
2. **Extract Content** - Reads and extracts content from each file based on its type
3. **Load Projects** - Reads README files from existing project folders (if provided)
4. **AI Categorization** - Uses local LLM to:
   - Match files to existing projects based on content similarity
   - Categorize unmatched files into logical groups
5. **Organize** - Creates organized folder structure with README files
6. **Report** - Generates a summary report of the organization

## Output Structure

```
Organized/
├── ORGANIZATION_REPORT.md
├── ProjectA/                    # Matched to existing project
│   ├── README.md
│   └── files/
│       ├── file1.py
│       └── file2.txt
├── Documents/                   # AI-categorized
│   ├── README.md
│   └── files/
│       ├── report.pdf
│       └── notes.docx
├── Images/                      # AI-categorized
│   ├── README.md
│   └── files/
│       ├── photo1.jpg
│       └── screenshot.png
└── Code/                        # AI-categorized
    ├── README.md
    └── files/
        ├── script.py
        └── config.json
```

## Performance Tips

1. **Model Selection**
   - `llama3.2:1b` - Fastest, good for large batches
   - `llama3.2:3b` - Balanced (recommended)
   - `llama3.1:8b` - Most accurate, slower

2. **Batch Processing**
   - Use `--max-files` to test on a small batch first
   - Process large directories in chunks if needed

3. **Dry Run First**
   - Always use `--dry-run` first to preview results
   - Verify the categorization before committing

## Troubleshooting

### "Ollama is not running"
```bash
# Start Ollama in a separate terminal
ollama serve
```

### "Model not found"
```bash
# Pull the model
ollama pull llama3.2:3b
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Slow Processing
- Use a smaller model: `--model llama3.2:1b`
- Process fewer files at once: `--max-files 50`
- Ensure Ollama is running locally (not in a container)

## Privacy & Security

- ✅ All processing happens **locally** on your machine
- ✅ No data is sent to external servers
- ✅ No API keys or cloud services required
- ✅ File contents stay on your computer

## Examples

### Example 1: Organize Downloads Folder
```bash
python main.py ~/Downloads -o ~/Downloads/Organized --dry-run
# Review the output, then run without --dry-run
python main.py ~/Downloads -o ~/Downloads/Organized
```

### Example 2: Match Files to Projects
```bash
# Assuming you have projects in ~/MyProjects/
python main.py ~/Desktop/random-files -o ~/Desktop/Organized -p ~/MyProjects
```

### Example 3: Clean Up Documents Recursively
```bash
python main.py ~/Documents -o ~/Documents/Organized -r --move
```

## License

MIT License - Feel free to use and modify as needed.

## Contributing

This is a personal project, but suggestions and improvements are welcome!
