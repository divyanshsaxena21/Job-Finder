"""
Ensure Playwright browsers are installed on startup
"""
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)


def ensure_playwright_installed():
    """Install Playwright browsers if not already installed"""
    try:
        logger.info("Checking if Playwright browsers are installed...")
        # Try to import playwright - if it fails, browsers aren't installed
        from playwright.async_api import async_playwright
        
        # Quick check: try to access a browser executable
        import os
        playwright_dir = os.path.expanduser("~/.cache/ms-playwright")
        
        if os.path.exists(playwright_dir) and os.listdir(playwright_dir):
            logger.info("✓ Playwright browsers already installed")
            return True
        
        logger.warning("Playwright browsers not found. Installing...")
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            logger.info("✓ Playwright browsers installed successfully")
            return True
        else:
            logger.error(f"Failed to install Playwright browsers: {result.stderr}")
            return False
            
    except Exception as e:
        logger.warning(f"Could not verify/install Playwright browsers: {str(e)}")
        # Don't fail startup, but log the warning
        return False


if __name__ == "__main__":
    ensure_playwright_installed()
