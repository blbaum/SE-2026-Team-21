#!/bin/bash

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python3 not found!"; exit 1; }

# Check if pip exists
echo "Checking for pip..."
python3 -m pip --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "pip not found. Installing python3-pip..."
    sudo apt update
    sudo apt install -y python3-pip
fi

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
python3 -m pip install -r requirements.txt

# Check for tkinter and install if missing
echo "Checking for tkinter..."
python3 - <<END
try:
    import tkinter
    print("tkinter is already installed.")
except ImportError:
    print("WARNING: tkinter not found. Installing python3-tk...")
    import os
    os.system('sudo apt update && sudo apt install -y python3-tk')
END

echo "Installation complete!"
