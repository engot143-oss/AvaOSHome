@echo off
REM AVA OS Dashboard Launcher for Windows

setlocal enabledelayedexpansion

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

REM Parse port argument
set port=5000
if not "%1"=="" (
    set port=%1
)

echo Starting AVA OS Dashboard on http://localhost:%port%
echo Press Ctrl+C to stop
echo.

python scripts/dashboard.py --port %port%

if errorlevel 1 (
    echo.
    echo Error running dashboard
    pause
)
