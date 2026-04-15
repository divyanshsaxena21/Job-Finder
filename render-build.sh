#!/usr/bin/env bash
set -e

echo "======================================"
echo "Job Finder Backend - Render Build"
echo "======================================"

# Navigate to backend directory
cd backend

# Step 1: Upgrade core tools
echo "📦 Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Step 2: Install dependencies
echo "📥 Installing Python dependencies..."
# Try multiple installation strategies for better compatibility
if ! pip install --prefer-binary -r requirements.txt; then
    echo "⚠️  Standard install failed, trying without binary constraint..."
    pip install -r requirements.txt
fi

# Step 3: Verify imports
echo "✅ Validating dependency installation..."
python -c "from app.compat import check_imports; check_imports(); print('✓ All dependencies verified')"

echo "======================================"
echo "✅ Build completed successfully!"
echo "======================================"
