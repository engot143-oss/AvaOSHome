@echo off
REM AVA OS Chat Launcher for Windows

setlocal enabledelayedexpansion

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if ANTHROPIC_API_KEY is set
if "!ANTHROPIC_API_KEY!"=="" (
    echo Warning: ANTHROPIC_API_KEY is not set
    echo AVA won't be able to verify uncertain advice
    echo Get your key from: https://console.anthropic.com/account/keys
    echo.
    set /p api_key="Enter your API key (or press Enter to skip): "
    if not "!api_key!"=="" (
        set ANTHROPIC_API_KEY=!api_key!
    )
)

REM Get voice flag
if "%1"=="--voice" (
    echo Starting AVA OS with voice I/O...
    python -m avaos.chat --voice
) else (
    echo Starting AVA OS (text mode)...
    echo Tip: Use 'run_chat.bat --voice' for voice I/O
    echo.
    python -m avaos.chat
)

if errorlevel 1 (
    echo.
    echo Error running AVA OS
    pause
)
