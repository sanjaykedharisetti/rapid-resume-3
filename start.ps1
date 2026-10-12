Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "             MATCHLY AI - RESUME MATCHING SYSTEM                      " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

Write-Host "`n[1/3] Launching Backend Server on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; if (-not (Test-Path 'venv')) { Write-Host 'Creating virtual environment...' -ForegroundColor Green; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt } else { .\venv\Scripts\Activate.ps1 }; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Write-Host "[2/3] Launching Frontend Server on port 5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; if (-not (Test-Path 'node_modules')) { Write-Host 'Installing frontend packages...' -ForegroundColor Green; npm install }; npm run dev"

Write-Host "[3/3] Opening browser at http://localhost:5173 in 5 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host " All systems running!" -ForegroundColor Green
Write-Host " - Frontend: http://localhost:5173" -ForegroundColor White
Write-Host " - Backend:  http://localhost:8000" -ForegroundColor White
Write-Host " - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Green
