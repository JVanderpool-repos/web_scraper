# Quick activation script for Windows
# Run this file to activate the virtual environment

if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup_venv.ps1 first to create the environment." -ForegroundColor Yellow
    exit 1
}

Write-Host "🔄 Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
Write-Host "You can now run Python scripts with access to all installed packages." -ForegroundColor Cyan
Write-Host ""
Write-Host "Try running an example:" -ForegroundColor Yellow
Write-Host "   python examples\basic_scraper.py" -ForegroundColor White