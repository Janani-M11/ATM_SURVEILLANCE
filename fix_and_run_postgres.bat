@echo off
echo ========================================
echo Fix PostgreSQL and Run Project
echo ========================================
echo.
echo This script will help you fix PostgreSQL authentication
echo and then set up the database.
echo.
pause

echo.
echo Step 1: Fix PostgreSQL Authentication
echo.
echo We need to temporarily disable password authentication.
echo.
set PG_HBA=C:\Program Files\PostgreSQL\17\data\pg_hba.conf
if not exist "%PG_HBA%" (
    set PG_HBA=C:\Program Files\PostgreSQL\16\data\pg_hba.conf
)
if not exist "%PG_HBA%" (
    set PG_HBA=C:\Program Files\PostgreSQL\15\data\pg_hba.conf
)

if not exist "%PG_HBA%" (
    echo ERROR: Could not find pg_hba.conf
    echo Please locate it manually
    pause
    exit /b 1
)

echo Found: %PG_HBA%
echo.
echo Please do this manually:
echo 1. Open this file as Administrator: %PG_HBA%
echo 2. Find: host    all    all    127.0.0.1/32    scram-sha-256
echo 3. Change to: host    all    all    127.0.0.1/32    trust
echo 4. Save the file
echo.
pause

echo.
echo Step 2: Restart PostgreSQL service...
net stop postgresql-x64-17
timeout /t 2 /nobreak >nul
net start postgresql-x64-17
echo Service restarted.
timeout /t 2 /nobreak >nul

echo.
echo Step 3: Fix postgres role and set password...
set PSQL="C:\Program Files\PostgreSQL\17\bin\psql.exe"
if not exist %PSQL% (
    set PSQL="C:\Program Files\PostgreSQL\16\bin\psql.exe"
)
if not exist %PSQL% (
    set PSQL="C:\Program Files\PostgreSQL\15\bin\psql.exe"
)

echo Running SQL commands...
%PSQL% -U postgres -c "ALTER ROLE postgres WITH LOGIN SUPERUSER;"
%PSQL% -U postgres -c "ALTER ROLE postgres WITH PASSWORD 'Sadh5518';"

if %errorlevel% equ 0 (
    echo SUCCESS: Password set!
) else (
    echo ERROR: Could not set password
    echo Please run manually: psql -U postgres
    pause
    exit /b 1
)

echo.
echo Step 4: Restore pg_hba.conf security...
echo Please change 'trust' back to 'scram-sha-256' in %PG_HBA%
echo Then restart PostgreSQL service.
echo.
pause

echo.
echo Step 5: Setting up database...
cd /d "%~dp0"
python setup_postgres.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS: Database setup complete!
    echo ========================================
    echo.
    echo Now starting the servers...
    echo.
    start "Backend Server" cmd /k "cd /d %~dp0 && python backend/app.py"
    timeout /t 3 /nobreak >nul
    start "Frontend Server" cmd /k "cd /d %~dp0\frontend && npm start"
    echo.
    echo Backend: http://localhost:5000
    echo Frontend: http://localhost:3000
    echo.
    echo Login: admin@atm.com / admin123
) else (
    echo ERROR: Database setup failed
)

pause



