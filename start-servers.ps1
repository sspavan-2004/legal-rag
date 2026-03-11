# Kill any existing Node processes
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\spkmv\OneDrive\Desktop\LEGAL_RAG\backend-mern'; Write-Host 'Starting Backend...' -ForegroundColor Green; npm run dev"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\spkmv\OneDrive\Desktop\LEGAL_RAG\frontend'; Write-Host 'Starting Frontend...' -ForegroundColor Green; npm run dev"

Write-Host "`n✅ Servers are starting in separate windows..." -ForegroundColor Green
Write-Host "Backend: http://localhost:5001" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "`nWait 5-10 seconds for servers to fully start, then open http://localhost:5173`n" -ForegroundColor Yellow
