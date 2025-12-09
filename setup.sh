#!/bin/bash

echo "================================================"
echo "File Organizer Setup Script"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed."
    echo ""
    echo "Please install Ollama:"
    echo "  1. Visit https://ollama.ai"
    echo "  2. Download and install for macOS"
    echo "  3. Or use Homebrew: brew install ollama"
    echo ""
    exit 1
fi

echo "✅ Ollama found: $(ollama --version)"
echo ""

# Check if Ollama is running
if ! ollama list &> /dev/null; then
    echo "⚠️  Ollama is not running."
    echo ""
    echo "Starting Ollama service..."
    echo "Please run in a separate terminal: ollama serve"
    echo ""
    read -p "Press Enter once Ollama is running..."
fi

echo "✅ Ollama is running"
echo ""

# Check if model is available
echo "Checking for llama3.2:3b model..."
if ! ollama list | grep -q "llama3.2:3b"; then
    echo "⚠️  Model llama3.2:3b not found."
    echo ""
    read -p "Would you like to download it now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Downloading llama3.2:3b (this may take a few minutes)..."
        ollama pull llama3.2:3b
    else
        echo "You can download it later with: ollama pull llama3.2:3b"
    fi
else
    echo "✅ Model llama3.2:3b found"
fi

echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "================================================"
echo "Setup Complete! 🎉"
echo "================================================"
echo ""
echo "You can now run the file organizer:"
echo "  python3 main.py /path/to/folder -o /path/to/output"
echo ""
echo "For help:"
echo "  python3 main.py --help"
echo ""
echo "For a dry run (no files moved):"
echo "  python3 main.py /path/to/folder -o /path/to/output --dry-run"
echo ""
