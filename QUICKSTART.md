# Quick Start Guide

Get up and running with the File Organizer in 5 minutes!

## Step 1: Install Ollama

```bash
# Visit https://ollama.ai and download for macOS
# Or use Homebrew:
brew install ollama
```

## Step 2: Start Ollama and Download Model

```bash
# Terminal 1: Start Ollama service
ollama serve

# Terminal 2: Download the model (one-time setup)
ollama pull llama3.2:3b
```

## Step 3: Install Python Dependencies

```bash
cd ryan-file-organizer
pip install -r requirements.txt
```

Or use the automated setup script:

```bash
./setup.sh
```

## Step 4: Run Your First Organization

### Test with Dry Run (Recommended)

```bash
python main.py ~/Downloads -o ~/Downloads/Organized --dry-run --max-files 10
```

This will:
- Scan the first 10 files in your Downloads folder
- Show you how they would be organized
- NOT actually move any files

### Actually Organize Files

Once you're happy with the dry run results:

```bash
python main.py ~/Downloads -o ~/Downloads/Organized --max-files 10
```

## Step 5: Advanced Usage

### With Existing Projects

If you have project folders with README files:

```bash
python main.py ~/Desktop/random-files -o ~/Organized -p ~/Projects
```

### Organize Everything Recursively

```bash
python main.py ~/Documents -o ~/Documents/Organized -r
```

### Move Instead of Copy

```bash
python main.py ~/Downloads -o ~/Organized --move
```

## Common Issues

### "Ollama is not running"
**Solution:** Run `ollama serve` in a separate terminal

### "Model not found"
**Solution:** Run `ollama pull llama3.2:3b`

### Slow processing
**Solution:** Use a smaller model: `--model llama3.2:1b`

## What Gets Created?

After organization, you'll have:

```
Organized/
├── ORGANIZATION_REPORT.md    # Summary of what was organized
├── Category1/
│   ├── README.md             # Description of this category
│   └── files/                # Your organized files
│       ├── file1.txt
│       └── file2.pdf
├── Category2/
│   ├── README.md
│   └── files/
│       └── file3.jpg
```

## Tips

1. **Always dry run first** - Use `--dry-run` to preview
2. **Start small** - Use `--max-files 10` for testing
3. **Copy, don't move** - Default is copy mode (safer)
4. **Check the report** - Read `ORGANIZATION_REPORT.md` after organizing

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Try the [example_usage.py](example_usage.py) script
- Experiment with different models and options

## Need Help?

```bash
python main.py --help
```

Enjoy organizing! 🎉
