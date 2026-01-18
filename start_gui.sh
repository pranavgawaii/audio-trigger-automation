#!/bin/bash

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

# Activate the virtual environment and run the GUI app
./venv/bin/python3 gui.py
