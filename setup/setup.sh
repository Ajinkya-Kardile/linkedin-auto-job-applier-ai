#!/bin/bash

echo "===================================================="
echo " Setting up linkedin-auto-job-applier-ai (Linux) "
echo "===================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 could not be found."
    echo "Please install Python 3.10 or higher and try again."
    exit 1
fi

echo "✅ Python 3 detected."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "⚡ Virtual environment already exists."
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and install dependencies
echo "⬇️ Installing project dependencies..."
pip install --upgrade pip
pip install .

echo "===================================================="
echo "🎉 Setup Complete! "
echo "To start using the bot, run the following command:"
echo "source .venv/bin/activate"
echo "python main.py"
echo "===================================================="