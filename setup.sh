#!/bin/bash

echo "========================================"
echo "ATM Surveillance System - SQLite Version"
echo "========================================"
echo

echo "Setting up the project..."
echo

echo "1. Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error installing dependencies!"
    exit 1
fi

echo
echo "2. Setting up SQLite database..."
python setup_sqlite.py
if [ $? -ne 0 ]; then
    echo "Error setting up database!"
    exit 1
fi

echo
echo "3. Testing the system..."
python test_system.py
if [ $? -ne 0 ]; then
    echo "System test failed!"
    exit 1
fi

echo
echo "4. Installing frontend dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "Error installing frontend dependencies!"
    exit 1
fi
cd ..

echo
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo
echo "To start the system:"
echo "1. Backend: python backend/app.py"
echo "2. Frontend: cd frontend && npm start"
echo
echo "Login credentials:"
echo "Email: admin@atm.com"
echo "Password: admin123"
echo
