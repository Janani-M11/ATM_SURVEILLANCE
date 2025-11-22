@echo off
echo ========================================
echo ATM Surveillance System - PostgreSQL Setup
echo ========================================
echo.

echo Setting up PostgreSQL database...
echo.

echo 1. Installing Python dependencies (including psycopg2)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    pause
    exit /b 1
)

echo.
echo 2. Checking .env file...
if not exist .env (
    echo Creating .env file template...
    echo DB_TYPE=postgresql > .env
    echo DB_HOST=localhost >> .env
    echo DB_PORT=5432 >> .env
    echo DB_USER=postgres >> .env
    echo DB_PASSWORD= >> .env
    echo DB_NAME=atm_surveillance >> .env
    echo.
    echo IMPORTANT: Please edit .env file and add your PostgreSQL password!
    echo File location: %CD%\.env
    echo.
    pause
)

echo.
echo 3. Setting up PostgreSQL database...
python setup_postgres.py
if %errorlevel% neq 0 (
    echo.
    echo Error setting up PostgreSQL database!
    echo.
    echo Please check:
    echo 1. PostgreSQL is installed and running
    echo 2. .env file has correct credentials
    echo 3. PostgreSQL user has CREATE DATABASE permission
    echo.
    echo For help, see POSTGRESQL_SETUP_GUIDE.md
    pause
    exit /b 1
)

echo.
echo ========================================
echo PostgreSQL setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Start backend: python backend/app.py
echo 2. Start frontend: cd frontend && npm start
echo.
echo Login credentials:
echo Email: admin@atm.com
echo Password: admin123
echo.
pause

