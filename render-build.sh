#!/usr/bin/env bash
set -e

echo "Starting Render build process..."

# Navigate to backend directory
cd backend

# Upgrade pip, setuptools, and wheel to latest versions
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install dependencies using only pre-built wheels (no build from source)
# This avoids issues with maturin and Rust compilation on read-only filesystem
echo "Installing Python dependencies..."
pip install --only-binary=:all: -r requirements.txt || \
pip install --prefer-binary -r requirements.txt || \
pip install -r requirements.txt

echo "✓ Build completed successfully!"
