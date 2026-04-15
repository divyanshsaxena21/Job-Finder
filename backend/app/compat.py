"""
Version Compatibility Module

This module ensures the backend code works across multiple Python and
dependency versions without breaking changes.

Compatible Versions:
- Python: 3.8+
- FastAPI: 0.100+
- Pydantic: 2.0+
- Motor: 3.0+
- PyMongo: 4.0+
- PyJWT: 2.4+
- BCrypt: 3.2+
"""

import sys

# Python version check
PYTHON_VERSION = sys.version_info
if PYTHON_VERSION.major < 3 or (PYTHON_VERSION.major == 3 and PYTHON_VERSION.minor < 8):
    raise RuntimeError(f"Python 3.8+ required, got {PYTHON_VERSION.major}.{PYTHON_VERSION.minor}")


def check_imports():
    """Validate all critical imports are available"""
    required_modules = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'pydantic_settings',
        'motor',
        'pymongo',
        'bcrypt',
        'jwt',
        'email_validator',
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        raise ImportError(f"Missing required modules: {', '.join(missing)}")


__all__ = ['check_imports', 'PYTHON_VERSION']
