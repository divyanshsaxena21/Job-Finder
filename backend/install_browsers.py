"""Install Playwright browsers on startup"""
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)


def install_playwright_browsers():
    """Install Playwright browsers if not already installed"""
    try:
        logger.info("Checking/Installing Playwright browsers...")
        # Install chromium browser (used by scrapers)
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info("✓ Playwright browsers installed successfully")
            return True
        else:
            logger.warning(f"⚠️ Playwright installation had issues: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("⚠️ Playwright installation timed out")
        return False
    except Exception as e:
        logger.error(f"⚠️ Failed to install Playwright browsers: {str(e)}")
        return False
