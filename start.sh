#!/bin/bash

echo "🧪 Start.sh opravdu běží!"
playwright install chromium
echo "🚀 Spouštím skript..."
python3 main.py
