# SkillDCX Startup Script (PowerShell)
# This script starts both frontend and backend services

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " SkillDCX - Blockchain Certificate Platform" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-Not (Test-Path "frontend\.env.local")) {
    Write-Host "⚠️  Warning: frontend\.env.local not found!" -ForegroundColor Yellow
    Write-Host "   Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item "frontend\.env.example" "frontend\.env.local"
    Write-Host "   ✓ Created frontend\.env.local" -ForegroundColor Green
    Write-Host "   Please configure it with your settings" -ForegroundColor Yellow
    Write-Host ""
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js detected: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting SkillDCX services..." -ForegroundColor Cyan
Write-Host ""

# Function to start backend
$backendScript = {
    Write-Host "🚀 Starting Backend (FastAPI)..." -ForegroundColor Magenta
    Set-Location backend
    uvicorn main:app --reload
}

# Function to start frontend
$frontendScript = {
    Start-Sleep -Seconds 3
    Write-Host "🚀 Starting Frontend (Next.js)..." -ForegroundColor Blue
    Set-Location frontend
    npm run dev
}

# Start both services in separate windows
Write-Host "Opening backend terminal..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Write-Host "Opening frontend terminal..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Services Starting..." -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in the terminal windows to stop services" -ForegroundColor Gray
Write-Host ""
