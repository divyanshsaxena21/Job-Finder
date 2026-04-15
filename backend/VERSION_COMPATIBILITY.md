# Version Independence Configuration

This backend is designed to work with flexible dependency versions to maximize compatibility across different deployment environments.

## Requirements Strategy

- **No strict version pins** - Uses `>=` constraints only where necessary
- **Broad compatibility** - Supports multiple versions of each dependency
- **Automatic validation** - Checks dependencies at startup

## Compatible Versions

### Python
- Minimum: **3.8**
- Recommended: **3.11+**
- Tested: 3.11, 3.12, 3.14

### Core Dependencies
- **FastAPI**: 0.100+
- **Uvicorn**: 0.20+
- **Pydantic**: 2.0+ (v2 features)
- **Motor**: 3.0+ (async MongoDB)
- **PyMongo**: 4.0+
- **PyJWT**: 2.4+
- **BCrypt**: 3.2+

### Additional Features
- **Groq**: Latest stable
- **python-telegram-bot**: Latest stable
- **aiohttp**: 3.8+
- **tenacity**: 8.0+
- **gunicorn**: 20.1+

## Deployment Notes

### Local Development
```bash
pip install -r backend/requirements.txt
python -m app.main
```

### Render Deployment
```bash
bash render-build.sh
```

The build script automatically:
1. Upgrades pip, setuptools, wheel
2. Installs dependencies with fallback strategies
3. Validates all imports at startup

### Vercel Deployment (Frontend Only)
Frontend deployment is handled separately on Vercel with its own package.json.

## Compatibility Features

The backend includes a compatibility layer (`app/compat.py`) that:
- ✅ Validates Python version (3.8+)
- ✅ Checks all critical imports
- ✅ Handles import path changes across versions
- ✅ Provides fallback imports for different package versions

## Troubleshooting

If you encounter version conflicts:

1. **Check Python version**: `python --version` (3.8+ required)
2. **Validate imports**: `python -c "from app.compat import check_imports; check_imports()"`
3. **Check installed packages**: `pip list`
4. **Upgrade pip**: `pip install --upgrade pip`

## Future-Proofing

As dependencies release new major versions, this codebase is designed to:
- Support new versions without breaking changes
- Maintain backward compatibility where possible
- Use stable, well-maintained APIs
- Avoid deprecated patterns
