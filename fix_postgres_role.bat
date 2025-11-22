@echo off
echo ========================================
echo Fix PostgreSQL Role Issue
echo ========================================
echo.
echo This script will fix the postgres role to allow login.
echo.
echo The command you showed creates a role with NOLOGIN,
echo which prevents authentication. We need to fix this.
echo.
pause

echo.
echo Step 1: We need to temporarily disable password authentication
echo to fix the role issue.
echo.
echo Please edit pg_hba.conf:
echo Location: C:\Program Files\PostgreSQL\17\data\pg_hba.conf
echo.
echo Find line: host    all    all    127.0.0.1/32    scram-sha-256
echo Change to: host    all    all    127.0.0.1/32    trust
echo.
pause

echo.
echo Step 2: Restart PostgreSQL service...
echo.
set /p restart="Restart PostgreSQL service now? (Y/N): "
if /i "%restart%"=="Y" (
    echo Stopping PostgreSQL...
    net stop postgresql-x64-17
    timeout /t 2 /nobreak >nul
    echo Starting PostgreSQL...
    net start postgresql-x64-17
    echo Service restarted.
)

echo.
echo Step 3: Fix the postgres role...
echo.
set PSQL="C:\Program Files\PostgreSQL\17\bin\psql.exe"
if not exist %PSQL% (
    set PSQL="C:\Program Files\PostgreSQL\16\bin\psql.exe"
)
if not exist %PSQL% (
    set PSQL="C:\Program Files\PostgreSQL\15\bin\psql.exe"
)

if exist %PSQL% (
    echo Running SQL commands to fix role...
    %PSQL% -U postgres -f fix_postgres_role.sql
    if %errorlevel% equ 0 (
        echo.
        echo SUCCESS: Role fixed!
        echo.
        echo Now restore pg_hba.conf (change 'trust' back to 'scram-sha-256')
        echo and restart PostgreSQL service.
        echo.
    ) else (
        echo.
        echo ERROR: Could not fix role.
        echo Please run the SQL commands manually:
        echo psql -U postgres
        echo Then run the commands from fix_postgres_role.sql
    )
) else (
    echo ERROR: psql.exe not found.
    echo Please run manually:
    echo psql -U postgres
    echo Then run commands from fix_postgres_role.sql
)

pause



