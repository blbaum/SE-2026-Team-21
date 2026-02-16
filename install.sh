#!/bin/bash

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python3 not found!"; exit 1; }

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
python3 -m pip install -r requirements.txt

echo "Installation complete!"

# Check for tkinter
python3 - <<END
try:
    import tkinter
except ImportError:
    print("WARNING: tkinter not found. On Linux, run: sudo apt-get install python3-tk")
END
