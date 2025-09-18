#!/bin/bash

# EchoSoul AI Platform Backend Service Entrypoint
# This script sets up the Python virtual environment and starts the service

set -e  # Exit on any error

echo "Starting EchoSoul AI Platform Backend Service..."

# Determine virtual environment path based on environment
if [ -d "/opt/venv" ]; then
    # Docker environment
    VENV_PATH="/opt/venv"
    echo "Detected Docker environment, using /opt/venv"
elif [ -d "venv" ]; then
    # Local development environment
    VENV_PATH="venv"
    echo "Detected local environment, using ./venv"
else
    # Create virtual environment if it doesn't exist
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    VENV_PATH="venv"
fi

# Activate virtual environment
echo "Activating virtual environment at: $VENV_PATH"
source $VENV_PATH/bin/activate

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