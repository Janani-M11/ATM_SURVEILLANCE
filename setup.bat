@echo off
echo ========================================
echo ATM Surveillance System - Setup
echo ========================================
echo.

echo Setting up the project...
echo.

echo 1. Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    pause
    exit /b 1
)

echo.
echo 2. Database setup...
echo Choose database type:
echo [1] PostgreSQL (Recommended for production)
echo [2] SQLite (Quick setup for testing)
echo.
set /p db_choice="Enter choice (1 or 2): "

if "%db_choice%"=="1" (
    echo.
    echo Setting up PostgreSQL database...
    echo Make sure PostgreSQL is installed and running!
    echo.
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
        echo Then run: python setup_postgres.py
        pause
    )
    python setup_postgres.py
    if %errorlevel% neq 0 (
        echo Error setting up PostgreSQL database!
        echo Please check your PostgreSQL connection and .env configuration.
        pause
        exit /b 1
    )
) else (
    echo.
    echo Setting up SQLite database...
    python setup_sqlite.py
    if %errorlevel% neq 0 (
        echo Error setting up database!
        pause
        exit /b 1
    )
)

echo.
echo 3. Testing the system...
python test_system.py
if %errorlevel% neq 0 (
    echo System test failed!
    pause
    exit /b 1
)

echo.
echo 4. Installing frontend dependencies...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo Error installing frontend dependencies!
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the system:
echo 1. Backend: python backend/app.py
echo 2. Frontend: cd frontend && npm start
echo.
echo Login credentials:
echo Email: admin@atm.com
echo Password: admin123
echo.
pause
