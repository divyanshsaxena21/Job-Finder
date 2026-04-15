#!/usr/bin/env bash
# Render build script

cd backend

# Upgrade pip to latest
pip install --upgrade pip

# Install dependencies with preference for wheels (no build from source)
pip install --prefer-binary -r requirements.txt

echo "Dependencies installed successfully!"
