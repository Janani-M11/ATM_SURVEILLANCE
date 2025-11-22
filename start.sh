#!/bin/bash

echo "Starting ATM Surveillance System..."
echo

echo "Setting up database..."
python3 backend/setup_database.py
if [ $? -ne 0 ]; then
    echo "Database setup failed!"
    exit 1
fi

echo
echo "Starting Flask backend..."
cd backend
python3 app.py &
BACKEND_PID=$!

echo
echo "Waiting for backend to start..."
sleep 5

echo
echo "Starting React frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo
echo "ATM Surveillance System is starting..."
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo
echo "Login credentials:"
echo "Email: admin@atm.com"
echo "Password: admin123"
echo
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
