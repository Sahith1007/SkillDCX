# SkillDCX - Run All Tests
# This script starts the backend and runs tests automatically

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           SkillDCX Certificate NFT System - Test Runner          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Set error action
$ErrorActionPreference = "Continue"

# Store original location
$originalLocation = Get-Location

# Function to cleanup on exit
function Cleanup {
    Write-Host "`n`n[Cleanup] Stopping all processes..." -ForegroundColor Yellow
    
    # Kill backend if running
    if ($backendProcess -and !$backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "[Cleanup] Backend stopped" -ForegroundColor Yellow
    }
    
    # Return to original location
    Set-Location $originalLocation
    
    Write-Host "[Cleanup] Done!" -ForegroundColor Green
}

# Register cleanup on exit
Register-EngineEvent PowerShell.Exiting -Action { Cleanup } | Out-Null

try {
    # Step 1: Check if backend directory exists
    Write-Host "[1/5] Checking backend directory..." -ForegroundColor Cyan
    
    if (!(Test-Path "backend")) {
        Write-Host "ERROR: backend directory not found!" -ForegroundColor Red
        Write-Host "Make sure you're running this from: C:\Users\Sahith\OneDrive\Desktop\SkillDCX" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "  ✓ Backend directory found" -ForegroundColor Green
    
    # Step 2: Check if node_modules exists
    Write-Host "`n[2/5] Checking backend dependencies..." -ForegroundColor Cyan
    
    if (!(Test-Path "backend\node_modules")) {
        Write-Host "  Installing backend dependencies..." -ForegroundColor Yellow
        Set-Location backend
        npm install
        Set-Location ..
    } else {
        Write-Host "  ✓ Dependencies already installed" -ForegroundColor Green
    }
    
    # Step 3: Start backend in background
    Write-Host "`n[3/5] Starting backend server..." -ForegroundColor Cyan
    
    Set-Location backend
    
    # Start backend as a background job
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        npm start
    }
    
    Set-Location ..
    
    Write-Host "  ✓ Backend starting (Job ID: $($backendJob.Id))" -ForegroundColor Green
    Write-Host "  Waiting for backend to be ready..." -ForegroundColor Yellow
    
    # Wait for backend to start (check port 8000)
    $maxAttempts = 30
    $attempt = 0
    $backendReady = $false
    
    while ($attempt -lt $maxAttempts -and !$backendReady) {
        $attempt++
        Start-Sleep -Seconds 1
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 2 -ErrorAction SilentlyContinue
            $backendReady = $true
            Write-Host "  ✓ Backend is ready!" -ForegroundColor Green
        } catch {
            Write-Host "  Attempt $attempt/$maxAttempts..." -ForegroundColor DarkGray -NoNewline
            Write-Host "`r" -NoNewline
        }
    }
    
    if (!$backendReady) {
        Write-Host "`n  WARNING: Backend didn't respond after 30 seconds" -ForegroundColor Yellow
        Write-Host "  Continuing with tests anyway..." -ForegroundColor Yellow
    }
    
    # Step 4: Check Python and dependencies
    Write-Host "`n[4/5] Checking Python environment..." -ForegroundColor Cyan
    
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "  ERROR: Python not found!" -ForegroundColor Red
        Write-Host "  Install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
        throw "Python not installed"
    }
    
    # Check if required Python packages are installed
    $requiredPackages = @("algosdk", "requests", "pyteal")
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        $result = python -c "import $package" 2>&1
        if ($LASTEXITCODE -ne 0) {
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host "  Installing missing Python packages: $($missingPackages -join ', ')" -ForegroundColor Yellow
        pip install $missingPackages
    } else {
        Write-Host "  ✓ All Python packages installed" -ForegroundColor Green
    }
    
    # Step 5: Run tests
    Write-Host "`n[5/5] Running test suite..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor DarkGray
    Write-Host ""
    
    Set-Location contracts
    python test_verification_flows.py
    $testExitCode = $LASTEXITCODE
    Set-Location ..
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor DarkGray
    
    # Step 6: Show results
    if ($testExitCode -eq 0) {
        Write-Host "`n✅ ALL TESTS PASSED!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  SOME TESTS FAILED" -ForegroundColor Yellow
        Write-Host "Check the output above for details" -ForegroundColor Yellow
    }
    
    # Step 7: Show backend logs
    Write-Host "`n[Backend Logs] Last 20 lines:" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor DarkGray
    
    $backendOutput = Receive-Job -Job $backendJob | Select-Object -Last 20
    if ($backendOutput) {
        $backendOutput | ForEach-Object { Write-Host $_ -ForegroundColor DarkGray }
    } else {
        Write-Host "No backend logs available yet" -ForegroundColor DarkGray
    }
    
    Write-Host "========================================" -ForegroundColor DarkGray
    
    # Ask user if they want to keep backend running
    Write-Host "`n"
    Write-Host "Backend is still running on http://localhost:8000" -ForegroundColor Green
    Write-Host ""
    $keepRunning = Read-Host "Keep backend running? (Y/n)"
    
    if ($keepRunning -eq "n" -or $keepRunning -eq "N") {
        Write-Host "Stopping backend..." -ForegroundColor Yellow
        Stop-Job -Job $backendJob
        Remove-Job -Job $backendJob
        Write-Host "✓ Backend stopped" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Backend will keep running in the background" -ForegroundColor Green
        Write-Host "To stop it later, run: Stop-Job -Id $($backendJob.Id)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Test the API manually:" -ForegroundColor Cyan
        Write-Host "  Invoke-RestMethod -Uri http://localhost:8000/api/verification/pricing" -ForegroundColor Gray
        Write-Host ""
    }
    
    exit $testExitCode
}
catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkRed
    
    Cleanup
    exit 1
}
finally {
    # Cleanup is handled by the registered event
}
