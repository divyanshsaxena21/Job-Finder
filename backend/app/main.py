from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.models.database import MongoDB
from app.api import auth, jobs, applications, preferences, auto_apply
from app.compat import check_imports
from app.scheduler import init_scheduler, stop_scheduler
from install_browsers import install_playwright_browsers

import logging

# Validate all dependencies are available
check_imports()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_allowed_origins() -> list:
    """Get list of allowed origins for CORS"""
    origins = settings.cors_origins_list
    return list(set(origins)) if origins else [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://job-finder-pearl.vercel.app",
        "https://job-finder-beta-seven.vercel.app"
    ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle: startup and shutdown"""
    
    # Startup
    logger.info("🚀 Starting Job Finder API...")
    
    # Install Playwright browsers (for job scrapers)
    install_playwright_browsers()
    
    await MongoDB.connect_db(settings.mongodb_url, settings.db_name)
    
    # Initialize scheduler for auto-apply tasks
    try:
        init_scheduler()
        logger.info("✓ Scheduler initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize scheduler: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Job Finder API...")
    stop_scheduler()
    await MongoDB.close_db()


# Create FastAPI app
app = FastAPI(
    title="Job Finder API",
    description="AI-powered job application assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow requests from frontend
allowed_origins = get_allowed_origins()
logger.info(f"✓ CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(preferences.router)
app.include_router(auto_apply.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Job Finder API",
        "description": "AI-powered job application assistant",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
