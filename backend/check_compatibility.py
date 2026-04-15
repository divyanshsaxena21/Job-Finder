#!/usr/bin/env python3
"""
Version Compatibility Checker

Run this script to verify your installation is compatible:
    python backend/check_compatibility.py
"""

import sys
import importlib
from typing import Tuple, List

def check_python_version() -> Tuple[bool, str]:
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    return False, f"❌ Python {version.major}.{version.minor} (requires 3.8+)"


def check_package(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        return True, f"✅ {package_name}: {version}"
    except ImportError:
        return False, f"❌ {package_name}: NOT INSTALLED"


def main():
    print("=" * 60)
    print("Job Finder Backend - Compatibility Check")
    print("=" * 60)
    print()
    
    # Check Python
    print("📌 Python Version")
    success, message = check_python_version()
    print(f"   {message}")
    if not success:
        sys.exit(1)
    print()
    
    # Check required packages
    packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('pydantic', 'pydantic'),
        ('pydantic-settings', 'pydantic_settings'),
        ('pymongo', 'pymongo'),
        ('motor', 'motor'),
        ('bcrypt', 'bcrypt'),
        ('python-dotenv', 'dotenv'),
        ('pyjwt', 'jwt'),
        ('email-validator', 'email_validator'),
        ('groq', 'groq'),
        ('python-telegram-bot', 'telegram'),
        ('aiohttp', 'aiohttp'),
        ('tenacity', 'tenacity'),
    ]
    
    print("📦 Required Packages")
    all_ok = True
    for pkg_name, import_name in packages:
        success, message = check_package(pkg_name, import_name)
        print(f"   {message}")
        if not success:
            all_ok = False
    print()
    
    # Check optional packages
    optional = [
        ('gunicorn', 'gunicorn'),
    ]
    
    print("🔧 Optional Packages")
    for pkg_name, import_name in optional:
        success, message = check_package(pkg_name, import_name)
        print(f"   {message}")
    print()
    
    if all_ok:
        print("=" * 60)
        print("✅ All required packages are installed!")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("❌ Some required packages are missing")
        print("   Run: pip install -r requirements.txt")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
