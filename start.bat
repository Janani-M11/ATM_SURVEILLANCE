@echo off
echo ========================================
echo Starting ATM Surveillance System
echo ========================================
echo.

echo Starting backend server...
start "Backend Server" cmd /k "cd /d %~dp0 && python backend/app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting frontend...
start "Frontend Server" cmd /k "cd /d %~dp0\frontend && npm start"

echo.
echo ========================================
echo System started successfully!
echo ========================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Login credentials:
echo Email: admin@atm.com
echo Password: admin123
echo.
pause