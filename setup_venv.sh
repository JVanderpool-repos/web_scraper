#!/bin/bash

echo "🚀 Setting up Web Scraper Virtual Environment"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created successfully!"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "📋 Installing requirements from requirements.txt..."
    pip install -r requirements.txt
    echo "✅ Requirements installed successfully!"
else
    echo "⚠️  requirements.txt not found. Skipping package installation."
fi

echo ""
echo "🎉 Setup complete!"
echo "To activate the virtual environment in the future, run:"
echo "   source venv/bin/activate"
echo ""
echo "To run examples:"
echo "   python examples/basic_scraper.py"
echo "   python examples/ecommerce_scraper.py"
echo ""
echo "Happy scraping! 🕷️"