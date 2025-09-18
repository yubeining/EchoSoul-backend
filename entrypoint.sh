#!/bin/bash

# EchoSoul AI Platform Backend Service Entrypoint
# This script sets up the Python virtual environment and starts the service

set -e  # Exit on any error

echo "Starting EchoSoul AI Platform Backend Service..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing/updating dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Verify Python environment
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Start the FastAPI application with uvicorn
echo "Starting EchoSoul FastAPI server..."
echo "Server will be available at:"
echo "  - Main page: http://localhost:8080"
echo "  - API docs: http://localhost:8080/docs"
echo "  - ReDoc: http://localhost:8080/redoc"
echo "  - Health check: http://localhost:8080/health"

# Start with uvicorn for production
uvicorn hello:app --host 0.0.0.0 --port 8080 --workers 1