@echo off
echo ========================================
echo PostgreSQL Connection Fix Script
echo ========================================
echo.
echo This will help you fix PostgreSQL password authentication
echo.

echo Step 1: Checking PostgreSQL service...
sc query | findstr /i postgres
echo.

echo Step 2: Testing current connection...
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', user='postgres', password='S@dh551811'); print('Connection successful!')" 2>&1
if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Connection works! Password is correct.
    echo You can now run: python setup_postgres.py
    pause
    exit /b 0
)

echo.
echo Connection failed. Let's fix it...
echo.

echo Option 1: Try connecting with pgAdmin
echo - Open pgAdmin
echo - Try connecting with password: S@dh551811
echo - If it works, password is correct but connection method might be different
echo.
pause

echo.
echo Option 2: Reset password using pg_hba.conf
echo.
echo This will temporarily disable password authentication
echo so you can change the password.
echo.
set /p continue="Continue with password reset? (Y/N): "
if /i not "%continue%"=="Y" exit /b 0

echo.
echo Finding pg_hba.conf...
set PG_HBA=C:\Program Files\PostgreSQL\17\data\pg_hba.conf
if not exist "%PG_HBA%" (
    set PG_HBA=C:\Program Files\PostgreSQL\16\data\pg_hba.conf
)
if not exist "%PG_HBA%" (
    set PG_HBA=C:\Program Files\PostgreSQL\15\data\pg_hba.conf
)

if not exist "%PG_HBA%" (
    echo ERROR: Could not find pg_hba.conf
    echo Please locate it manually: C:\Program Files\PostgreSQL\[VERSION]\data\pg_hba.conf
    pause
    exit /b 1
)

echo Found: %PG_HBA%
echo.
echo Please do the following manually:
echo.
echo 1. Open this file as Administrator: %PG_HBA%
echo 2. Find line: host    all    all    127.0.0.1/32    scram-sha-256
echo 3. Change to: host    all    all    127.0.0.1/32    trust
echo 4. Save the file
echo 5. Restart PostgreSQL service
echo.
pause

echo.
echo Restarting PostgreSQL service...
for /f "tokens=*" %%i in ('sc query ^| findstr /i "postgres"') do (
    for /f "tokens=2" %%j in ("%%i") do (
        echo Stopping %%j...
        net stop "%%j"
        timeout /t 2 /nobreak >nul
        echo Starting %%j...
        net start "%%j"
    )
)

echo.
echo Now try connecting without password:
echo psql -U postgres
echo.
echo Then change password:
echo ALTER USER postgres WITH PASSWORD 'S@dh551811';
echo \q
echo.
pause

echo.
echo After changing password, restore pg_hba.conf:
echo Change 'trust' back to 'scram-sha-256'
echo Then restart PostgreSQL again
echo.
pause


