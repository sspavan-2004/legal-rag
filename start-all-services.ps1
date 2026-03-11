# Start RAG Service and Chat Backend Together
# This script starts both services in separate windows

Write-Host "=== Starting Legal RAG System ===" -ForegroundColor Green

# Check if Python is available
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "Error: Python not found. Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

Write-Host "Using Python: $pythonCmd" -ForegroundColor Cyan

# Kill any existing Node.js processes
Write-Host "`nStopping existing Node.js processes..." -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start RAG Service in new window
Write-Host "`nStarting RAG Service (Python)..." -ForegroundColor Cyan
$ragServicePath = Join-Path $PSScriptRoot "rag-service"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ragServicePath'; Write-Host 'Installing dependencies...' -ForegroundColor Cyan; $pythonCmd -m pip install -r requirements.txt --quiet; Write-Host 'Starting RAG Service on port 8000...' -ForegroundColor Green; $pythonCmd server.py"

Start-Sleep -Seconds 3

# Start Backend (Node.js) in new window
Write-Host "Starting Chat Backend (Node.js)..." -ForegroundColor Cyan
$backendPath = Join-Path $PSScriptRoot "backend-mern"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host 'Starting backend on port 5001...' -ForegroundColor Green; npm run dev"

Start-Sleep -Seconds 3

# Start Frontend (React) in new window
Write-Host "Starting Frontend (React)..." -ForegroundColor Cyan
$frontendPath = Join-Path $PSScriptRoot "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host 'Starting frontend on port 5173...' -ForegroundColor Green; npm run dev"

Write-Host "`n=== All Services Started ===" -ForegroundColor Green
Write-Host "RAG Service:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Backend API:  http://localhost:5001" -ForegroundColor Cyan
Write-Host "Frontend:     http://localhost:5173" -ForegroundColor Cyan
Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
