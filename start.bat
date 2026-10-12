@echo off
title Matchly AI Launcher
cls
echo ======================================================================
echo              MATCHLY AI - RESUME MATCHING SYSTEM
echo ======================================================================
echo.
echo [1/3] Launching Backend (FastAPI on http://localhost:8000)...
start "Matchly AI - Backend Server" cmd /k "cd /d ""%~dp0backend"" && if not exist venv (echo Setting up Python virtual environment... && python -m venv venv && call venv\Scripts\activate.bat && pip install -r requirements.txt) else (call venv\Scripts\activate.bat) && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/3] Launching Frontend (React + Vite on http://localhost:5173)...
start "Matchly AI - Frontend Server" cmd /k "cd /d ""%~dp0frontend"" && if not exist node_modules (echo Installing frontend dependencies... && npm install) && npm run dev"

echo [3/3] Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

echo Opening browser at http://localhost:5173 ...
start http://localhost:5173

echo.
echo ======================================================================
echo  All systems running!
echo  - Frontend Web App:  http://localhost:5173
echo  - Backend API:       http://localhost:8000
echo  - API Documentation: http://localhost:8000/docs
echo ======================================================================
echo.
echo (Keep the two opened terminal windows running while using the app)
pause
