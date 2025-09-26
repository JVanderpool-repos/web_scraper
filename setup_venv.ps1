# Virtual Environment Setup Script for Web Scraper

Write-Host "🚀 Setting up Web Scraper Virtual Environment" -ForegroundColor Cyan
Write-Host "=" * 50

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created successfully!" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
if (Test-Path "requirements.txt") {
    Write-Host "📋 Installing requirements from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "✅ Requirements installed successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️  requirements.txt not found. Skipping package installation." -ForegroundColor Orange
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host "To activate the virtual environment in the future, run:" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To run examples:" -ForegroundColor Cyan
Write-Host "   python examples\basic_scraper.py" -ForegroundColor White
Write-Host "   python examples\ecommerce_scraper.py" -ForegroundColor White
Write-Host ""
Write-Host "Happy scraping! 🕷️" -ForegroundColor Green