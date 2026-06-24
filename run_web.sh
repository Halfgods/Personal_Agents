#!/usr/bin/env bash

# Run the FastAPI server in the background
echo "Starting backend server..."
.venv/bin/python server.py &
BACKEND_PID=$!

# Run the Vite React frontend
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "Web application is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop."

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait
