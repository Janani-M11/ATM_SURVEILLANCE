@echo off
echo ========================================
echo PostgreSQL Password Reset Script
echo ========================================
echo.
echo This script will temporarily disable password authentication
echo to allow you to change the PostgreSQL password.
echo.
echo WARNING: This modifies PostgreSQL configuration files.
echo Make sure you have administrator privileges.
echo.
pause

echo.
echo Step 1: Finding pg_hba.conf file...
set PG_HBA="C:\Program Files\PostgreSQL\17\data\pg_hba.conf"

REM Check if file exists, if not try other common locations
if not exist %PG_HBA% (
    set PG_HBA="C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
)
if not exist %PG_HBA% (
    set PG_HBA="C:\Program Files\PostgreSQL\15\data\pg_hba.conf"
)
if not exist %PG_HBA% (
    set PG_HBA="C:\Program Files\PostgreSQL\14\data\pg_hBA.conf"
)

if not exist %PG_HBA% (
    echo ERROR: Could not find pg_hba.conf file
    echo Please locate it manually and edit it.
    echo.
    echo Look for: C:\Program Files\PostgreSQL\[VERSION]\data\pg_hba.conf
    pause
    exit /b 1
)

echo Found: %PG_HBA%
echo.
echo Step 2: Creating backup...
copy %PG_HBA% "%PG_HBA%.backup" >nul
echo Backup created: %PG_HBA%.backup
echo.
echo Step 3: Modifying pg_hba.conf...
echo Please edit the file manually:
echo.
echo 1. Open as Administrator: %PG_HBA%
echo 2. Find line: host    all    all    127.0.0.1/32    scram-sha-256
echo 3. Change to: host    all    all    127.0.0.1/32    trust
echo 4. Save the file
echo.
pause

echo.
echo Step 4: Restarting PostgreSQL service...
echo Please run these commands as Administrator:
echo.
echo net stop postgresql-x64-17
echo net start postgresql-x64-17
echo.
pause

echo.
echo Step 5: Connect and change password...
echo Run these commands:
echo.
echo psql -U postgres
echo ALTER USER postgres WITH PASSWORD 'your_new_password';
echo \q
echo.
pause

echo.
echo Step 6: Restore pg_hba.conf...
echo After changing password, restore the original file:
echo.
echo copy "%PG_HBA%.backup" %PG_HBA%
echo.
echo Then change 'trust' back to 'scram-sha-256' and restart PostgreSQL.
echo.
pause


