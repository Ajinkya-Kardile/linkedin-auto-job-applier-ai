@echo off
echo ====================================================
echo  Setting up linkedin-auto-job-applier-ai (Windows)
echo ====================================================

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [X] Error: Python could not be found.
    echo Please install Python 3.10 or higher, ensure "Add to PATH" is checked during installation, and try again.
    pause
    exit /b
)

echo [v] Python detected.

:: Create virtual environment if it doesn't exist
IF NOT EXIST ".venv\" (
    echo [i] Creating virtual environment ^(.venv^)...
    python -m venv .venv
) ELSE (
    echo [i] Virtual environment already exists.
)

:: Activate virtual environment
echo [i] Activating virtual environment...
call .venv\Scripts\activate.bat

:: Upgrade pip and install dependencies
echo [i] Installing project dependencies...
python -m pip install --upgrade pip
pip install .

echo ====================================================
echo [v] Setup Complete!
echo To start using the bot, activate your environment:
echo .venv\Scripts\activate
echo Then run: python main.py
echo ====================================================
pause