# Users API Setup Script for Windows
Write-Host "Setting up Users API project..." -ForegroundColor Cyan

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
. .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -r requirements.txt

# Run tests
Write-Host "Running tests..." -ForegroundColor Green
pytest -xvs tests/

Write-Host "Setup complete!" -ForegroundColor Cyan
Write-Host "To run the local API, use: python -m src.app" -ForegroundColor Yellow
Write-Host "The API will be available at: http://localhost:5000/api/v1/users" -ForegroundColor Yellow