# 🎯 START HERE

Welcome to the **Intelligent File Organizer**! This tool uses AI running locally on your MacBook to automatically organize your messy files.

## 🚀 Quick Start (5 Minutes)

### 1. Install Ollama
```bash
# Visit https://ollama.ai or use Homebrew
brew install ollama
```

### 2. Setup
```bash
# Run the automated setup script
./setup.sh
```

### 3. Test It Out
```bash
# Try organizing a few files (dry run - safe!)
python main.py ~/Downloads -o ~/test_output --dry-run --max-files 5
```

### 4. Organize For Real
```bash
# Once you're happy with the test results
python main.py ~/Downloads -o ~/Downloads/Organized
```

## 📚 Documentation Guide

**New to this project?** Read in this order:

1. **[QUICKSTART.md](QUICKSTART.md)** ← Start here for setup
2. **[README.md](README.md)** ← Full documentation
3. **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** ← Real-world examples

**Having issues?**
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** ← Common problems & solutions

**Want to understand how it works?**
- **[WORKFLOW.md](WORKFLOW.md)** ← Visual workflow diagrams
- **[ARCHITECTURE.md](ARCHITECTURE.md)** ← Technical details
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** ← Complete overview

## ✨ What This Does

```
BEFORE:                          AFTER:
~/Downloads/                     ~/Downloads/Organized/
├── report.pdf                   ├── ProjectA/
├── script.py                    │   └── files/
├── photo.jpg                    │       └── report.pdf
├── notes.docx                   ├── Code/
├── data.json                    │   └── files/
├── random_file.txt              │       └── script.py
└── ...100 more files            ├── Images/
                                 │   └── files/
                                 │       └── photo.jpg
                                 └── Documents/
                                     └── files/
                                         ├── notes.docx
                                         └── random_file.txt
```

## 🔑 Key Features

- ✅ **100% Private** - Everything runs locally on your Mac
- ✅ **Smart AI** - Understands file content, not just names
- ✅ **Multi-Format** - PDFs, Word, Excel, images, videos, code, etc.
- ✅ **Project Matching** - Matches files to your existing projects
- ✅ **Safe** - Copy mode by default, dry-run available
- ✅ **Fast** - Processes 100 files in ~5-10 minutes

## 🎮 Common Commands

```bash
# Basic organization
python main.py ~/Downloads -o ~/Organized

# With existing projects
python main.py ~/Downloads -o ~/Organized -p ~/Projects

# Preview first (safe!)
python main.py ~/Downloads -o ~/Organized --dry-run

# Faster processing
python main.py ~/Downloads -o ~/Organized --model llama3.2:1b

# Help
python main.py --help
```

## 📁 Project Files

### Core Files (Python)
- `main.py` - Main application
- `file_extractor.py` - Extracts content from files
- `llm_categorizer.py` - AI categorization
- `project_manager.py` - File organization logic

### Documentation
- `START_HERE.md` - This file
- `QUICKSTART.md` - 5-minute setup guide
- `README.md` - Complete documentation
- `WORKFLOW.md` - Visual diagrams
- `USAGE_EXAMPLES.md` - Real examples
- `TROUBLESHOOTING.md` - Problem solving
- `ARCHITECTURE.md` - Technical details
- `PROJECT_SUMMARY.md` - Overview

### Setup
- `requirements.txt` - Python dependencies
- `setup.sh` - Automated setup script
- `example_usage.py` - Demo script

## ⚡ Troubleshooting Quick Fixes

### "Ollama is not running"
```bash
ollama serve
```

### "Model not found"
```bash
ollama pull llama3.2:3b
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### Too slow?
```bash
python main.py ~/folder -o ~/output --model llama3.2:1b
```

## 🎯 Use Cases

1. **Clean Downloads folder** - Organize random downloads
2. **Project organization** - Match files to projects
3. **Document management** - Categorize work documents
4. **Media library** - Organize photos/videos
5. **Code cleanup** - Group code files by project

## 🔒 Privacy

- ✅ All processing happens on YOUR MacBook
- ✅ No internet required (after setup)
- ✅ No cloud services
- ✅ No API keys needed
- ✅ Your files never leave your computer

## 📊 Performance

- **Speed:** ~2-5 seconds per file
- **Accuracy:** High for clear file types
- **Scale:** Can handle thousands of files
- **Resources:** Moderate CPU, low memory

## 🛠️ Requirements

- macOS
- Python 3.8+
- Ollama
- 4GB+ RAM
- 10GB+ disk space

## 🎓 Learning Path

### Beginner
1. Run `./setup.sh`
2. Try `python main.py ~/Downloads -o ~/test --dry-run --max-files 5`
3. Read [QUICKSTART.md](QUICKSTART.md)

### Intermediate
1. Organize with projects: `-p ~/Projects`
2. Try different models: `--model llama3.2:1b`
3. Read [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)

### Advanced
1. Batch processing large folders
2. Customize categorization prompts
3. Read [ARCHITECTURE.md](ARCHITECTURE.md)

## 💡 Tips

1. **Always dry-run first** - Use `--dry-run` to preview
2. **Start small** - Use `--max-files 10` for testing
3. **Copy, don't move** - Default is safer (copy mode)
4. **Check reports** - Review `ORGANIZATION_REPORT.md`
5. **Good project READMEs** - Better descriptions = better matching

## 🚨 Important Notes

- Default mode **copies** files (originals stay safe)
- Use `--move` only if you're sure
- Always test with `--dry-run` first
- Check the output before deleting originals

## 🎉 Ready to Start?

```bash
# 1. Setup (one-time)
./setup.sh

# 2. Test with a few files
python main.py ~/Downloads -o ~/test --dry-run --max-files 5

# 3. Organize for real
python main.py ~/Downloads -o ~/Downloads/Organized

# 4. Check the results
open ~/Downloads/Organized
cat ~/Downloads/Organized/ORGANIZATION_REPORT.md
```

## 📞 Need Help?

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Read [QUICKSTART.md](QUICKSTART.md)
3. Review [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
4. Run `python main.py --help`

## 📈 Next Steps

After your first successful organization:
1. Review the organized files
2. Check category README files
3. Adjust settings as needed
4. Set up regular organization (weekly/monthly)

---

**Ready?** → Start with [QUICKSTART.md](QUICKSTART.md)

**Questions?** → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Examples?** → See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)

---

**Let's organize your files! 🚀**
