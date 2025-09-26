#!/bin/bash
# Quick activation script for Linux/Mac
# Run: source activate.sh

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup_venv.sh first to create the environment."
    exit 1
fi

echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "You can now run Python scripts with access to all installed packages."
echo ""
echo "Try running an example:"
echo "   python examples/basic_scraper.py"