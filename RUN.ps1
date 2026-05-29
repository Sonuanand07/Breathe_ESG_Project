# Breathe ESG - Quick Start Script
# This script starts both backend and frontend in separate windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Breathe ESG - Starting Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend setup is done
if (-Not (Test-Path "backend\db.sqlite3")) {
    Write-Host "Database not found! Running setup first..." -ForegroundColor Yellow
    & ".\SETUP.ps1"
}

# Start Backend
Write-Host "Starting Backend (Django on port 8000)..." -ForegroundColor Green
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; venv\Scripts\Activate.ps1; python manage.py runserver"
Start-Sleep -Milliseconds 2000

# Start Frontend
Write-Host "Starting Frontend (React on port 3000)..." -ForegroundColor Green
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Application Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000/api" -ForegroundColor Cyan
Write-Host "Admin: http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host ""
Write-Host "Default Login:" -ForegroundColor Yellow
Write-Host "  Email: analyst@breatheesg.com" -ForegroundColor White
Write-Host "  Password: demo1234" -ForegroundColor White
Write-Host ""
Write-Host "Close this window to stop both services." -ForegroundColor Yellow
