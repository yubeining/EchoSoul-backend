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

# Start the application
echo "Starting EchoSoul HTTP server..."
python hello.py