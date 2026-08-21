#!/bin/bash

# AVA OS Chat Launcher for macOS/Linux

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Install Python 3.9+ from https://www.python.org or using:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu: sudo apt-get install python3"
    exit 1
fi

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Warning: ANTHROPIC_API_KEY is not set"
    echo "AVA won't be able to verify uncertain advice"
    echo "Get your key from: https://console.anthropic.com/account/keys"
    echo ""
    read -p "Enter your API key (or press Enter to skip): " api_key
    if [ ! -z "$api_key" ]; then
        export ANTHROPIC_API_KEY="$api_key"
    fi
fi

# Handle voice flag
if [ "$1" == "--voice" ]; then
    echo "Starting AVA OS with voice I/O..."
    python3 -m avaos.chat --voice
else
    echo "Starting AVA OS (text mode)"
    echo "Tip: Use './run_chat.sh --voice' for voice I/O"
    echo ""
    python3 -m avaos.chat
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "Error running AVA OS"
    exit 1
fi
