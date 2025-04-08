#!/bin/bash

echo "Installing Playwright dependencies..."
playwright install chromium

echo "Starting main script..."
python3 main.py
