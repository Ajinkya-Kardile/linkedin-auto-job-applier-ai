Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Setting up linkedin-auto-job-applier-ai (PowerShell) " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Check if Python is installed
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python could not be found." -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher, ensure 'Add to PATH' is checked, and try again." -ForegroundColor Yellow
    Exit
}

Write-Host "✅ Python detected." -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path ".venv")) {
    Write-Host "📦 Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "⚡ Virtual environment already exists." -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
$env:Path = "$PWD\.venv\Scripts;$env:Path"

# Upgrade pip and install dependencies
Write-Host "⬇️ Installing project dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install .

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "To start using the bot, run the following commands:" -ForegroundColor White
Write-Host ".venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "python main.py" -ForegroundColor Yellow
Write-Host "====================================================" -ForegroundColor Cyan