#!/bin/bash

echo "✅ Instalace Playwrightu..."
playwright install chromium

echo "🚀 Spouštím skript..."
python3 main.py
