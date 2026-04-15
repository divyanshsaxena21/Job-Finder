#!/usr/bin/env bash
set -e

echo "Starting Render build process..."

# Navigate to backend directory
cd backend

# Upgrade pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install all Python dependencies
# Use --no-build-isolation to avoid read-only filesystem issues
echo "Installing Python dependencies..."
pip install --no-build-isolation -r requirements.txt

echo "✓ Build completed successfully!"
