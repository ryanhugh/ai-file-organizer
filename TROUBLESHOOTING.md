# Troubleshooting Guide

Common issues and solutions for the File Organizer.

## Installation Issues

### "Ollama is not running"

**Symptoms:**
```
RuntimeError: Ollama is not running. Please install and start Ollama
```

**Solutions:**
1. Start Ollama service:
   ```bash
   ollama serve
   ```
   Keep this terminal open while organizing files.

2. Verify Ollama is running:
   ```bash
   ollama list
   ```

### "Model not found"

**Symptoms:**
```
Error: model 'llama3.2:3b' not found
```

**Solutions:**
1. Download the model:
   ```bash
   ollama pull llama3.2:3b
   ```

2. List available models:
   ```bash
   ollama list
   ```

3. Use a different model:
   ```bash
   python main.py ~/Downloads -o ~/Organized --model llama3.2:1b
   ```

### Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'ollama'
```

**Solutions:**
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Use pip3 if needed:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Runtime Issues

### Slow Processing

**Symptoms:**
- Takes a long time to process files
- Each file takes 5-10 seconds

**Solutions:**
1. Use a smaller, faster model:
   ```bash
   python main.py ~/Downloads -o ~/Organized --model llama3.2:1b
   ```

2. Process fewer files at once:
   ```bash
   python main.py ~/Downloads -o ~/Organized --max-files 20
   ```

3. Ensure Ollama is running locally (not in Docker)

4. Check system resources (CPU/RAM usage)

### "Permission Denied" Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
1. Check file permissions:
   ```bash
   ls -la /path/to/file
   ```

2. Run with appropriate permissions (avoid sudo if possible)

3. Choose a different output directory where you have write access

4. Check if files are in use by another program

### "File Already Exists" Warnings

**Symptoms:**
- Files with `_1`, `_2` suffixes
- Warnings about duplicate files

**Solutions:**
This is normal behavior! The organizer automatically handles name conflicts by adding numbers.

To avoid this:
1. Use a fresh output directory
2. Or manually review and remove duplicates first

### Out of Memory

**Symptoms:**
```
MemoryError: Unable to allocate array
```

**Solutions:**
1. Process files in smaller batches:
   ```bash
   python main.py ~/Downloads -o ~/Organized --max-files 50
   ```

2. Use a smaller model:
   ```bash
   python main.py ~/Downloads -o ~/Organized --model llama3.2:1b
   ```

3. Close other applications to free up RAM

## File Extraction Issues

### PDF Extraction Fails

**Symptoms:**
```
Error reading PDF: ...
```

**Solutions:**
1. Install/reinstall PyPDF2:
   ```bash
   pip install --upgrade PyPDF2
   ```

2. The file may be corrupted or password-protected
3. The organizer will still categorize based on filename

### DOCX Extraction Fails

**Symptoms:**
```
Error reading DOCX: ...
```

**Solutions:**
1. Install/reinstall python-docx:
   ```bash
   pip install --upgrade python-docx
   ```

2. File may be corrupted or in old .doc format
3. Consider converting .doc to .docx

### Image Metadata Extraction Fails

**Symptoms:**
```
Error extracting image metadata
```

**Solutions:**
1. Install/reinstall Pillow:
   ```bash
   pip install --upgrade Pillow
   ```

2. Image may be corrupted
3. Organizer will still categorize the image file

## Categorization Issues

### All Files Go to "Uncategorized"

**Symptoms:**
- Most/all files end up in "Uncategorized" folder

**Possible Causes:**
1. LLM is not responding correctly
2. Model is too small/not suitable
3. File contents are not being extracted

**Solutions:**
1. Check Ollama is running:
   ```bash
   ollama list
   ```

2. Try a larger model:
   ```bash
   python main.py ~/Downloads -o ~/Organized --model llama3.1:8b
   ```

3. Run with `--dry-run` and check the output

4. Verify files have readable content

### Files Not Matching Projects

**Symptoms:**
- Files that should match projects don't
- All files go to generic categories

**Solutions:**
1. Check project README files are readable:
   ```bash
   cat ~/Projects/MyProject/README.md
   ```

2. Ensure README files have good descriptions

3. Make project descriptions more specific

4. Try with a larger model for better understanding

### Strange Category Names

**Symptoms:**
- Categories like "Category_123" or garbled names

**Solutions:**
1. This is rare but can happen with small models
2. Try a larger model
3. Manually rename categories after organization

## Performance Optimization

### Speed Up Processing

1. **Use smaller model:**
   ```bash
   ollama pull llama3.2:1b
   python main.py ~/Downloads -o ~/Organized --model llama3.2:1b
   ```

2. **Process in batches:**
   ```bash
   # First 100 files
   python main.py ~/Downloads -o ~/Organized --max-files 100
   
   # Next 100 files (move organized files first)
   python main.py ~/Downloads -o ~/Organized --max-files 100
   ```

3. **Skip recursive scanning:**
   ```bash
   # Don't use -r flag unless needed
   python main.py ~/Downloads -o ~/Organized
   ```

### Reduce Memory Usage

1. Process fewer files at once
2. Use smaller model
3. Close other applications
4. Restart Ollama if it's using too much memory:
   ```bash
   pkill ollama
   ollama serve
   ```

## Validation & Testing

### Test Before Organizing

Always use dry run first:
```bash
python main.py ~/Downloads -o ~/Organized --dry-run
```

This shows what would happen without moving files.

### Test with Small Batch

Start with a few files:
```bash
python main.py ~/Downloads -o ~/Organized --max-files 5 --dry-run
```

### Verify Output

After organizing, check:
1. `ORGANIZATION_REPORT.md` - Summary of what was done
2. Category README files - Descriptions of each category
3. Files are in correct locations

## Getting Help

### Check Logs

Look for error messages in the terminal output.

### Verify Setup

```bash
# Check Python version (need 3.8+)
python3 --version

# Check Ollama
ollama --version
ollama list

# Check dependencies
pip list | grep -E "ollama|docx|PyPDF2|pillow"
```

### Debug Mode

Add print statements to see what's happening:
```python
# In llm_categorizer.py, add:
print(f"Prompt: {prompt}")
print(f"Response: {response}")
```

### Common Command Issues

**Wrong:**
```bash
python main.py ~/Downloads ~/Organized  # Missing -o flag
```

**Right:**
```bash
python main.py ~/Downloads -o ~/Organized
```

**Wrong:**
```bash
python main.py ~/Downloads -o ~/Downloads  # Same directory
```

**Right:**
```bash
python main.py ~/Downloads -o ~/Downloads/Organized
```

## Still Having Issues?

1. Check all prerequisites are installed
2. Run the setup script: `./setup.sh`
3. Try the example script: `python example_usage.py`
4. Review the [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md)
5. Check Ollama documentation: https://ollama.ai

## Reporting Bugs

If you find a bug, note:
- Python version
- Ollama version
- Model being used
- Full error message
- Steps to reproduce
