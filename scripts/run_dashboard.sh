#!/bin/bash

# AVA OS Dashboard Launcher for macOS/Linux

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Install Python 3.9+ from https://www.python.org or using:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu: sudo apt-get install python3"
    exit 1
fi

# Parse port argument
port=${1:-5000}

echo "Starting AVA OS Dashboard on http://localhost:$port"
echo "Press Ctrl+C to stop"
echo ""

python3 scripts/dashboard.py --port $port

if [ $? -ne 0 ]; then
    echo ""
    echo "Error running dashboard"
    exit 1
fi
